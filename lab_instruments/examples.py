"""
Bundled example scripts for the SCPI Instrument REPL.

Each entry in EXAMPLES has:
  "description" : one-line summary shown by `examples` command
  "lines"       : list of script lines (same format as .repl_scripts.json)

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
            "set voltage 5.0",
            "set label vtest",
            "",
            'print "=== PSU/DMM Voltage Test ==="',
            'print "Target: {voltage}V"',
            "",
            "# Turn on PSU and set voltage",
            "psu1 chan 1 on",
            "psu1 set {voltage}",
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
            "  psu1 set {v}",
            "  sleep 0.5",
            "  v_{v} = dmm1 meas unit=V",
            "end",
            "",
            "psu1 chan 1 off",
            'print "=== Sweep complete ==="',
            "log print",
            "log save voltage_sweep.csv",
        ],
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
            "set freq 1000",
            "set amp 2.0",
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
            "meas_freq = scope1 meas unit=Hz",
            "",
            'print "=== Results ==="',
            "log print",
        ],
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
            "  freq_{f} = scope1 meas unit=Hz",
            "end",
            "",
            "awg1 chan 1 off",
            'print "=== Sweep complete ==="',
            "log print",
            "log save freq_sweep.csv",
        ],
    },
    # ------------------------------------------------------------------
    # ===  PYTHON EXAMPLES  ================================================
    # ------------------------------------------------------------------
    "psu_dmm_test_py": {
        "description": "Python: Set PSU voltage, measure with DMM, log result",
        "type": "python",
        "code": '''\
"""PSU + DMM voltage test — Python API version.

This script is equivalent to the psu_dmm_test SCPI example.
When run via the REPL ('python psu_dmm_test_py.py') or the GUI (F5),
the following variables are injected automatically:
    devices  — dict of connected instrument drivers
    repl     — the REPL instance
    ColorPrinter — colored terminal output
"""
import time

# --- Configuration ---
VOLTAGE = 5.0
CURRENT_LIMIT = 0.5
CHANNEL = 1  # HP E3631A: 1=6V, 2=25V+, 3=25V-

# --- Get instruments ---
psu = devices.get("psu") or devices.get("psu1")
dmm = devices.get("dmm") or devices.get("dmm1")

if not psu:
    ColorPrinter.error("No PSU found. Run 'scan' first.")
    raise SystemExit

# --- Resolve channel for multi-channel PSUs ---
ch = CHANNEL
channel_map = getattr(psu.__class__, "CHANNEL_FROM_NUMBER", {})
if channel_map:
    ch = channel_map.get(CHANNEL, CHANNEL)

# --- Run test ---
ColorPrinter.header(f"PSU/DMM Voltage Test — {VOLTAGE}V")

psu.set_output_channel(ch, VOLTAGE, CURRENT_LIMIT)
psu.enable_output(True)
time.sleep(0.5)

psu_v = psu.measure_voltage(ch) if hasattr(psu, "select_channel") else psu.measure_voltage()
ColorPrinter.info(f"PSU output:  {psu_v:.4f} V")

if dmm:
    dmm_v = float(dmm.query("MEASURE:VOLTAGE:DC?"))
    ColorPrinter.info(f"DMM reading: {dmm_v:.6f} V")
else:
    ColorPrinter.warning("No DMM connected — skipping DMM measurement")

ColorPrinter.success("Test complete")
''',
    },
    # ------------------------------------------------------------------
    "voltage_sweep_py": {
        "description": "Python: Sweep PSU voltages, log DMM reading at each step",
        "type": "python",
        "code": '''\
"""Voltage sweep — Python API version.

Sweeps the PSU through a list of voltages and records DMM measurements.
"""
import time

# --- Configuration ---
VOLTAGES = [1.0, 2.0, 3.3, 5.0, 9.0, 12.0]
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

# --- Run sweep ---
ColorPrinter.header("Voltage Sweep")

psu.enable_output(True)
results = []

for target_v in VOLTAGES:
    psu.set_output_channel(ch, target_v, CURRENT_LIMIT)
    time.sleep(0.5)
    measured = float(dmm.query("MEASURE:VOLTAGE:DC?"))
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
    "awg_scope_check_py": {
        "description": "Python: Output sine on AWG, measure frequency on scope",
        "type": "python",
        "code": '''\
"""AWG + Scope signal check — Python API version.

