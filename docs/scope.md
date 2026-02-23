# Scope — Oscilloscope

Controls oscilloscopes over VISA.

- Channels are numbered `1`–`4`. Use `all` to affect every channel at once.
- Multiple scopes are named `scope1`, `scope2`, etc.

---

## Acquisition Control

### scope autoset

Auto-configure the scope for the current input signal.

```
scope autoset
```

Automatically adjusts time/division, voltage/division, and trigger settings to display the input signal cleanly. Equivalent to pressing the Autoset button on the front panel.

### scope run / stop / single

```
scope run       # start continuous acquisition
scope stop      # freeze the display
scope single    # arm single-shot trigger
```

| Command | Effect |
|---------|--------|
| `run` | Start continuous acquisition (free-running) |
| `stop` | Freeze the display at the current waveform |
| `single` | Arm the trigger — capture one waveform then stop |

---

## Channel Control

### scope chan

Enable or disable channel display.

```
scope chan <1-4|all> <on|off>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1-4\|all` | required | `1`, `2`, `3`, `4`, `all` | Channel number, or `all`. |
| `on\|off` | required | `on`, `off` | Show or hide the channel. |

```
scope chan 1 on      # show channel 1
scope chan 3 off     # hide channel 3
scope chan all on    # show all channels
```

### scope coupling

Set input coupling for one or more channels.

```
scope coupling <1-4|all> <DC|AC|GND>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1-4\|all` | required | `1`–`4`, `all` | Channel(s) to configure. |
| `DC\|AC\|GND` | required | `DC`, `AC`, `GND` | Coupling mode. DC = pass all frequencies. AC = block DC component. GND = disconnect input (shows 0 V reference). |

```
scope coupling 1 AC       # AC-couple channel 1
scope coupling all DC     # DC-couple all channels
```

### scope probe

Set probe attenuation so the scope displays correct voltages.

```
scope probe <1-4|all> <attenuation>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1-4\|all` | required | `1`–`4`, `all` | Channel(s). |
| `attenuation` | required | `1`, `10`, `100` | Probe attenuation ratio. `1` = direct connection, `10` = 10× probe, `100` = 100× high-voltage probe. |

```
scope probe 1 10    # channel 1 has a 10× probe
scope probe all 1   # all channels: direct (1×) connection
```

---

## Horizontal (Time) Axis

### scope hscale

Set the time per division.

```
scope hscale <s/div>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `s/div` | required | float (s) | Seconds per division. E.g. `0.001` = 1 ms/div, `1e-6` = 1 µs/div. |

```
scope hscale 0.001      # 1 ms/div
scope hscale 0.0001     # 100 µs/div
```

### scope hpos / hmove

Set or adjust the horizontal trigger position.

```
scope hpos <percentage>     # set absolute position
scope hmove <delta>         # adjust relative to current position
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `percentage` | required (hpos) | Trigger position as percent of screen width. |
| `delta` | required (hmove) | Relative adjustment amount. |

```
scope hpos 50     # center trigger at 50%
scope hmove 10    # shift right by 10%
```

---

## Vertical (Voltage) Axis

### scope vscale

Set voltage per division for one or more channels.

```
scope vscale <1-4|all> <V/div> [pos]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1-4\|all` | required | `1`–`4`, `all` | Channel(s). |
| `V/div` | required | float (V) | Voltage per division. |
| `pos` | optional | float (divisions) | Vertical position offset. Default: `0` (centered). |

```
scope vscale 1 0.5           # channel 1: 0.5 V/div
scope vscale 1 0.5 -2        # 0.5 V/div, shifted down 2 divisions
scope vscale all 1.0 0       # all channels: 1 V/div, centered
```

### scope vpos / vmove

Set or adjust vertical position.

```
scope vpos <1-4|all> <divisions>    # set absolute position
scope vmove <1-4|all> <delta>       # adjust relative to current
```

```
scope vpos 1 0        # center channel 1
scope vmove 1 -1      # move channel 1 down by 1 division
```

---

## Trigger

### scope trigger

Configure the trigger.

