"""Multi-plot PSU ramp -- Python API version.

Opens two independent live-plot tabs (voltage and current) and ramps the PSU
through a series of setpoints.  Works with --mock.
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
if not psu:
    ColorPrinter.error("No PSU found. Run 'scan' first.")
    raise SystemExit

ch = CHANNEL
channel_map = getattr(psu.__class__, "CHANNEL_FROM_NUMBER", {})
if channel_map:
    ch = channel_map.get(CHANNEL, CHANNEL)

# --- Open two live plots (each becomes its own tab) ---
repl.onecmd('liveplot psu_v_* --title "PSU Voltage" --xlabel "Time (s)" --ylabel "Voltage (V)"')
repl.onecmd('liveplot psu_i_* --title "PSU Current" --xlabel "Time (s)" --ylabel "Current (A)"')

# --- Build linspace ---
step = (V_END - V_START) / STEPS
voltages = [V_START + step * i for i in range(STEPS + 1)]

# --- Ramp ---
ColorPrinter.header(f"Multi-Plot PSU Ramp: {V_START}V -> {V_END}V in {STEPS+1} points")
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
