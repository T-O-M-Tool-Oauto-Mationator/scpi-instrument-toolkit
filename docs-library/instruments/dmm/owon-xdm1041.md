# OWON XDM1041

7.5-digit bench digital multimeter. Interface: USB (115200 baud serial).

```python
from lab_instruments import Owon_XDM1041
```

!!! warning "Non-Standard SCPI"
    The XDM1041 uses a **non-standard SCPI implementation**:

    - Uses `MEAS?` instead of `:READ?`
    - Range is passed directly to `CONFigure` commands
    - `SYSTem:ERRor?` is not supported
    - Measurements require a **2-second settle delay** (handled automatically)

---

## Quick Example

```python
dmm = Owon_XDM1041("ASRL5::INSTR")
dmm.connect()

try:
    dmm.configure_dc_voltage()
    voltage = dmm.measure()
    print(f"DC Voltage: {voltage:.7f} V")
finally:
    dmm.disconnect()
```

---

## Context Manager

```python
dmm = Owon_XDM1041("ASRL5::INSTR")
dmm.connect()

with dmm:
    voltage = dmm.measure_dc_voltage()
    print(f"{voltage:.7f} V")
# Instrument reset on exit
```

---

## Methods

### Configuration

| Method | Description |
|--------|-------------|
| `configure_dc_voltage(range_val=None)` | DC voltage. Range: 500e-3, 5, 50, 500, 1000 or `None` for auto |
| `configure_ac_voltage(range_val=None)` | AC voltage. Range: 500e-3, 5, 50, 500, 750 |
| `configure_dc_current(range_val=None)` | DC current. Range: 500e-6, 5e-3, 50e-3, 500e-3, 5, 10 |
| `configure_ac_current(range_val=None)` | AC current |
| `configure_resistance_2wire(range_val=None)` | 2-wire resistance. Range: 500, 5e3, 50e3, 500e3, 5e6, 50e6 |
| `configure_resistance_4wire(range_val=None)` | 4-wire resistance. Max 50kOhm |
| `configure_frequency()` | Frequency |
| `configure_period()` | Period |
| `configure_capacitance(range_val=None)` | Capacitance |
| `configure_temperature(rtd_type="KITS90")` | Temperature. RTD: `"KITS90"` (K-type) or `"PT100"` |
| `configure_diode()` | Diode test |
| `configure_continuity()` | Continuity test |
| `set_mode(mode)` | Set mode by name: `vdc`, `vac`, `idc`, `iac`, `res`, `fres`, `freq`, `per`, `cap`, `temp`, `diod`, `cont` |

### Reading

| Method | Returns | Description |
|--------|---------|-------------|
| `measure()` | `float` | Take a measurement using current config (2s settle) |
| `read()` | `float` | Alias for `measure()` (compatibility) |

### Immediate Measurement

Each method configures and measures in one call:

| Method | Returns |
|--------|---------|
| `measure_dc_voltage(range_val=None)` | `float` |
| `measure_ac_voltage(range_val=None)` | `float` |
| `measure_dc_current(range_val=None)` | `float` |
| `measure_ac_current(range_val=None)` | `float` |
| `measure_resistance_2wire(range_val=None)` | `float` |
| `measure_resistance_4wire(range_val=None)` | `float` |
| `measure_frequency()` | `float` |
| `measure_period()` | `float` |
| `measure_capacitance(range_val=None)` | `float` |
| `measure_temperature(rtd_type="KITS90")` | `float` |
| `measure_diode()` | `float` |

---

## Notes

- The `range_val=None` parameter enables auto-range. Pass a specific value for fixed range.
- All measurements have an inherent **2-second settle delay** due to the device's processing time.
- The serial connection uses 115200 baud, 8N1, with `\r\n` write termination.
- 4-wire resistance is limited to a maximum range of 50 kOhm.
