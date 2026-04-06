# Keysight EDU34450A

5.5-digit digital multimeter with 11 measurement functions. Interface: USB, LAN.

```python
from lab_instruments import Keysight_EDU34450A
```

---

## Quick Example

```python
dmm = Keysight_EDU34450A("USB0::0x2A8D::0x0401::MY12345678::INSTR")
dmm.connect()

try:
    dmm.configure_dc_voltage()
    voltage = dmm.read()
    print(f"DC Voltage: {voltage:.5f} V")
finally:
    dmm.disconnect()
```

---

## Context Manager

```python
dmm = Keysight_EDU34450A("USB0::0x2A8D::0x0401::MY12345678::INSTR")
dmm.connect()

with dmm:
    dmm.configure_dc_voltage()
    reading = dmm.read()
# Instrument reset on exit
```

---

## Methods

### Configuration

| Method | Description |
|--------|-------------|
| `configure_dc_voltage(range_val="DEF", resolution="DEF")` | DC voltage |
| `configure_ac_voltage(range_val="DEF", resolution="DEF")` | AC voltage |
| `configure_dc_current(range_val="DEF", resolution="DEF")` | DC current |
| `configure_ac_current(range_val="DEF", resolution="DEF")` | AC current |
| `configure_resistance_2wire(range_val="DEF", resolution="DEF")` | 2-wire resistance |
| `configure_resistance_4wire(range_val="DEF", resolution="DEF")` | 4-wire resistance |
| `configure_frequency(range_val="DEF", resolution="DEF")` | Frequency |
| `configure_period(range_val="DEF", resolution="DEF")` | Period |
| `configure_continuity()` | Continuity test |
| `configure_diode()` | Diode test |
| `configure_capacitance(range_val="DEF")` | Capacitance |
| `configure_temperature()` | Temperature |
| `set_mode(mode)` | Set mode by friendly name (see below) |

**Friendly mode names** for `set_mode()`: `vdc`, `vac`, `idc`, `iac`, `res`, `fres`, `freq`, `per`, `cont`, `diode`, `cap`, `temp`.

### Reading

| Method | Returns | Description |
|--------|---------|-------------|
| `read()` | `float` | Trigger and return measurement |
| `fetch()` | `float` | Return last measurement |

### Immediate Measurement

| Method | Returns |
|--------|---------|
| `measure_dc_voltage(range_val, resolution)` | `float` |
| `measure_ac_voltage(range_val, resolution)` | `float` |
| `measure_dc_current(range_val, resolution)` | `float` |
| `measure_ac_current(range_val, resolution)` | `float` |
| `measure_resistance_2wire(range_val, resolution)` | `float` |
| `measure_resistance_4wire(range_val, resolution)` | `float` |
| `measure_frequency(range_val, resolution)` | `float` |
| `measure_period(range_val, resolution)` | `float` |
| `measure_continuity()` | `float` |
| `measure_diode()` | `float` |
| `measure_capacitance(range_val)` | `float` |
| `measure_temperature()` | `float` |

### Trigger

| Method | Description |
|--------|-------------|
| `set_trigger_source(source="IMM")` | `IMM`, `BUS`, or `EXT` |
| `set_trigger_delay(delay="MIN")` | Delay in seconds |
| `set_sample_count(count=1)` | Samples per trigger |
| `trigger()` | Software trigger |
| `init()` | Arm the trigger system |

### Display & Utility

| Method | Description |
|--------|-------------|
| `set_display(enabled)` | Enable/disable display |
| `display_text(text)` | Show custom text (max 12 chars) |
| `clear_display_text()` | Clear custom text |
| `set_beeper(enabled)` | Enable/disable beeper |
| `beep()` | Sound beeper |
| `get_error()` | Read error queue |

---

## Differences from HP 34401A

| Feature | HP 34401A | Keysight EDU34450A |
|---------|-----------|-------------------|
| Resolution | 6.5 digits | 5.5 digits |
| NPLC control | Yes | No (uses speed modes) |
| Capacitance | No | Yes |
| Temperature | No | Yes |
| Interface | GPIB | USB + LAN |

---

## Capacitance & Temperature Example

```python
dmm = Keysight_EDU34450A("USB0::0x2A8D::0x0401::MY12345678::INSTR")
dmm.connect()

with dmm:
    # Measure capacitance
    cap = dmm.measure_capacitance()
    print(f"Capacitance: {cap * 1e6:.2f} uF")

    # Measure temperature
    temp = dmm.measure_temperature()
    print(f"Temperature: {temp:.1f} C")
```
