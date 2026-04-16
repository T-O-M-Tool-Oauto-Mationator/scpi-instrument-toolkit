"""
Bundled example scripts for the SCPI Instrument REPL.

Each entry in EXAMPLES can have:
  "description" : one-line summary shown by ``examples`` command
  "lines"       : list of SCPI script lines  (→ name.scpi)
  "code"        : Python source string        (→ name.py)

An entry may contain *both* ``lines`` and ``code`` — the GUI will
export both ``name.scpi`` and ``name.py`` into the workspace.

Load any example into your session with:  examples load <name>
Load all at once with:                    examples load all
Then run with:                            script run <name> [params]
"""

EXAMPLES: dict[str, dict] = {
    # ------------------------------------------------------------------
    "psu_dmm_test": {
        "description": "Set PSU to a voltage, measure with DMM, log result",
        "lines": [
            "# v1.0.2",
            "# psu_dmm_test",
            "# Params: voltage (default 5.0), label (default 'vtest')",
            "#",
            "# Usage: script run psu_dmm_test voltage=5.0 label=vtest",
            "#        uses psu1 and dmm1 — rename with 'examples load' then edit if needed",
            "",
            "voltage = 5.0",
            "label = vtest",
            "",
            'print "=== PSU/DMM Voltage Test ==="',
            'print "Target: {voltage}V"',
            "",
            "# Turn on PSU and set voltage",
            "psu1 chan 1 on",
            "psu1 set 1 {voltage}",
            "sleep 0.5",
            "",
            "# Read PSU output",
            "psu_v = psu1 meas v unit=V",
            "",
            "# Read DMM",
            "dmm1 config vdc",
            "{label} = dmm1 meas unit=V",
            "",
            'print "=== Test complete ==="',
            "log print",
        ],
        "code": '''\
# v1.0.2
"""PSU + DMM voltage test — Python API version."""
import time

VOLTAGE = 5.0
CURRENT_LIMIT = 0.5
CHANNEL = 1

psu = devices.get("psu") or devices.get("psu1")
dmm = devices.get("dmm") or devices.get("dmm1")

if not psu:
    ColorPrinter.error("No PSU found. Run 'scan' first.")
    raise SystemExit

ch = CHANNEL
channel_map = getattr(psu.__class__, "CHANNEL_FROM_NUMBER", {})
if channel_map:
    ch = channel_map.get(CHANNEL, CHANNEL)

ColorPrinter.header(f"PSU/DMM Voltage Test — {VOLTAGE}V")

psu.set_output_channel(ch, VOLTAGE, CURRENT_LIMIT)
psu.enable_output(True)
time.sleep(0.5)

psu_v = psu.measure_voltage(ch) if hasattr(psu, "select_channel") else psu.measure_voltage()
ColorPrinter.info(f"PSU output:  {psu_v:.4f} V")

if dmm:
    dmm_v = dmm.measure_dc_voltage()
    ColorPrinter.info(f"DMM reading: {dmm_v:.6f} V")
else:
    ColorPrinter.warning("No DMM connected — skipping DMM measurement")

ColorPrinter.success("Test complete")
''',
    },
    # ------------------------------------------------------------------
    "voltage_sweep": {
        "description": "Sweep PSU through a list of voltages, log DMM reading at each step",
        "lines": [
            "# v1.0.2",
            "# voltage_sweep",
            "# Sweeps PSU through preset voltages and logs DMM measurements",
            "# Edit the 'for' line to change the voltage list",
            "",
            'print "=== Voltage Sweep ==="',
            "psu1 chan 1 on",
            "sleep 0.3",
            "dmm1 config vdc",
            "",
            "for v 1.0 2.0 3.3 5.0 9.0 12.0",
            '  print "Setting {v}V..."',
            "  psu1 set 1 {v}",
            "  sleep 0.5",
            "  v_{v} = dmm1 meas unit=V",
            "end",
            "",
            "psu1 chan 1 off",
            'print "=== Sweep complete ==="',
            "log print",
            "log save voltage_sweep.csv",
        ],
        "code": '''\
# v1.0.2
"""Voltage sweep — Python API version."""
import time

VOLTAGES = [1.0, 2.0, 3.3, 5.0, 9.0, 12.0]
CURRENT_LIMIT = 0.5
CHANNEL = 1

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

ColorPrinter.header("Voltage Sweep")
psu.enable_output(True)
results = []

for target_v in VOLTAGES:
    psu.set_output_channel(ch, target_v, CURRENT_LIMIT)
    time.sleep(0.5)
    measured = dmm.measure_dc_voltage()
    results.append((target_v, measured))
    ColorPrinter.info(f"  {target_v:6.1f} V  ->  DMM: {measured:.6f} V")

psu.enable_output(False)
ColorPrinter.success("Sweep complete")
print("\\nResults:")
print(f"  {'Target':>8s}  {'Measured':>12s}  {'Error':>10s}")
for target, meas in results:
    error = meas - target
    print(f"  {target:8.3f}  {meas:12.6f}  {error:+10.6f}")
''',
    },
    # ------------------------------------------------------------------
    "awg_scope_check": {
        "description": "Output sine wave on AWG ch1, measure frequency and PK2PK on scope",
        "lines": [
            "# v1.0.2",
            "# awg_scope_check",
            "# Params: freq (default 1000), amp (default 2.0)",
            "#",
            "# Usage: script run awg_scope_check freq=1000 amp=2.0",
            "",
            "freq = 1000",
            "amp = 2.0",
            "",
            'print "=== AWG + Scope Signal Check ==="',
            'print "Frequency: {freq} Hz   Amplitude: {amp} Vpp"',
            "",
            "# Configure AWG",
            "awg1 chan 1 on",
            "awg1 wave 1 sine freq={freq} amp={amp} offset=0",
            "sleep 0.5",
            "",
            "# Autoset scope and measure",
            "scope1 autoset",
            "sleep 1.0",
            "",
            "meas_freq = scope1 meas 1 FREQUENCY unit=Hz",
            "",
            'print "=== Results ==="',
            "log print",
        ],
        "code": '''\
# v1.0.2
"""AWG + Scope signal check — Python API version."""
import time

FREQUENCY = 1000
AMPLITUDE = 2.0
CHANNEL = 1

awg = devices.get("awg") or devices.get("awg1")
scope = devices.get("scope") or devices.get("scope1")

if not awg:
    ColorPrinter.error("No AWG found. Run 'scan' first.")
    raise SystemExit
if not scope:
    ColorPrinter.error("No scope found. Run 'scan' first.")
    raise SystemExit

ColorPrinter.header(f"AWG + Scope Check — {FREQUENCY} Hz, {AMPLITUDE} Vpp")

awg.set_waveform(CHANNEL, "SIN", frequency=FREQUENCY, amplitude=AMPLITUDE, offset=0)
awg.enable_output(CHANNEL, True)
time.sleep(0.5)

if hasattr(scope, "autoset"):
    scope.autoset()
    time.sleep(1.5)

ColorPrinter.info(f"AWG set to: {FREQUENCY} Hz, {AMPLITUDE} Vpp on CH{CHANNEL}")
ColorPrinter.success("Check complete — verify waveform on scope display")
''',
    },
    # ------------------------------------------------------------------
    "freq_sweep": {
        "description": "Sweep AWG through a list of frequencies, scope measures each",
        "lines": [
            "# v1.0.2",
            "# freq_sweep",
            "# Sweeps AWG ch1 through frequencies, measures scope CH1 at each",
            "# Edit the 'for' line to change the frequency list",
            "",
            'print "=== Frequency Sweep ==="',
            "awg1 chan 1 on",
            "awg1 wave 1 sine amp=2.0 offset=0",
            "sleep 0.3",
            "",
            "for f 100 500 1000 5000 10000 50000 100000",
            '  print "Testing {f} Hz..."',
            "  awg1 freq 1 {f}",
            "  sleep 0.4",
            "  freq_{f} = scope1 meas 1 FREQUENCY unit=Hz",
            "end",
            "",
            "awg1 chan 1 off",
            'print "=== Sweep complete ==="',
            "log print",
            "log save freq_sweep.csv",
        ],
        "code": '''\
# v1.0.2
"""Frequency sweep — Python API version."""
import time

FREQUENCIES = [100, 500, 1000, 5000, 10000, 50000, 100000]
AMPLITUDE = 2.0
CHANNEL = 1

awg = devices.get("awg") or devices.get("awg1")
scope = devices.get("scope") or devices.get("scope1")

if not awg:
    ColorPrinter.error("No AWG found. Run 'scan' first.")
    raise SystemExit

ColorPrinter.header("Frequency Sweep")
awg.set_waveform(CHANNEL, "SIN", amplitude=AMPLITUDE, offset=0)
awg.enable_output(CHANNEL, True)
time.sleep(0.3)

for freq in FREQUENCIES:
    awg.set_frequency(CHANNEL, freq)
    time.sleep(0.4)
    ColorPrinter.info(f"  {freq:>8,} Hz — output active")

awg.enable_output(CHANNEL, False)
ColorPrinter.success("Sweep complete")
''',
    },
    # ------------------------------------------------------------------
    "psu_ramp": {
        "description": "Ramp PSU voltage from start to end in N equal steps",
        "lines": [
            "# v1.0.2",
            "# psu_ramp",
            "# Params: v_start, v_end, steps, delay",
            "#",
            "# Usage: script run psu_ramp v_start=0 v_end=12.0 steps=7 delay=0.5",
            "",
            "v_start = 0",
            "v_end = 12.0",
            "steps = 7",
            "delay = 0.5",
            "",
            'print "=== PSU Voltage Ramp ==="',
            'print "{v_start}V -> {v_end}V in {steps} steps"',
            "",
            "psu1 chan 1 on",
            "",
            "# Build step list: pre-calculated values",
            "# (edit this for loop to match v_start, v_end, steps)",
            "for v {v_start} 2.0 4.0 6.0 8.0 10.0 {v_end}",
            '  print "Ramping to {v}V"',
            "  psu1 set 1 {v}",
            "  sleep {delay}",
            "  ramp_{v} = psu1 meas v unit=V",
            "end",
            "",
            'print "=== Ramp complete ==="',
            "log print",
        ],
        "code": '''\
# v1.0.2
"""PSU voltage ramp — Python API version."""
import time

V_START = 0.0
V_END = 12.0
STEPS = 7
DELAY = 0.5
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

ColorPrinter.header(f"PSU Ramp: {V_START}V -> {V_END}V in {STEPS} steps")
psu.enable_output(True)
results = []

for i in range(STEPS + 1):
    v = V_START + (V_END - V_START) * i / STEPS
    psu.set_output_channel(ch, v, CURRENT_LIMIT)
    time.sleep(DELAY)
    measured = psu.measure_voltage(ch) if hasattr(psu, "select_channel") else psu.measure_voltage()
    results.append((v, measured))
    ColorPrinter.info(f"  Step {i}/{STEPS}: set {v:.2f}V, measured {measured:.4f}V")

ColorPrinter.success("Ramp complete")
print("\\nResults:")
for target, meas in results:
    print(f"  {target:8.3f} V  ->  {meas:.4f} V")
''',
    },
    # ------------------------------------------------------------------
    # ===  LIVE PLOT EXAMPLES  =============================================
    # ------------------------------------------------------------------
    "live_voltage_sweep": {
        "description": "Sweep PSU voltages with a live plot tracking DMM readings",
        "lines": [
            "# v1.0.2",
            "# live_voltage_sweep",
            "# Sweeps PSU through voltages while a live plot shows DMM measurements",
            "# in real time.  Works with --mock.",
            "",
            'print "=== Live Voltage Sweep ==="',
            "",
            "# Start live plot BEFORE collecting data",
            'liveplot dmm_* --title "Voltage Sweep" --xlabel "Time (s)" --ylabel "Voltage (V)"',
            "",
            "psu1 chan 1 on",
            "dmm1 config vdc",
            "sleep 0.3",
            "",
            "# Use linspace for many points so the plot updates visibly",
            "sweep_voltages = linspace 0.5 12.0 50",
            "for v {sweep_voltages}",
            '  print "Setting {v}V..."',
            "  psu1 set 1 {v}",
            "  sleep 200ms",
            "  dmm_{v}V = dmm1 meas unit=V",
            "end",
            "",
            "psu1 chan 1 off",
            'print "=== Sweep complete ==="',
            "log print",
        ],
        "code": '''\
# v1.0.2
"""Live voltage sweep — Python API version.

Sweeps the PSU through voltages and records DMM measurements.
A live plot tracks the readings in real time.  Works with --mock.
"""
import time

V_START = 0.5
V_END = 12.0
STEPS = 50
DELAY = 0.15
CURRENT_LIMIT = 0.5
CHANNEL = 1

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

repl.onecmd('liveplot dmm_* --title "Voltage Sweep" --xlabel "Time (s)" --ylabel "Voltage (V)"')

step = (V_END - V_START) / STEPS
voltages = [V_START + step * i for i in range(STEPS + 1)]

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
''',
    },
    # ------------------------------------------------------------------
    "live_multi_plot": {
        "description": "Two live plots: PSU voltage + current during a ramp",
        "lines": [
            "# v1.0.2",
            "# live_multi_plot",
            "# Opens two independent live plots — one for voltage, one for current.",
            "# Watch both update in real time as the PSU ramps.  Works with --mock.",
            "",
            'print "=== Multi-Plot PSU Ramp ==="',
            "",
            "# Open two live plots (each gets its own tab)",
            'liveplot psu_v_* --title "PSU Voltage" --xlabel "Time (s)" --ylabel "Voltage (V)"',
            'liveplot psu_i_* --title "PSU Current" --xlabel "Time (s)" --ylabel "Current (A)"',
            "",
            "psu1 chan 1 on",
            "sleep 0.3",
            "",
            "ramp_voltages = linspace 0.5 12.0 50",
            "for v {ramp_voltages}",
            '  print "Ramping to {v}V..."',
            "  psu1 set 1 {v}",
            "  sleep 250ms",
            "  psu_v_{v} = psu1 meas v unit=V",
            "  psu_i_{v} = psu1 meas i unit=A",
            "end",
            "",
            "psu1 chan 1 off",
            'print "=== Ramp complete ==="',
            "log print",
        ],
        "code": '''\
# v1.0.2
"""Multi-plot PSU ramp — Python API version.

Opens two independent live-plot tabs (voltage and current) and ramps the PSU
through a series of setpoints.  Works with --mock.
"""
import time

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

repl.onecmd('liveplot psu_v_* --title "PSU Voltage" --xlabel "Time (s)" --ylabel "Voltage (V)"')
repl.onecmd('liveplot psu_i_* --title "PSU Current" --xlabel "Time (s)" --ylabel "Current (A)"')

step = (V_END - V_START) / STEPS
voltages = [V_START + step * i for i in range(STEPS + 1)]

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
''',
    },
    # ------------------------------------------------------------------
    "live_freq_sweep": {
        "description": "Live plot of scope frequency measurements during AWG sweep",
        "lines": [
            "# v1.0.2",
            "# live_freq_sweep",
            "# Sweeps AWG frequencies while a live plot tracks scope measurements.",
            "# Works with --mock.",
            "",
            'print "=== Live Frequency Sweep ==="',
            "",
            'liveplot freq_* --title "Frequency Response" --xlabel "Time (s)" --ylabel "Frequency (Hz)"',
            "",
            "awg1 chan 1 on",
            "awg1 wave 1 sine amp=2.0 offset=0",
            "sleep 0.3",
            "",
            "for f 100 200 500 750 1000 2000 3000 5000 7500 10000 15000 20000 30000 50000 75000 100000",
            '  print "Testing {f} Hz..."',
            "  awg1 freq 1 {f}",
            "  sleep 250ms",
            "  freq_{f} = scope1 meas 1 FREQUENCY unit=Hz",
            "end",
            "",
            "awg1 chan 1 off",
            'print "=== Sweep complete ==="',
            "log print",
        ],
        "code": '''\
# v1.0.2
"""Live frequency sweep — Python API version.

Sweeps AWG through frequencies while a live plot tracks scope measurements.
Works with --mock.
"""
import time

FREQUENCIES = [100, 200, 500, 750, 1000, 2000, 3000, 5000, 7500,
               10000, 15000, 20000, 30000, 50000, 75000, 100000]
AMPLITUDE = 2.0
CHANNEL = 1

awg = devices.get("awg") or devices.get("awg1")
scope = devices.get("scope") or devices.get("scope1")

if not awg:
    ColorPrinter.error("No AWG found. Run 'scan' first.")
    raise SystemExit
if not scope:
    ColorPrinter.error("No scope found. Run 'scan' first.")
    raise SystemExit

repl.onecmd('liveplot freq_* --title "Frequency Response" --xlabel "Time (s)" --ylabel "Frequency (Hz)"')

ColorPrinter.header("Live Frequency Sweep")
awg.set_waveform(CHANNEL, "SIN", amplitude=AMPLITUDE, offset=0)
awg.enable_output(CHANNEL, True)
time.sleep(0.3)

for freq in FREQUENCIES:
    awg.set_frequency(CHANNEL, freq)
    time.sleep(0.25)
    measured = scope.measure_bnf(CHANNEL, "FREQUENCY")
    repl.ctx.measurements.record(f"freq_{freq}", measured, "Hz", "scope1")
    ColorPrinter.info(f"  {freq:>8,} Hz  ->  Scope: {measured:.3f} Hz")

awg.enable_output(CHANNEL, False)
ColorPrinter.success("Sweep complete")
''',
    },
    # ------------------------------------------------------------------
    "live_combined_plot": {
        "description": "PSU voltage + current overlaid on ONE live plot during a ramp",
        "lines": [
            "# v1.0.2",
            "# live_combined_plot",
            "# Plots voltage AND current as two series on a single chart.",
            "# Multiple glob patterns on one liveplot = multiple series, one chart.",
            "# Works with --mock.",
            "",
            'print "=== Combined V+I Live Plot ==="',
            "",
            "# Two patterns on ONE liveplot = two series on one chart",
            'liveplot psu_v_* psu_i_* --title "PSU Voltage & Current" --xlabel "Time (s)"',
            "",
            "psu1 chan 1 on",
            "sleep 0.3",
            "",
            "ramp_voltages = linspace 0.5 12.0 50",
            "for v {ramp_voltages}",
            '  print "Ramping to {v}V..."',
            "  psu1 set 1 {v}",
            "  sleep 200ms",
            "  psu_v_{v} = psu1 meas v unit=V",
            "  psu_i_{v} = psu1 meas i unit=A",
            "end",
            "",
            "psu1 chan 1 off",
            'print "=== Ramp complete ==="',
            "log print",
        ],
        "code": '''\
# v1.0.2
"""Combined live plot — Python API version.

Plots PSU voltage AND current as two series overlaid on a single chart.
The key: pass multiple glob patterns to ONE liveplot command.
Works with --mock.
"""
import time

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
''',
    },
    # ------------------------------------------------------------------
    "cross_script_demo": {
        "description": "Single SCPI script that collects data then calls Python for analysis",
        "category": "cross_script",
        "lines": [
            "# v1.0.2",
            "# cross_script_demo",
            "# Collects PSU/DMM measurements, then calls Python inline for analysis.",
            "# REPL variables are auto-injected into the Python script as native types.",
            "# Works with --mock.",
            "",
            'print "=== Cross-Script Demo ==="',
            "",
            "target = 5.0",
            "tolerance = 0.05",
            "",
            "psu1 chan 1 on",
            "dmm1 config vdc",
            "psu1 set 1 {target}",
            "sleep 0.3",
            "",
            "# Collect 10 readings at the target voltage",
            "for i 1 2 3 4 5 6 7 8 9 10",
            "  reading_{i} = dmm1 meas unit=V",
            "  sleep 100ms",
            "end",
            "",
            "psu_v = psu1 meas v unit=V",
            "psu1 chan 1 off",
            "",
            "# Call Python for analysis — target, tolerance, psu_v are auto-available",
            "python cross_script_demo.py",
            "",
            "log print",
            'print "Analysis complete. See variables: mean_v, std_dev, error_pct"',
        ],
        "code": '''\
# v1.0.2
"""Cross-script demo — Python analysis called inline from SCPI.

All REPL variables (target, tolerance, psu_v, reading_1..10) are
auto-injected as native Python types. No manual repl.ctx access needed.
Works with --mock.
"""

# target, tolerance, psu_v are auto-injected as floats
ColorPrinter.header("Cross-Script Demo (Python Analysis)")
ColorPrinter.info(f"Target: {target} V, Tolerance: +/- {tolerance} V")
ColorPrinter.info(f"PSU readback: {psu_v} V")

# Gather all DMM readings from the measurement store
readings = []
for entry in repl.ctx.measurements.entries:
    if entry["label"].startswith("reading_") and entry["unit"] == "V":
        readings.append(entry["value"])

if not readings:
    ColorPrinter.error("No readings found — run the SCPI script, not this file directly.")
    raise SystemExit

# Analyze
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

# Pass/fail
if abs(error) <= tolerance:
    ColorPrinter.success(f"PASS: error {error:+.6f} V is within +/- {tolerance} V")
else:
    ColorPrinter.error(f"FAIL: error {error:+.6f} V exceeds +/- {tolerance} V")
''',
    },
    # ------------------------------------------------------------------
    "conditional_psu_check": {
        "description": "if/elif/else: check PSU voltage is in range and print status",
        "lines": [
            "# v1.0.2",
            "# conditional_psu_check",
            "# Demonstrates if/elif/else conditional branching.",
            "# Works in --mock mode (mock PSU returns ~5.0 V).",
            "",
            "psu1 chan 1 on",
            "psu1 set 1 5.0",
            "sleep 0.3",
            "psu_v = psu1 meas v unit=V",
            "",
            "if psu_v > 5.1",
            '  print "[WARN] Overvoltage: {psu_v} V"',
            "elif psu_v < 4.9",
            '  print "[WARN] Undervoltage: {psu_v} V"',
            "else",
            '  print "[PASS] Voltage in range: {psu_v} V"',
            "end",
            "",
            "psu1 chan 1 off",
        ],
        "code": '''\
# v1.0.2
"""conditional_psu_check — Python API version."""
import time

psu = devices.get("psu") or devices.get("psu1")
if not psu:
    ColorPrinter.error("No PSU found. Run \'scan\' first.")
    raise SystemExit

psu.enable_output(True)
psu.set_output(5.0, 0.5)
time.sleep(0.3)
psu_v = psu.measure_voltage()
repl.ctx.script_vars["psu_v"] = str(psu_v)
repl.ctx.measurements.record("psu_v", psu_v, "V", "psu")

if psu_v > 5.1:
    ColorPrinter.warning(f"[WARN] Overvoltage: {psu_v} V")
elif psu_v < 4.9:
    ColorPrinter.warning(f"[WARN] Undervoltage: {psu_v} V")
else:
    ColorPrinter.success(f"[PASS] Voltage in range: {psu_v} V")

psu.enable_output(False)
''',
    },
    # ------------------------------------------------------------------
    "assert_limits": {
        "description": "assert: verify PSU voltage is within hard safety bounds",
        "lines": [
            "# v1.0.2",
            "# assert_limits",
            "# Demonstrates assert statements for safety-limit checking.",
            "# Works in --mock mode (mock PSU returns ~5.0 V).",
            "",
            "upper_limit psu1 voltage 5.5",
            "psu1 chan 1 on",
            "psu1 set 1 5.0",
            "sleep 0.3",
            "v = psu1 meas v unit=V",
            "",
            'assert v > 0.0 "Voltage must be positive"',
            'assert v < 6.0 "Voltage must be below 6 V"',
            'print "[PASS] Assertions passed — measured {v} V"',
            "",
            "psu1 chan 1 off",
        ],
        "code": '''\
# v1.0.2
"""assert_limits — Python API version."""
import time

psu = devices.get("psu") or devices.get("psu1")
if not psu:
    ColorPrinter.error("No PSU found. Run \'scan\' first.")
    raise SystemExit

psu.enable_output(True)
psu.set_output(5.0, 0.5)
time.sleep(0.3)
v = psu.measure_voltage()
repl.ctx.script_vars["v"] = str(v)
repl.ctx.measurements.record("v", v, "V", "psu")

assert v > 0.0, f"Voltage must be positive (got {v})"
assert v < 6.0, f"Voltage must be below 6 V (got {v})"
ColorPrinter.success(f"[PASS] Assertions passed — measured {v} V")

psu.enable_output(False)
''',
    },
    # ------------------------------------------------------------------
    "while_counter": {
        "description": "while: take 5 PSU voltage samples with a counter and compute average",
        "lines": [
            "# v1.0.2",
            "# while_counter",
            "# Demonstrates while loop with += counter and average calculation.",
            "# Works in --mock mode (mock PSU returns ~5.0 V).",
            "",
            "count = 0",
            "total = 0.0",
            "psu1 chan 1 on",
            "psu1 set 1 5.0",
            "sleep 0.2",
            "",
            "while count < 5",
            "  count += 1",
            "  sample = psu1 meas v unit=V",
            "  total = total + sample",
            '  print "Sample {count}: {sample} V"',
            "  sleep 100ms",
            "end",
            "",
            "avg = total / count unit=V",
            'print "Average over {count} samples: {avg} V"',
            "psu1 chan 1 off",
            "log print",
        ],
        "code": '''\
# v1.0.2
"""while_counter — Python API version."""
import time

psu = devices.get("psu") or devices.get("psu1")
if not psu:
    ColorPrinter.error("No PSU found. Run \'scan\' first.")
    raise SystemExit

psu.enable_output(True)
psu.set_output(5.0, 0.5)
time.sleep(0.2)

samples = []
for i in range(1, 6):
    v = psu.measure_voltage()
    samples.append(v)
    repl.ctx.measurements.record(f"sample_{i}", v, "V", "psu")
    ColorPrinter.info(f"Sample {i}: {v} V")
    time.sleep(0.1)

avg = sum(samples) / len(samples)
repl.ctx.script_vars["avg"] = str(avg)
repl.ctx.measurements.record("avg", avg, "V", "calc")
ColorPrinter.success(f"Average over {len(samples)} samples: {avg:.6f} V")

psu.enable_output(False)
''',
    },
    # ------------------------------------------------------------------
    "syntax_reference": {
        "description": "Full syntax tour: variables, calc, if/elif/else, while, assert, check, boolean ops",
        "lines": [
            "# v1.0.2",
            "# syntax_reference",
            "# A complete tour of all REPL scripting features.",
            "# Works in --mock mode — no real instruments required.",
            "",
            "# ── Variables & expressions ─────────────────────────────",
            "x = 10",
            "y = 3",
            "z = x * y + 1          # arithmetic: z = 31",
            'name = "voltage"        # string assignment',
            "ratio = x / y          # float division",
            "bits = 0xFF & 0x0F     # bitwise AND",
            "shifted = 1 << 4       # left shift: 16",
            "",
            "# ── Augmented assignment & increment/decrement ───────────",
            "count = 0",
            "count += 1             # count = 1",
            "count += 1             # count = 2",
            "count -= 1             # count = 1",
            "count++                # count = 2",
            "count--                # count = 1",
            'print "count = {count}"',
            "",
            "# ── Ternary expression ───────────────────────────────────",
            "label = x > 5 if x > 5 else 0  # ternary: 10 > 5 → True",
            "category = 10 if x > 5 else 0  # proper ternary: 10",
            'print "category = {category}"',
            "",
            "# ── Math functions & constants ───────────────────────────",
            "sq = sqrt(x)           # sqrt(10)",
            "lg = log10(1000)       # 3.0",
            "angle = degrees(pi)    # 180.0",
            'print "sqrt(10) = {sq}  log10(1000) = {lg}  180deg = {angle}"',
            "",
            "# ── Computed assignment with unit logging ─────────────────",
            "a = 5.0",
            "b = 2.0",
            "power = a * b unit=W   # power stored in log with unit W",
            "error_pct = (a - b) / b * 100 unit=%",
            'print "power = {power} W   error_pct = {error_pct} %"',
            "",
            "# ── calc keyword (alternative form) ─────────────────────",
            "calc gain = a / b      # equivalent to: gain = a / b",
            'print "gain = {gain}"',
            "",
            "# ── if / elif / else ─────────────────────────────────────",
            "voltage = 5.05",
            "if voltage > 5.1",
            '  verdict = "OVER"',
            "elif voltage < 4.9",
            '  verdict = "UNDER"',
            "else",
            '  verdict = "OK"',
            "end",
            'print "Voltage {voltage} V → {verdict}"',
            "",
            "# ── assert (hard stop — script aborts on failure) ────────",
            'assert voltage > 0.0 "voltage must be positive"',
            'assert voltage < 6.0 "voltage below safety limit"',
            'print "[PASS] Both asserts passed"',
            "",
            "# ── check (soft — records PASS/FAIL, continues) ──────────",
            'check voltage > 4.9 "above lower bound"',
            'check voltage < 5.1 "below upper bound"',
            'check voltage > 100 "this will fail but script continues"',
            "",
            "# ── while loop ───────────────────────────────────────────",
            "i = 0",
            "total = 0",
            "while i < 5",
            "  i += 1",
            "  total += i",
            '  print "  iter {i}: total = {total}"',
            "end",
            'print "Sum 1..5 = {total}"',
            "",
            "# ── while with break/continue ────────────────────────────",
            "j = 0",
            "while j < 20",
            "  j++",
            "  if j == 3",
            "    continue           # skip 3",
            "  end",
            "  if j > 6",
            "    break              # stop at 6",
            "  end",
            "end",
            'print "j stopped at {j}"',
            "",
            "# ── for loop ─────────────────────────────────────────────",
            "for v 1.0 2.0 3.3 5.0",
            '  print "  for: v = {v}"',
            "end",
            "",
            "# ── Boolean operators (and / or / not / && / ||) ─────────",
            "ok = voltage > 4.9 and voltage < 5.1",
            "also_ok = voltage > 4.9 && voltage < 5.1  # && is alias for and",
            'print "In spec (and): {ok}  In spec (&&): {also_ok}"',
            "",
            "# ── log report (shows check results) ────────────────────",
            "log report",
            "log print",
        ],
        "code": '''\
# v1.0.2
"""syntax_reference — Python API version demonstrating all script features."""
import math

# Variables & expressions
x, y = 10, 3
z = x * y + 1
ratio = x / y
bits = 0xFF & 0x0F
shifted = 1 << 4

# Augmented assignment & increment
count = 0
count += 2
count -= 1
count += 1   # count = 2

# Ternary
category = 10 if x > 5 else 0

# Math functions
sq = math.sqrt(x)
lg = math.log10(1000)
angle = math.degrees(math.pi)
ColorPrinter.info(f"sqrt(10)={sq:.4f}  log10(1000)={lg:.1f}  180deg={angle:.1f}")

# Computed assignments with units
a, b = 5.0, 2.0
power = a * b
repl.ctx.script_vars["power"] = str(power)
repl.ctx.measurements.record("power", power, "W", "calc")
error_pct = (a - b) / b * 100
repl.ctx.script_vars["error_pct"] = str(error_pct)
repl.ctx.measurements.record("error_pct", error_pct, "%", "calc")

# if / elif / else
voltage = 5.05
if voltage > 5.1:
    verdict = "OVER"
elif voltage < 4.9:
    verdict = "UNDER"
else:
    verdict = "OK"
ColorPrinter.info(f"Voltage {voltage} V → {verdict}")

# assert
assert voltage > 0.0, "voltage must be positive"
assert voltage < 6.0, "voltage below safety limit"
ColorPrinter.success("[PASS] Both asserts passed")

# while loop
i = 0
total = 0
while i < 5:
    i += 1
    total += i
ColorPrinter.info(f"Sum 1..5 = {total}")

# for loop
for v in [1.0, 2.0, 3.3, 5.0]:
    ColorPrinter.info(f"  for: v = {v}")

# Boolean operators
ok = voltage > 4.9 and voltage < 5.1
ColorPrinter.info(f"In spec: {ok}")
''',
    },
    # ------------------------------------------------------------------
    # ===  COMPLETE CROSS-SCRIPT EXAMPLE  ================================
    # ------------------------------------------------------------------
    "complete_cross_script": {
        "description": "Comprehensive showcase: every instrument, loop, syntax feature, and all 20 Python/SCPI interop patterns",
        "category": "cross_script",
        "lines": [
            "# v1.0.2",
            "# complete_cross_script",
            "# Comprehensive REPL feature showcase.",
            "# Demonstrates EVERY scripting feature, instrument command,",
            "# and all 10 SCPI-context Python interop patterns (1-10).",
            "#",
            "# Run with: examples load complete_cross_script",
            "#           script run complete_cross_script",
            "#",
            "# Then run the Python analysis phase:",
            "#   python examples/Cross\\ Script/complete_cross_script.py",
            "#",
            "# Works with --mock mode.",
            "#",
            "# Full source: examples/Cross Script/complete_cross_script.scpi",
            "",
            'print "=== Complete Cross Script — REPL Feature Showcase ==="',
            "",
            "# -- Setup --",
            "set +e",
            "target = 5.0",
            "tolerance = 0.05",
            "",
            "# -- PSU sweep with glob-friendly labels --",
            "psu1 chan 1 on",
            "for v 1.0 2.0 3.3 5.0 9.0 12.0",
            "  psu1 set 1 {v}",
            "  sleep 100ms",
            "  psu_sweep_{v} = psu1 meas v unit=V",
            "end",
            "psu1 chan 1 off",
            "",
            "# -- DMM readings in a loop (glob: dmm_reading_*) --",
            "dmm1 config vdc",
            "for i 1 2 3 4 5",
            "  dmm_reading_{i} = dmm1 meas unit=V",
            "  sleep 50ms",
            "end",
            "",
            "# -- Glob pattern plots --",
            'plot psu_sweep_* --title "PSU Sweep"',
            'plot dmm_reading_* --title "DMM Readings"',
            "",
            "# -- Python interop patterns (1, 3, 5, 7, 9 shown inline) --",
            "",
            "# PATTERN 1: pyeval inline",
            "pyeval 6 * 7",
            'print "Pattern 1: 6*7 = {_}"',
            "",
            "# PATTERN 3: pyeval in a loop",
            "for n 1 2 3",
            "  pyeval {n} ** 2",
            '  print "  {n}^2 = {_}"',
            "end",
            "",
            "# PATTERN 5: SCPI var read by pyeval",
            "scpi_greeting = hello_world",
            "pyeval vars['scpi_greeting'].upper()",
            'print "Pattern 5: {_}"',
            "",
            "# PATTERN 7: SCPI var modified by pyeval",
            "modify_me = 10",
            "pyeval float(vars['modify_me']) * 3 + 7",
            "modify_me = {_}",
            'print "Pattern 7: modify_me = {modify_me}"',
            "",
            "# PATTERN 9: pyeval creates value for SCPI",
            "pyeval 2 ** 10",
            "pyeval_result = {_}",
            'print "Pattern 9: pyeval_result = {pyeval_result}"',
            "",
            "# Patterns 2, 4, 6, 8, 10 require helper file —",
            "# see full script: examples/Cross Script/complete_cross_script.scpi",
            "",
            "log print",
            'print "=== SCPI phase complete ==="',
        ],
        "code": '''\
# v1.0.2
"""Complete cross-script demo — Python analysis phase (summary).

Full source: examples/Cross Script/complete_cross_script.py

Demonstrates all 10 Python-context interop patterns (11-20),
statistical analysis, matplotlib plots, and glob pattern demos.
Works with --mock mode.
"""

ColorPrinter.header("Complete Cross-Script Analysis (Python Phase)")
script_vars = repl.ctx.script_vars
all_entries = repl.ctx.measurements.entries

ColorPrinter.info(f"Total measurements: {len(all_entries)}")
ColorPrinter.info(f"Total variables: {len(script_vars)}")

# PATTERN 11: calling SCPI inline
repl.onecmd("psu1 chan 1 on")
repl.onecmd("psu1 set 1 5.0")
repl.onecmd("sleep 100ms")
repl.onecmd("p11_v = psu1 meas v unit=V")
repl.onecmd("psu1 chan 1 off")
ColorPrinter.info(f"Pattern 11: p11_v = {repl.ctx.script_vars.get('p11_v')}")

# PATTERN 13: SCPI inline in a loop
repl.onecmd("psu1 chan 1 on")
for step_v in [1.0, 2.0, 3.0]:
    repl.onecmd(f"psu1 set 1 {step_v}")
    repl.onecmd("sleep 50ms")
    repl.onecmd(f"p13_{step_v} = psu1 meas v unit=V")
repl.onecmd("psu1 chan 1 off")
ColorPrinter.info("Pattern 13: SCPI inline loop complete")

# PATTERN 15: Python var in SCPI inline via f-string
py_voltage = 7.5
repl.onecmd("psu1 chan 1 on")
repl.onecmd(f"psu1 set 1 {py_voltage}")
repl.onecmd("p15_v = psu1 meas v unit=V")
repl.onecmd("psu1 chan 1 off")
ColorPrinter.info(f"Pattern 15: set {py_voltage}V, read {repl.ctx.script_vars.get('p15_v')}")

# PATTERN 17: Python var modified by SCPI inline
repl.ctx.script_vars["py_counter"] = "50"
repl.onecmd("py_counter += 25")
ColorPrinter.info(f"Pattern 17: 50 + 25 = {repl.ctx.script_vars.get('py_counter')}")

# PATTERN 19: value created in SCPI inline, read in Python
repl.onecmd("scpi_inline_val = from_scpi")
ColorPrinter.info(f"Pattern 19: {repl.ctx.script_vars.get('scpi_inline_val')}")

# Patterns 12, 14, 16, 18, 20 require helper SCPI file —
# see full script: examples/Cross Script/complete_cross_script.py

# Glob pattern demos
repl.onecmd('plot psu_sweep_* --title "PSU Sweep (from Python)"')
repl.onecmd('plot dmm_reading_* --title "DMM Readings (from Python)"')

repl.ctx.script_vars["python_was_here"] = "true"
repl.ctx.script_vars["verdict"] = "PASS"
ColorPrinter.success("Analysis complete.")
''',
    },
}
