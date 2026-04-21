#!/usr/bin/env python3
"""Walk every docs/*.md file, extract REPL code blocks, and execute them.

Shares extraction/runner logic with ``tests/test_docs_examples_live.py`` via
``lab_instruments._docs_extract``. Exits non-zero on any FAIL.
"""

from __future__ import annotations

import argparse
import contextlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lab_instruments._docs_extract import (  # noqa: E402
    _build_mock_repl,
    classify_block,
    extract_blocks,
    iter_doc_files,
    not_repl_reason,
    run_block,
)

ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"


def _fmt(status: str) -> str:
    return {
        "pass": f"{ANSI_GREEN}PASS{ANSI_RESET}",
        "fail": f"{ANSI_RED}FAIL{ANSI_RESET}",
        "skip": f"{ANSI_YELLOW}SKIP{ANSI_RESET}",
    }[status]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", help="Restrict to a single docs/*.md file.")
    parser.add_argument(
        "--first-failure",
        action="store_true",
        help="Stop at the first FAIL.",
    )
    parser.add_argument(
        "--show-skipped",
        action="store_true",
        help="List every SKIPped block with its reason.",
    )
    args = parser.parse_args()

    docs_dir = PROJECT_ROOT / "docs"
    if not docs_dir.is_dir():
        print(f"error: no docs directory at {docs_dir}", file=sys.stderr)
        return 2

    files = list(iter_doc_files(docs_dir))
    if args.file:
        target = Path(args.file).resolve()
        files = [p for p in files if p.resolve() == target]
        if not files:
            print(f"error: {args.file} not among tracked docs files", file=sys.stderr)
            return 2

    totals = {"pass": 0, "fail": 0, "skip": 0}
    any_failure = False

    def _close_shared(repl):
        if repl is not None:
            with contextlib.suppress(Exception):
                repl.close()

    for md in files:
        rel = md.relative_to(PROJECT_ROOT)
        print(f"\n{ANSI_CYAN}=== {rel} ==={ANSI_RESET}")
        blocks = extract_blocks(md)
        # Per-file shared REPL for setup+run chaining.
        shared_repl = None
        setup_failed = False
        for block in blocks:
            kind = classify_block(block)
            if kind == "not-repl":
                totals["skip"] += 1
                if args.show_skipped:
                    reason = not_repl_reason(block) or "unknown"
                    print(f"  {_fmt('skip')}  {block.short_id}  (not-repl: {reason})")
                continue
            if setup_failed:
                # A prior setup block in this file failed -- skip remaining
                # blocks rather than running them against a broken REPL. This
                # matches the pytest harness's ``_SETUP_FAILED`` semantics.
                totals["skip"] += 1
                if args.show_skipped:
                    print(f"  {_fmt('skip')}  {block.short_id}  (setup failed earlier in file)")
                continue
            if kind == "setup":
                shared_repl = _build_mock_repl() if shared_repl is None else shared_repl
                status, message = run_block(block, repl=shared_repl)
                print(f"  [setup] {_fmt(status)}  {block.short_id}  {message}")
                totals[status] += 1
                if status == "fail":
                    any_failure = True
                    setup_failed = True
                    if args.first_failure:
                        _close_shared(shared_repl)
                        _summary(totals)
                        return 1
                continue

            repl_arg = shared_repl
            status, message = run_block(block, repl=repl_arg)
            totals[status] += 1
            label = f"{_fmt(status)}  {block.short_id}"
            if status == "fail":
                any_failure = True
                print(f"  {label}\n      {message}")
                if args.first_failure:
                    _close_shared(shared_repl)
                    _summary(totals)
                    return 1
            elif status == "skip":
                if args.show_skipped:
                    print(f"  {label}  ({message})")
            else:
                print(f"  {label}")

        _close_shared(shared_repl)

    _summary(totals)
    return 1 if any_failure else 0


def _summary(totals: dict[str, int]) -> None:
    total = sum(totals.values())
    print()
    print(
        f"Summary: {ANSI_GREEN}{totals['pass']} pass{ANSI_RESET}  "
        f"{ANSI_RED}{totals['fail']} fail{ANSI_RESET}  "
        f"{ANSI_YELLOW}{totals['skip']} skip{ANSI_RESET}  "
        f"(total {total})"
    )


if __name__ == "__main__":
    raise SystemExit(main())
