# SMU — Source Measure Unit

Controls source measure units (SMUs) that can both source a precise voltage and simultaneously measure current (or vice versa).

- Multiple SMUs are named `smu1`, `smu2`, etc.
- Address a specific SMU directly: `smu1 set 5.0` — or use `use smu1` then `smu set 5.0`

=== "NI PXIe-4139"
    ±60 V / 3 A four-quadrant SMU (20 W source, 12 W sink). Uses the **nidcpower** Python package (not VISA/SCPI). Install with: `pip install nidcpower`. Output range: −60 V to +60 V, −3 A to +3 A DC (10 A pulse).

---

## smu on / smu off

Enable or disable the SMU output.

```bash
smu on     # enable output
smu off    # disable output
```

Safety limits set with `upper_limit` / `lower_limit` are enforced before enabling.

---

## smu set

Set output voltage and optional current limit.

```bash
smu set <voltage> [current_limit]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `voltage` | required | −60.0 – 60.0 (V) | Target output voltage. |
| `current_limit` | optional | 0.0 – 3.0 (A) | Current compliance limit (always positive). If omitted, the existing limit is kept. |

```bash
smu set 5.0          # set 5 V, keep existing current limit
smu set 5.0 0.01     # set 5 V with 10 mA current limit
smu set -12.0 0.1    # negative voltage for four-quadrant operation
```

!!! warning
    Setting a voltage without a current limit uses whatever limit was set previously (default: 10 mA). Always specify the limit when powering an unknown DUT. DC source power is capped at 20 W and sink power at 12 W by the hardware.

!!! tip "How to sink current"
    Use `smu set_mode current` instead of `smu set`. In current mode, the SMU acts as a programmable electronic load — positive current = sink from DUT, negative current = source into DUT. See [smu set_mode](#smu-set_mode) below.

---

## smu meas

Take a single measurement and print the result.

```bash
smu meas [v|i|vi]
```

| Mode | Alias | Description |
|------|-------|-------------|
| *(no arg)* or `vi` | `both`, `all` | Atomic V+I+compliance read in one call (default) |
| `v` | `volt`, `voltage` | Measure actual output voltage only |
| `i` | `curr`, `current` | Measure actual output current only |

```bash
smu meas       # prints e.g.  V=5.000012V  I=0.009987A
smu meas vi    # same as above; appends [COMPLIANCE] if current-limited
smu meas v     # prints e.g.  5.000012V
smu meas i     # prints e.g.  0.009987A
```

!!! tip
    `smu meas` / `smu meas vi` performs an atomic measurement that reads voltage, current, and compliance state in a single driver call — use this instead of separate `v` and `i` calls when you need a consistent snapshot.

---

## smu set_mode

Switch the SMU between voltage-source and current-source modes.

```bash
smu set_mode voltage <v> [current_limit]
smu set_mode current <i> [voltage_limit]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `voltage` / `current` | required | mode keyword | Select sourcing mode. Alias: `v` / `i`. |
| second arg | required | float | Setpoint in volts (voltage mode) or amps (current mode, −3.0 to 3.0). |
| third arg | optional | float | Compliance limit for the opposing quantity (always positive). |

```bash
smu set_mode voltage 3.3 0.1    # source 3.3 V with 100 mA current limit
smu set_mode current 0.010 3.0  # sink 10 mA from DUT (electronic load), 3 V compliance
smu set_mode current -0.5 5.0   # source 0.5 A into DUT, 5 V compliance
```

!!! note "Current mode polarity"
    In current mode, **positive current = sink** (draw current from the DUT, acting as a load) and **negative current = source** (push current into the DUT). This is the standard four-quadrant SMU convention. Use positive values when the SMU is loading an LDO, regulator, or other voltage source.

Safety limits (`upper_limit` / `lower_limit`) are enforced before the mode switch is applied.

---

## smu meas_store

Measure and record the result to the measurement log.

```bash
smu meas_store <v|i> <label> [unit=<str>]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `v\|i` | required | `v`, `i` | What to measure. |
| `label` | required | string, no spaces | Name for this entry in the log. |
| `unit=` | optional | string | Unit shown in `log print`. Defaults to `V` or `A`. |

```bash
smu meas_store v smu_vout unit=V
smu meas_store i smu_iout unit=A
calc power m["smu_vout"] * m["smu_iout"] unit=W
```

See [Log & Calc](logging.md) for full details.

---

## smu compliance

Query whether the SMU is currently in compliance (i.e. the output is being current- or voltage-limited by the instrument's protection circuit).

```bash
smu compliance
```

Prints `Not in compliance` when the DUT is drawing within limits, or a warning banner `IN COMPLIANCE - output is current-limited` when the limit has been hit. Use `smu meas vi` to see the compliance flag alongside a measurement.

---

## smu source_delay

Get or set the settling delay the SMU inserts between applying a new source value and taking a measurement.

```bash
smu source_delay           # read current delay
smu source_delay <seconds> # set delay (0 – 167 s)
```

```bash
smu source_delay           # prints e.g.  source_delay = 0.0020 s
smu source_delay 0.05      # set 50 ms settle time
smu source_delay 0         # disable delay
```

---

## smu avg

Get or set the number of samples averaged per measurement.

```bash
smu avg        # read current value
smu avg <N>    # set to N samples (integer ≥ 1)
```

```bash
smu avg        # prints e.g.  samples_to_average = 1
smu avg 10     # average 10 readings per measurement call
smu avg 1      # back to single-sample mode
```

Higher values reduce noise but increase measurement time proportionally.

---

## smu temp

Read the internal temperature sensor of the instrument.

```bash
smu temp
```

Prints the temperature in degrees Celsius, e.g. `34.5 degrees C`. Useful for confirming the unit has warmed up to a stable operating temperature before precision measurements. Expected range for a powered-on PXIe-4139 is approximately 20 – 60 °C.

---

## smu get

Show the current voltage setpoint, current limit, and output state.

```bash
smu get
```

Prints: `Setpoint: <V>V @ <A>A, Output: ON|OFF`

---

## smu state

```bash
smu state <on|off|safe|reset>
```

| Value | Effect |
|-------|--------|
| `on` | Enable output |
| `off` | Disable output |
| `safe` | Disable output |
| `reset` | Disconnect and re-initialize the session |

---

## Safety limits

`upper_limit` and `lower_limit` work with SMUs using the same `voltage` and `current` parameters as PSUs:

```bash
upper_limit smu voltage 5.5     # SMU output ≤ 5.5 V
upper_limit smu current 0.1     # current limit ≤ 100 mA
lower_limit smu voltage -0.3    # SMU output ≥ −0.3 V
```

See [Safety Limits](scripting.md#safety-limits) for the full reference.

---

## Typical workflow

```bash
upper_limit smu1 voltage 6.0
upper_limit smu1 current 0.05

smu1 set 5.0 0.02     # 5 V, 20 mA limit
smu1 on
sleep 0.5

smu1 meas_store v vout unit=V
smu1 meas_store i iout unit=A
calc power m["vout"] * m["iout"] unit=W

log print
smu1 off
```
