"""Run a REPL command block with mock instruments and report pass/fail.

Usage:
    python scripts/run_repl_doc_block.py <path-to-lines-file>
    python scripts/run_repl_doc_block.py -       # read lines from stdin

The input is one REPL command per line. Blank lines and comment-only lines (`# ...`)
are passed through to the REPL (it tolerates them). For each line the script prints:

    [OK  ] <line>
    [FAIL] <line>    -> <exception repr>

Exit code is 0 if every line succeeded, 1 otherwise.

Intended for automated verification of doc-example blocks.
"""

import io
import os
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Windows consoles default to cp1252 and choke on arrows/Ω. Force utf-8 with replace
# so the reporter can echo any REPL line containing unicode without crashing.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _install_mocks():
    from lab_instruments import mock_instruments
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True, force=False, **kw: (
        mock_instruments.get_mock_devices(verbose=False)
    )


def run_lines(lines):
    _install_mocks()
    from lab_instruments.repl.shell import InstrumentRepl

    repl = InstrumentRepl()

    results = []
    for raw in lines:
        line = raw.rstrip("\n").rstrip("\r")
        # Empty lines: skip silently
        if not line.strip():
            continue
        out = io.StringIO()
        err = io.StringIO()
        try:
            with redirect_stdout(out), redirect_stderr(err):
                repl.onecmd(line)
            results.append(("OK", line, out.getvalue(), err.getvalue(), None))
        except SystemExit:
            results.append(("OK", line, out.getvalue(), err.getvalue(), None))
        except BaseException as exc:
            tb = traceback.format_exc()
            results.append(("FAIL", line, out.getvalue(), err.getvalue(), f"{exc!r}\n{tb}"))
    return results


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: run_repl_doc_block.py <file|->\n")
        sys.exit(2)

    src = sys.argv[1]
    if src == "-":
        lines = sys.stdin.readlines()
    else:
        with open(src, "r", encoding="utf-8") as f:
            lines = f.readlines()

    results = run_lines(lines)

    failures = 0
    for status, line, stdout, stderr, err in results:
        tag = "[OK  ]" if status == "OK" else "[FAIL]"
        print(f"{tag} {line}")
        if status == "FAIL":
            failures += 1
            if err:
                for eline in err.splitlines():
                    print(f"        {eline}")

    total = len(results)
    print(f"\n--- SUMMARY: {total - failures}/{total} passed, {failures} failed ---")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
