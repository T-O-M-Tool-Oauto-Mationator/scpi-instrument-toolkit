# Examples

Complete Python scripts demonstrating common lab workflows.

---

## PSU + DMM: Voltage Verification

Set a voltage on the power supply and verify it with a multimeter.

```python
from lab_instruments import HP_E3631A, HP_34401A

psu = HP_E3631A("GPIB0::5::INSTR")
dmm = HP_34401A("GPIB0::22::INSTR")
psu.connect()
dmm.connect()

try:
    # Set PSU to 3.3V
    psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, 3.3, current_limit=0.5)
    psu.enable_output(True)

    # Measure with DMM
    dmm.configure_dc_voltage()
    measured = dmm.read()
    expected = 3.3

    error = measured - expected
    print(f"Set:      {expected:.3f} V")
    print(f"Measured: {measured:.6f} V")
    print(f"Error:    {error * 1000:.3f} mV")
finally:
    psu.enable_output(False)
    psu.disconnect()
    dmm.disconnect()
```

---

## Voltage Sweep with Data Collection

Sweep a power supply through voltages and log DMM readings.

```python
import time
import csv
from lab_instruments import HP_E3631A, HP_34401A

psu = HP_E3631A("GPIB0::5::INSTR")
dmm = HP_34401A("GPIB0::22::INSTR")
psu.connect()
dmm.connect()

voltages = [1.0, 2.0, 3.3, 5.0]
results = []

try:
    psu.enable_output(True)
    dmm.configure_dc_voltage()

    for target_v in voltages:
        psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, target_v, current_limit=0.5)
        time.sleep(0.5)  # Settle time

        measured_v = dmm.read()
        measured_i = psu.measure_current(HP_E3631A.Channel.POSITIVE_6V)
        results.append({"target": target_v, "measured_v": measured_v, "current": measured_i})
        print(f"{target_v:.1f} V -> {measured_v:.6f} V, {measured_i:.4f} A")

    # Export to CSV
    with open("sweep_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["target", "measured_v", "current"])
        writer.writeheader()
        writer.writerows(results)
    print("Saved to sweep_results.csv")
finally:
    psu.enable_output(False)
    psu.disconnect()
    dmm.disconnect()
```

---

## AWG + Scope: Signal Check

Output a sine wave from the AWG and measure it on the oscilloscope.

```python
import time
from lab_instruments import Keysight_EDU33212A, Rigol_DHO804

awg = Keysight_EDU33212A("USB0::0x2A8D::0x1602::MY12345678::INSTR")
scope = Rigol_DHO804("USB0::0x1AB1::0x044C::DHO8A000000::INSTR")
awg.connect()
scope.connect()

try:
    # Output 1 kHz sine, 2 Vpp
    awg.set_waveform(1, "SIN", frequency=1000, amplitude=2.0)
    awg.enable_output(1, True)
    time.sleep(0.5)

    # Measure on scope
    scope.enable_channel(1)
    scope.autoset()
    time.sleep(1.0)

    freq = scope.measure_frequency(1)
    vpp = scope.measure_vpp(1)
    print(f"Frequency: {freq:.1f} Hz")
    print(f"Amplitude: {vpp:.3f} Vpp")

    # Capture waveform
    waveform = scope.acquire_waveform(1)
    waveform.plot("1 kHz Sine Wave")
finally:
    awg.disable_all_channels()
    awg.disconnect()
    scope.disconnect()
```

---

## Auto-Discovery

Let the toolkit find and connect to all instruments automatically.

```python
from lab_instruments import find_all

instruments = find_all()

for name, inst in instruments.items():
    print(f"{name}: {type(inst).__name__} at {inst.resource_name}")

# Access by name
if "psu1" in instruments:
    psu = instruments["psu1"]
    psu.enable_output(True)
    psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, 5.0)
```

---

## SMU: IV Curve

Sweep voltage and measure current on the NI PXIe-4139 SMU.

