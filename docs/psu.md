# PSU — Power Supply

!!! tip "Auto-generated reference"
    For the definitive command list extracted directly from source code, see [REPL Command Reference](generated/repl-ref.md#psu-power-supply).

Controls power supply units over VISA.

- **Single-channel** PSUs (e.g. HP E3631A): channel is always `1`
- **Multi-channel** PSUs (e.g. Matrix MPS-6010H): channels `1`, `2`, `3`, or `all`
- Multiple PSUs are named `psu1`, `psu2`, etc.

Address a specific PSU directly: `psu1 set 5.0` — or use `use psu1` then `psu set 5.0`.

=== "HP E3631A"
    Triple-output power supply. Channels: 1 (0–6 V), 2 (0–25 V), 3 (0– −25 V). Supports tracking mode for ±supply configurations.

=== "Keysight EDU36311A"
    Triple-output power supply. Channels: 1 (0–6 V / 5 A), 2 (0–30 V / 1 A), 3 (0–30 V / 1 A). USB/LAN interface. Supports tracking mode, OVP/OCP protection, save/recall (5 slots).

=== "Matrix MPS-6010H"
    Single-channel programmable PSU with serial interface. Supports remote mode control.

---

## psu chan

Enable or disable an output channel.

=== "Single-channel PSU"
    ```text
    psu chan <on|off>
    ```

=== "Multi-channel PSU"
    ```text
    psu chan <channel> <on|off>
    ```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `channel` | multi-ch only | `1`, `2`, `3`, `all` | Channel number. Omit entirely for single-channel PSUs. Use `all` to toggle all channels at once. |
| `on\|off` | required | `on`, `off` | `on` = enable output voltage; `off` = disable output. |

```text
psu chan on          # enable output (single-channel PSU)
psu chan off         # disable output (single-channel PSU)
psu chan 2 off       # disable channel 2 (multi-channel PSU)
psu chan all off     # disable all channels at once
```

---

## psu set

Set output voltage and optional current limit. Channel is always required.

```text
psu set <channel> <voltage> [current]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `channel` | required | `1`, `2`, `3` | Channel number. Single-channel PSUs use `1`. |
| `voltage` | required | float (V) | Target output voltage in volts. |
| `current` | optional | float (A) | Current limit in amperes. If omitted, the current limit is unchanged. |

```text
psu set 1 5.0             # channel 1 to 5 V
psu set 1 5.0 0.5         # channel 1: 5 V, 0.5 A limit
psu set 2 12.0            # channel 2 to 12 V
psu set 2 12.0 1.0        # channel 2: 12 V, 1 A limit
```

---

## psu meas

Measure and print the live output value. Channel is always required.

```text
psu meas <channel> <v|i>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `channel` | required | `1`, `2`, `3` | Channel to measure. Single-channel PSUs use `1`. |
| `v\|i` | required | `v`, `i` | `v` = measure output voltage; `i` = measure output current. |

```text
psu meas 1 v       # channel 1 voltage
psu meas 1 i       # channel 1 current
psu meas 2 v       # channel 2 voltage
```

!!! note
    `psu meas` prints the value but does not record it. To record for export or calculations, use the assignment syntax: `label = psu meas 1 v unit=V`.

!!! tip "Recording measurements"
    Use assignment syntax to measure **and** store the result to the measurement log in one step:

    ```text
    <label> = psu meas <channel> <v|i> [unit=<str>]
    ```

    | Parameter | Required | Values | Description |
    |-----------|----------|--------|-------------|
    | `label` | required | string, no spaces | **Name for this entry in the log.** Appears as the row identifier in `log print` output. Also used as the bare variable name in `calc` expressions. Use underscores instead of spaces — e.g. `ch1_voltage`. |
    | `channel` | required | `1`, `2`, `3` | Channel to measure. Single-channel PSUs use `1`. |
    | `v\|i` | required | `v`, `i` | Quantity to measure: `v` = voltage, `i` = current. |
    | `unit=` | optional | string | Unit label shown in `log print` output (e.g. `V`, `A`). **Display-only** — does not affect the stored numeric value or any calculation. |

    ```text
    ch1_v = psu meas 1 v unit=V       # store channel 1 voltage
    ch1_i = psu meas 1 i unit=A       # store channel 1 current
    ch2_v = psu meas 2 v unit=V       # store channel 2 voltage
    ```

    After storing, view with `log print` or compute derived values with `calc`:

    ```text
    psu_v = psu meas 1 v unit=V
    psu_i = psu meas 1 i unit=A
    calc power psu_v * psu_i unit=W    # compute power
    log print
    ```

    See [Log & Calc](logging.md) for full details.

---

## psu get

Show the programmed voltage/current setpoints (not the live measured output).

```text
psu get
```

For live measured values use `psu meas`.

---

## psu track

Enable or disable channel tracking mode (multi-channel PSUs only).

```text
psu track <on|off>
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `on\|off` | required | `on` = link channels in tracking mode (±supply); `off` = independent control. |

In tracking mode the two adjustable channels mirror each other — one outputs positive, the other negative — for split-supply configurations.

```text
psu track on     # enable tracking (±supply mode)
psu track off    # return to independent channel control
```

---

## psu save / recall

Save or restore voltage/current settings to a numbered slot (multi-channel PSUs only).

```text
psu save <1-3>
psu recall <1-3>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1-3` | required | `1`, `2`, `3` | Slot number to save to or recall from. |

```text
psu save 1      # save current settings to slot 1
psu recall 1    # restore settings from slot 1
```

---

## psu on / psu off

Enable or disable the power supply output (shorthand).

```bash
psu on     # enable output
psu off    # disable output
```

Equivalent to `psu chan on` / `psu chan off`. Works on both single-channel and multi-channel PSUs.

---

## psu state

```text
psu state <on|off|safe|reset>
```

| Value | Effect |
|-------|--------|
| `on` | Enable output |
| `off` | Disable output |
| `safe` | Outputs off, voltage setpoints zeroed |
| `reset` | `*RST` — factory defaults |
