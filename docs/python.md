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
method_name = f"measure_{mode}"         # → "measure_dc_voltage"
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