```python
import csv
from lab_instruments import NI_PXIe_4139

smu = NI_PXIe_4139("PXI1Slot2")
smu.connect()

voltages = [v * 0.1 for v in range(0, 34)]  # 0 to 3.3V in 100mV steps
results = []

try:
    smu.set_current_limit(0.1)
    smu.enable_output(True)

    for v in voltages:
        smu.set_voltage(v)
        result = smu.measure_vi()
        results.append({
            "voltage_set": v,
            "voltage_meas": result["voltage"],
            "current": result["current"],
            "compliance": result["in_compliance"],
        })
        print(f"{v:.1f} V -> {result['current']*1000:.3f} mA")

    # Export
    with open("iv_curve.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
finally:
    smu.enable_output(False)
    smu.disconnect()
```

---

## Multi-Instrument with Context Managers

```python
from lab_instruments import HP_E3631A, HP_34401A, Rigol_DHO804

psu = HP_E3631A("GPIB0::5::INSTR")
dmm = HP_34401A("GPIB0::22::INSTR")
scope = Rigol_DHO804("USB0::0x1AB1::0x044C::DHO8A000000::INSTR")

psu.connect()
dmm.connect()
scope.connect()

try:
    with psu:
        psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, 5.0, current_limit=1.0)
        psu.enable_output(True)

        with dmm:
            dmm.configure_dc_voltage()
            voltage = dmm.read()
            print(f"DMM reads: {voltage:.6f} V")

        scope.enable_channel(1)
        scope.autoset()
        freq = scope.measure_frequency(1)
        vpp = scope.measure_vpp(1)
        print(f"Scope: {freq:.1f} Hz, {vpp:.3f} Vpp")
finally:
    psu.disconnect()
    dmm.disconnect()
    scope.disconnect()
```

---

## Data Collection with pandas

```python
import time
import pandas as pd
from lab_instruments import HP_E3631A, HP_34401A

psu = HP_E3631A("GPIB0::5::INSTR")
dmm = HP_34401A("GPIB0::22::INSTR")
psu.connect()
dmm.connect()

data = []

try:
    psu.enable_output(True)
    dmm.configure_dc_voltage()

    for target in [1.0, 2.0, 3.3, 5.0]:
        psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, target, current_limit=0.5)
        time.sleep(0.5)

        # Take 5 readings at each voltage
        readings = [dmm.read() for _ in range(5)]
        for r in readings:
            data.append({"target_v": target, "measured_v": r})

    df = pd.DataFrame(data)
    summary = df.groupby("target_v")["measured_v"].agg(["mean", "std", "count"])
    print(summary)
    df.to_csv("measurements.csv", index=False)
finally:
    psu.enable_output(False)
    psu.disconnect()
    dmm.disconnect()
```

---

## REPL Scripting Examples

The REPL includes a full scripting engine with variables, loops, conditionals,
and Python integration.  Use `--mock` mode to test without hardware:

```bash
scpi-repl --mock
```

### SCPI Script: Voltage Sweep with Glob Plots

```scpi
# voltage_sweep.scpi — run via: script run voltage_sweep
psu1 chan 1 on
dmm1 config vdc

# linspace generates 10 evenly-spaced voltages from 0.5 to 12V
sweep_voltages = linspace 0.5 12.0 10

# Loop through voltages — labels like dmm_reading_0.5, dmm_reading_1.77, ...
for v {sweep_voltages}
  psu1 set 1 {v}
  sleep 100ms
  dmm_reading_{v} = dmm1 meas unit=V
end

psu1 chan 1 off

# Glob patterns: dmm_reading_* matches all labels above
plot dmm_reading_* --title "DMM Readings"
liveplot dmm_reading_* --title "Live DMM" --xlabel "Step" --ylabel "V"
log print
log save sweep_results.csv
```

### Inline Python with `pyeval`

`pyeval` evaluates a Python expression with access to all REPL variables:

```scpi
x = 5.0
if 1 > 0
  pyeval float(vars['x']) ** 2 + 1
  result = {_}
  pyeval "x squared plus one = " + str(vars.get('result', '?'))
end
```

