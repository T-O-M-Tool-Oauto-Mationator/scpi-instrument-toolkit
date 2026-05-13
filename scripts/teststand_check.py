#!/usr/bin/env python3
"""Probe + repair a NI TestStand Python adapter setup, head-less, via COM.

This is the bulletproof recovery path for the two issues new TAs and students
hit repeatedly when wiring TestStand to the toolkit (see #118, #121, #126):

  (a) **"I cannot find the Display Console checkbox in the Advanced tab."**
      The Python adapter's UI varies between TestStand point-releases; the
      underlying COM property ``DisplayConsoleForInterpreterSessions`` is
      stable. ``--fix-adapter`` flips it on without touching the UI.

  (b) **"My Numeric Limit Test step shows Measurement {0} even though the
      Python function clearly returned the right value."**
      Caused by a missing ``Return Value`` row in ``step.Module.Parameters``.
      That row's ``ValueExpr=Step.Result.Numeric`` is the channel from the
      function's return into the limit comparison; without it the Measurement
      stays at 0. ``--fix-seq <path>`` walks the sequence, re-introspects every
      Python NLT step via ``step.LoadModule()``, and saves.

The script never opens the TestStand GUI -- it dispatches the
``TestStand.Engine`` COM server in-process. All API names were verified
against ``TestStandAPIReferencePoster.pdf`` (Engine, Sequence, Step,
PythonAdapter, PythonModule, PythonParameter classes).

Run with no arguments for an adapter probe; add a ``.seq`` path to audit
that file's Python NLT steps; add ``--fix`` to repair.

Requires ``pywin32``. TestStand 2025+ exposes the ``Python Adapter`` key;
older releases call it ``LabWindows/CVI Python`` -- adjust ``ADAPTER_KEY``.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

ADAPTER_KEY = "Python Adapter"
EXPECTED_RETURN_NAME = "Return Value"
EXPECTED_RETURN_VEXPR = "Step.Result.Numeric"


def _need_win32():
    try:
        import win32com.client  # noqa: F401
    except ImportError:
        sys.stderr.write("ERROR: pywin32 is not installed. From your TestStand venv run:\n  pip install pywin32\n")
        sys.exit(2)


def probe_adapter(engine, *, fix_adapter: bool = False) -> dict[str, Any]:
    """Read (and optionally fix) the Python adapter properties."""
    ad = engine.GetAdapterByKeyName(ADAPTER_KEY)
    props = {}
    for name in (
        "DisplayConsoleForInterpreterSessions",
        "PythonVersion",
        "PythonVirtualEnvironmentPath",
        "EnableDebugging",
        "InterpreterSessionScope",
        "ReloadModifiedModulesDuringExecution",
    ):
        try:
            props[name] = getattr(ad, name)
        except Exception as exc:  # property absent in this TS version
            props[name] = f"<unavailable: {exc}>"

    print(f"Python Adapter (KeyName={ad.KeyName!r})")
    for name, val in props.items():
        print(f"  {name} = {val!r}")

    if fix_adapter and props.get("DisplayConsoleForInterpreterSessions") is False:
        print("\n[--fix-adapter] Setting DisplayConsoleForInterpreterSessions = True")
        ad.DisplayConsoleForInterpreterSessions = True
        # Re-read to confirm persistence in this session
        print(f"  now = {ad.DisplayConsoleForInterpreterSessions!r}")
        print("  Restart TestStand once for the setting to take effect across runs.")
    return props


def _is_python_nlt(step) -> bool:
    if (step.AdapterKeyName or "") != ADAPTER_KEY:
        return False
    stype = step.StepType.Name if step.StepType else ""
    return "NumericLimitTest" in stype or "Numeric Limit" in stype


def _return_value_row(params):
    """Return the PythonParameter row whose Name == 'Return Value', or None."""
    for k in range(params.Count):
        try:
            p = params.Item(k)
        except Exception:
            try:
                p = params.GetItem(k)
            except Exception:
                p = params[k]
        try:
            if p.ParameterName == EXPECTED_RETURN_NAME:
                return p
        except Exception:
            continue
    return None


def audit_seq(engine, seq_path: str, *, fix: bool = False) -> tuple[int, int]:
    """Walk every Python NLT step in *seq_path*. Returns (ok, broken) counts."""
    abs_path = os.path.abspath(seq_path)
    if not os.path.exists(abs_path):
        print(f"ERROR: sequence file not found: {abs_path}", file=sys.stderr)
        return (0, -1)

    print(f"\nAuditing {abs_path}")
    sf = engine.GetSequenceFileEx(abs_path, 1, 0)
    ok = 0
    broken = 0
    fixed: list[str] = []
    try:
        for i in range(sf.NumSequences):
            seq = sf.GetSequence(i)
            for gi, gname in enumerate(("Setup", "Main", "Cleanup")):
                try:
                    nsteps = seq.GetNumSteps(gi)
                except Exception:
                    continue
                for j in range(nsteps):
                    step = seq.GetStep(j, gi)
                    if not _is_python_nlt(step):
                        continue
                    label = f"{seq.Name}/{gname}/{step.Name}"
                    params = step.Module.Parameters
                    row = _return_value_row(params)
                    if row is None:
                        broken += 1
                        print(f"  FAIL {label}: missing 'Return Value' row")
                        if fix:
                            try:
                                step.LoadModule()
                                # Re-check after re-introspection
                                row = _return_value_row(step.Module.Parameters)
                                if row is not None:
                                    fixed.append(label)
                                    print(f"       FIXED via step.LoadModule(); ValueExpr={row.ValueExpr!r}")
                                else:
                                    print("       FAILED to repair via LoadModule()")
                            except Exception as exc:
                                print(f"       LoadModule() raised: {exc}")
                    else:
                        try:
                            ve = row.ValueExpr
                        except Exception:
                            ve = "?"
                        if ve == EXPECTED_RETURN_VEXPR:
                            ok += 1
                            print(f"  OK   {label}: Return Value -> {ve}")
                        else:
                            broken += 1
                            print(
                                f"  WARN {label}: Return Value ValueExpr is {ve!r}, expected {EXPECTED_RETURN_VEXPR!r}"
                            )
        if fix and fixed:
            sf.IncChangeCount()
            engine.SaveSequenceFile(sf, "")
            print(f"\nSaved {abs_path} ({len(fixed)} step(s) repaired).")
    finally:
        engine.ReleaseSequenceFileEx(sf, 0)
    return (ok, broken)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/teststand_check.py\n"
            "  python scripts/teststand_check.py --fix-adapter\n"
            "  python scripts/teststand_check.py path/to/sequence.seq\n"
            "  python scripts/teststand_check.py path/to/sequence.seq --fix\n"
        ),
    )
    parser.add_argument("seq_file", nargs="?", help="Optional .seq file to audit.")
    parser.add_argument(
        "--fix-adapter",
        action="store_true",
        help="Set DisplayConsoleForInterpreterSessions=True via COM.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="When auditing a .seq file, re-introspect any broken Python NLT step via step.LoadModule() and save.",
    )
    args = parser.parse_args(argv)

    _need_win32()
    import win32com.client as wc

    engine = wc.Dispatch("TestStand.Engine")
    print(f"TestStand Engine v{engine.MajorVersion}.{engine.MinorVersion}")
    probe_adapter(engine, fix_adapter=args.fix_adapter)

    if args.seq_file is None:
        if args.fix:
            print("\n--fix has no effect without a .seq file path.", file=sys.stderr)
            return 1
        return 0

    ok, broken = audit_seq(engine, args.seq_file, fix=args.fix)
    if broken < 0:
        return 1
    print(f"\nSummary: {ok} OK, {broken} broken.")
    return 0 if broken == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
