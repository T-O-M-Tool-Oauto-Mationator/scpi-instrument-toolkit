# Python API

Control instruments directly from Python — no REPL required.

---

## Quickstart — autodiscovery (recommended)

No USB addresses needed. `find_all()` scans exactly like `scan` in the REPL and returns the same named device dict.

```python
from lab_instruments import find_all, HP_E3631A

instruments = find_all()          # scans USB/GPIB/Serial — same as 'scan' in the REPL
psu = instruments["psu"]          # "psu1", "psu2", etc. if multiple of the same type

psu.enable_output(True)
psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, voltage=5.0)
v = psu.measure_voltage(HP_E3631A.Channel.POSITIVE_6V)
print(f"{v:.4f} V")
psu.enable_output(False)
```

Keys returned by `find_all()` are the same names you see from `list` in the REPL (`psu`, `psu1`, `dmm`, `scope1`, etc.).

---

## Direct instantiation — when you know the address

Use when you have a specific instrument address (find it with `list` in the REPL, or NI MAX / `pyvisa-shell`).

```python
from lab_instruments import HP_E3631A

psu = HP_E3631A("GPIB0::5::INSTR")
psu.connect()

with psu:   # disable_all_channels called automatically on exit
    psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, voltage=3.3, current_limit=0.2)
    psu.enable_output(True)
    v = psu.measure_voltage(HP_E3631A.Channel.POSITIVE_6V)
    print(f"{v:.4f} V")
```

---

## Channel enums

Instruments with named output channels expose a `Channel` enum on the driver class. Pass enum members directly — your IDE will autocomplete them and catch typos at write time.

### HP E3631A

```python
from lab_instruments import HP_E3631A

HP_E3631A.Channel.POSITIVE_6V   # +6 V output  (channel 1 in the REPL)
HP_E3631A.Channel.POSITIVE_25V  # +25 V output (channel 2 in the REPL)
HP_E3631A.Channel.NEGATIVE_25V  # −25 V output (channel 3 in the REPL)
```

```python
psu.set_output_channel(HP_E3631A.Channel.POSITIVE_25V, voltage=12.0, current_limit=0.5)
v = psu.measure_voltage(HP_E3631A.Channel.POSITIVE_25V)
i = psu.measure_current(HP_E3631A.Channel.POSITIVE_25V)
```

Passing a plain string or integer raises `TypeError` immediately with a clear message telling you the valid members — no silent misbehaviour.

### Single-channel instruments

Single-channel instruments (e.g. `MATRIX_MPS6010H`) take no channel argument:

```python
from lab_instruments import find_all

instr = find_all()
psu = instr["psu"]
v = psu.measure_voltage()   # no channel argument needed
```

---

## Instrument enums

Domain-specific parameters (waveform type, DMM mode, coupling, trigger edge) are typed enumerations. Pass them directly to driver methods — they compare equal to their string values so no conversion is needed.

```python
from lab_instruments import WaveformType, DMMMode, CouplingMode, TriggerEdge
```

### WaveformType — AWG waveform shapes

```python
from lab_instruments import find_all, WaveformType

instr = find_all()
awg = instr["awg"]

awg.set_waveform(1, WaveformType.SIN, frequency=1000, amplitude=2.0)
awg.set_waveform(2, WaveformType.SQU, frequency=500, amplitude=1.0)
```

Resolve user input at runtime with `from_alias`:

```python
WaveformType.from_alias("sine")    # → WaveformType.SIN
WaveformType.from_alias("square")  # → WaveformType.SQU
WaveformType.from_alias("SIN")     # → WaveformType.SIN
```

### DMMMode — measurement modes

```python
from lab_instruments import find_all, DMMMode

instr = find_all()
dmm = instr["dmm"]

dmm.configure_dc_voltage()              # configure then read separately
v = dmm.measure_dc_voltage()           # configure + read in one call
r = dmm.measure_resistance_2wire()

# Resolve REPL shorthand to a DMMMode member
mode = DMMMode.from_alias("vdc")        # → DMMMode.DC_VOLTAGE
method_name = f"measure_{mode.value}"    # → "measure_dc_voltage"
```

### CouplingMode — oscilloscope input coupling

```python
from lab_instruments import find_all, CouplingMode

instr = find_all()
scope = instr["scope"]

scope.set_coupling(1, CouplingMode.DC)
scope.set_coupling(2, CouplingMode.AC)
```

