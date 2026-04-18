"""Doc-block extractor + runner for the REPL mkdocs examples.

Walks every ``docs/*.md`` file, pulls out fenced code blocks that look like
REPL script syntax, and feeds them line-by-line to ``InstrumentRepl.onecmd``
in mock mode. Used by both the standalone CLI (``scripts/validate_all_doc_examples.py``)
and the parametrized pytest harness (``tests/test_docs_examples_live.py``).

Opt-out markers live in HTML comments directly above the fence so they do not
render in the built docs:

    <!-- doc-test: skip reason="uses liveplot; needs GUI" -->

``<!-- doc-test: setup -->`` marks a per-file bootstrap block whose state
carries into the subsequent runnable blocks from the same file.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import re
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

__all__ = [
    "DocBlock",
    "iter_doc_files",
    "extract_blocks",
    "extract_indented_blocks",
    "extract_all_blocks",
    "classify_block",
    "classify_language",
    "not_repl_reason",
    "parametrize_ids",
    "run_block",
    "run_python_snippet",
    "RunResult",
]

# Doc files whose fenced examples are NOT REPL syntax. python.md is the Python
# API surface; the rest are reference/architecture pages without runnable REPL
# blocks.
EXCLUDED_FILES: frozenset[str] = frozenset(
    {
        "python.md",
        "index.md",
        "install.md",
        "instruments.md",
        "labview.md",
        "ni_pxie.md",
        "plotting.md",
        "troubleshooting.md",
        "architecture.md",
    }
)

# First token of each line is checked against this set to classify a fence as
# REPL-looking. Device aliases are matched via a regex below.
_REPL_KEYWORDS: frozenset[str] = frozenset(
    {
        "set",
        "get",
        "print",
        "log",
        "measure",
        "read",
        "write",
        "assert",
        "check",
        "calc",
        "plot",
        "liveplot",
        "wait",
        "sleep",
        "pause",
        "input",
        "for",
        "while",
        "if",
        "elif",
        "else",
        "end",
        "break",
        "continue",
        "repeat",
        "let",
        "var",
        "call",
        "run",
        "source",
        "include",
        "script",
        "save",
        "load",
        "export",
        "import",
        "enable",
        "disable",
        "reset",
        "beep",
        "idn",
        "query",
        "send",
        "config",
        "select",
        "use",
        "unset",
        "pyeval",
        "python",
        "data",
        "report",
        "help",
        "exit",
        "quit",
    }
)

_DEVICE_RE = re.compile(r"^(?:psu|dmm|scope|awg|smu|ev2300)\d*$")
_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z_0-9]*\s*(?:\+\+|--|[+\-*/%]?=)")
_SHELL_PREFIX_RE = re.compile(
    r"^(?:\$|pip|python3?|git|cd|export|mkdocs|pytest|mv|cp|rm|ls|cat|echo|curl|"
    r"ruff|scpi-repl|lab-instruments|source|make|sudo|brew|apt|choco|powershell)\b"
)
_OUTPUT_RE = re.compile(
    r"^(?:"
    r"└|├|│|─|"  # box-drawing characters from table/tree output
    r"=>|"  # literal arrow in output
    r"\[(?:PASS|FAIL|SUCCESS|ERROR|WARNING|INFO|OK|DEBUG)\]|"  # ColorPrinter status tags
    r"Output:|"
    r">>>|"  # Python REPL prompt in sample output
    r"eset>|"  # scpi-instrument-toolkit REPL prompt in sample output
    r"\(dbg\)|"  # script debugger prompt
    r"\.{3}"  # ellipsis continuation in truncated samples
    r")"
)
# Markdown / prose lines that should NOT count as REPL. When a large
# fraction of an indented block matches these (common in MkDocs tabbed
# sections whose body is all indented), we reject the block.
_PROSE_RE = re.compile(
    r"^(?:"
    r"\||"  # table rows start with |
    r"!!!\s|"  # MkDocs admonition (!!! note, !!! tip, ...)
    r"\*\*[^*]|"  # markdown bold header line
    r"-\s|"  # bullet-list item
    r"[0-9]+\.\s"  # numbered-list item
    r")"
)
# Placeholder syntax that marks a block as a SYNTAX reference, not runnable
# commands: <value>, [optional], <v|i>. These blocks show the shape of a
# command; the accompanying Examples block below is what students actually run.
#
# The pattern requires a placeholder-ish signal inside the brackets -- either
# whitespace (``<on|off>`` has none, ``<seconds>`` has none, but ``[name here]``
# does) or a ``|`` alternation (``<v|i>``). It also forbids the opening bracket
# from following an identifier character, so bare subscripts like ``xs[i]`` or
# ``d[key]`` inside real REPL code are NOT treated as placeholders.
_PLACEHOLDER_RE = re.compile(
    r"(?<![A-Za-z0-9_])<[A-Za-z_][A-Za-z0-9_]*(?:[| ][A-Za-z0-9_| ]*)?>"
    r"|(?<![A-Za-z0-9_\]])\[[A-Za-z_][A-Za-z0-9_]*(?:[| ][A-Za-z0-9_| ]*)?\]"
)
_FENCE_OPEN_RE = re.compile(r"^(\s*)```([A-Za-z0-9_-]*)\s*$")
_FENCE_CLOSE_RE = re.compile(r"^(\s*)```\s*$")
_SKIP_DIRECTIVE_RE = re.compile(r"<!--\s*doc-test:\s*(skip|setup)(?:\s+reason=\"([^\"]+)\")?\s*-->")
# CommonMark 4-space-indented code block opener.
_INDENT_RE = re.compile(r"^( {4}|\t)")
# Python-ish content markers -- if any line starts with these, the block is
# almost certainly Python rather than REPL syntax.
_PYTHON_HINT_RE = re.compile(r"^(?:import |from [\w.]+ import |def |class |@[A-Za-z_])")
# Broader body-level Python signals: common data-analysis recipes that chain
# pandas / matplotlib / numpy calls without an import line (they assume
# imports from an earlier snippet). These patterns don't appear in REPL
# grammar so catching them is safe.
_PYTHON_BODY_RE = re.compile(
    r"(?:"
    r"(?:^|\W)(?:pd|np|plt|df|sns|pltg)\.[A-Za-z_]|"  # attribute access on common aliases
    r"(?:^|\W)(?:df|runs|data|results|sweep)\[[\"'\w]"  # pandas-style subscript: df["col"]
    r"|\.(?:read_csv|read_json|read_excel|figure|subplots|xlabel|ylabel|title|legend|savefig|show|plot|hist|scatter|describe|groupby|to_csv)\("
    r"|\.iloc\[|\.loc\[|\.loc\s*=|\.append\("  # pandas indexing / builder
    r"|\[[^\]]*\bfor\b[^\]]*\bin\b[^\]]*\]"  # list/dict/set comprehension
    r"|\bwith\s+open\(|\bwith\s+[A-Za-z_][A-Za-z0-9_.]*\([^)]*\)\s+as\b"  # context manager
    r"|(?:^|[\s=(,])self\.[A-Za-z_]"  # self.attr after = / whitespace / open-paren / comma
    r"|\bf\"|\bf'"  # f-string prefix (unambiguous Python marker)
    r")"
)
# Line-starting keywords that indicate Python code -- anchored to line start
# so ``return`` in prose ("measurements return valid values") doesn't
# trigger. Used as a separate per-line check in classify_language.
_PYTHON_STATEMENT_RE = re.compile(r"^(?:return|raise|yield|except|finally|try:)\b")
# Third-party import prefixes we skip during import-resolution (so TA guide
# snippets don't require every analytics library to be installed).
_SKIP_IMPORT_PREFIXES = (
    "pandas",
    "numpy",
    "matplotlib",
    "scipy",
    "docx",
    "fpdf",
    "seaborn",
    "plotly",
    "pytest",
    "pyvisa",
)
# Markdown parent segments we recognize for short_id / error-location paths.
_RELATIVE_ROOTS: tuple[str, ...] = ("docs", "manuals")

RunResult = Literal["pass", "fail", "skip"]


def _docs_relative_path(source: Path) -> str:
    """Return ``<root>/<rest>`` for a DocBlock source path.

    Preserves whichever top-level segment (``docs`` or ``manuals``) the file
    lives under so nested subdirectories and sibling roots keep distinct IDs.
    Falls back to ``docs/<basename>`` if neither segment is found (e.g. tests
    that construct DocBlocks with synthetic paths).
    """
    parts = source.parts
    for idx in range(len(parts) - 1, -1, -1):
        if parts[idx] in _RELATIVE_ROOTS:
            return "/".join(parts[idx:])
    return f"docs/{source.name}"


@dataclass(frozen=True)
class DocBlock:
    """A single code block (fenced or indented) extracted from a markdown file.

    ``kind`` distinguishes triple-backtick fences from CommonMark 4-space
    indented blocks. Indented blocks carry their 4-space (or tab) prefix on
    every line of ``lines``; :attr:`runnable_lines` dedents them before they
    reach the runner. Fenced blocks preserve the author's indentation as-is.
    """

    source: Path
    start_line: int
    end_line: int
    lang: str
    lines: tuple[str, ...]
    directives: frozenset[str] = field(default_factory=frozenset)
    skip_reason: str | None = None
    is_setup: bool = False
    kind: Literal["fenced", "indented"] = "fenced"

    @property
    def runnable_lines(self) -> tuple[tuple[int, str], ...]:
        """Return ``(absolute_line_no, text)`` for each line that should be fed
        to ``onecmd``.

        Drops blank lines, ``#``-comment-only lines, and lines that look like
        sample output (leading ``└``, ``Output:``, etc.). For indented blocks
        also strips the leading 4-space/tab prefix so the runner sees the
        author's original content.
        """
        pairs: list[tuple[int, str]] = []
        for offset, raw in enumerate(self.lines):
            line_no = self.start_line + 1 + offset
            if self.kind == "indented":
                # Strip one leading indent unit (4 spaces or a tab). Lines
                # that don't start with it are blank markdown separators.
                if raw.startswith("    "):
                    raw_for_run = raw[4:]
                elif raw.startswith("\t"):
                    raw_for_run = raw[1:]
                else:
                    raw_for_run = raw
            else:
                raw_for_run = raw
            stripped = raw_for_run.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if _OUTPUT_RE.match(stripped):
                continue
            pairs.append((line_no, raw_for_run))
        return tuple(pairs)

    @property
    def dedented_text(self) -> str:
        """Full body text with indent prefix stripped. Used by the Python runner."""
        if self.kind != "indented":
            return "\n".join(self.lines)
        out: list[str] = []
        for raw in self.lines:
            if raw.startswith("    "):
                out.append(raw[4:])
            elif raw.startswith("\t"):
                out.append(raw[1:])
            else:
                out.append(raw)
        return "\n".join(out)

    @property
    def short_id(self) -> str:
        """Stable pytest node ID / error location tag for this block.

        Uses the path starting at the last ``docs`` segment so nested
        subdirectories (``docs/api/foo.md`` vs ``docs/foo.md``) keep distinct
        IDs -- otherwise two basename-equal files collide under the same
        pytest parametrize ID and their error messages become ambiguous.
        """
        return f"{_docs_relative_path(self.source)}:L{self.start_line}-L{self.end_line}"


def iter_doc_files(docs_dir: Path) -> Iterator[Path]:
    """Yield every ``docs/**/*.md`` file that might contain REPL blocks.

    Scans recursively so nested subdirectories (e.g. ``docs/api/*.md``) are
    included. Files whose *basename* is in :data:`EXCLUDED_FILES` are skipped
    regardless of their depth.
    """
    for path in sorted(docs_dir.rglob("*.md")):
        if path.name in EXCLUDED_FILES:
            continue
        yield path


def extract_blocks(md_path: Path) -> list[DocBlock]:
    """Parse ``md_path`` and return all fenced code blocks as ``DocBlock``s.

    Reads HTML ``<!-- doc-test: ... -->`` directives on the line(s) directly
    preceding each fence (blank lines between the comment and the fence are
    tolerated).
    """
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    blocks: list[DocBlock] = []

    i = 0
    while i < len(lines):
        open_match = _FENCE_OPEN_RE.match(lines[i])
        if not open_match:
            i += 1
            continue
        fence_indent = open_match.group(1)
        lang = open_match.group(2) or ""
        start = i + 1  # 1-based line number of opening fence
        # Walk backwards over blank lines and HTML comments to collect directives.
        directives: set[str] = set()
        skip_reason: str | None = None
        is_setup = False
        j = i - 1
        while j >= 0 and lines[j].strip() == "":
            j -= 1
        # At most three contiguous comment lines are scanned so a long
        # prose block of HTML comments above an unrelated fence can't
        # silently feed directives into it.
        comments_seen = 0
        while j >= 0 and lines[j].lstrip().startswith("<!--") and comments_seen < 3:
            m = _SKIP_DIRECTIVE_RE.search(lines[j])
            if m:
                directive = m.group(1)
                directives.add(directive)
                if directive == "skip":
                    skip_reason = m.group(2)
                elif directive == "setup":
                    is_setup = True
            j -= 1
            comments_seen += 1

        # Collect body until matching closing fence at same indent.
        body: list[str] = []
        k = i + 1
        while k < len(lines):
            close = _FENCE_CLOSE_RE.match(lines[k])
            if close and close.group(1) == fence_indent:
                break
            body.append(lines[k])
            k += 1
        end = k + 1  # 1-based line number of closing fence
        blocks.append(
            DocBlock(
                source=md_path,
                start_line=start,
                end_line=end,
                lang=lang,
                lines=tuple(body),
                directives=frozenset(directives),
                skip_reason=skip_reason,
                is_setup=is_setup,
            )
        )
        i = k + 1

    return blocks


def extract_indented_blocks(md_path: Path, exclude_ranges: Iterable[tuple[int, int]] = ()) -> list[DocBlock]:
    """Parse *md_path* for CommonMark 4-space-indented code blocks.

    An indented block opens on the first indented line that follows at least
    one blank line (standard CommonMark rule) and closes on the first
    non-indented, non-blank line. Leading-indent-only blank lines inside the
    block are preserved so a snippet's own blank separators survive.

    *exclude_ranges* is an iterable of ``(start_line, end_line)`` 1-based
    inclusive ranges to skip -- typically the ranges already covered by
    fenced blocks, so a fenced block inside an MkDocs tabbed section
    (``=== "Tab"`` with 4-space indented content) isn't double-captured as
    both fenced AND indented.

    Skip/setup directives are read from HTML comments immediately above the
    opening indented line, same three-line cap as fenced extraction.
    """
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    blocks: list[DocBlock] = []

    # Build a fast per-line mask of lines already covered by fenced blocks.
    # Use 0-based offsets into `lines`; fenced ranges are 1-based inclusive.
    excluded = bytearray(len(lines))  # 0 => not excluded, 1 => excluded
    for start, end in exclude_ranges:
        lo = max(0, start - 1)
        hi = min(len(lines), end)
        for k in range(lo, hi):
            excluded[k] = 1

    i = 0
    prev_was_blank = True  # treat start-of-file as "blank"
    while i < len(lines):
        line = lines[i]
        if excluded[i]:
            # Fenced block already covers this line; treat its boundary line
            # as "blank" for the purposes of the next indented block opener.
            prev_was_blank = True
            i += 1
            continue
        if not prev_was_blank or not _INDENT_RE.match(line):
            prev_was_blank = line.strip() == ""
            i += 1
            continue
        # Block opens on `i`. Scan forward to the first non-indented non-blank
        # line, keeping blank lines inside the block only if they are followed
        # by more indented content (otherwise CommonMark treats them as the
        # separator that ends the block). Also stop at any line already
        # captured by a fenced block -- an indented block should never swallow
        # a sibling fenced block that happens to share indentation (common in
        # MkDocs tabbed sections).
        body: list[str] = []
        start = i + 1  # 1-based
        k = i
        while k < len(lines):
            if excluded[k]:
                break
            cur = lines[k]
            if _INDENT_RE.match(cur):
                body.append(cur)
                k += 1
                continue
            if cur.strip() == "":
                # Tentatively include the blank; commit only if an indented
                # non-excluded line follows.
                look = k + 1
                while look < len(lines) and lines[look].strip() == "":
                    look += 1
                if look < len(lines) and not excluded[look] and _INDENT_RE.match(lines[look]):
                    body.extend(lines[k:look])
                    k = look
                    continue
                break
            break
        end = k  # 1-based = number of lines from start up to but not incl. k
        # Trim trailing blank-indent pad lines from body.
        while body and body[-1].strip() == "":
            body.pop()
        if not body:
            prev_was_blank = True
            i = k
            continue

        # Walk backward for doc-test directives on HTML comment lines above.
        directives: set[str] = set()
        skip_reason: str | None = None
        is_setup = False
        j = i - 1
        while j >= 0 and lines[j].strip() == "":
            j -= 1
        comments_seen = 0
        while j >= 0 and lines[j].lstrip().startswith("<!--") and comments_seen < 3:
            m = _SKIP_DIRECTIVE_RE.search(lines[j])
            if m:
                directive = m.group(1)
                directives.add(directive)
                if directive == "skip":
                    skip_reason = m.group(2)
                elif directive == "setup":
                    is_setup = True
            j -= 1
            comments_seen += 1

        blocks.append(
            DocBlock(
                source=md_path,
                start_line=start,
                end_line=end,
                lang="",
                lines=tuple(body),
                directives=frozenset(directives),
                skip_reason=skip_reason,
                is_setup=is_setup,
                kind="indented",
            )
        )
        prev_was_blank = True
        i = k

    return blocks


def extract_all_blocks(md_path: Path) -> list[DocBlock]:
    """Return all code blocks in *md_path* (fenced + indented) sorted by line.

    Fenced blocks take precedence: ranges covered by a triple-backtick fence
    are excluded from indented-block detection, preventing double-capture
    when MkDocs tabbed sections (``=== "Tab"`` indent nested fenced blocks
    4 spaces) surface those fences as spurious indented candidates.
    """
    fenced = extract_blocks(md_path)
    fenced_ranges = [(b.start_line, b.end_line) for b in fenced]
    indented = extract_indented_blocks(md_path, exclude_ranges=fenced_ranges)
    combined = fenced + indented
    combined.sort(key=lambda b: b.start_line)
    return combined


def not_repl_reason(block: DocBlock) -> str | None:
    """Return the first reason ``block`` fails the REPL-content heuristic.

    ``None`` means the block looks like REPL content. A non-None string is a
    short label used for observability (``--show-skipped`` in the CLI, debug
    listings) so doc coverage regressions are noticeable.
    """
    if block.lang not in ("", "text", "bash", "scpi-repl"):
        return f"fence lang {block.lang!r} not allowed"

    non_blank = [raw.strip() for raw in block.lines if raw.strip()]
    if not non_blank:
        return "empty block"

    non_comment = [s for s in non_blank if not s.startswith("#")]
    if not non_comment:
        return "all lines are comments"

    first = non_comment[0]
    if _SHELL_PREFIX_RE.match(first):
        return f"shell prefix: {first[:40]!r}"

    output_hits = sum(1 for s in non_blank if _OUTPUT_RE.match(s))
    if output_hits / max(len(non_blank), 1) >= 0.3:
        return "looks like sample output (>=30% output-like lines)"

    # MkDocs tabbed sections indent everything under ``=== "Tab"`` by 4
    # spaces, which our indented-block extractor grabs even when the body
    # is prose, tables, or admonitions. If a large fraction of lines look
    # like markdown/prose, reject the block so only genuine REPL code runs.
    prose_hits = sum(1 for s in non_blank if _PROSE_RE.match(s))
    if prose_hits / max(len(non_blank), 1) >= 0.3:
        return "looks like markdown prose / table / admonition"

    # Reject syntax-reference blocks containing <placeholder> or [optional]
    # tokens: those demonstrate the shape of a command rather than being
    # literal commands.
    for s in non_comment:
        m = _PLACEHOLDER_RE.search(s)
        if m:
            return f"placeholder syntax: {m.group(0)!r}"

    for stripped in non_comment:
        token = stripped.split(None, 1)[0].lower()
        if token in _REPL_KEYWORDS:
            return None
        if _DEVICE_RE.match(token):
            return None
        if _ASSIGN_RE.match(stripped):
            return None

    return f"no REPL keyword / device / assignment found (first line: {first[:40]!r})"


def _looks_like_repl(block: DocBlock) -> bool:
    """Back-compat boolean wrapper around :func:`not_repl_reason`."""
    return not_repl_reason(block) is None


def classify_block(block: DocBlock) -> Literal["run", "skip", "not-repl", "setup"]:
    """Decide what to do with a block.

    * ``setup`` -- bootstrap REPL state for the rest of the file.
    * ``skip``  -- explicitly opted out via ``<!-- doc-test: skip reason=... -->``.
    * ``not-repl`` -- does not look like REPL script content.
    * ``run``   -- execute line-by-line and assert no error is reported.
    """
    if block.is_setup:
        return "setup"
    if "skip" in block.directives:
        return "skip"
    if not _looks_like_repl(block):
        return "not-repl"
    return "run"


def classify_language(block: DocBlock) -> Literal["repl", "python", "shell", "reference"]:
    """Classify a block's content language for routing to the right runner.

    The REPL harness already dispatches ``run`` vs ``not-repl`` via
    :func:`classify_block`; this helper adds a finer split:

    * ``"python"`` -- fence tag ``python`` OR body contains Python-ish syntax
      (``import X``, ``from X import Y``, ``def``, ``class``, decorators).
    * ``"shell"`` -- first non-comment line starts with a shell prefix
      (same regex the REPL classifier uses, which is why those already fall
      through to ``not-repl`` today -- we just surface "shell" for reporting).
    * ``"repl"`` -- passes the existing REPL heuristic.
    * ``"reference"`` -- everything else (ASCII tables, sample output).

    Explicit fence tags are trusted: a ``text`` / ``bash`` / ``scpi-repl`` tag
    means the author declared REPL/shell intent even if the body happens to
    start with an identifier that could be read as Python (e.g. the REPL
    grammar's ``import`` directive).
    """
    if block.lang == "python":
        return "python"
    if block.lang in ("bash", "shell", "sh", "console"):
        return "shell"
    # Explicit REPL fence tag: don't second-guess into Python.
    if block.lang in ("text", "scpi-repl"):
        if _looks_like_repl(block):
            return "repl"
        return "reference"

    non_blank = [raw.strip() for raw in block.lines if raw.strip()]
    if not non_blank:
        return "reference"
    non_comment = [s for s in non_blank if not s.startswith("#")]
    sample = non_comment or non_blank

    for line in sample:
        if _PYTHON_HINT_RE.match(line):
            return "python"
        if _PYTHON_STATEMENT_RE.match(line):
            return "python"

    # Body-level Python signals (pandas/numpy/matplotlib recipes that assume
    # imports from an earlier block). Match against any non-blank line.
    for line in non_blank:
        if _PYTHON_BODY_RE.search(line):
            return "python"

    # Shell detection: first non-comment line's leading token.
    if sample and _SHELL_PREFIX_RE.match(sample[0]):
        return "shell"

    if _looks_like_repl(block):
        return "repl"
    return "reference"


def run_python_snippet(block: DocBlock) -> tuple[RunResult, str]:
    """Validate a Python-language block.

    Two cheap, side-effect-free checks:

    1. ``ast.parse`` -- catches syntax errors with real line numbers.
    2. For every ``import`` / ``from ... import`` node that references a
       ``lab_instruments.*`` module, resolve the module via
       :func:`importlib.util.find_spec` and confirm each imported symbol
       actually exists on it. Third-party imports (pandas, matplotlib,
       pytest, etc.) are ignored so snippets stay runnable without the
       full analysis stack installed.

    Does not execute the snippet. For hardware-driving examples that would
    be unsafe or impractical to exec, that restraint is the whole point.
    """
    text = block.dedented_text
    if not text.strip():
        return "skip", "empty python block"

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        # exc.lineno is 1-based inside the snippet; translate to markdown line.
        rel_line = exc.lineno or 1
        abs_line = block.start_line + rel_line
        return (
            "fail",
            f"{block.short_id}:L{abs_line}: SyntaxError: {exc.msg}",
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                err = _check_import(alias.name, None, block, node.lineno)
                if err:
                    return "fail", err
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue  # relative import without module; skip
            for alias in node.names:
                err = _check_import(node.module, alias.name, block, node.lineno)
                if err:
                    return "fail", err

    return "pass", ""


def _check_import(module: str, symbol: str | None, block: DocBlock, rel_line: int) -> str | None:
    """Return a ``"fail"`` message if *module*(.*symbol*) can't be resolved, else None."""
    # Skip third-party and stdlib-ish modules we don't vendor.
    top = module.split(".", 1)[0]
    if top in _SKIP_IMPORT_PREFIXES:
        return None
    if top != "lab_instruments":
        return None  # only strict-check our own package

    abs_line = block.start_line + rel_line
    try:
        spec = importlib.util.find_spec(module)
    except (ImportError, ValueError) as exc:
        return f"{block.short_id}:L{abs_line}: ModuleNotFoundError: {module!r} ({exc})"
    if spec is None:
        return f"{block.short_id}:L{abs_line}: ModuleNotFoundError: no module named {module!r}"

    if symbol is None or symbol == "*":
        return None
    try:
        mod = importlib.import_module(module)
    except Exception as exc:  # pragma: no cover -- defensive; importable-but-broken
        return f"{block.short_id}:L{abs_line}: ImportError resolving {module!r}: {exc}"
    if not hasattr(mod, symbol):
        return f"{block.short_id}:L{abs_line}: ImportError: cannot import name {symbol!r} from {module!r}"
    return None


def parametrize_ids(blocks: Iterable[DocBlock]) -> list[str]:
    return [b.short_id for b in blocks]


# ---------------------------------------------------------------------------
# Block runner -- shared by pytest harness and standalone CLI.
# ---------------------------------------------------------------------------


def _build_mock_repl():
    """Create an ``InstrumentRepl`` wired to ONE mock device per instrument type.

    Docs examples that use the bare ``psu`` / ``dmm`` / ``scope`` / ``awg``
    aliases expect a single-instrument session; a multi-instrument mock
    breaks those examples with an "ambiguous device" warning. We therefore
    instantiate exactly one of each supported type so ``psu set 1 5.0``
    unambiguously targets the sole PSU.
    """
    from lab_instruments.mock_instruments import (
        MockDSOX1204G,
        MockEDU33212A,
        MockEV2300,
        MockHP_34401A,
        MockHP_E3631A,
        MockNI_PXIe_4139,
    )
    from lab_instruments.repl.shell import InstrumentRepl
    from lab_instruments.src import discovery as _disc

    # Consistent numbered aliases for every device type. Bare forms
    # (``psu``, ``smu``, ``ev2300``) still resolve via the registry's
    # base-type fallback, so both ``smu set ...`` and ``smu1 set ...`` work.
    devices = {
        "psu1": MockHP_E3631A(),
        "dmm1": MockHP_34401A(),
        "scope1": MockDSOX1204G(),
        "awg1": MockEDU33212A(),
        "smu1": MockNI_PXIe_4139(),
        "ev23001": MockEV2300(),
    }

    _orig_init = _disc.InstrumentDiscovery.__init__
    _orig_scan = _disc.InstrumentDiscovery.scan

    # NOTE: class-level monkeypatch is process-wide. This is safe for
    # pytest-xdist (separate processes) but NOT for concurrent in-process
    # REPL construction. The validator and the pytest harness both run
    # single-threaded, so this is fine in practice.
    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices
    try:
        # auto_scan=False skips the background-scan thread + per-block safe_all
        # noise. We attach the mock devices directly to the registry instead.
        repl = InstrumentRepl(register_lifecycle=False, auto_scan=False)
    finally:
        _disc.InstrumentDiscovery.__init__ = _orig_init
        _disc.InstrumentDiscovery.scan = _orig_scan

    repl.ctx.registry.devices.update(devices)
    return repl


def run_block(block: DocBlock, repl=None) -> tuple[RunResult, str]:
    """Execute a single ``DocBlock``. Returns ``(status, message)``.

    * ``status`` is ``"pass"`` / ``"fail"`` / ``"skip"``.
    * ``message`` is a human-readable explanation; empty on pass.

    If ``repl`` is passed, state is reused (used for ``setup`` blocks that
    share context with subsequent run-blocks from the same file). Otherwise
    a fresh REPL is built and closed on exit.
    """
    kind = classify_block(block)
    if kind == "not-repl":
        return "skip", "not REPL content"
    if kind == "skip":
        reason = block.skip_reason or "no reason given"
        return "skip", reason

    owns_repl = repl is None
    if owns_repl:
        repl = _build_mock_repl()
    try:
        ctx = repl.ctx
        ctx.command_had_error = False
        # Prior test state may have stamped a source/line; clear it so the
        # doc block gets a clean location. Preserve subdirectory info so
        # nested docs (``docs/api/foo.md``) don't collide with top-level
        # files of the same basename.
        ctx.current_script_source = _docs_relative_path(block.source)

        for line_no, raw in block.runnable_lines:
            ctx.current_script_line = line_no
            ctx.command_had_error = False
            # Capture any error message that ctx.report_error emits by reading
            # the terminal buffer post-call. We rely on command_had_error as
            # the primary signal; the message is printed by ColorPrinter.
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    repl.onecmd(raw)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as exc:  # pragma: no cover -- last-line safety net
                    # Forward any output captured before the crash so pytest /
                    # the CLI see everything that printed prior to the fault.
                    sys.stdout.write(buf.getvalue())
                    return (
                        "fail",
                        f"{block.short_id}:L{line_no}: uncaught {type(exc).__name__}: {exc}",
                    )
            if ctx.command_had_error:
                # Error was already formatted onto stdout; relay the captured
                # message so the test failure shows the Python-style error.
                captured = buf.getvalue()
                # Strip ANSI colors for readable assertion output.
                captured = re.sub(r"\x1b\[[0-9;]*m", "", captured).strip()
                return (
                    "fail",
                    f"{block.short_id}:L{line_no}: {captured}",
                )
            # Forward stdout captured this iteration (print output, etc.)
            sys.stdout.write(buf.getvalue())
        return "pass", ""
    finally:
        if owns_repl:
            with contextlib.suppress(Exception):
                repl.close()


def collect_runnable_blocks(docs_dir: Path) -> list[DocBlock]:
    """Convenience: all blocks across all docs classified as ``run`` or ``setup``."""
    out: list[DocBlock] = []
    for md in iter_doc_files(docs_dir):
        for block in extract_blocks(md):
            if classify_block(block) in ("run", "setup"):
                out.append(block)
    return out
