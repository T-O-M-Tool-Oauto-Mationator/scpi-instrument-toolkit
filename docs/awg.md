# AWG — Function Generator

Controls arbitrary waveform generators and function generators.

- Channels are numbered `1`, `2`, or use `all` to affect both simultaneously
- Multiple AWGs are named `awg1`, `awg2`, etc.

=== "Keysight EDU33212A"
    Dual-channel function/arbitrary waveform generator. Full SCPI support for all waveform types.

=== "JDS6600 (Seesii DDS)"
    DDS function generator with serial interface. Supports standard waveforms and arbitrary waveform loading.

=== "BK Precision 4063"
    Single-channel function generator with USB interface.

---

## awg chan

Enable or disable an output channel.

```
awg chan <1|2|all> <on|off>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1\|2\|all` | required | `1`, `2`, `all` | Channel to control. `all` affects both channels. |
| `on\|off` | required | `on`, `off` | Enable or disable the output. |

```
awg chan 1 on       # enable channel 1
awg chan 2 off      # disable channel 2
awg chan all off    # disable both channels
```

---

## awg wave

Configure waveform type and parameters in one command.

```
awg wave <1|2|all> <type> [freq=<Hz>] [amp=<Vpp>] [offset=<V>] [duty=<%>] [phase=<deg>]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1\|2\|all` | required | `1`, `2`, `all` | Channel to configure. |
| `type` | required | see below | Waveform shape. |
| `freq=` | optional | float (Hz) | Output frequency in hertz. |
| `amp=` | optional | float (Vpp) | Peak-to-peak amplitude in volts. |
| `offset=` | optional | float (V) | DC offset voltage in volts. |
| `duty=` | optional | 0.0–100.0 | Duty cycle percent — applies to square and pulse waveforms. |
| `phase=` | optional | 0.0–360.0 | Phase offset in degrees. |

**Waveform types:**

| Type | Description |
|------|-------------|
| `sine` | Sinusoidal wave |
| `square` | Square wave (use `duty=` to control duty cycle) |
| `ramp` | Ramp / sawtooth wave |
| `triangle` | Symmetric triangle wave |
| `pulse` | Pulse wave |
| `noise` | White noise |
| `dc` | DC level (set with `offset=`) |
| `arb` | Arbitrary waveform (device-dependent) |

All keyword arguments are optional — omitted parameters keep their current values.

```
awg wave 1 sine freq=1000 amp=2.0 offset=0     # 1 kHz sine, 2 Vpp
awg wave 1 square freq=500 duty=25              # 500 Hz square, 25% duty
awg wave all sine freq=10000                    # set both channels to 10 kHz sine
awg wave 2 ramp freq=100 amp=5.0               # 100 Hz ramp on channel 2
```

---

## awg freq

Set output frequency without changing other parameters.

```
awg freq <1|2|all> <Hz>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1\|2\|all` | required | `1`, `2`, `all` | Channel to configure. |
| `Hz` | required | float > 0 | Frequency in hertz. |

```
awg freq 1 1000      # set channel 1 to 1 kHz
awg freq all 50000   # set both channels to 50 kHz
```

---

## awg amp

Set peak-to-peak amplitude without changing other parameters.

```
awg amp <1|2|all> <Vpp>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1\|2\|all` | required | `1`, `2`, `all` | Channel to configure. |
| `Vpp` | required | float (V) | Peak-to-peak amplitude in volts. |

```
awg amp 1 3.3    # set channel 1 to 3.3 Vpp
awg amp 2 1.0    # set channel 2 to 1 Vpp
```

---

## awg offset

Set DC offset without changing other parameters.

```
awg offset <1|2|all> <V>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1\|2\|all` | required | `1`, `2`, `all` | Channel to configure. |
| `V` | required | float (V) | DC offset in volts. Negative values shift the signal below ground. |

```
awg offset 1 1.65    # shift channel 1 waveform up by 1.65 V
awg offset 2 -0.5    # shift channel 2 down by 0.5 V
```

---

## awg duty

Set square wave duty cycle without changing other parameters.

```
awg duty <1|2|all> <%>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1\|2\|all` | required | `1`, `2`, `all` | Channel to configure. |
| `%` | required | 0.0–100.0 | Duty cycle as a percentage. |

```
awg duty 1 25    # set channel 1 to 25% duty cycle
awg duty 1 50    # 50% duty cycle (symmetric square wave)
```

---

## awg phase

Set phase offset without changing other parameters.

```
awg phase <1|2|all> <degrees>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1\|2\|all` | required | `1`, `2`, `all` | Channel to configure. |
| `degrees` | required | 0.0–360.0 | Phase offset in degrees. |

```
awg phase 2 180    # invert channel 2 (180° phase offset)
awg phase 2 90     # 90° phase offset between channels
```

---

## awg sync

Enable or disable the sync/trigger output signal.

```
awg sync <on|off>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `on\|off` | required | `on`, `off` | Enable or disable the sync output. |

```
awg sync on     # enable sync output
awg sync off    # disable sync output
```

!!! note
    Sync output is only available on AWGs that support it.

---

## awg state

```
awg state <on|off|safe|reset>
```

| Value | Effect |
|-------|--------|
| `on` | Enable all outputs |
| `off` | Disable all outputs |
| `safe` | Outputs off, returns to known defaults |
| `reset` | `*RST` — factory defaults |
