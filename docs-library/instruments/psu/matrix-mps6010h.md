# Matrix MPS-6010H

Single-channel DC power supply (60V/10A). Interface: Serial (9600 baud).

```python
from lab_instruments import MATRIX_MPS6010H
```

!!! warning "No Readback"
    This device **does not support query commands**. All `measure_*` methods return **cached setpoint values**, not actual measured values. Use an external DMM for accurate measurements.

---

## Quick Example

```python
psu = MATRIX_MPS6010H("ASRL3::INSTR")
psu.connect()

try:
    psu.set_voltage(12.0)
    psu.set_current_limit(1.0)
    psu.enable_output(True)

    # Returns cached setpoint, NOT measured value
    v = psu.measure_voltage()
    print(f"Setpoint: {v} V")
finally:
    psu.enable_output(False)
    psu.disconnect()
```

---

## Context Manager

```python
psu = MATRIX_MPS6010H("ASRL3::INSTR")
psu.connect()

with psu:
    psu.set_output(24.0, 2.0)  # 24V, 2A limit
    psu.enable_output(True)
    # ...
# Output disabled and remote mode returned to local on exit
```

---

## Specifications

| Parameter | Value |
|-----------|-------|
| Max Voltage | 60.0 V |
| Max Current | 10.0 A |
| Interface | Serial (9600 baud, 8N1) |
| Remote Mode | Must send `REM:ON` before commands work (handled by `connect()`) |

---

## Methods

### Output Control

| Method | Description |
|--------|-------------|
| `set_voltage(voltage)` | Set output voltage (0-60V) |
| `set_current_limit(current)` | Set current limit (0-10A) |
| `set_output(voltage, current_limit)` | Set both voltage and current limit |
| `enable_output(enabled=True)` | Enable or disable output |
| `disable_output()` | Disable output and zero setpoints |
| `set_output_channel(channel, voltage, current_limit=None)` | Compatibility method (ignores channel) |

### Measurement (Cached Values)

| Method | Returns | Description |
|--------|---------|-------------|
| `measure_voltage()` | `float` | Last voltage setpoint (not measured) |
| `measure_current()` | `float` | Last current limit (not measured) |

### Query (Cached Values)

| Method | Returns | Description |
|--------|---------|-------------|
| `get_voltage_setpoint()` | `float` | Cached voltage setpoint |
| `get_current_limit()` | `float` | Cached current limit |
| `get_output_state()` | `bool` | Cached output state |
| `get_error()` | `str` | Returns "not supported" message |

### Inherited from DeviceManager

| Method | Description |
|--------|-------------|
| `connect()` | Connect via serial and enable remote mode |
| `disconnect()` | Close connection |
| `send_command(command)` | Send raw command |
| `reset()` | Reset instrument |

---

## Notes

- **Remote mode** is automatically enabled on `connect()` and disabled on context manager exit.
- The serial connection uses 9600 baud, 8 data bits, no parity, 1 stop bit.
- Uses `VOLT` / `CURR` / `OUTP` command syntax (not standard SCPI `VSET` / `ISET` / `OUTPUT`).
- To return to local (front panel) mode manually: `psu.send_command("REM:OFF")` or press Shift+7 on the instrument.
