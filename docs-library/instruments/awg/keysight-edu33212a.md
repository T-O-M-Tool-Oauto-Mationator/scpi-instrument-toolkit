# Keysight EDU33212A

Dual-channel Trueform arbitrary waveform generator. Interface: USB, LAN.

```python
from lab_instruments import Keysight_EDU33212A
```

---

## Quick Example

```python
awg = Keysight_EDU33212A("USB0::0x2A8D::0x1602::MY12345678::INSTR")
awg.connect()

try:
    awg.set_waveform(1, "SIN", frequency=1000, amplitude=2.0, offset=0)
    awg.enable_output(1, True)
    # Signal is now outputting on CH1
finally:
    awg.disable_all_channels()
    awg.disconnect()
```

---

## Context Manager

```python
awg = Keysight_EDU33212A("USB0::0x2A8D::0x1602::MY12345678::INSTR")
awg.connect()

with awg:
    awg.set_waveform(1, "SQU", frequency=5000, amplitude=3.3)
    awg.enable_output(1, True)
    # ...
# All outputs disabled and zeroed on exit
```

---

## Channels

Dual-channel: channel `1` and channel `2`.

---

## Methods

### Output Control

| Method | Description |
|--------|-------------|
| `enable_output(channel, enabled=True)` | Enable/disable output for channel 1 or 2 |
| `disable_all_channels()` | Zero all parameters and disable both outputs |
| `set_output_load(channel, load)` | Set output impedance: ohms (1-10000) or `"INF"` for high-Z |
| `set_output_polarity(channel, normal=True)` | Set normal or inverted polarity |
| `set_sync_output(enabled=True)` | Enable/disable Sync output |

### Waveform Configuration

| Method | Description |
|--------|-------------|
| `set_waveform(channel, wave_type, frequency=None, amplitude=None, offset=None, duty=None, symmetry=None)` | Set waveform type and parameters in one call |
| `set_function(channel, func)` | Set waveform type: `SIN`, `SQU`, `RAMP`, `PULS`, `NOIS`, `PRBS`, `DC`, `ARB` |
| `set_frequency(channel, frequency)` | Set frequency in Hz |
| `set_amplitude(channel, amplitude)` | Set amplitude in Vpp |
| `set_offset(channel, offset)` | Set DC offset in V |
| `set_high_low(channel, high, low)` | Set output using high/low voltage levels |
| `set_voltage_unit(channel, unit)` | Set unit: `VPP`, `VRMS`, or `DBM` |
| `set_dc_output(channel, voltage)` | Set DC output at specified voltage |

### Waveform Shape

| Method | Description |
|--------|-------------|
| `set_square_duty(channel, duty_cycle)` | Duty cycle for square wave (0.01-99.99%) |
| `set_ramp_symmetry(channel, symmetry)` | Ramp symmetry (0-100%). 50% = triangle |

### Pulse Parameters

| Method | Description |
|--------|-------------|
| `set_pulse_period(channel, period)` | Pulse period in seconds |
| `set_pulse_width(channel, width)` | Pulse width in seconds (min 16 ns) |
| `set_pulse_duty(channel, duty_cycle)` | Pulse duty cycle (0.01-99.99%) |
| `set_pulse_edge(channel, leading=None, trailing=None)` | Edge transition times (8.4 ns to 1 us) |

### Modulation

| Method | Description |
|--------|-------------|
| `set_am(channel, state, depth=100, mod_freq=10, mod_func="SIN", source="INTernal", dssc=False)` | Amplitude modulation |
| `set_fm(channel, state, deviation=100, mod_freq=10, mod_func="SIN", source="INTernal")` | Frequency modulation |
| `set_pm(channel, state, deviation=180, mod_freq=10, mod_func="SIN", source="INTernal")` | Phase modulation |
| `set_fsk(channel, state, hop_freq=100, rate=10, source="INTernal")` | Frequency-shift keying |
| `set_pwm(channel, state, deviation=None, mod_freq=10, mod_func="SIN", source="INTernal")` | Pulse width modulation |

### Sweep & Burst

| Method | Description |
|--------|-------------|
| `set_sweep(channel, state, start=100, stop=1000, time=1.0, spacing="LINear", ...)` | Frequency sweep |
| `set_burst(channel, state, mode="TRIGgered", n_cycles=1, period=0.01, phase=0)` | Burst mode |
| `set_trigger_source(channel, source="IMMediate")` | Trigger source for sweep/burst |
| `send_trigger()` | Software trigger |

### Query

| Method | Returns | Description |
|--------|---------|-------------|
| `get_amplitude(channel)` | `float` | Current amplitude (Vpp) |
| `get_offset(channel)` | `float` | Current DC offset |
| `get_frequency(channel)` | `float` | Current frequency (Hz) |
| `get_output_state(channel)` | `bool` | Whether output is enabled |
| `get_error()` | `str` | Error queue |

### State Management

| Method | Description |
|--------|-------------|
| `save_state(location)` | Save to memory (0-4) |
| `recall_state(location)` | Recall from memory (0-4) |

---

## Dual-Channel Example

```python
awg = Keysight_EDU33212A("USB0::0x2A8D::0x1602::MY12345678::INSTR")
awg.connect()

with awg:
    # CH1: 1 kHz sine
    awg.set_waveform(1, "SIN", frequency=1000, amplitude=2.0)
    awg.enable_output(1, True)

    # CH2: 1 kHz square (same frequency, different shape)
    awg.set_waveform(2, "SQU", frequency=1000, amplitude=3.3)
    awg.set_square_duty(2, 50.0)
    awg.enable_output(2, True)
```

---

## Sweep Example

```python
awg = Keysight_EDU33212A("USB0::0x2A8D::0x1602::MY12345678::INSTR")
awg.connect()

with awg:
    awg.set_waveform(1, "SIN", amplitude=1.0)
    awg.set_sweep(1, True, start=100, stop=100_000, time=5.0, spacing="LOGarithmic")
    awg.enable_output(1, True)
```
