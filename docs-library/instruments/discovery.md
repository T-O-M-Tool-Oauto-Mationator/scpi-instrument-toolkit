# InstrumentDiscovery & find_all

Auto-detect connected instruments and return typed driver instances.

```python
from lab_instruments import InstrumentDiscovery, find_all
```

---

## find_all()

Convenience function that scans all VISA resources and returns a dictionary of detected instruments.

```python
instruments = find_all()
```

**Returns:** `dict[str, DeviceManager]` — Keys are auto-assigned names (`psu1`, `dmm1`, `scope1`, etc.), values are connected driver instances.

### Example

```python
from lab_instruments import find_all

instruments = find_all()

for name, inst in instruments.items():
    print(f"{name}: {type(inst).__name__} at {inst.resource_name}")
# psu1: HP_E3631A at GPIB0::5::INSTR
# dmm1: HP_34401A at GPIB0::22::INSTR
# scope1: Rigol_DHO804 at USB0::0x1AB1::0x044C::DHO8A000000::INSTR
```

---

## InstrumentDiscovery

Class for more control over the discovery process.

### Constructor

```python
discovery = InstrumentDiscovery()
```

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `scan()` | Scan all VISA resources, identify instruments, return connected drivers | `dict[str, DeviceManager]` |

### Class Attributes

| Attribute | Description |
|-----------|-------------|
| `MODEL_MAP` | `dict` mapping model substrings to driver classes |
| `NAME_MAP` | `dict` mapping model substrings to friendly names (`psu`, `dmm`, `scope`, `awg`, `smu`) |

### Example

```python
from lab_instruments import InstrumentDiscovery

discovery = InstrumentDiscovery()
instruments = discovery.scan()

# Access by auto-assigned name
psu = instruments.get("psu1")
if psu:
    psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, 5.0)
```

### Supported Model Detection

The discovery system identifies instruments by matching substrings in the `*IDN?` response:

| Substring | Driver | Name |
|-----------|--------|------|
| `E3631A` | `HP_E3631A` | `psu` |
| `EDU36311A` | `Keysight_EDU36311A` | `psu` |
| `MPS-6010H-1C` | `MATRIX_MPS6010H` | `psu` |
| `34401A` | `HP_34401A` | `dmm` |
| `EDU34450A` | `Keysight_EDU34450A` | `dmm` |
| `XDM1041` | `Owon_XDM1041` | `dmm` |
| `EDU33212A` | `Keysight_EDU33212A` | `awg` |
| `4063` | `BK_4063` | `awg` |
| `JDS6600` | `JDS6600_Generator` | `awg` |
| `DHO804` | `Rigol_DHO804` | `scope` |
| `MSO2024` | `Tektronix_MSO2024` | `scope` |
| `DSOX1204G` | `Keysight_DSOX1204G` | `scope` |
| `PXIe-4139` | `NI_PXIe_4139` | `smu` |
| `EV2300` | `TI_EV2300` | `ev2300` |