The `vars` dict contains all script variables.  The result is stored in `_`.
Use `if 1 > 0 ... end` blocks to read runtime values (pyeval results,
python file modifications) — outside if blocks, `{var}` is resolved at
expansion time.

---

## Cross-Script Workflow (SCPI + Python)

The toolkit supports a two-phase workflow:

1. **SCPI phase** — collect measurements with instrument commands
2. **Python phase** — analyze data with matplotlib, statistics, etc.

Variables and measurements flow between the two via `repl.ctx.script_vars`
and `repl.ctx.measurements`.

### All 20 Python ↔ SCPI Interop Patterns

The `complete_cross_script` example demonstrates all 20 permutations:

**From SCPI context (patterns 1-10):**

| # | Pattern | Mechanism |
|---|---------|-----------|
| 1 | Call Python inline | `pyeval <expr>` |
| 2 | Call Python file in a loop | `python file.py` inside `for` |
| 3 | Call Python inline in a loop | `pyeval` inside `for` |
| 4 | Call Python file | `python file.py` |
| 5 | SCPI var → pyeval | `pyeval vars['varname']` |
| 6 | SCPI var → Python file | Python reads `repl.ctx.script_vars` |
| 7 | SCPI var modified by pyeval | `pyeval` computes, `_ = {result}` |
| 8 | SCPI var modified by Python file | Python writes `repl.ctx.script_vars` |
| 9 | pyeval value → SCPI | pyeval result in `_`, SCPI uses `{_}` |
| 10 | Python file value → SCPI | Python sets `repl.ctx.script_vars`, SCPI reads |

**From Python context (patterns 11-20):**

| # | Pattern | Mechanism |
|---|---------|-----------|
| 11 | Call SCPI inline | `repl.onecmd("psu1 set 1 5.0")` |
| 12 | Call SCPI file in a loop | `repl.onecmd("script run X")` in `for` |
| 13 | Call SCPI inline in a loop | `repl.onecmd()` in Python `for` |
| 14 | Call SCPI file | `repl.onecmd("script run X")` |
| 15 | Python var → SCPI inline | f-string: `repl.onecmd(f"psu1 set 1 {v}")` |
| 16 | Python var → SCPI file | Store in `script_vars`, script reads `{var}` |
| 17 | Python var modified by SCPI inline | SCPI modifies `script_vars`, Python reads back |
| 18 | Python var modified by SCPI file | Script modifies `script_vars`, Python reads back |
| 19 | SCPI inline value → Python | `repl.onecmd` sets var, Python reads `script_vars` |
| 20 | SCPI file value → Python | Script sets var, Python reads `script_vars` |

### Key Concept: Expansion Time vs Runtime

In SCPI scripts, `{variable}` substitution happens at **expansion time**
(before the script runs).  To read values set at **runtime** (by `pyeval`,
`python`, or instrument reads), wrap the dependent code in an
`if 1 > 0 ... end` block — inside `if`/`while` blocks, all commands
execute at runtime with live variable access.

```scpi
# This does NOT work (expansion-time substitution):
pyeval 6 * 7
print "Result: {_}"     # Shows old value of _

# This DOES work (runtime context):
if 1 > 0
  pyeval 6 * 7
  print "Result: {_}"   # Shows 42
end
```

### Running the Complete Example

```bash
scpi-repl --mock
```

```
examples load complete_cross_script
script run complete_cross_script
python examples/Cross\ Script/complete_cross_script.py
```

Or load from files directly:

```
script import complete "examples/Cross Script/complete_cross_script.scpi"
script run complete
python "examples/Cross Script/complete_cross_script.py"
```

### Glob Patterns in Plots

Measurement labels created in loops (e.g. `dmm_reading_{v}`) produce
labels like `dmm_reading_1.0`, `dmm_reading_2.0`, etc.  Use glob patterns
to match them:

```scpi
plot dmm_reading_*                           # single pattern
plot psu_v_* psu_i_* --title "V and I"      # multiple series
liveplot sweep_* --title "Live" --xlabel "Step" --ylabel "V"
plot sweep_* --save results.png              # save to file
```