### TriggerEdge — trigger slope

```python
from lab_instruments import TriggerEdge, TriggerMode

scope.configure_trigger(channel=1, level=1.0, slope=TriggerEdge.RISE)
```

---

## Using `find_all()` in scripts

```python
from lab_instruments import find_all, HP_E3631A, HP_34401A

instr = find_all()

psu: HP_E3631A = instr["psu"]
dmm: HP_34401A = instr["dmm"]

psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, voltage=5.0)
psu.enable_output(True)

import time
time.sleep(0.5)

v_psu = psu.measure_voltage(HP_E3631A.Channel.POSITIVE_6V)
v_dmm = dmm.measure_dc_voltage()

print(f"PSU reads: {v_psu:.4f} V")
print(f"DMM reads: {v_dmm:.4f} V")
print(f"Error:     {abs(v_psu - v_dmm) * 1000:.2f} mV")

psu.enable_output(False)
```

---

## Voltage sweep with plotting

Sweep a PSU through a range of voltages, measure with a DMM at each step, and plot the results with matplotlib.

```python
import time
import numpy as np
import matplotlib.pyplot as plt
from lab_instruments import find_all

instr = find_all()
psu = instr["psu"]
dmm = instr["dmm"]

# Sweep parameters
V_START, V_END, STEPS = 1.0, 12.0, 23
SETTLE_S = 0.3

voltages = np.linspace(V_START, V_END, STEPS)
measured = []

try:
    psu.enable_output(True)

    for v_set in voltages:
        psu.set_voltage(float(v_set))
        time.sleep(SETTLE_S)
        v_meas = dmm.measure_dc_voltage()
        measured.append(v_meas)
        print(f"  Set {v_set:6.2f} V → Measured {v_meas:.4f} V")
finally:
    psu.enable_output(False)

# Plot setpoint vs measured
measured = np.array(measured)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

ax1.plot(voltages, measured, "o-", markersize=3)
ax1.plot(voltages, voltages, "--", color="gray", label="Ideal")
ax1.set_ylabel("Measured (V)")
ax1.set_title("Voltage Sweep: PSU Setpoint vs DMM Reading")
ax1.legend()
ax1.grid(True, alpha=0.3)

error_mv = (measured - voltages) * 1000
ax2.bar(voltages, error_mv, width=(voltages[1] - voltages[0]) * 0.6)
ax2.set_xlabel("Setpoint (V)")
ax2.set_ylabel("Error (mV)")
ax2.axhline(0, color="gray", linewidth=0.5)
ax2.grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig("voltage_sweep.png", dpi=150)
plt.show()
```

---

## Multi-instrument test with safe shutdown

When using multiple instruments, always wrap your test in `try/finally` so outputs are disabled even if something crashes.

```python
import time
from lab_instruments import find_all

instr = find_all()
psu = instr["psu"]
dmm = instr["dmm"]
awg = instr["awg"]

try:
    # Configure AWG — DC output to bias a sensor
    awg.set_dc_output(1, 3.0)
    awg.enable_output(1, True)
    time.sleep(1)

    # Ramp PSU and collect readings
    psu.enable_output(True)
    results = []

    for voltage in [3.3, 5.0, 9.0, 12.0]:
        psu.set_voltage(voltage)
        time.sleep(0.5)
        reading = dmm.measure_dc_voltage()
        results.append((voltage, reading))
        print(f"  {voltage:5.1f} V → {reading:.4f} V")

    print(f"\n  Collected {len(results)} data points.")

except KeyboardInterrupt:
    print("\n  Ctrl+C — shutting down safely...")
finally:
    # Always disable outputs — each in its own try/except
    # so a failure on one doesn't skip the others
    try:
        psu.enable_output(False)
    except Exception:
        pass
    try:
        awg.enable_output(1, False)
    except Exception:
        pass
    print("  All outputs disabled.")
```

---

## I2C register read/write via EV2300

The EV2300 USB-to-I2C adapter lets you read and write registers on I2C devices. This example initializes a BQ76920 battery monitor AFE and reads its ADC calibration — the same pattern used in real lab tests.

