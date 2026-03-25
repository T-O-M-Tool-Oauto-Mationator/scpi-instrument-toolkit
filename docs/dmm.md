# DMM — Multimeter

Controls digital multimeters.

- Multiple DMMs are named `dmm1`, `dmm2`, etc.
- **Typical workflow:** configure mode → take readings → store results
- Or use `dmm meas` for a one-shot measurement without a separate configure step

=== "HP 34401A"
    6½-digit multimeter with GPIB interface. Supports NPLC control, display text, fetch, and high-accuracy measurements.

=== "OWON XDM1041"
    4½-digit multimeter with USB/serial interface. Supports basic DMM commands.

---

## dmm config

Configure the measurement mode. The mode stays active until changed.

```
dmm config <mode> [range] [resolution] [nplc=<n>]
dmm mode <mode> [range] [resolution] [nplc=<n>]
```

!!! note
    `dmm mode` is an alias for `dmm config` — both are identical.

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `mode` | required | see below | What to measure. |
| `range` | optional | float, `DEF`, `MIN`, `MAX` | Measurement range (e.g. `10` for 10 V range). `DEF` = auto-range. |
| `resolution` | optional | float, `DEF`, `MIN`, `MAX` | Resolution (number of significant digits). `DEF` = default. |
| `nplc=` | optional | `0.02`, `0.2`, `1`, `10`, `100` | Integration time in **power line cycles**. Higher = slower but lower noise. HP 34401A only, DC modes only. |

**Measurement modes:**

| Mode | Measures |
|------|----------|
| `vdc` | DC voltage |
| `vac` | AC voltage (RMS) |
| `idc` | DC current |
| `iac` | AC current (RMS) |
| `res` | Resistance, 2-wire |
| `fres` | Resistance, 4-wire (Kelvin) |
| `freq` | Frequency |
| `per` | Period |
| `cont` | Continuity |
| `diode` | Diode forward voltage |
| `cap` | Capacitance (device-dependent) |
| `temp` | Temperature (device-dependent) |

```
dmm config vdc                    # DC voltage, auto-range
dmm config vdc 10                 # DC voltage, 10 V range
dmm config vdc 10 DEF nplc=10    # high-accuracy DC voltage (slow)
dmm config res                    # 2-wire resistance, auto-range
dmm config fres DEF DEF nplc=1   # 4-wire resistance, 1 PLC
dmm config freq                   # frequency measurement
```

!!! tip
    For a single quick reading, use [`dmm meas`](#dmm-meas) instead — it configures and reads in one step.

---

## dmm read

Take a reading using the currently configured mode.

```
dmm read
```

Call `dmm config` first to set the mode. `dmm read` does not store the result — use [`dmm meas_store`](#dmm-meas_store) to record it.

```
dmm config vdc
dmm read       # take one DC voltage reading
```

---

## dmm meas_store

Read and record the result to the measurement log.

```
dmm meas_store <label> [scale=<factor>] [unit=<str>]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `label` | required | string, no spaces | **Name for this entry in the log.** Appears as the row identifier in `log print` output. Also used as the dictionary key in `calc` expressions: `m["label"]`. Use underscores instead of spaces — e.g. `vout_mv`. |
| `scale=` | optional | float | **Multiply the raw reading by this factor before storing.** Useful for unit conversion — e.g. `scale=1000` to convert V → mV, or `scale=0.001` to convert mA → A. Default: `1.0` (no scaling). |
| `unit=` | optional | string | Unit label shown in `log print` output (e.g. `V`, `mV`, `A`, `Ω`). **Display-only** — does not affect the stored value or calculations. |

!!! warning "Requires dmm config first"
    Call `dmm config <mode>` before using `meas_store`. The DMM must be in the correct mode.

```
dmm config vdc
dmm meas_store vout unit=V                  # store as 'vout', access as m["vout"]

dmm config res
dmm meas_store r_load unit=Ω               # store resistance

dmm config vdc
dmm meas_store vout_mv scale=1000 unit=mV  # convert V → mV before storing
```

**Using stored values in calculations:**

```
dmm config vdc
dmm meas_store voltage unit=V

dmm config idc
dmm meas_store current unit=A

calc power m["voltage"] * m["current"] unit=W    # compute power
log print
```

See [Log & Calc](logging.md) for full details.

---

## dmm meas

One-shot measurement — configure and read in a single command.

```
dmm meas <mode> [range] [resolution]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `mode` | required | same as `dmm config` | Measurement mode. |
| `range` | optional | float or `DEF` | Measurement range. Default: auto-range. |
| `resolution` | optional | float or `DEF` | Resolution. Default: default. |

```
dmm meas vdc        # quick DC voltage reading
dmm meas res        # quick resistance reading
dmm meas freq       # quick frequency reading
```

!!! note
    `dmm meas` does not support `nplc=` or storing results. For high-accuracy or repeated measurements, use `dmm config` + `dmm read` / `dmm meas_store`.

---

## dmm fetch

Fetch the last reading without triggering a new measurement.

```
dmm fetch
```

Returns the most recent measurement result without re-triggering. HP 34401A only.

---

## dmm beep

Trigger an audible beep from the DMM.

```
dmm beep
```

Useful as audio confirmation during scripted tests — e.g. beep when a measurement is complete.

---

## dmm display

Control the front panel display.

```
dmm display <on|off>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `on\|off` | required | `on`, `off` | Turn the display on or off. |

```
dmm display off    # blank the display (speeds up measurements on HP 34401A)
dmm display on     # restore display
```

---

## dmm text

Show custom text on the DMM display.

```
dmm text <message> [scroll=<auto|on|off>] [delay=<s>] [loops=<n>] [pad=<n>] [width=<n>]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `message` | required | string | Text to show on the front panel. |
| `scroll=` | optional | `auto`, `on`, `off` | Scroll behavior for messages wider than the display. `auto` = scroll only if too wide. |
| `delay=` | optional | float (s) | Delay between scroll steps in seconds. |
| `loops=` | optional | int | Number of times to repeat the scroll animation. |

```
dmm text READY
dmm text TESTING scroll=auto delay=0.2
```

!!! note
    HP 34401A only.

---

## dmm text_loop

Scroll text continuously across the DMM display in a background loop.

```
dmm text_loop <message> [delay=<s>] [pad=<n>] [width=<n>]
dmm text_loop off
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `message` | required | string | Text to scroll. |
| `delay=` | optional | float (s) | Seconds between scroll steps. Default: `0.2`. |
| `pad=` | optional | int | Blank characters to pad each side of the message. Default: `4`. |
| `width=` | optional | int | Display window width in characters. Default: `12`. |
| `off` | — | — | Stop the scrolling loop and clear the display. |

```
dmm text_loop TESTING delay=0.15    # start scrolling
dmm text_loop off                   # stop
```

!!! note
    HP 34401A only. The loop runs until `dmm text_loop off` is called or the REPL exits.

---

## dmm cleartext

Clear any custom text from the DMM display and restore the measurement display.

```
dmm cleartext
```

!!! note
    HP 34401A only.

---

## dmm ranges

Print the valid measurement ranges for the connected DMM model.

```
dmm ranges
```

---

## dmm state

```
dmm state <safe|reset>
```

| Value | Effect |
|-------|--------|
| `safe` | Returns to safe defaults |
| `reset` | `*RST` — factory defaults |
