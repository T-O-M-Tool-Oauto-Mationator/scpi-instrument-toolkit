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

import contextlib
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
    "classify_block",
    "not_repl_reason",
    "parametrize_ids",
    "run_block",
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
_SHELL_PREFIX_RE = re.compile(r"^(?:\$|pip|python|git|cd|export|mkdocs|pytest|mv|cp|rm|ls|cat|echo|curl)\b")
_OUTPUT_RE = re.compile(r"^(?:└|├|│|─|=>|\[PASS\]|\[FAIL\]|Output:|>>>|\.{3})")
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

RunResult = Literal["pass", "fail", "skip"]


def _docs_relative_path(source: Path) -> str:
    """Return ``docs/<rest>`` for a DocBlock source path.

    If a ``docs`` segment exists in the path, keep everything from that
    segment onward so nested subdirectories are preserved. Otherwise fall
    back to the basename (tests that construct DocBlocks with made-up
    paths still get a sensible string).
    """
    parts = source.parts
    for idx in range(len(parts) - 1, -1, -1):
        if parts[idx] == "docs":
            return "/".join(parts[idx:])
    return f"docs/{source.name}"


@dataclass(frozen=True)
class DocBlock:
    """A single fenced code block extracted from a markdown file."""

    source: Path
    start_line: int
    end_line: int
    lang: str
    lines: tuple[str, ...]
    directives: frozenset[str] = field(default_factory=frozenset)
    skip_reason: str | None = None
    is_setup: bool = False

    @property
    def runnable_lines(self) -> tuple[tuple[int, str], ...]:
        """Return ``(absolute_line_no, text)`` for each line that should be fed
        to ``onecmd``.

        Drops blank lines, ``#``-comment-only lines, and lines that look like
        sample output (leading ``└``, ``Output:``, etc.).
        """
        pairs: list[tuple[int, str]] = []
        for offset, raw in enumerate(self.lines):
            line_no = self.start_line + 1 + offset
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if _OUTPUT_RE.match(stripped):
                continue
            pairs.append((line_no, raw))
        return tuple(pairs)

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
