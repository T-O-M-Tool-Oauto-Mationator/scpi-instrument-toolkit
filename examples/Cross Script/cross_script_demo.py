# v1.0.2
"""Cross-script demo -- Python analysis version.

Reads measurements and REPL variables left by the SCPI version of this
example, then performs statistical analysis.  Run the SCPI version first,
then this one.  Works with --mock.
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

# --- Read REPL variables set by the SCPI script ---
target = float(repl.ctx.script_vars.get("target", "5.0"))
tolerance = float(repl.ctx.script_vars.get("tolerance", "0.05"))
psu_v = repl.ctx.script_vars.get("psu_v", None)

ColorPrinter.header("Cross-Script Demo (Python Analysis)")
ColorPrinter.info(f"Target: {target} V, Tolerance: +/- {tolerance} V")
if psu_v:
    ColorPrinter.info(f"PSU readback from SCPI run: {psu_v} V")

# --- Gather all DMM readings from the measurement store ---
readings = []
for entry in repl.ctx.measurements.entries:
    if entry["label"].startswith("reading_") and entry["unit"] == "V":
        readings.append(entry["value"])

if not readings:
    ColorPrinter.error("No readings found. Run the SCPI version first!")
    ColorPrinter.info("  examples load cross_script_demo")
    ColorPrinter.info("  script run cross_script_demo")
    raise SystemExit

# --- Analyze ---
n = len(readings)
mean_v = sum(readings) / n
min_v = min(readings)
max_v = max(readings)
spread = max_v - min_v
error = mean_v - target

# Standard deviation
variance = sum((r - mean_v) ** 2 for r in readings) / n
std_dev = variance ** 0.5

ColorPrinter.info(f"Samples:   {n}")
ColorPrinter.info(f"Mean:      {mean_v:.6f} V")
ColorPrinter.info(f"Min:       {min_v:.6f} V")
ColorPrinter.info(f"Max:       {max_v:.6f} V")
ColorPrinter.info(f"Spread:    {spread:.6f} V")
ColorPrinter.info(f"Std dev:   {std_dev:.6f} V")
ColorPrinter.info(f"Error:     {error:+.6f} V ({error/target*100:+.4f}%)")

# Store results back into REPL variables for further use
repl.ctx.script_vars["mean_v"] = str(round(mean_v, 6))
repl.ctx.script_vars["std_dev"] = str(round(std_dev, 6))
repl.ctx.script_vars["error_pct"] = str(round(error / target * 100, 4))

# Pass/fail check
if abs(error) <= tolerance:
    ColorPrinter.success(f"PASS: error {error:+.6f} V is within +/- {tolerance} V")
else:
    ColorPrinter.error(f"FAIL: error {error:+.6f} V exceeds +/- {tolerance} V")

ColorPrinter.info(f"\nVariables set: mean_v={repl.ctx.script_vars['mean_v']}, "
                  f"std_dev={repl.ctx.script_vars['std_dev']}, "
                  f"error_pct={repl.ctx.script_vars['error_pct']}")
