# Keysight EDU36311A

Triple-output DC power supply (P6V/5A, P30V/1A, N30V/1A). Interface: USB, LAN.

```python
from lab_instruments import Keysight_EDU36311A
```

---

## Quick Example

```python
psu = Keysight_EDU36311A("USB0::0x2A8D::0x3402::MY12345678::INSTR")
psu.connect()

try:
    psu.set_output_channel("p6v_channel", 5.0, current_limit=1.0)
    psu.enable_output(True)

    voltage = psu.measure_voltage("p6v_channel")
    print(f"Output: {voltage:.3f} V")
finally:
    psu.enable_output(False)
    psu.disconnect()
```

---

## Context Manager

```python
psu = Keysight_EDU36311A("USB0::0x2A8D::0x3402::MY12345678::INSTR")
psu.connect()

with psu:
    psu.set_output_channel("p30v_channel", 12.0)
    psu.enable_output(True)
    # ...
# All channels zeroed and output disabled on exit
```

---

## Channels

| Channel Key | SCPI Name | Voltage Range | Current Range |
|-------------|-----------|---------------|---------------|
| `"p6v_channel"` | P6V | 0-6.18 V | 0-5.15 A |
| `"p30v_channel"` | P30V | 0-30.9 V | 0-1.03 A |
| `"n30v_channel"` | N30V | 0-30.9 V | 0-1.03 A |

---

## Methods

### Output Control

| Method | Description |
|--------|-------------|
| `enable_output(enabled=True)` | Enable or disable the power supply output |
| `set_output_channel(channel, voltage, current_limit=None)` | Set voltage and current limit for a channel |
| `set_voltage(channel, voltage)` | Set voltage only |
| `set_current_limit(channel, current)` | Set current limit only |
| `select_channel(channel)` | Select the active channel |
| `disable_all_channels()` | Disable output and zero all setpoints |

### Measurement

| Method | Returns | Description |
|--------|---------|-------------|
| `measure_voltage(channel)` | `float` | Measure output voltage (V) |
| `measure_current(channel)` | `float` | Measure output current (A) |

### Query

| Method | Returns | Description |
|--------|---------|-------------|
| `get_voltage_setpoint(channel=None)` | `float` | Query voltage setpoint |
| `get_current_limit(channel=None)` | `float` | Query current limit |
| `get_output_state()` | `bool` | Query whether output is enabled |
| `get_error()` | `str` | Read from the error queue |

### State Management

| Method | Description |
|--------|-------------|
| `set_tracking(enable)` | Enable/disable tracking for +/-30V supplies |
| `save_state(location)` | Save state to memory (1-5) |
| `recall_state(location)` | Recall saved state (1-5) |

### Inherited from DeviceManager

| Method | Description |
|--------|-------------|
| `connect()` | Connect and initialize |
| `disconnect()` | Close connection |
| `send_command(command)` | Send raw SCPI |
| `query(command)` | Send SCPI query |
| `reset()` | Reset instrument |
| `clear_status()` | Clear status byte |

---

## Notes

- The API is nearly identical to [HP E3631A](hp-e3631a.md), with different channel names and memory locations (1-5 instead of 1-3).
- The `"n30v_channel"` outputs a negative voltage — the `voltage` parameter should be a positive number representing the magnitude.
