# v1.0.2
"""Live voltage sweep -- Python API version.

Sweeps the PSU through voltages and records DMM measurements.
A live plot tracks the readings in real time.  Works with --mock.
"""
import time

# --- Configuration ---
V_START = 0.5
V_END = 12.0
STEPS = 50
DELAY = 0.15  # seconds between points
CURRENT_LIMIT = 0.5
CHANNEL = 1

# --- Get instruments ---
psu = devices.get("psu") or devices.get("psu1")
dmm = devices.get("dmm") or devices.get("dmm1")

if not psu:
    ColorPrinter.error("No PSU found. Run 'scan' first.")
    raise SystemExit
if not dmm:
    ColorPrinter.error("No DMM found. Run 'scan' first.")
    raise SystemExit

ch = CHANNEL
channel_map = getattr(psu.__class__, "CHANNEL_FROM_NUMBER", {})
if channel_map:
    ch = channel_map.get(CHANNEL, CHANNEL)

# --- Start live plot (opens tab immediately, updates as data arrives) ---
repl.onecmd('liveplot dmm_* --title "Voltage Sweep" --xlabel "Time (s)" --ylabel "Voltage (V)"')

# --- Build linspace ---
step = (V_END - V_START) / STEPS
voltages = [V_START + step * i for i in range(STEPS + 1)]

# --- Run sweep ---
ColorPrinter.header(f"Live Voltage Sweep: {V_START}V -> {V_END}V in {STEPS+1} points")
psu.enable_output(True)

for target_v in voltages:
    psu.set_output_channel(ch, target_v, CURRENT_LIMIT)
    time.sleep(DELAY)
    measured = dmm.measure_dc_voltage()
    repl.ctx.measurements.record(f"dmm_{target_v:.2f}V", measured, "V", "dmm1")
    ColorPrinter.info(f"  {target_v:6.2f} V  ->  DMM: {measured:.6f} V")

psu.enable_output(False)
ColorPrinter.success("Sweep complete")