```
scope trigger <channel> <level> [slope=<RISE|FALL>] [mode=<AUTO|NORM|SINGLE>]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `channel` | required | `1`–`4` | Trigger source channel. |
| `level` | required | float (V) | Trigger threshold voltage. |
| `slope=` | optional | `RISE`, `FALL` | Edge to trigger on. Default: `RISE`. |
| `mode=` | optional | `AUTO`, `NORM`, `SINGLE` | Trigger mode. `AUTO` = free-run if no trigger; `NORM` = wait for trigger; `SINGLE` = one-shot. Default: `AUTO`. |

```
scope trigger 1 0.0                           # ch1, 0 V threshold, rising edge
scope trigger 1 1.5 slope=FALL                # ch1, 1.5 V, falling edge
scope trigger 1 0.0 slope=RISE mode=NORM      # ch1, normal mode
```

---

## Measurements

### scope meas

Take and print a single measurement.

```
scope meas <1-4|all> <type>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1-4\|all` | required | `1`–`4`, `all` | Channel to measure. |
| `type` | required | see below | Measurement type (case-insensitive). |

=== "Rigol DHO804"

    All types are case-insensitive. Aliases are separated by `/`.

    **Voltage**

    | Type / Aliases | Description |
    |----------------|-------------|
    | `VPP` / `PK2PK` | Peak-to-peak voltage |
    | `VRMS` / `RMS` | RMS voltage |
    | `ACRMS` | AC RMS voltage |
    | `VMAX` / `MAXIMUM` | Maximum voltage |
    | `VMIN` / `MINIMUM` | Minimum voltage |
    | `VTOP` / `TOP` | Top voltage (high state) |
    | `VBASE` / `BASE` | Base voltage (low state) |
    | `VAMP` / `AMPLITUDE` | Amplitude (Vtop − Vbase) |
    | `VAVG` / `MEAN` / `AVERAGE` | Mean voltage |
    | `VMID` / `MID` | Mid voltage |
    | `VUPPER` / `UPPER` | Upper threshold voltage |
    | `VLOWER` / `LOWER` | Lower threshold voltage |
    | `VARIANCE` / `VAR` | Voltage variance |
    | `PVRMS` | Per-period RMS voltage |
    | `TVMAX` | Time at Vmax |
    | `TVMIN` | Time at Vmin |

    **Time**

    | Type / Aliases | Description |
    |----------------|-------------|
    | `FREQUENCY` / `FREQ` | Signal frequency |
    | `PERIOD` | Signal period |
    | `RISE` / `RISETIME` | Rise time (10%–90%) |
    | `FALL` / `FALLTIME` | Fall time (90%–10%) |
    | `PWIDTH` | Positive pulse width |
    | `NWIDTH` | Negative pulse width |

    **Duty Cycle**

    | Type / Aliases | Description |
    |----------------|-------------|
    | `PDUTY` / `POSDUTY` | Positive duty cycle |
    | `NDUTY` / `NEGDUTY` | Negative duty cycle |

    **Shape**

    | Type / Aliases | Description |
    |----------------|-------------|
    | `OVERSHOOT` / `OVER` | Overshoot |
    | `PRESHOOT` / `PRE` | Preshoot |
    | `PSLEWRATE` / `POSSLEW` | Positive slew rate |
    | `NSLEWRATE` / `NEGSLEW` | Negative slew rate |

    **Area**

    | Type / Aliases | Description |
    |----------------|-------------|
    | `MAREA` / `AREA` | Waveform area |
    | `MPAREA` / `PERIODAREA` | Period area |

    **Counts**

    | Type / Aliases | Description |
    |----------------|-------------|
    | `PPULSES` | Positive pulse count |
    | `NPULSES` | Negative pulse count |
    | `POSEDGES` / `PEDGES` | Positive edge count |
    | `NEGEDGES` / `NEDGES` | Negative edge count |

    ```
    scope meas 1 FREQUENCY    # print channel 1 frequency
    scope meas 1 PK2PK        # print channel 1 peak-to-peak
    scope meas 2 RISE         # print channel 2 rise time
    scope meas 3 OVERSHOOT    # print channel 3 overshoot
    ```

=== "Tektronix MSO2024"

    **Voltage**

    | Type | Description |
    |------|-------------|
    | `PK2PK` | Peak-to-peak voltage |
    | `RMS` | RMS voltage |
    | `CRMS` | Cycle RMS voltage |
    | `MEAN` | Mean voltage |
    | `AMPLITUDE` | Amplitude (high − low) |
    | `MINIMUM` | Minimum voltage |
    | `MAXIMUM` | Maximum voltage |
    | `HIGH` | High voltage level |
    | `LOW` | Low voltage level |

    **Time**

    | Type | Description |
    |------|-------------|
    | `FREQUENCY` | Signal frequency |
    | `PERIOD` | Signal period |
    | `RISE` | Rise time |
    | `FALL` | Fall time |
    | `PWIDTH` | Positive pulse width |
    | `NWIDTH` | Negative pulse width |

    **Shape**

    | Type | Description |
    |------|-------------|
    | `POSOVERSHOOT` | Positive overshoot |
    | `NEGOVERSHOOT` | Negative overshoot |

    ```
    scope meas 1 FREQUENCY    # print channel 1 frequency
    scope meas 1 PK2PK        # print channel 1 peak-to-peak
    scope meas 2 RISE         # print channel 2 rise time
    ```

!!! note
    `scope meas` prints the result but does not record it. Use `scope meas_store` to save to the log.

### scope meas_setup

Configure a measurement slot before capturing so the scope computes the value when the trigger fires.

```
scope meas_setup <1-4|all> <type>
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1-4\|all` | required | `1`–`4`, `all` | Channel(s) to configure. |
| `type` | required | see measurement types above | Measurement to compute on next capture. |

=== "Rigol DHO804"

    ```
    scope meas_setup 3 RISE     # configure CH3 rise time slot
    scope meas_setup 4 RISE     # configure CH4 rise time slot
    scope single
    scope wait_stop timeout=10
    scope meas_force            # force DSP computation
    scope meas_store 3 RISE ch3_rise unit=s
    ```

    !!! note
        Call `scope meas_setup` **before** `scope single`. Use `scope meas_force` after `wait_stop` to ensure computation is complete before querying.

=== "Tektronix MSO2024"
    Not supported. The MSO2024 computes measurements on demand — use `scope meas_store` directly after capture without a prior setup step.

### scope meas_force

Force the scope's measurement DSP to compute all configured slots.

=== "Rigol DHO804"

    ```
    scope meas_force
    ```

    The DHO804 computes measurements lazily — values are only finalized when the display refreshes. `scope meas_force` triggers an internal display refresh (no file written) so that `scope meas_store` returns valid values immediately after `scope wait_stop`.

    !!! note
        Use after `scope wait_stop` and before `scope meas_store` when you do not want to save a screenshot first. If you already call `scope screenshot` before `scope meas_store`, this step is redundant.

=== "Tektronix MSO2024"
    Not supported. The MSO2024 computes measurements on demand — no force step is needed.

### scope meas_clear

Remove all measurement items from the on-screen results panel.

=== "Rigol DHO804"

    ```
    scope meas_clear
    ```

    Sends `:MEASure:CLEar` to hide the measurement sidebar. Use before `scope screenshot` to capture a clean image without the measurement overlay.

    ```
    scope meas_force
    scope meas_store 3 RISE ch3_rise unit=s
    scope meas_clear              # close the panel
    scope screenshot cap.png      # clean screenshot
    ```

=== "Tektronix MSO2024"
    Not supported. The MSO2024 does not maintain an on-screen measurement panel via SCPI.

### scope meas_store

Measure and record to the measurement log.

```
scope meas_store <1-4|all> <type> <label> [unit=<str>]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `1-4\|all` | required | `1`–`4`, `all` | Channel to measure. |
| `type` | required | see measurement types above | Measurement type. |
| `label` | required | string, no spaces | **Name for this entry in the log.** Appears in `log print` and used as the dictionary key in `calc` expressions: `m["label"]`. Use underscores — e.g. `ch1_freq`. |
| `unit=` | optional | string | Unit shown in `log print` (e.g. `Hz`, `V`). **Display-only** — does not affect the stored value or calculations. |

