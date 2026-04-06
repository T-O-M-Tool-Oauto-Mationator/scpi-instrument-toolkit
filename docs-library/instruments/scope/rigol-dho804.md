# Rigol DHO804

4-channel 70 MHz digital oscilloscope. Interface: USB-TMC.

```python
from lab_instruments import Rigol_DHO804
```

This is the most feature-rich oscilloscope driver, with support for waveform capture, cursors, math channels, recording/playback, mask testing, histograms, counters, DVM, and built-in AWG.

---

## Quick Example

```python
scope = Rigol_DHO804("USB0::0x1AB1::0x044C::DHO8A000000::INSTR")
scope.connect()

try:
    scope.enable_channel(1)
    scope.autoset()
    freq = scope.measure(1, "frequency")
    vpp = scope.measure(1, "vpp")
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
| `single()` | Arm single-shot acquisition |
| `autoset()` | Auto-optimize display settings |
| `force_trigger()` | Force a trigger event |
| `clear()` | Clear waveform display |
| `wait_for_stop(timeout=10.0)` | Wait for acquisition to complete |

### Channel Control

| Method | Description |
|--------|-------------|
| `enable_channel(channel)` | Enable channel (1-4) |
| `disable_channel(channel)` | Disable channel |
| `set_vertical_scale(channel, volts_per_div, offset=0.0)` | Set V/div and offset |
| `set_vertical_position(channel, position)` | Set vertical offset |
| `get_vertical_position(channel)` | Get vertical offset |
| `move_vertical(channel, delta)` | Move channel vertically |
| `set_coupling(channel, coupling)` | Set coupling: `DC`, `AC`, `GND` |
| `set_bandwidth_limit(channel, limit)` | Set bandwidth limit: `OFF`, `20M` |
| `invert_channel(channel, enable)` | Invert channel display |
| `set_probe_attenuation(channel, ratio)` | Set probe ratio (e.g., 10 for 10x) |
| `set_channel_label(channel, label, show=True)` | Set channel label |

### Horizontal

| Method | Description |
|--------|-------------|
| `set_horizontal_scale(seconds_per_div)` | Set time/div |
| `set_horizontal_offset(offset)` | Set horizontal position |
| `set_timebase_mode(mode)` | Set mode: `MAIN`, `WINDOW`, `XY`, `ROLL` |
| `enable_delayed_timebase(enable)` | Enable zoom timebase |
| `set_delayed_offset(offset)` | Set zoom offset |
| `set_delayed_scale(scale)` | Set zoom scale |
| `enable_xy_mode(enable, x_channel, y_channel)` | Enable X-Y mode |

### Trigger

| Method | Description |
|--------|-------------|
| `configure_trigger(channel, level, slope="RISE", mode="AUTO")` | Configure edge trigger |
| `set_trigger_sweep(sweep)` | Set sweep: `AUTO`, `NORMal`, `SINGle` |
| `set_trigger_coupling(coupling)` | Set trigger coupling |
| `set_trigger_holdoff(time)` | Set holdoff time |
| `get_trigger_status()` | Get trigger status string |
| `configure_pulse_trigger(...)` | Configure pulse width trigger |
| `configure_timeout_trigger(...)` | Configure timeout trigger |

### Measurements

| Method | Returns | Description |
|--------|---------|-------------|
| `measure(channel, measurement_type)` | `float` | Take a measurement |
| `measure_vpp(channel)` | `float` | Peak-to-peak voltage |
| `measure_vrms(channel)` | `float` | RMS voltage |
| `measure_frequency(channel)` | `float` | Frequency |
| `measure_period(channel)` | `float` | Period |
| `measure_amplitude(channel)` | `float` | Amplitude |
| `measure_rise_time(channel)` | `float` | Rise time |
| `measure_fall_time(channel)` | `float` | Fall time |
| `measure_duty_cycle(channel)` | `float` | Duty cycle |
| `measure_delay(ch1, ch2, edge1, edge2)` | `float` | Delay between channels |
| `configure_measurement(channel, measurement_type)` | `None` | Configure without reading |
| `clear_measurements()` | `None` | Clear all measurements |

**Measurement types**: `vpp`, `pk2pk`, `vrms`, `rms`, `vmax`, `vmin`, `vtop`, `vbase`, `vamp`, `mean`, `frequency`, `period`, `rise`, `fall`, `pwidth`, `nwidth`, `pduty`, `overshoot`, `preshoot`

### Waveform Data

| Method | Returns | Description |
|--------|---------|-------------|
| `acquire_waveform(channel, mode="NORMAL")` | `WaveformData` | Capture waveform data |
| `save_waveform_csv(channel, filename, ...)` | `None` | Save waveform to CSV |
| `save_waveforms_csv(channels, filename, ...)` | `None` | Save multiple channels to CSV |

**`WaveformData`** is a dataclass with:
- `time` — numpy array of time values (seconds)
- `voltage` — numpy array of voltage values (volts)
- `channel`, `sample_rate`, `points`, `time_per_div`, `volts_per_div`
- `plot(title=None)` — plot with matplotlib

### Math Channels

| Method | Description |
|--------|-------------|
| `enable_math_channel(math_ch, enable=True)` | Enable/disable math channel |
| `configure_math_operation(math_ch, operation, source1, source2)` | Math: ADD, SUBTract, MULTiply, DIVision |
| `configure_math_function(math_ch, function, source)` | Function: SQRT, LOG, LN, EXP, ABS, etc. |
| `configure_fft(math_ch, source, window="RECT")` | FFT analysis |
| `configure_digital_filter(...)` | Digital filter |
| `set_math_scale(math_ch, scale, offset=None)` | Set math display scale |

### Recording & Playback

| Method | Description |
|--------|-------------|
| `set_recording_enable(enable)` | Enable/disable recording |
| `set_recording_frames(frames)` | Set number of frames |
| `start_recording()` / `stop_recording()` | Control recording |
| `start_playback()` / `stop_playback()` | Control playback |
| `set_playback_current_frame(frame)` | Jump to frame |

### Mask Testing

| Method | Description |
|--------|-------------|
| `set_mask_enable(enable)` | Enable/disable mask test |
| `set_mask_source(channel)` | Set mask source channel |
| `set_mask_tolerance_x(tol)` / `set_mask_tolerance_y(tol)` | Set tolerances |
| `create_mask()` | Create mask from current waveform |
| `start_mask_test()` / `stop_mask_test()` | Control test |
| `get_mask_statistics()` | Get pass/fail/total counts |

### Display

| Method | Description |
|--------|-------------|
| `get_screenshot()` | Returns screenshot as `bytes` (PNG) |
| `clear_display()` | Clear display |
| `set_persistence(time_val)` | Set persistence |
| `set_display_type(display_type)` | Set: `VECTors`, `DOTS` |
| `set_waveform_brightness(brightness)` | Set brightness (0-100) |

---

## Waveform Capture Example

```python
scope = Rigol_DHO804("USB0::0x1AB1::0x044C::DHO8A000000::INSTR")
scope.connect()

try:
    scope.enable_channel(1)
    scope.set_vertical_scale(1, 1.0)      # 1 V/div
    scope.set_horizontal_scale(0.001)      # 1 ms/div
    scope.configure_trigger(1, 0.5)        # Trigger at 0.5V
    scope.run()

    waveform = scope.acquire_waveform(1)
    print(f"Captured {waveform.points} points at {waveform.sample_rate:.0f} Sa/s")

    # Plot
    waveform.plot("Channel 1 Capture")

    # Save to CSV
    scope.save_waveform_csv(1, "ch1_data.csv")
finally:
    scope.disconnect()
```
