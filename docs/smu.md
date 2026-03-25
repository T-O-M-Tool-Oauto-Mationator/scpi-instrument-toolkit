# SMU — Source Measure Unit

Controls source measure units (SMUs) that can both source a precise voltage and simultaneously measure current (or vice versa).

- Multiple SMUs are named `smu1`, `smu2`, etc.
- Address a specific SMU directly: `smu1 set 5.0` — or use `use smu1` then `smu set 5.0`

=== "NI PXIe-4139"
    ±60 V / 1 A four-quadrant SMU. Uses the **nidcpower** Python package (not VISA/SCPI). Install with: `pip install nidcpower`. Output range: −60 V to +60 V, 0 A to 1 A.

---

## smu on / smu off

Enable or disable the SMU output.

```
smu on     # enable output
smu off    # disable output
```

Safety limits set with `upper_limit` / `lower_limit` are enforced before enabling.

---

## smu set

Set output voltage and optional current limit.

```
smu set <voltage> [current_limit]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `voltage` | required | −60.0 – 60.0 (V) | Target output voltage. |
| `current_limit` | optional | 0.0 – 1.0 (A) | Current compliance limit. If omitted, the existing limit is kept. |

```
smu set 5.0          # set 5 V, keep existing current limit
smu set 5.0 0.01     # set 5 V with 10 mA current limit
smu set -12.0 0.1    # negative voltage for four-quadrant operation
```

!!! warning
    Setting a voltage without a current limit uses whatever limit was set previously (default: 10 mA). Always specify the limit when powering an unknown DUT.

---

## smu meas

Take a single measurement and print the result.

```
smu meas v    # measure output voltage
smu meas i    # measure output current
```

| Mode | Alias | Description |
|------|-------|-------------|
| `v` | `volt`, `voltage` | Measure actual output voltage |
| `i` | `curr`, `current` | Measure actual output current |

```
smu meas v    # prints e.g.  5.000012V
smu meas i    # prints e.g.  0.009987A
```

---

## smu meas_store

Measure and record the result to the measurement log.

```
smu meas_store <v|i> <label> [unit=<str>]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `v\|i` | required | `v`, `i` | What to measure. |
| `label` | required | string, no spaces | Name for this entry in the log. |
| `unit=` | optional | string | Unit shown in `log print`. Defaults to `V` or `A`. |

```
smu meas_store v smu_vout unit=V
smu meas_store i smu_iout unit=A
calc power m["smu_vout"] * m["smu_iout"] unit=W
```

See [Log & Calc](logging.md) for full details.

---

## smu get

Show the current voltage setpoint, current limit, and output state.

```
smu get
```

Prints: `Setpoint: <V>V @ <A>A, Output: ON|OFF`

---

## smu state

```
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

```
upper_limit smu voltage 5.5     # SMU output ≤ 5.5 V
upper_limit smu current 0.1     # current limit ≤ 100 mA
lower_limit smu voltage -0.3    # SMU output ≥ −0.3 V
```

See [Safety Limits](scripting.md#safety-limits) for the full reference.

---

## Typical workflow

```
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