=== "Rigol DHO804"

    ```
    scope meas_store 1 FREQUENCY meas_freq unit=Hz
    scope meas_store 1 PK2PK     meas_pk2pk unit=V
    scope meas_store 3 RISE      ch3_rise unit=s
    ```

=== "Tektronix MSO2024"

    ```
    scope meas_store 1 FREQUENCY meas_freq unit=Hz
    scope meas_store 1 PK2PK     meas_pk2pk unit=V
    scope meas_store 2 RISE      ch2_rise unit=s
    ```

Then use in calculations:

```
calc crest_factor m["meas_pk2pk"] / m["meas_rms"]   # compute crest factor
log print
```

### scope meas_delay

Measure the time delay between two channels.

```
scope meas_delay <ch1> <ch2> [edge1=RISE] [edge2=RISE]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `ch1` / `ch2` | required | `1`–`4` | Source and reference channel numbers. |
| `edge1=` / `edge2=` | optional | `RISE`, `FALL` | Which edge to detect on each channel. Default: `RISE`. |

=== "Rigol DHO804"

    ```
    scope meas_delay 1 2              # delay from ch1 rising to ch2 rising
    scope meas_delay 1 2 edge2=FALL  # delay from ch1 rising to ch2 falling
    ```

=== "Tektronix MSO2024"

    ```
    scope meas_delay 1 2              # delay from ch1 rising to ch2 rising
    scope meas_delay 1 2 edge2=FALL  # delay from ch1 rising to ch2 falling
    ```

### scope meas_delay_store

Measure delay and record to the log.

```
scope meas_delay_store <ch1> <ch2> <label> [edge1=RISE] [edge2=RISE] [direction=FORWARDS] [unit=]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `ch1` / `ch2` | required | `1`–`4` | Channel numbers. |
| `label` | required | string | Log entry name — same rules as `meas_store`. |
| `edge1=` / `edge2=` | optional | `RISE`, `FALL` | Edge selection. Default: `RISE`. |
| `direction=` | optional | `FORWARDS`, `BACKWARDS` | Search direction. Default: `FORWARDS`. |
| `unit=` | optional | string | Unit shown in log (e.g. `s`, `ms`). Display-only. |

