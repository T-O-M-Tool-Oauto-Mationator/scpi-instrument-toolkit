# NI PXIe-4139 (SMU)

Source Measure Unit: DC voltage/current source with measurement. Interface: PXI (via nidcpower).

```python
from lab_instruments import NI_PXIe_4139
```

!!! warning "Optional Dependency"
    Requires the `nidcpower` package: `pip install nidcpower`. Also requires NI-DCPower driver software. If not installed, `NI_PXIe_4139` will be `None` when imported.

!!! note "Not SCPI-Based"
    This driver uses the NI-DCPower Python API, **not** PyVISA/SCPI. It does not inherit from `DeviceManager`.

---

## Quick Example

```python
from lab_instruments import NI_PXIe_4139

smu = NI_PXIe_4139("PXI1Slot2")
smu.connect()

try:
    smu.set_voltage(3.3)
    smu.set_current_limit(0.1)
    smu.enable_output(True)

    result = smu.measure_vi()
    print(f"V: {result['voltage']:.4f} V")
    print(f"I: {result['current']:.6f} A")
    print(f"Compliance: {result['in_compliance']}")
finally:
    smu.enable_output(False)
    smu.disconnect()
```

---

## Context Manager

```python
smu = NI_PXIe_4139("PXI1Slot2")
smu.connect()

with smu:
    smu.set_voltage(5.0)
    smu.set_current_limit(0.5)
    smu.enable_output(True)
    # ...
# Output disabled and zeroed on exit
```

---

## Specifications

| Parameter | Value |
|-----------|-------|
| Voltage Range | -60 V to +60 V |
| Current Range | -3 A to +3 A (DC) |
| Max Source Power | 20 W |
| Max Sink Power | 12 W |
| Default Current Limit | 10 mA |

---

## Methods

### Output Control

| Method | Description |
|--------|-------------|
| `enable_output(enabled=True)` | Enable/disable output |
| `disable_all_channels()` | Set to safe state (0V, low limit, off) |
| `set_voltage(voltage)` | Set DC voltage level (-60 to +60 V) |
| `set_current_limit(current)` | Set current limit (0 to 3 A) |
| `set_output_channel(channel, voltage, current_limit=None)` | Compatibility method (ignores channel) |

### Measurement

| Method | Returns | Description |
|--------|---------|-------------|
| `measure_vi()` | `dict` | `{"voltage": float, "current": float, "in_compliance": bool}` |
| `measure_voltage()` | `float` | Output voltage |
| `measure_current()` | `float` | Output current |
| `query_in_compliance()` | `bool` | Whether compliance limit is hit |

### Output Mode

| Method | Description |
|--------|-------------|
| `set_voltage_mode(voltage, current_limit=None)` | Switch to voltage source mode |
| `set_current_mode(current, voltage_limit=None)` | Switch to current source mode |
| `get_output_mode()` | Returns `"voltage"` or `"current"` |

### Configuration

| Method | Description |
|--------|-------------|
| `set_source_delay(seconds)` | Set settle delay before measurement (0-167 s) |
| `get_source_delay()` | Get current source delay |
| `set_samples_to_average(n)` | Set averaging count for noise reduction |
| `get_samples_to_average()` | Get current averaging count |

### Query

| Method | Returns | Description |
|--------|---------|-------------|
| `get_voltage_setpoint()` | `float` | Configured voltage level |
| `get_current_limit()` | `float` | Configured current limit |
| `get_output_state()` | `bool` | Whether output is enabled |
| `read_temperature()` | `float` | SMU temperature (Celsius) |

### System

| Method | Description |
|--------|-------------|
| `reset()` | Full session teardown and reconnect (recovers from OLP) |

---

## Current Source Example

```python
smu = NI_PXIe_4139("PXI1Slot2")
smu.connect()

with smu:
    # Source 100 mA, limit voltage to 5V
    smu.set_current_mode(0.1, voltage_limit=5.0)
    smu.enable_output(True)

    result = smu.measure_vi()
    print(f"V: {result['voltage']:.3f} V at 100 mA")
```

---

## Averaging Example

```python
smu = NI_PXIe_4139("PXI1Slot2")
smu.connect()

with smu:
    smu.set_voltage(3.3)
    smu.set_current_limit(0.1)
    smu.set_samples_to_average(100)   # Average 100 samples
    smu.set_source_delay(0.01)        # 10 ms settle time
    smu.enable_output(True)

    v = smu.measure_voltage()
    i = smu.measure_current()
    print(f"{v:.6f} V, {i:.9f} A")
```
