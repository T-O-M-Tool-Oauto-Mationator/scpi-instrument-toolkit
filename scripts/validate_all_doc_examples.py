#!/usr/bin/env python3
"""Walk markdown doc roots, extract code blocks, and validate them.

Shares extraction/runner logic with ``tests/test_docs_examples_live.py`` via
``lab_instruments._docs_extract``. Exits non-zero on any FAIL.

Three block languages are handled:

* **REPL** (``text`` / ``bash`` / unlabeled fences, CommonMark 4-space
  indented blocks) -- executed line-by-line against a mock instrument
  session. Blocks inside a file with a ``<!-- doc-test: setup -->`` marker
  share REPL state so later blocks can build on earlier context.
* **Python** (``python`` fence or body with ``import`` / ``def`` / ``class``)
  -- ``ast.parse`` + ``lab_instruments.*`` symbol-resolution check. No
  ``exec``.
* **Shell** (``bash`` fence with a known shell prefix, or any block starting
  with ``pip`` / ``git`` / ``pytest`` / etc.) -- always SKIP, logged with
  ``--show-skipped``.
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
    classify_language,
    extract_all_blocks,
    iter_doc_files,
    not_repl_reason,
    run_block,
    run_python_snippet,
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


def _resolve_roots(explicit_roots: list[str]) -> list[Path]:
    """Return the directories to scan. Defaults to ``<project>/docs``."""
    if not explicit_roots:
        return [PROJECT_ROOT / "docs"]
    out: list[Path] = []
    for r in explicit_roots:
        p = Path(r)
        p = (PROJECT_ROOT / p).resolve() if not p.is_absolute() else p.resolve()
        out.append(p)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        metavar="DIR",
        help="Directory to scan for *.md files. Repeatable. Defaults to <project>/docs.",
    )
    parser.add_argument(
        "--file",
        help="Restrict to a single *.md file (must live under one of the --root dirs).",
    )
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

    roots = _resolve_roots(args.root)
    files: list[Path] = []
    for root in roots:
        if not root.is_dir():
            print(f"error: no such directory: {root}", file=sys.stderr)
            return 2
        files.extend(iter_doc_files(root))

    if args.file:
        target = Path(args.file).resolve()
        files = [p for p in files if p.resolve() == target]
        if not files:
            print(f"error: {args.file} not among tracked markdown files", file=sys.stderr)
            return 2

    totals = {"pass": 0, "fail": 0, "skip": 0}
    any_failure = False

    def _close_shared(repl):
        if repl is not None:
            with contextlib.suppress(Exception):
                repl.close()

    for md in files:
        try:
            rel = md.relative_to(PROJECT_ROOT)
        except ValueError:
            rel = md
        print(f"\n{ANSI_CYAN}=== {rel} ==={ANSI_RESET}")
        blocks = extract_all_blocks(md)
        # Per-file shared REPL for setup+run chaining.
        shared_repl = None
        setup_failed = False
        for block in blocks:
            kind = classify_block(block)
            lang = classify_language(block)

            # Python blocks use their own runner regardless of REPL classify.
            if lang == "python" and kind not in ("skip", "setup"):
                status, message = run_python_snippet(block)
                totals[status] += 1
                label = f"{_fmt(status)}  {block.short_id}  [python]"
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
                continue

            # Shell recipes are documentation, not runnable under the harness.
            if lang == "shell":
                totals["skip"] += 1
                if args.show_skipped:
                    print(f"  {_fmt('skip')}  {block.short_id}  [shell] (not executed)")
                continue

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
