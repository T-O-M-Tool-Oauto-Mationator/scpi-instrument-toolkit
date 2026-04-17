"""Parametrized pytest harness that executes every REPL-looking code block
in ``docs/*.md``.

Blocks are grouped per source file. For each file the harness builds one
mock REPL, then feeds the classified blocks in document order so
``<!-- doc-test: setup -->`` blocks can prime state used by subsequent
``run`` blocks -- this matches the behavior of
``scripts/validate_all_doc_examples.py``.

Each ``run`` block becomes its own pytest node whose ID is shaped
``docs/FILE.md:Lstart-Lend``, so a failing block still surfaces its exact
doc location even though the REPL is shared with its siblings.

Skip a block explicitly with an HTML comment directly above its fence:

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
    extract_blocks,
    iter_doc_files,
    run_block,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"


@dataclass(frozen=True)
class _FileGroup:
    """All blocks for a single markdown file, in document order."""

    source: Path
    blocks: tuple[DocBlock, ...]


def _collect_groups() -> list[_FileGroup]:
    groups: list[_FileGroup] = []
    if not DOCS_DIR.is_dir():
        return groups
    for md in iter_doc_files(DOCS_DIR):
        blocks = tuple(extract_blocks(md))
        # Only keep groups that contain at least one testable block.
        if any(classify_block(b) in ("run", "setup") for b in blocks):
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
            if classify_block(block) == "run":
                pairs.append((group, block))
    return pairs


_RUN_PAIRS = _enumerate_run_blocks()


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
