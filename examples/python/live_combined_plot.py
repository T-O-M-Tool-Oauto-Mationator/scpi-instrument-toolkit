# v1.0.2
"""Combined live plot -- Python API version.

Plots PSU voltage AND current as two series overlaid on a single chart.
The key: pass multiple glob patterns to ONE liveplot command.
Works with --mock.
"""
import time
from typing import TYPE_CHECKING

# Type hints for names injected by the SCPI REPL's `python` command at exec()
# time. The `if TYPE_CHECKING:` block is never executed at runtime -- it only
# teaches Pylance / pyright what these names are. See do_python() in
# lab_instruments/repl/commands/scripting.py.
if TYPE_CHECKING:
    from lab_instruments.repl.shell import InstrumentRepl
    from lab_instruments.src.terminal import ColorPrinter

    repl: InstrumentRepl
    devices: dict

V_START = 0.5
V_END = 12.0
STEPS = 50
DELAY = 0.15
CURRENT_LIMIT = 0.5
CHANNEL = 1

psu = devices.get("psu") or devices.get("psu1")
if not psu:
    ColorPrinter.error("No PSU found. Run 'scan' first.")
    raise SystemExit

ch = CHANNEL
channel_map = getattr(psu.__class__, "CHANNEL_FROM_NUMBER", {})
if channel_map:
    ch = channel_map.get(CHANNEL, CHANNEL)

# Two patterns, ONE liveplot = two series on ONE chart
repl.onecmd('liveplot psu_v_* psu_i_* --title "PSU Voltage & Current" --xlabel "Time (s)"')

step = (V_END - V_START) / STEPS
voltages = [V_START + step * i for i in range(STEPS + 1)]

ColorPrinter.header(f"Combined V+I Plot: {V_START}V -> {V_END}V in {STEPS+1} points")
psu.enable_output(True)

for target_v in voltages:
    psu.set_output_channel(ch, target_v, CURRENT_LIMIT)
    time.sleep(DELAY)
    v_meas = psu.measure_voltage(ch) if hasattr(psu, "select_channel") else psu.measure_voltage()
    i_meas = psu.measure_current(ch) if hasattr(psu, "select_channel") else psu.measure_current()
    repl.ctx.measurements.record(f"psu_v_{target_v:.2f}", v_meas, "V", "psu1")
    repl.ctx.measurements.record(f"psu_i_{target_v:.2f}", i_meas, "A", "psu1")
    ColorPrinter.info(f"  {target_v:5.2f} V  ->  V={v_meas:.4f}  I={i_meas:.6f}")

psu.enable_output(False)
ColorPrinter.success("Ramp complete")