```python
import time
from lab_instruments import find_all

instr = find_all()
ev = instr["ev2300"]

# BQ76920 register map (datasheet SLUSBK2I)
I2C_ADDR      = 0x08
REG_SYS_STAT  = 0x00
REG_SYS_CTRL1 = 0x04
REG_SYS_CTRL2 = 0x05
REG_OV_TRIP   = 0x09
REG_UV_TRIP   = 0x0A
REG_CC_CFG    = 0x0B
REG_ADCGAIN1  = 0x50
REG_ADCOFFSET = 0x51
REG_ADCGAIN2  = 0x59

# --- Initialize: clear faults, enable ADC, enable CHG + DSG ---
init_writes = [
    (REG_SYS_STAT,  0xFF, "clear all faults"),
    (REG_SYS_CTRL1, 0x10, "enable ADC"),
    (REG_SYS_CTRL2, 0x03, "enable CHG + DSG"),
    (REG_CC_CFG,    0x19, "coulomb counter config"),
]
for reg, val, desc in init_writes:
    r = ev.write_byte(I2C_ADDR, reg, val)
    status = "OK" if r["ok"] else f"FAIL: {r['status_text']}"
    print(f"  Write 0x{reg:02X} = 0x{val:02X} ({desc}) — {status}")
    time.sleep(0.1)

time.sleep(1)  # wait for ADC to stabilize

# --- Read ADC calibration ---
g1 = ev.read_byte(I2C_ADDR, REG_ADCGAIN1)["value"]
g2 = ev.read_byte(I2C_ADDR, REG_ADCGAIN2)["value"]
offset = ev.read_byte(I2C_ADDR, REG_ADCOFFSET)["value"]

gain_uv = 365 + (((g1 >> 3) & 0x03) << 3) | ((g2 >> 5) & 0x07)
offset_mv = offset if offset < 128 else offset - 256
print(f"  ADC gain: {gain_uv} uV/LSB, offset: {offset_mv} mV")

# --- Set OV/UV thresholds ---
ev.write_byte(I2C_ADDR, REG_OV_TRIP, 0xBE)  # ~4.301 V/cell
ev.write_byte(I2C_ADDR, REG_UV_TRIP, 0x97)   # ~2.505 V/cell

# --- Monitor: read status register to check for fault flags ---
r = ev.read_byte(I2C_ADDR, REG_SYS_STAT)
if r["ok"]:
    stat = r["value"]
    print(f"  SYS_STAT: 0x{stat:02X} — OV={'SET' if stat & 0x04 else 'clear'}, UV={'SET' if stat & 0x08 else 'clear'}")
```

---

## Saving results to CSV

Use pandas to collect measurements into a DataFrame and export.

```python
import time
import numpy as np
import pandas as pd
from lab_instruments import find_all

instr = find_all()
psu = instr["psu"]
dmm = instr["dmm"]

voltages = np.linspace(1.0, 12.0, 23)
rows = []

try:
    psu.enable_output(True)
    for v_set in voltages:
        psu.set_voltage(float(v_set))
        time.sleep(0.3)
        v_meas = dmm.measure_dc_voltage()
        rows.append({"setpoint_V": round(float(v_set), 3), "measured_V": round(v_meas, 6)})
finally:
    psu.enable_output(False)

df = pd.DataFrame(rows)
df["error_mV"] = (df["measured_V"] - df["setpoint_V"]) * 1000
df.to_csv("sweep_results.csv", index=False)
print(df.to_string(index=False))
```

---

## Where to find more

See the [API reference](api/base.md) for full method signatures generated directly from driver source. All drivers are documented with Google-style docstrings.

| Driver | Instrument |
|--------|------------|
| `HP_E3631A` | Triple-output PSU (+6 V / ±25 V) |
| `Keysight_EDU36311A` | Triple-output PSU (+6 V / ±30 V) |
| `MATRIX_MPS6010H` | Single-channel PSU (0–60 V / 0–10 A) |
| `HP_34401A` | 6.5-digit bench DMM |
| `Keysight_EDU34450A` | 5.5-digit bench DMM |
| `Owon_XDM1041` | 7.5-digit bench DMM |
| `Rigol_DHO804` | 4-channel oscilloscope |
| `Tektronix_MSO2024` | 4-channel mixed-signal oscilloscope |
| `Keysight_DSOX1204G` | 4-channel oscilloscope |
| `Keysight_EDU33212A` | Dual-channel arbitrary waveform generator |
| `BK_4063` | Dual-channel arbitrary waveform generator |
| `JDS6600_Generator` | DDS signal generator (serial/USB) |
| `NI_PXIe_4139` | Source measure unit (SMU) |
| `TI_EV2300` | USB-to-I2C/SMBus adapter |