=== "Rigol DHO804"

    ```
    scope meas_delay_store 1 2 prop_delay unit=s
    ```

=== "Tektronix MSO2024"

    ```
    scope meas_delay_store 1 2 prop_delay unit=s
    ```

---

## Waveform Capture

### scope save

Download waveform data and save to a CSV file.

```
scope save <channels> <file.csv> [record=<s>] [time=<s>] [points=<n>]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `channels` | required | `1`–`4` or comma-separated | Channel(s) to save. E.g. `1` or `1,2`. |
| `file.csv` | required | file path | Output file. Created or overwritten. |
| `record=` / `time=` | optional | float (s) | Record for this many seconds before saving. |
| `points=` | optional | int | Number of waveform points to request from scope. |

```
scope save 1 output.csv              # save channel 1 waveform
scope save 1,2 both.csv             # save channels 1 and 2
scope save 1 data.csv record=2.0    # record for 2 s then save
```

---

## Built-in Tools

These commands access built-in scope tools where available.

### scope awg

Control the built-in waveform generator (DHO914S and DHO924S only).

```
scope awg              # show available subcommands
scope awg on           # enable AWG output
scope awg off          # disable AWG output
scope awg sine 1000 2.0 0    # configure: sine, 1 kHz, 2 Vpp, 0 V offset
```

### scope counter

Control the built-in frequency counter.

```
scope counter on       # enable counter
scope counter off      # disable counter
scope counter read     # read current frequency
scope counter source 1 # set counter source to channel 1
```

### scope dvm

Control the built-in digital voltmeter.

```
scope dvm on           # enable DVM
scope dvm off          # disable DVM
scope dvm read         # read current DVM value
scope dvm source 1     # set DVM source to channel 1
```

---

## scope state

```
scope state <on|off|safe|reset>
```

| Value | Effect |
|-------|--------|
| `on` | Enable all channels |
| `off` | Disable all channels |
| `safe` | Channels off, trigger to default |
| `reset` | `*RST` — factory defaults |

---

## DHO804-Specific Features

The following commands are available on the Rigol DHO804 and similar Rigol oscilloscopes.

### scope screenshot

Capture the scope display and save as PNG.

=== "Rigol DHO804"
    ```
    scope screenshot                    # auto-named: screenshot_HHMMSS.png
    scope screenshot capture.png        # save as capture.png in data dir
    scope screenshot /path/to/file.png  # save to absolute path
    ```

    Screenshots are saved to `~/Documents/scpi-instrument-toolkit/data/` by default.

=== "Tektronix MSO2024"
    Not supported on this model.

### scope label / invert / bwlimit

=== "Rigol DHO804"
    ```
    scope label <1-4> <text>        # set channel label
    scope invert <1-4> <on|off>     # invert channel display
    scope bwlimit <1-4> <20M|OFF>   # set bandwidth limit
    ```

    | Command | Parameter | Description |
    |---------|-----------|-------------|
    | `label` | `<ch> <text>` | Set a custom label for the channel |
    | `invert` | `<ch> on\|off` | Flip the waveform vertically |
    | `bwlimit` | `<ch> 20M\|OFF` | Enable 20 MHz bandwidth limit filter |

    ```
    scope label 1 VCC
    scope invert 2 on
    scope bwlimit 1 20M
    ```

=== "Tektronix MSO2024"
    Not supported on this model.

### scope force

Force a trigger event immediately.

```
scope force
```

Useful when the trigger is armed but not triggering. Works on all scope models.

### scope reset

Reset the scope to factory defaults.

```
scope reset
```

Sends `*RST` to restore factory defaults. Works on all scope models.

---

### scope display

=== "Rigol DHO804"
    Control display settings.

    ```
    scope display clear                  # clear waveform display
    scope display brightness <0-100>     # set waveform brightness
    scope display grid <FULL|HALF|NONE>  # set grid style
    scope display gridbright <0-100>     # set grid brightness
    scope display persist <MIN|1|5|10|INF|OFF>  # set persistence time
    scope display type <VECTORS|DOTS>    # set display type
    ```

    | Subcommand | Parameter | Description |
    |------------|-----------|-------------|
    | `clear` | — | Clear waveform display |
    | `brightness` | `0`–`100` | Waveform brightness percentage |
    | `grid` | `FULL`, `HALF`, `NONE` | Grid style |
    | `gridbright` | `0`–`100` | Grid brightness percentage |
    | `persist` | `MIN`, `1`, `5`, `10`, `INF`, `OFF` | Persistence time |
    | `type` | `VECTORS`, `DOTS` | Waveform rendering mode |

=== "Tektronix MSO2024"
    Not supported on this model.

---

### scope acquire

=== "Rigol DHO804"
    Control acquisition settings.

    ```
    scope acquire type <NORMAL|AVERAGE|PEAK|HRES>  # set acquisition type
    scope acquire averages <count>                  # set number of averages
    scope acquire depth <AUTO|1K|10K|100K|1M|...>   # set memory depth
    scope acquire rate                              # show current sample rate
    ```

    | Subcommand | Parameter | Description |
    |------------|-----------|-------------|
    | `type` | `NORMAL`, `AVERAGE`, `PEAK`, `HRES` | Acquisition mode |
    | `averages` | integer (2, 4, 8, … 8192) | Number of averages |
    | `depth` | `AUTO`, `1K`, `10K`, `100K`, `1M`, `10M` | Memory depth |
    | `rate` | — | Display current sample rate |

=== "Tektronix MSO2024"
    Not supported on this model.

---

### scope cursor

=== "Rigol DHO804"
    Control measurement cursors.

    ```
    scope cursor off                        # disable cursors
    scope cursor manual <X|Y|XY> [source]   # enable manual cursors
    scope cursor set <ax> [ay] [bx] [by]    # set cursor positions
    scope cursor read                       # read cursor values
    ```

    | Subcommand | Parameter | Description |
    |------------|-----------|-------------|
    | `off` | — | Disable cursors |
    | `manual` | `X`, `Y`, `XY` + optional source | Enable manual cursors |
    | `set` | up to 4 float values | Set cursor positions |
    | `read` | — | Read and display cursor values |

    ```
    scope cursor manual X CH1         # enable X cursors on channel 1
    scope cursor set 0.001 0.002      # set A and B cursor positions
    scope cursor read                 # read delta values
    ```

=== "Tektronix MSO2024"
    Not supported on this model.

---

### scope math

=== "Rigol DHO804"
    Control math channels (operations, FFT, filters).

    ```
    scope math on|off [ch]                              # enable/disable math channel
    scope math op <ch> <ADD|SUB|MUL|DIV> <src1> [src2]  # arithmetic operation
    scope math func <ch> <ABS|SQRT|LG|LN|EXP> <src>    # math function
    scope math fft <ch> <src> [window=RECT]             # FFT analysis
    scope math filter <ch> <LPAS|HPAS|BPAS|BSTOP> <src> [upper=] [lower=]  # digital filter
    scope math scale <ch> <scale> [offset]              # set math channel scale
    ```

    | Subcommand | Description |
    |------------|-------------|
    | `on`/`off` | Enable or disable a math channel |
    | `op` | Arithmetic: ADD, SUB, MUL, DIV, AND, OR, XOR |
    | `func` | Functions: ABS, SQRT, LG, LN, EXP, DIFF, INTG |
    | `fft` | FFT analysis with configurable window |
    | `filter` | Digital filter: low-pass, high-pass, band-pass, band-stop |
    | `scale` | Adjust math channel vertical scale |

    ```
    scope math on 1                        # enable math channel 1
    scope math op 1 SUB CH1 CH2            # Math1 = CH1 - CH2
    scope math fft 1 CH1 window=HANN       # FFT of CH1 with Hanning window
    scope math filter 1 LPAS CH1 upper=1000  # 1 kHz low-pass filter
    ```

=== "Tektronix MSO2024"
    Not supported on this model.

---

### scope record

=== "Rigol DHO804"
    Control waveform recording and playback.

    ```
    scope record on|off           # enable/disable recording
    scope record frames <count>   # set number of frames to record
    scope record start            # start recording
    scope record stop             # stop recording
    scope record status           # show recording status
    scope record play             # start playback of recorded frames
    ```

    | Subcommand | Parameter | Description |
    |------------|-----------|-------------|
    | `on`/`off` | — | Enable or disable recording mode |
    | `frames` | integer | Number of frames to record |
    | `start` | — | Begin recording |
    | `stop` | — | Stop recording |
    | `status` | — | Display current recording status |
    | `play` | — | Start playback of recorded frames |

    ```
    scope record frames 500       # record 500 frames
    scope record start            # begin recording
    scope record status           # check status
    scope record play             # play back recording
    ```

=== "Tektronix MSO2024"
    Not supported on this model.

---

### scope mask

=== "Rigol DHO804"
    Control pass/fail mask testing.

    ```
    scope mask on|off                 # enable/disable mask testing
    scope mask source <1-4>           # set mask source channel
    scope mask tolerance <x> <y>      # set X and Y tolerance
    scope mask create                 # auto-create mask from current waveform
    scope mask start                  # start mask test
    scope mask stop                   # stop mask test
    scope mask stats                  # show pass/fail statistics
    scope mask reset                  # reset statistics
    ```

    | Subcommand | Parameter | Description |
    |------------|-----------|-------------|
    | `on`/`off` | — | Enable or disable mask testing |
    | `source` | `1`–`4` | Source channel for mask |
    | `tolerance` | `<x> <y>` | X and Y tolerance values |
    | `create` | — | Auto-create mask from current waveform |
    | `start`/`stop` | — | Start or stop mask test |
    | `stats` | — | Display pass/fail/total statistics |
    | `reset` | — | Reset statistics counters |

    ```
    scope mask source 1               # set mask source to CH1
    scope mask create                  # create mask from current waveform
    scope mask start                  # start testing
    scope mask stats                  # view results
    ```

=== "Tektronix MSO2024"
    Not supported on this model.
