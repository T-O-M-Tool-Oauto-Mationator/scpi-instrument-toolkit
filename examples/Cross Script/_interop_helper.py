# v1.0.2
"""Interop helper — called from the SCPI script via `python` command.

Demonstrates patterns 2, 4, 6, 8, 10 from the SCPI-side interop list:
  PATTERN 4: calling a python file from SCPI
  PATTERN 6: SCPI var read by a python file (via repl.ctx.script_vars)
  PATTERN 8: SCPI var modified by a python file (via repl.ctx.script_vars)
  PATTERN 10: python file creates a value used back in SCPI

Also called in a loop for PATTERN 2.

Works with --mock mode.
"""

# Type hints for names injected by the SCPI REPL's `python` command at exec()
# time. The `if TYPE_CHECKING:` block is never executed at runtime -- it only
# teaches Pylance / pyright what these names are. See do_python() in
# lab_instruments/repl/commands/scripting.py.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lab_instruments.repl.shell import InstrumentRepl
    from lab_instruments.src.terminal import ColorPrinter

    repl: InstrumentRepl
    vars: dict[str, str]

# ── PATTERN 6: read an SCPI variable inside a python file ────────────
# The SCPI script set  scpi_to_py_file = 42  before calling us.
# All script_vars are auto-injected as native Python types.
val = vars.get("scpi_to_py_file", "NOT_SET")
ColorPrinter.info(f"[helper.py] PATTERN 6: read SCPI var scpi_to_py_file = {val}")

# ── PATTERN 8: modify an SCPI variable from a python file ───────────
# The SCPI script set  scpi_modify_py_file = 100  before calling us.
old = vars.get("scpi_modify_py_file", "0")
new_val = float(old) + 1
repl.ctx.script_vars["scpi_modify_py_file"] = str(new_val)
ColorPrinter.info(f"[helper.py] PATTERN 8: modified scpi_modify_py_file {old} -> {new_val}")

# ── PATTERN 10: create a value for SCPI to use ──────────────────────
# Store a brand-new variable that the SCPI script reads back via {key}.
repl.ctx.script_vars["py_file_created"] = "hello_from_python_file"
ColorPrinter.info("[helper.py] PATTERN 10: set py_file_created = hello_from_python_file")

# ── Used in PATTERN 2 (loop): record something per call ─────────────
loop_idx = vars.get("helper_loop_idx", "0")
repl.ctx.script_vars["helper_last_call"] = str(loop_idx)
ColorPrinter.info(f"[helper.py] loop call index = {loop_idx}")

# Record a measurement so the SCPI script can verify it
repl.ctx.measurements.record(
    f"helper_meas_{loop_idx}", float(loop_idx) * 1.1, "V", "helper_py"
)

ColorPrinter.success("[helper.py] Interop helper complete.")
