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
    "while_demo": {
        "description": "while loop examples: countdown, accumulator, break/continue",
        "lines": [
            "# while_demo",
            "# Demonstrates while loops, break, continue, and compound assignment",
            "",
            'print "=== Countdown ==="',
            "n = 5",
            "while n > 0",
            "  print  {n}...",
            "  n--",
            "end",
            'print "Go!"',
            "",
            'print ""',
            'print "=== Accumulate (skip 5) ==="',
            "total = 0",
            "i = 1",
            "while i <= 10",
            "  if i == 5",
            "    i++",
            "    continue",
            "  end",
            "  total += i",
            "  i++",
            "end",
            'print "Sum of 1..10 (excl 5) = {total}"',
            "",
            'print ""',
            'print "=== Break on threshold ==="',
            "x = 0",
            "while x < 100",
            "  x += 7",
            "  if x > 30",
            "    break",
            "  end",
            "end",
            'print "Stopped at x={x}"',
            "",
            'print ""',
            'print "=== Power of 2 ==="',
            "val = 1",
            "step = 0",
            "while val < 1000",
            "  val *= 2",
            "  step++",
            "end",
            'print "2^{step} = {val}"',
        ],
    },
    # ------------------------------------------------------------------
    "if_elif_else_demo": {
        "description": "if/elif/else branching with numeric and string conditions",
        "lines": [
            "# if_elif_else_demo",
            "# Demonstrates if / elif / else with numeric and string comparisons",
            "",
            "# Numeric branching",
            'print "=== Numeric ==="',
            "voltage = 5.0",
            "if voltage > 5.2",
            '  print "OVER: {voltage}V"',
            "elif voltage < 4.8",
            '  print "UNDER: {voltage}V"',
            "else",
            '  print "PASS: {voltage}V"',
            "end",
            "",
            "# String branching",
            'print ""',
            'print "=== String mode select ==="',
            'mode = "fast"',
            'if mode == "fast"',
            '  print "High-speed mode selected"',
            'elif mode == "slow"',
            '  print "Low-speed mode selected"',
            "else",
            '  print "Unknown mode: {mode}"',
            "end",
            "",
            "# Nested if inside while",
            'print ""',
            'print "=== Nested if in while ==="',
            "i = 1",
            "while i <= 6",
            "  if i == 3 or i == 6",
            '    print "  {i} is divisible by 3"',
            "  else",
            '    print "  {i}"',
            "  end",
            "  i++",
            "end",
        ],
    },
    # ------------------------------------------------------------------
    "assert_demo": {
        "description": "assert (hard-stop) and check (soft) usage examples",
        "lines": [
            "# assert_demo",
            "# Demonstrates assert (hard-stop on failure) vs check (soft, continues)",
            "#",
            "# In this demo we use known values rather than real instruments.",
            "# In real use: replace static assignments with instrument reads.",
            "",
            "voltage = 5.01",
            "current = 0.123",
            "",
            "# assert: must pass or script stops",
            'print "=== Hard assertions ==="',
            "assert voltage > 0 and voltage < 30 \"Voltage in range\"",
            "assert current >= 0 \"Current non-negative\"",
            "",
            "# check: soft pass/fail, logged to report",
            'print ""',
            'print "=== Soft checks ==="',
            "check output_voltage 4.75 5.25",
            "check output_current 0.0 0.5",
            "",
            'print ""',
            'print "=== pyeval: derived values ==="',
            "power = pyeval voltage * current",
            'print "Power = {power}W"',
            "assert power > 0 \"Power must be positive\"",
            "check output_power 0.0 10.0",
            "",
            "log print",
        ],
    },
    # ------------------------------------------------------------------
    "pyeval_demo": {
        "description": "pyeval: compute derived variables with Python math",
        "lines": [
            "# pyeval_demo",
            "# Demonstrates pyeval for inline Python expression evaluation",
            "",
            "# Basic arithmetic",
            "voltage = 5.0",
            "current = 0.25",
            "power   = pyeval voltage * current",
            'print "P = V*I = {voltage} * {current} = {power}"',
            "",
            "# Math functions (sqrt, log, sin, cos, exp, etc.)",
            "pk2pk = 2.828",
            "rms   = pyeval sqrt(pk2pk ** 2 / 8)",
            'print "Vrms (sine) = {rms}"',
            "",
            "vin  = 1.0",
            "vout = 10.0",
            "gain_db = pyeval 20 * log(vout / vin)",
            'print "Gain = {gain_db} dB"',
            "",
            "# Use math constants",
            "freq = 1000",
            "omega = pyeval 2 * pi * freq",
            'print "omega = {omega} rad/s"',
            "",
            "# Round to N decimal places",
            "raw = 3.141592653",
            "approx = pyeval round(raw, 3)",
            'print "pi ≈ {approx}"',
            "",
            "# min/max",
            "a = 7",
            "b = 3",
            "lo = pyeval min(a, b)",
            "hi = pyeval max(a, b)",
            'print "min={lo}, max={hi}"',
        ],
    },
    # ------------------------------------------------------------------
    "cross_script_demo": {
        "description": "Pass REPL variables to an external Python script (auto-injection)",
        "lines": [
            "# cross_script_demo",
            "# Variables set here are automatically available in analysis.py",
            "# as native Python types — no float() or int() conversion needed.",
            "",
            "voltage   = 5.0",
            "current   = 0.25",
            "tolerance = 0.05",
            "label     = output_test",
            "steps     = 10",
            "",
            'print "Running analysis with: V={voltage}, I={current}, tol={tolerance}"',
            "python cross_script_demo.py",
        ],
        "code": '''\
"""cross_script_demo.py — uses REPL vars injected as native Python types.

All variables set in the SCPI script (voltage, current, tolerance, label,
steps) are available directly in this file without any float() or int()
conversion. They are also collected in the 'vars' dict.
"""

# 'voltage', 'current', etc. are already float/int/str — use them directly
low  = voltage * (1 - tolerance)
high = voltage * (1 + tolerance)

print(f"Testing '{label}'")
print(f"  V = {voltage} V  (acceptable {low:.3f} – {high:.3f} V)")
print(f"  I = {current} A")

power = voltage * current
print(f"  P = {power:.4f} W")

# 'steps' is already an int
print(f"  Sweeping {steps} steps:")
for i in range(steps):
    frac = i / (steps - 1) if steps > 1 else 0
    v_step = low + frac * (high - low)
    print(f"    step {i+1:2d}/{steps}: V={v_step:.4f}")

# 'vars' dict always available (all values as strings)
print(f"\\nAll script vars: {vars}")
''',
    },
    # ------------------------------------------------------------------
    "syntax_reference": {
        "description": "Comprehensive SCPI script covering all language features",
        "lines": [
            "# syntax_reference",
            "# A tour of every scripting feature in one file.",
            "# Run with: script run syntax_reference",
            "",
            "# ── Variables & arithmetic ─────────────────────────────",
            "voltage = 5.0",
            "current = 0.25",
            "label   = test_run",
            "",
            "doubled = voltage * 2",
            "offset  = voltage - 0.5",
            'print "doubled={doubled}, offset={offset}"',
            "",
            "# ── Compound assignment & increment ────────────────────",
            "count = 0",
            "count++",
            "count++",
            "count += 3",
            'print "count={count}"',
            "",
            "total = 10",
            "total -= 3",
            "total *= 2",
            "total /= 7",
            'print "total={total}"',
            "",
            "# ── pyeval ─────────────────────────────────────────────",
            "power  = pyeval voltage * current",
            "gain   = pyeval 20 * log(10.0 / 1.0)",
            'print "power={power}, gain_dB={gain}"',
            "",
            "# ── linspace + for ─────────────────────────────────────",
            "VSWEEP = linspace 1 5 5",
            "for v {VSWEEP}",
            '  print "  v={v}"',
            "end",
            "",
            "# ── while + break + continue ───────────────────────────",
            "x = 0",
            "while x < 10",
            "  x++",
            "  if x == 4",
            "    continue",
            "  end",
            "  if x == 7",
            "    break",
            "  end",
            '  print "  x={x}"',
            "end",
            'print "Final x={x}"',
            "",
            "# ── if / elif / else ───────────────────────────────────",
            "score = 82",
            "if score >= 90",
            '  print "Grade: A"',
            "elif score >= 80",
            '  print "Grade: B"',
            "elif score >= 70",
            '  print "Grade: C"',
            "else",
            '  print "Grade: F"',
            "end",
            "",
            "# ── String comparison ──────────────────────────────────",
            'mode = "fast"',
            'if mode == "fast"',
            '  print "Mode: high-speed"',
            "else",
            '  print "Mode: normal"',
            "end",
            "",
            "# ── Boolean operators ──────────────────────────────────",
            "a = 5",
            "b = 3",
            "if a > 0 and b > 0",
            '  print "Both positive"',
            "end",
            "if a > 10 or b > 0",
            '  print "At least one condition"',
            "end",
            "",
            "# ── assert vs check ────────────────────────────────────",
            "measured = 5.01",
            "assert measured > 0 \"Must be positive\"",
            "check output 4.75 5.25",
            "",
            "# ── sleep ──────────────────────────────────────────────",
            "sleep 10ms",
            "",
            'print "=== syntax_reference complete ==="',
        ],
    },
}
