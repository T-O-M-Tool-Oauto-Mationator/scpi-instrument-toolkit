"""Parametrized pytest harness that executes every REPL-looking code block
in ``docs/*.md``.

Each block becomes its own pytest node ID shaped
``docs/FILE.md:Lstart-Lend`` so failures surface the exact doc location.

Extraction + execution logic lives in ``lab_instruments._docs_extract`` --
the standalone CLI at ``scripts/validate_all_doc_examples.py`` shares the
same helpers so local iteration and CI both run the same checks.

Skip a block explicitly with an HTML comment directly above its fence:

    <!-- doc-test: skip reason="requires GUI liveplot" -->
    ```text
    liveplot ...
    ```
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments._docs_extract import (  # noqa: E402
    DocBlock,
    _build_mock_repl,
    classify_block,
    extract_blocks,
    iter_doc_files,
    run_block,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"


def _collect() -> list[DocBlock]:
    blocks: list[DocBlock] = []
    for md in iter_doc_files(DOCS_DIR):
        blocks.extend(extract_blocks(md))
    return blocks


_ALL_BLOCKS = _collect() if DOCS_DIR.is_dir() else []
_RUN_BLOCKS = [b for b in _ALL_BLOCKS if classify_block(b) == "run"]


@pytest.mark.parametrize("block", _RUN_BLOCKS, ids=[b.short_id for b in _RUN_BLOCKS])
def test_doc_block(block: DocBlock) -> None:
    """Run one REPL code block end-to-end; any ``ctx.command_had_error`` fails the test."""
    import contextlib

    repl = _build_mock_repl()
    try:
        status, message = run_block(block, repl=repl)
    finally:
        with contextlib.suppress(Exception):
            repl.close()
    if status == "fail":
        pytest.fail(message, pytrace=False)
    if status == "skip":
        pytest.skip(message)
