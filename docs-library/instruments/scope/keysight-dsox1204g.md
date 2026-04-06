# Keysight DSOX1204G

4-channel 70 MHz oscilloscope with built-in WaveGen. Interface: USB, LAN.

```python
from lab_instruments import Keysight_DSOX1204G
```

This oscilloscope includes a built-in arbitrary waveform generator (WaveGen) accessible through `awg_*` methods.

---

## Quick Example

```python
scope = Keysight_DSOX1204G("USB0::0x2A8D::0x9045::MY12345678::INSTR")
scope.connect()

try:
    scope.enable_channel(1)
    scope.autoset()
    freq = scope.measure_frequency(1)
    vpp = scope.measure_vpp(1)
    print(f"Frequency: {freq:.1f} Hz, Vpp: {vpp:.3f} V")
finally:
    scope.disconnect()
```

---

## Methods

### Basic Control

| Method | Description |
|--------|-------------|
| `run()` | Start continuous acquisition |
| `stop()` | Stop acquisition |
| `single()` | Arm single-shot |
| `autoset()` | Autoscale (Keysight uses `:AUToscale`) |
| `force_trigger()` | Force a trigger |
| `wait_for_stop(timeout=10.0)` | Wait for acquisition to stop |

### Channel Control

| Method | Description |
|--------|-------------|
| `enable_channel(channel)` | Enable channel (1-4) |
| `disable_channel(channel)` | Disable channel |
| `enable_all_channels()` / `disable_all_channels()` | All channels |
| `set_vertical_scale(channel, volts_per_div, offset=0.0)` | V/div and offset |
| `set_vertical_position(channel, position)` | Vertical offset |
| `move_vertical(channel, delta)` | Move vertically |
| `set_coupling(channel, coupling)` | `DC`, `AC`, `GND` |
| `set_probe_attenuation(channel, ratio)` | Probe ratio |
| `set_channel_label(channel, label, show=True)` | Channel label |
| `invert_channel(channel, enable)` | Invert display |
| `set_bandwidth_limit(channel, limit)` | `OFF`, `20M` |

### Horizontal

| Method | Description |
|--------|-------------|
| `set_horizontal_scale(seconds_per_div)` | Set time/div |
| `set_horizontal_offset(offset)` | Set position |
| `move_horizontal(delta)` | Move by delta |

### Trigger

| Method | Description |
|--------|-------------|
| `configure_trigger(channel, level, slope="RISE", mode="AUTO")` | Edge trigger |
| `set_trigger_sweep(sweep)` | `AUTO`, `NORMal`, `SINGle` |
| `get_trigger_status()` | Trigger status string |

### Measurements

| Method | Returns | Description |
|--------|---------|-------------|
| `measure(channel, measurement_type)` | `float` | Take a measurement |
| `measure_vpp(channel)` | `float` | Peak-to-peak |
| `measure_vrms(channel)` | `float` | RMS |
| `measure_frequency(channel)` | `float` | Frequency |
| `measure_period(channel)` | `float` | Period |
| `measure_amplitude(channel)` | `float` | Amplitude |
| `measure_delay(ch1, ch2, edge1, edge2)` | `float` | Channel delay |
| `configure_measurement(channel, measurement_type)` | `None` | Configure only |
| `clear_measurements()` | `None` | Clear all |

**Measurement types**: `vpp`, `pk2pk`, `vrms`, `rms`, `vmax`, `vmin`, `vtop`, `vbase`, `vamp`, `mean`, `frequency`, `period`, `rise`, `fall`, `pwidth`, `nwidth`, `pduty`, `duty`, `overshoot`, `preshoot`

### Waveform Data

| Method | Returns | Description |
|--------|---------|-------------|
| `acquire_waveform(channel, mode="NORMAL")` | `WaveformData` | Capture waveform |
| `save_waveform_csv(channel, filename, ...)` | `None` | Save to CSV |
| `save_waveforms_csv(channels, filename, ...)` | `None` | Multi-channel CSV |

