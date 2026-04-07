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

Single-channel instruments (e.g. `MATRIX_MPS6010H`, `HP_34401A`) take no channel argument:

```python
dmm = instruments["dmm"]
v = dmm.measure_voltage()   # no channel needed
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
v_dmm = dmm.measure_voltage()

print(f"PSU reads: {v_psu:.4f} V")
print(f"DMM reads: {v_dmm:.4f} V")
print(f"Error:     {abs(v_psu - v_dmm) * 1000:.2f} mV")

psu.enable_output(False)
```

---

## Where to find more

The driver source files are the canonical reference for every method, valid range, and error condition:

| Driver | File |
|--------|------|
| `HP_E3631A` | `lab_instruments/src/hp_e3631a.py` |
| `MATRIX_MPS6010H` | `lab_instruments/src/matrix_mps6010h.py` |
| `HP_34401A` | `lab_instruments/src/hp_34401a.py` |
| `Keysight_EDU36311A` | `lab_instruments/src/keysight_edu36311a.py` |
| `Keysight_EDU34450A` | `lab_instruments/src/keysight_edu34450a.py` |
| `Rigol_DHO804` | `lab_instruments/src/rigol_dho804.py` |
| `Tektronix_MSO2024` | `lab_instruments/src/tektronix_mso2024.py` |
| `Keysight_EDU33212A` | `lab_instruments/src/keysight_edu33212a.py` |
| `NI_PXIe_4139` | `lab_instruments/src/ni_pxie_4139.py` |
