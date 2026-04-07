# Tektronix MSO2024

4-channel mixed signal oscilloscope (legacy MSO2000 series). Interface: USB, GPIB.

```python
from lab_instruments import Tektronix_MSO2024
```

---

## Quick Example

```python
scope = Tektronix_MSO2024("USB0::0x0699::0x0373::C000000::INSTR")
scope.connect()

try:
    scope.enable_channel(1)
    scope.autoset()
    freq = scope.measure_frequency(1)
    vpp = scope.measure_peak_to_peak(1)
    print(f"Frequency: {freq:.1f} Hz, Vpp: {vpp:.3f} V")
finally:
    scope.disconnect()
```

---

## Context Manager

```python
scope = Tektronix_MSO2024("USB0::0x0699::0x0373::C000000::INSTR")
scope.connect()

with scope:
    scope.enable_channel(1)
    scope.autoset()
    # ...
# All channels disabled on exit
```

---

## Methods

### Basic Control

| Method | Description |
|--------|-------------|
| `run()` | Start acquisition |
| `stop()` | Stop acquisition |
| `single()` | Arm single-shot acquisition |
| `autoset()` | Perform autoset |
| `is_running()` | Returns `True` if running |
| `get_acquisition_state()` | Returns `1` (running) or `0` (stopped) |

### Channel Control

| Method | Description |
|--------|-------------|
| `enable_channel(channel)` | Enable channel (1-4) |
| `disable_channel(channel)` | Disable channel |
| `enable_all_channels()` | Enable all 4 channels |
| `disable_all_channels()` | Disable all channels + math |
| `set_vertical_scale(channel, scale, position=0.0)` | Set V/div and position |
| `set_vertical_position(channel, position)` | Set position (divisions) |
| `get_vertical_position(channel)` | Get position |
| `move_vertical(channel, delta)` | Move by delta divisions |
| `set_coupling(channel, coupling)` | `DC`, `AC`, or `GND` |
| `set_probe_attenuation(channel, attenuation)` | Set probe ratio |
| `set_channel_label(channel, label)` | Set label (max 30 chars) |

### Horizontal & Acquisition

| Method | Description |
|--------|-------------|
| `set_horizontal_scale(scale)` | Set seconds/div |
| `set_horizontal_offset(offset)` | Set horizontal delay |
| `set_horizontal_position(position)` | Set position (0-100%) |
| `get_horizontal_position()` | Get position |
| `move_horizontal(delta)` | Move by delta percent |
| `set_acquisition_mode(mode, num_averages=16)` | `SAMPLE`, `AVERAGE`, `PEAKDETECT`, `HIRES`, `ENVELOPE` |
| `set_acquisition_stop_after(mode)` | `RUNSTop` or `SEQuence` |

### Trigger

| Method | Description |
|--------|-------------|
| `configure_trigger(source_channel, level, slope="RISE", mode="AUTO")` | Configure edge trigger |

### Measurements

| Method | Returns | Description |
|--------|---------|-------------|
| `measure_bnf(channel, measure_type)` | `float` | Generic measurement |
| `configure_measurement(channel, measurement_type)` | `None` | Configure without reading |
| `measure_peak_to_peak(channel)` | `float` | Vpp |
| `measure_frequency(channel)` | `float` | Frequency |
| `measure_rms(channel)` | `float` | RMS voltage |
| `measure_mean(channel)` | `float` | Mean voltage |
| `measure_max(channel)` | `float` | Maximum voltage |
| `measure_min(channel)` | `float` | Minimum voltage |
| `measure_period(channel)` | `float` | Period |
| `measure_rise_time(channel)` | `float` | Rise time |
| `measure_fall_time(channel)` | `float` | Fall time |
| `measure_delay(src1, src2, edge1, edge2, direction)` | `float` | Channel-to-channel delay |

**Valid measurement types** for `measure_bnf()`: `FREQUENCY`, `MEAN`, `PERIOD`, `PK2PK`, `CRMS`, `MINIMUM`, `MAXIMUM`, `RISE`, `FALL`, `PWIDTH`, `NWIDTH`, `RMS`, `AMPLITUDE`, `HIGH`, `LOW`, `POSOVERSHOOT`, `NEGOVERSHOOT`, `DELAY`

### Math

| Method | Description |
|--------|-------------|
| `configure_math(expression, scale=None, position=None)` | Set math expression (e.g., `"CH1-CH2"`) |
| `measure_math_bnf(measure_type)` | Measure on math waveform |

### Waveform Data

| Method | Returns | Description |
|--------|---------|-------------|
| `get_waveform_data(channel)` | `list[float]` | Raw unscaled data points |
| `get_waveform_scaled(channel)` | `(list, list)` | (time_values, voltage_values) |
| `save_waveform_csv(channel, filename, max_points=None, time_window=None)` | `None` | Save to CSV |
| `save_waveforms_csv(channels, filename, max_points=None, time_window=None)` | `None` | Multi-channel CSV |

---

## Waveform Capture Example

```python
scope = Tektronix_MSO2024("USB0::0x0699::0x0373::C000000::INSTR")
scope.connect()

try:
    scope.enable_channel(1)
    scope.set_vertical_scale(1, 1.0)
    scope.set_horizontal_scale(0.001)
    scope.configure_trigger(1, 0.5)
    scope.run()

    times, voltages = scope.get_waveform_scaled(1)
    print(f"Captured {len(times)} points")

    scope.save_waveform_csv(1, "ch1_data.csv")
finally:
    scope.disconnect()
```

---

## Math Example

```python
scope.configure_math("CH1-CH2", scale=0.5)
diff_rms = scope.measure_math_bnf("RMS")
print(f"Differential RMS: {diff_rms:.3f} V")
```
