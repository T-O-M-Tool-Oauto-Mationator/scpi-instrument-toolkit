"""Validate that bundled SCPI examples run under --mock and that
docs/examples.md stays in sync with the EXAMPLES dict.

Usage:
    python scripts/validate_doc_examples.py            # run all checks
    python scripts/validate_doc_examples.py --sync-only # only check doc sync
    python scripts/validate_doc_examples.py --run-only  # only run examples

Exit code 0 = all pass, 1 = any failure.
"""

import re
import signal
import sys
import traceback
from pathlib import Path

# Ensure the project root is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Timeout helper (Unix only; no-op on Windows)
# ---------------------------------------------------------------------------
class _Timeout:
    """Context manager that raises TimeoutError after *seconds*."""

    def __init__(self, seconds: int):
        self.seconds = seconds
        self._old_handler = None

    def _handler(self, signum, frame):
        raise TimeoutError(f"Example timed out after {self.seconds}s")

    def __enter__(self):
        if hasattr(signal, "SIGALRM"):
            self._old_handler = signal.signal(signal.SIGALRM, self._handler)
            signal.alarm(self.seconds)
        return self

    def __exit__(self, *exc):
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)
            if self._old_handler is not None:
                signal.signal(signal.SIGALRM, self._old_handler)
        return False


# ---------------------------------------------------------------------------
# Lines that cannot run headless (GUI, interactive, external file)
# ---------------------------------------------------------------------------
_SKIP_PREFIXES = ("pause", "input", "liveplot", "plot ", "python ")


def _should_skip_line(line: str) -> bool:
    """Return True if *line* requires GUI or interactive input."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False  # comments and blanks are fine
    for pfx in _SKIP_PREFIXES:
        if stripped.startswith(pfx):
            return True
    # Also skip assignment forms: var = input ...
    return bool(re.match(r"^\w+\s*=\s*input\b", stripped))


# ---------------------------------------------------------------------------
# Part A: Run each bundled example with mock instruments
# ---------------------------------------------------------------------------
def _run_examples() -> list[tuple[str, str, str]]:
    """Run every EXAMPLES entry with mock instruments.

    Returns list of (name, status, detail) where status is PASS/FAIL/SKIP.
    """
    from lab_instruments import mock_instruments
    from lab_instruments.examples import EXAMPLES
    from lab_instruments.repl.shell import InstrumentRepl
    from lab_instruments.src import discovery as _disc

    results = []

    for name, entry in EXAMPLES.items():
        lines = entry.get("lines")
        if not lines:
            results.append((name, "SKIP", "no SCPI lines"))
            continue

        # Check if example calls external python file
        has_external_python = any(
            ln.strip().startswith("python ") and not ln.strip().startswith("python -")
            for ln in lines
            if not ln.strip().startswith("#")
        )

        # Filter to runnable lines
        runnable = [ln for ln in lines if not _should_skip_line(ln)]
        if not runnable:
            results.append((name, "SKIP", "all lines require GUI/interactive"))
            continue

        # Patch discovery for mock mode
        orig_init = _disc.InstrumentDiscovery.__init__
        orig_scan = _disc.InstrumentDiscovery.scan
        _disc.InstrumentDiscovery.__init__ = lambda self: None
        _disc.InstrumentDiscovery.scan = lambda self, verbose=True: mock_instruments.get_mock_devices(verbose)

        try:
            with _Timeout(30):
                repl = InstrumentRepl(register_lifecycle=False)
                repl.onecmd("scan")
                for line in runnable:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    repl.onecmd(stripped)
            status = "PASS"
            detail = ""
            if has_external_python:
                detail = "(external python call skipped)"
        except TimeoutError as e:
            status = "FAIL"
            detail = str(e)
        except Exception as e:
            status = "FAIL"
            detail = f"{type(e).__name__}: {e}"
            if "--verbose" in sys.argv:
                traceback.print_exc()
        finally:
            _disc.InstrumentDiscovery.__init__ = orig_init
            _disc.InstrumentDiscovery.scan = orig_scan

        results.append((name, status, detail))

    return results


# ---------------------------------------------------------------------------
# Part B: Check docs/examples.md sync with EXAMPLES dict
# ---------------------------------------------------------------------------
def _extract_doc_examples(doc_path: Path) -> dict[str, list[str]]:
    """Extract 'Script source' code blocks from docs/examples.md.

    Returns {example_name: [lines]} for each block found under a ## heading
    that is followed by a ```text block labeled 'Script source'.
    """
    if not doc_path.exists():
        return {}

    text = doc_path.read_text()
    blocks: dict[str, list[str]] = {}
    current_heading = None

    # State machine: track headings and code blocks
    in_source_section = False
    in_code_block = False
    code_lines: list[str] = []
    saw_script_source = False

    for line in text.splitlines():
        # Track ## and ### headings
        heading_match = re.match(r"^#{2,3}\s+(\S+)", line)
        if heading_match and not in_code_block:
            if in_source_section and code_lines and current_heading:
                blocks[current_heading] = code_lines[:]
            current_heading = heading_match.group(1).strip()
            in_source_section = False
            saw_script_source = False
            code_lines = []

        # Detect "Script source:" or "**Script source:**"
        if re.search(r"\*\*Script source:?\*\*", line, re.IGNORECASE) or re.match(
            r"Script source:", line, re.IGNORECASE
        ):
            saw_script_source = True

        # Code block boundaries
        if line.strip().startswith("```") and not in_code_block:
            if saw_script_source:
                in_code_block = True
                in_source_section = True
                code_lines = []
                saw_script_source = False
            continue
        if line.strip() == "```" and in_code_block:
            in_code_block = False
            if in_source_section and current_heading:
                blocks[current_heading] = code_lines[:]
                in_source_section = False
            continue
        if in_code_block and in_source_section:
            code_lines.append(line)

    return blocks