Outputs a sine wave on AWG channel 1 and measures it with the scope.
"""
import time

# --- Configuration ---
FREQUENCY = 1000    # Hz
AMPLITUDE = 2.0     # Vpp
CHANNEL = 1

# --- Get instruments ---
awg = devices.get("awg") or devices.get("awg1")
scope = devices.get("scope") or devices.get("scope1")

if not awg:
    ColorPrinter.error("No AWG found. Run 'scan' first.")
    raise SystemExit
if not scope:
    ColorPrinter.error("No scope found. Run 'scan' first.")
    raise SystemExit

# --- Configure AWG ---
ColorPrinter.header(f"AWG + Scope Check — {FREQUENCY} Hz, {AMPLITUDE} Vpp")

awg.set_waveform(CHANNEL, "SIN", frequency=FREQUENCY, amplitude=AMPLITUDE, offset=0)
awg.enable_output(CHANNEL, True)
time.sleep(0.5)

# --- Measure on scope ---
if hasattr(scope, "autoset"):
    scope.autoset()
    time.sleep(1.5)

ColorPrinter.info(f"AWG set to: {FREQUENCY} Hz, {AMPLITUDE} Vpp on CH{CHANNEL}")
ColorPrinter.success("Check complete — verify waveform on scope display")
''',
    },
    # ------------------------------------------------------------------
    "freq_sweep_py": {
        "description": "Python: Sweep AWG frequencies, measure with scope",
        "type": "python",
        "code": '''\
"""Frequency sweep — Python API version.

Sweeps the AWG through a list of frequencies.
"""
import time

# --- Configuration ---
FREQUENCIES = [100, 500, 1000, 5000, 10000, 50000, 100000]
AMPLITUDE = 2.0  # Vpp
CHANNEL = 1

# --- Get instruments ---
awg = devices.get("awg") or devices.get("awg1")
scope = devices.get("scope") or devices.get("scope1")

if not awg:
    ColorPrinter.error("No AWG found. Run 'scan' first.")
    raise SystemExit

# --- Run sweep ---
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
    "psu_ramp_py": {
        "description": "Python: Ramp PSU voltage from start to end in N steps",
        "type": "python",
        "code": '''\
"""PSU voltage ramp — Python API version.

Ramps the PSU from V_START to V_END in STEPS equal increments.
"""
import time

# --- Configuration ---
V_START = 0.0
V_END = 12.0
STEPS = 7
DELAY = 0.5
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

# --- Run ramp ---
ColorPrinter.header(f"PSU Ramp: {V_START}V -> {V_END}V in {STEPS} steps")

psu.enable_output(True)
results = []

for i in range(STEPS + 1):
    v = V_START + (V_END - V_START) * i / STEPS
    psu.set_output_channel(ch, v, CURRENT_LIMIT)
    time.sleep(DELAY)

    if hasattr(psu, "select_channel"):
        measured = psu.measure_voltage(ch)
    else:
        measured = psu.measure_voltage()

    results.append((v, measured))
    ColorPrinter.info(f"  Step {i}/{STEPS}: set {v:.2f}V, measured {measured:.4f}V")

ColorPrinter.success("Ramp complete")
print("\\nResults:")
for target, meas in results:
    print(f"  {target:8.3f} V  ->  {meas:.4f} V")
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
            "set v_start 0",
            "set v_end 12.0",
            "set steps 7",
            "set delay 0.5",
            "",
            'print "=== PSU Voltage Ramp ==="',
            'print "{v_start}V \u2192 {v_end}V in {steps} steps"',
            "",
            "psu1 chan 1 on",
            "",
            "# Build step list: pre-calculated values",
            "# (edit this for loop to match v_start, v_end, steps)",
            "for v {v_start} 2.0 4.0 6.0 8.0 10.0 {v_end}",
            '  print "Ramping to {v}V"',
            "  psu1 set {v}",
            "  sleep {delay}",
            "  ramp_{v} = psu1 meas v unit=V",
            "end",
            "",
            'print "=== Ramp complete ==="',
            "log print",
        ],
    },
}
