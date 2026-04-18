"""Parametrized pytest harness that executes every REPL-looking code block
in ``docs/*.md`` **and** every block in the manuals under ``manuals/**/*.md``.

Blocks are grouped per source file. For each file the harness builds one
mock REPL, then feeds the classified blocks in document order so
``<!-- doc-test: setup -->`` blocks can prime state used by subsequent
``run`` blocks -- this matches the behavior of
``scripts/validate_all_doc_examples.py``.

Each ``run`` block becomes its own pytest node whose ID is shaped
``<root>/FILE.md:Lstart-Lend``. Python-language blocks (detected by fence
tag or body heuristics) get their own parametrized test function
(:func:`test_python_snippet`) that validates syntax + ``lab_instruments.*``
imports without executing the code.

Skip a block explicitly with an HTML comment directly above its fence
(or blank line above an indented block):

    <!-- doc-test: skip reason="requires GUI liveplot" -->
    ```text
    liveplot ...
    ```
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from pathlib import Path

import pytest

from lab_instruments._docs_extract import (
    DocBlock,
    _build_mock_repl,
    classify_block,
    classify_language,
    extract_all_blocks,
    iter_doc_files,
    run_block,
    run_python_snippet,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Roots scanned by pytest collection. docs/ is the public mkdocs site; the
# manuals/ directories carry PR #83's standalone student + TA references.
_DOC_ROOTS: tuple[Path, ...] = (
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "manuals" / "student",
    PROJECT_ROOT / "manuals" / "ta-developer",
)


@dataclass(frozen=True)
class _FileGroup:
    """All blocks for a single markdown file, in document order."""

    source: Path
    blocks: tuple[DocBlock, ...]


def _collect_groups() -> list[_FileGroup]:
    groups: list[_FileGroup] = []
    for root in _DOC_ROOTS:
        if not root.is_dir():
            continue
        for md in iter_doc_files(root):
            blocks = tuple(extract_all_blocks(md))
            # Only keep groups with at least one testable block (REPL or Python).
            has_testable = any(
                classify_block(b) in ("run", "setup") or classify_language(b) == "python" for b in blocks
            )
            if has_testable:
                groups.append(_FileGroup(source=md, blocks=blocks))
    return groups


_GROUPS = _collect_groups()


# ---------------------------------------------------------------------------
# File-group fixture: builds one mock REPL per file, runs every ``setup``
# block eagerly so subsequent ``run`` blocks (which are each their own pytest
# node) can assume the primed state.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _file_repls():
    """Lazy per-file REPL cache; built on first demand, closed at teardown.

    A ``None`` entry means "no setup blocks in this file; each run block
    builds its own REPL". A :data:`_SETUP_FAILED` sentinel means "the file's
    setup chain failed -- skip the remaining run blocks cleanly".
    """
    cache: dict[Path, object] = {}
    yield cache
    for repl in cache.values():
        if repl is None or repl is _SETUP_FAILED:
            continue
        with contextlib.suppress(Exception):
            repl.close()


_UNSET = object()  # sentinel for "group not yet seen" in the cache
_SETUP_FAILED = object()  # sentinel stored in the cache when setup fails


def _get_shared_repl(group: _FileGroup, file_repls):
    """Return (repl, setup_failed) for *group*.

    Mirrors the CLI's behavior in ``scripts/validate_all_doc_examples.py``:
    only files with ``<!-- doc-test: setup -->`` blocks chain state across
    run blocks. For files without setup blocks ``repl`` is ``None`` so
    :func:`run_block` will build a fresh isolated REPL per block.
    """
    cache = file_repls
    cached = cache.get(group.source, _UNSET)
    if cached is _SETUP_FAILED:
        return None, True
    if cached is not _UNSET:
        return cached, False
    has_setup = any(classify_block(b) == "setup" for b in group.blocks)
    if not has_setup:
        cache[group.source] = None
        return None, False
    repl = _build_mock_repl()
    # Run every ``setup`` block eagerly in document order. If any setup
    # block fails, mark the group so subsequent run blocks skip cleanly
    # instead of cascading.
    for block in group.blocks:
        if classify_block(block) != "setup":
            continue
        status, message = run_block(block, repl=repl)
        if status == "fail":
            with contextlib.suppress(Exception):
                repl.close()
            cache[group.source] = _SETUP_FAILED
            pytest.fail(
                f"setup block failed: {block.short_id}: {message}",
                pytrace=False,
            )
    cache[group.source] = repl
    return repl, False


# ---------------------------------------------------------------------------
# Parametrization: emit one test per ``run`` block, carrying its file group
# so the shared REPL is built lazily by `_get_shared_repl`.
# ---------------------------------------------------------------------------


def _enumerate_run_blocks() -> list[tuple[_FileGroup, DocBlock]]:
    pairs: list[tuple[_FileGroup, DocBlock]] = []
    for group in _GROUPS:
        for block in group.blocks:
            # Python-language blocks route to test_python_snippet instead.
            if classify_language(block) == "python":
                continue
            if classify_block(block) == "run":
                pairs.append((group, block))
    return pairs


def _enumerate_python_blocks() -> list[DocBlock]:
    out: list[DocBlock] = []
    for group in _GROUPS:
        for block in group.blocks:
            if classify_language(block) != "python":
                continue
            kind = classify_block(block)
            if kind in ("skip", "setup"):
                continue
            out.append(block)
    return out


_RUN_PAIRS = _enumerate_run_blocks()
_PY_BLOCKS = _enumerate_python_blocks()


@pytest.mark.parametrize(
    ("group", "block"),
    _RUN_PAIRS,
    ids=[block.short_id for _, block in _RUN_PAIRS],
)
def test_doc_block(group: _FileGroup, block: DocBlock, _file_repls) -> None:
    """Run one REPL block; shares REPL state with the file's setup blocks."""
    repl, setup_failed = _get_shared_repl(group, _file_repls)
    if setup_failed:
        pytest.skip(f"setup block for {group.source.name} failed earlier")
    status, message = run_block(block, repl=repl)
    if status == "fail":
        pytest.fail(message, pytrace=False)
    if status == "skip":
        pytest.skip(message)


@pytest.mark.parametrize(
    "block",
    _PY_BLOCKS,
    ids=[b.short_id for b in _PY_BLOCKS],
)
def test_python_snippet(block: DocBlock) -> None:
    """Validate a Python code block: ast.parse + lab_instruments.* imports.

    No ``exec`` -- the check is syntax correctness + that every referenced
    ``lab_instruments`` symbol actually exists. Third-party imports
    (pandas, matplotlib, etc.) are ignored so the harness works without
    those installed.
    """
    status, message = run_python_snippet(block)
    if status == "fail":
        pytest.fail(message, pytrace=False)
    if status == "skip":
        pytest.skip(message)