def _normalize_lines(lines: list[str]) -> list[str]:
    """Normalize lines for comparison: strip, skip leading comment-only headers.

    The EXAMPLES dict includes version headers (``# v1.0.2``) and usage
    comments that docs intentionally omit for readability.  We skip all
    leading comment/blank lines so the comparison starts at the first
    substantive line.
    """
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue  # skip all comment-only lines
        result.append(stripped)
    return result


def _check_sync(doc_path: Path) -> list[tuple[str, str, str]]:
    """Compare docs/examples.md script source blocks against EXAMPLES dict.

    Returns list of (name, status, detail) where status is SYNC/DRIFT/MISSING.
    """
    from lab_instruments.examples import EXAMPLES

    results = []
    doc_blocks = _extract_doc_examples(doc_path)

    for name, entry in EXAMPLES.items():
        lines = entry.get("lines")
        if not lines:
            continue

        if name not in doc_blocks:
            results.append((name, "MISSING", "not in docs/examples.md"))
            continue

        doc_lines = _normalize_lines(doc_blocks[name])
        src_lines = _normalize_lines(lines)

        if doc_lines == src_lines:
            results.append((name, "SYNC", ""))
        else:
            # Find first difference
            for i, (d, s) in enumerate(zip(doc_lines, src_lines, strict=False)):
                if d != s:
                    results.append((name, "DRIFT", f"line {i + 1}: doc has '{d[:60]}' vs src '{s[:60]}'"))
                    break
            else:
                if len(doc_lines) != len(src_lines):
                    results.append(
                        (
                            name,
                            "DRIFT",
                            f"line count differs: doc={len(doc_lines)} vs src={len(src_lines)}",
                        )
                    )
                else:
                    results.append((name, "SYNC", ""))

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    sync_only = "--sync-only" in sys.argv
    run_only = "--run-only" in sys.argv

    doc_path = _PROJECT_ROOT / "docs" / "examples.md"
    exit_code = 0

    # Part A: Run examples
    if not sync_only:
        print("=" * 60)
        print("  Part A: Running bundled SCPI examples with --mock")
        print("=" * 60)
        run_results = _run_examples()
        passed = sum(1 for _, s, _ in run_results if s == "PASS")
        failed = sum(1 for _, s, _ in run_results if s == "FAIL")
        skipped = sum(1 for _, s, _ in run_results if s == "SKIP")

        for name, status, detail in run_results:
            suffix = f" -- {detail}" if detail else ""
            print(f"  {status:4s}  {name}{suffix}")

        print(f"\n  {passed} passed, {failed} failed, {skipped} skipped")
        if failed:
            exit_code = 1

    # Part B: Sync check
    if not run_only:
        print()
        print("=" * 60)
        print("  Part B: docs/examples.md sync check")
        print("=" * 60)
        sync_results = _check_sync(doc_path)
        synced = sum(1 for _, s, _ in sync_results if s == "SYNC")
        drifted = sum(1 for _, s, _ in sync_results if s == "DRIFT")
        missing = sum(1 for _, s, _ in sync_results if s == "MISSING")

        for name, status, detail in sync_results:
            suffix = f" -- {detail}" if detail else ""
            print(f"  {status:7s}  {name}{suffix}")

        print(f"\n  {synced} synced, {drifted} drifted, {missing} missing from docs")
        if drifted:
            exit_code = 1
        if missing:
            print("  (MISSING is informational -- add Script source blocks to docs/examples.md)")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