### Math Channels

| Method | Description |
|--------|-------------|
| `enable_math_channel(math_ch, enable=True)` | Enable/disable |
| `configure_math_operation(math_ch, operation, source1, source2)` | Math operations |
| `configure_math_function(math_ch, function, source)` | Functions |
| `configure_fft(math_ch, source, window="RECT")` | FFT |
| `set_math_scale(math_ch, scale, offset=None)` | Scale |

### Acquisition

| Method | Description |
|--------|-------------|
| `set_acquisition_type(acq_type)` | `NORMal`, `AVERage`, `PEAK`, `HRES` |
| `set_average_count(count)` | Averaging count (power of 2) |
| `set_memory_depth(depth)` | Memory depth: `AUTO`, `1000`, `10000`, etc. |
| `get_sample_rate()` | Get sample rate (Sa/s) |

### Mask Testing

| Method | Description |
|--------|-------------|
| `set_mask_enable(enable)` | Enable/disable |
| `set_mask_source(channel)` | Source channel |
| `set_mask_tolerance_x(tol)` / `set_mask_tolerance_y(tol)` | Tolerances |
| `create_mask()` | Create from waveform |
| `start_mask_test()` / `stop_mask_test()` | Control |
| `get_mask_statistics()` | Pass/fail/total |

### Display

| Method | Description |
|--------|-------------|
| `get_screenshot()` | Returns PNG bytes |
| `clear_display()` | Clear display |
| `set_persistence(time_val)` | Persistence time |
| `set_display_type(display_type)` | `VECTors`, `DOTS` |

### Built-in WaveGen (AWG)

| Method | Description |
|--------|-------------|
| `awg_set_output_enable(enable)` | Enable/disable WaveGen output |
| `awg_set_function(function)` | Set waveform: `SINusoid`, `SQUare`, `RAMP`, `PULSe`, `NOISe`, `DC` |
| `awg_set_frequency(freq)` | Set frequency (Hz) |
| `awg_set_amplitude(amp)` | Set amplitude (Vpp) |
| `awg_set_offset(offset)` | Set DC offset (V) |
| `awg_set_square_duty(duty)` | Square duty cycle (%) |
| `awg_set_ramp_symmetry(sym)` | Ramp symmetry (%) |
| `awg_configure_simple(function, frequency, amplitude, offset=0, duty=None, symmetry=None)` | Configure all WaveGen params at once |

### DVM (Digital Voltmeter)

| Method | Description |
|--------|-------------|
| `set_dvm_enable(enable)` | Enable/disable DVM |
| `get_dvm_current()` | Get DVM reading |
| `set_dvm_source(source)` | Set DVM source channel |
| `set_dvm_mode(mode)` | `ACRMs`, `DC`, `DCRMs`, `FREQuency` |

---

## WaveGen Example

```python
scope = Keysight_DSOX1204G("USB0::0x2A8D::0x9045::MY12345678::INSTR")
scope.connect()

try:
    # Use built-in WaveGen as signal source
    scope.awg_configure_simple("SINusoid", 1000, 2.0)
    scope.awg_set_output_enable(True)

    # Measure on CH1
    scope.enable_channel(1)
    scope.autoset()
    freq = scope.measure_frequency(1)
    print(f"Measured: {freq:.1f} Hz")
finally:
    scope.awg_set_output_enable(False)
    scope.disconnect()
```

---

## Waveform Capture Example

```python
scope = Keysight_DSOX1204G("USB0::0x2A8D::0x9045::MY12345678::INSTR")
scope.connect()

try:
    scope.enable_channel(1)
    scope.set_vertical_scale(1, 1.0)
    scope.set_horizontal_scale(0.001)
    scope.configure_trigger(1, 0.5)

    waveform = scope.acquire_waveform(1)
    waveform.plot("Channel 1")
    scope.save_waveform_csv(1, "capture.csv")
finally:
    scope.disconnect()
```
