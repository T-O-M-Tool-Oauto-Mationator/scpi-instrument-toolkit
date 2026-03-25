# Log & Calc

---

## The measurement log — what it is and why you need it

Every time you run a `meas_store` command, the REPL saves the result to a persistent **measurement log** — a table that accumulates all your readings for the current session.

```
┌─────────────────────────────────────────────────────────┐
│  psu meas_store v    output_v  unit=V                   │
│       │               │                                 │
│       │               └─ label: the name you choose     │
│       │                   for this row in the table     │
│       └─ what to measure (voltage)                      │
└─────────────────────────────────────────────────────────┘
```

After running a few `meas_store` commands, the log looks like:

```
Label       Value       Unit   Source
output_v    4.9987      V      psu.meas
dmm_v       4.9992      V      dmm.read
freq_ch1    999.87      Hz     scope.meas.FREQUENCY
```

`log print` shows it. `log save results.csv` exports it. `calc` does math on the values.

---

## What is a label?

A **label** is the name you give a stored measurement — the row key in the table above.

**Rules:**

- No spaces — use underscores: `output_v`, `ch1_pk2pk`, `r_load`
- Must be unique per session — storing twice with the same label **overwrites** the earlier value
- You reference it in `calc` as `m["label"]`

**Why labels matter:** without a name, you can't retrieve the value later. `psu meas v` just prints to the screen and is gone. `psu meas_store v output_v` saves it so you can compute `calc error m["output_v"] - 5.0` afterwards.

```
# meas = print only (nothing saved):
psu meas v          # prints 4.9987, then forgotten

# meas_store = save with a name:
psu meas_store v output_v unit=V    # saves 4.9987 as "output_v"
calc error m["output_v"] - 5.0      # retrieves it: 4.9987 - 5.0 = -0.0013
log print                            # shows the full table
```

---

## log print

Display all recorded measurements in the terminal.

```
log print
```

Prints a formatted table with columns: **Label | Value | Unit | Source**.

Run this at the end of a test sequence to review all results.

---

## log save

Export the measurement log to a file.

```
log save <filename> [csv|txt]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `filename` | required | file path | Output file path. |
| `csv\|txt` | optional | `csv`, `txt` | Format. Defaults to `csv` if the filename ends in `.csv`, otherwise `txt`. |

```
log save results.csv          # CSV format (opens in Excel)
log save results.txt          # formatted text table
log save sweep_data.csv       # save to named file
```

CSV files can be opened directly in Excel, LibreOffice Calc, or imported into Python with pandas.

---

## log clear

Remove all measurements from the log.

```
log clear
```

Use this before starting a new test sequence to ensure only the new results are saved.

```
log clear
script run my_test
log print
log save my_test_results.csv
```

---

## calc

Compute a derived value from stored measurements and add it to the log.

```
calc <label> <expression> [unit=<str>]
```

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `label` | required | string, no spaces | Name for the computed result. Appears in `log print` and can be referenced in later `calc` expressions. |
| `expression` | required | Python arithmetic | Math expression. Access stored measurements by label using `m["label"]`. Use `last` for the most recently stored value. |
| `unit=` | optional | string | Unit label shown in `log print`. Display-only. |

### Accessing stored measurements

Use `m["label"]` to reference any value previously stored in the log:

```
psu1 meas_store v psu_v unit=V
psu1 meas_store i psu_i unit=A
calc power m["psu_v"] * m["psu_i"] unit=W
```

Use `last` to reference the most recently stored value:

```
dmm1 config vdc
dmm1 meas_store my_reading unit=V
calc doubled last * 2 unit=V
```

### Available functions and constants

| Name | Description |
|------|-------------|
| `m["label"]` | Access a stored measurement by label |
| `last` | The most recently stored value |
| `abs(x)` | Absolute value |
| `min(a, b)` | Minimum of two values |
| `max(a, b)` | Maximum of two values |
| `round(x, n)` | Round to n decimal places |
| `pi` | π (3.14159...) |
| `sqrt(x)` | Square root |
| `log(x)` | Natural logarithm |
| `log10(x)` | Base-10 logarithm |

### Chained calculations

The result of `calc` is stored in the log, so you can chain calculations:

```
psu1 meas_store v v_in unit=V
psu1 meas_store i i_in unit=A
dmm1 config vdc
dmm1 meas_store v_out unit=V

calc power_in  m["v_in"] * m["i_in"] unit=W
calc power_out m["v_out"] * m["i_in"] unit=W      # assume same current
calc efficiency m["power_out"] / m["power_in"] * 100 unit=%
```

### Examples

**Compute percentage error:**

```
dmm1 config vdc
dmm1 meas_store measured unit=V
calc error_pct (m["measured"] - 5.0) / 5.0 * 100 unit=%
```

**Voltage ratio (gain):**

```
scope1 meas_store 1 PK2PK v_in unit=V
scope1 meas_store 2 PK2PK v_out unit=V
calc gain m["v_out"] / m["v_in"]
calc gain_db 20 * log10(m["gain"]) unit=dB
```

**Resistance from V and I:**

```
psu1 meas_store v v_supply unit=V
dmm1 meas_store idc i_load unit=A
calc resistance m["v_supply"] / m["i_load"] unit=Ω
```

**Crest factor:**

```
scope1 meas_store 1 PK2PK pk2pk unit=V
scope1 meas_store 1 RMS rms unit=V
calc crest_factor m["pk2pk"] / (2 * m["rms"])
```

---

## check

Assert that a stored measurement falls within acceptable limits. Appends a pass/fail result to the test report.

```
check <label> <min> <max>
check <label> <expected> tol=<N>
check <label> <expected> tol=<N>%
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `label` | required | Label of a stored measurement (must exist in the log). |
| `min` / `max` | required (range form) | Inclusive lower and upper bounds. |
| `expected` + `tol=` | required (tolerance form) | Center value and absolute tolerance. |
| `tol=<N>%` | optional | Percentage tolerance: pass if `|value − expected| ≤ N/100 × expected`. |

Prints `[PASS]` or `[FAIL]` with the measured value and limits. A failed check sets an error flag — scripts with `set -e` will stop on failure.

```
dmm1 config vdc
dmm1 meas_store vout unit=V

check vout 4.75 5.25          # pass if 4.75 V ≤ vout ≤ 5.25 V
check vout 5.0 tol=0.25       # pass if |vout − 5.0| ≤ 0.25 V
check vout 5.0 tol=5%         # pass if within 5% of 5.0 V
```

Results are collected in memory and shown with `report print` or exported with `report save`.

---

## report

View or export a lab test report containing all `check` pass/fail results.

```
report print
report save <path>
report clear
report title <text>
report operator <name>
```

| Subcommand | Description |
|------------|-------------|
| `print` | Print the check results table to the terminal |
| `save <path>` | Generate a PDF report at the given path |
| `clear` | Clear test results and the screenshot list |
| `title <text>` | Set the report title shown in the PDF header |
| `operator <name>` | Set the operator name shown in the report header |

```
report title "PSU Accuracy Test"
report operator "J. Smith"

# ... run checks ...

report print              # view results in terminal
report save results.pdf   # export PDF
```

!!! note
    `report save` requires `reportlab`: `pip install reportlab`

---

## data dir — controlling where files are saved

By default, screenshots, waveform CSVs, and `log save` files all land in `~/Documents/scpi-instrument-toolkit/data/`. Use `data dir` to point them anywhere you want for the current session.

```
data dir <path>    # set output directory (absolute or relative to cwd)
data dir           # print the current output directory
data dir reset     # go back to the default
```

| Example | Effect |
|---------|--------|
| `data dir .` | Save files in the current working directory |
| `data dir ./lab3` | Save files in a `lab3/` subfolder of cwd |
| `data dir /mnt/usb/captures` | Save to an absolute path |
| `data dir C:/Users/lab/output` | Windows path with forward slashes |
| `data dir reset` | Restore default (`~/Documents/scpi-instrument-toolkit/data/`) |

!!! tip "Windows paths"
    Forward slashes work on all platforms. Backslashes and spaces in paths are also supported without quoting:
    ```
    data dir C:\Users\lab\output
    data dir C:/My Documents/lab
    ```

The setting applies to every save command in the session — `scope screenshot`, `scope save`, and `log save` all respect it. Subdirectories within the output dir are still created automatically (e.g. `scope screenshot lab3/cap.png` → `<data_dir>/lab3/cap.png`).

You can also use it inside a `.scpi` script so the output location is part of the test setup:

```
# lab3.scpi
data dir .     # save everything relative to where I launched the REPL

log clear
for VIN {SWEEP}
  ...
  scope screenshot cap_{VIN}V.png
  scope save 1,2,3,4 wave_{VIN}V.csv
end
log save results.csv
```

!!! note
    `data dir` only affects the current REPL session. For a permanent default, set the `SCPI_DATA_DIR` environment variable before launching the REPL — it takes effect whenever `data dir` has not been set.

---

## Typical workflow

```
# 1. Clear previous results
log clear

# 2. Run measurements
psu1 chan 1 on
psu1 set 5.0
sleep 0.5

psu1 meas_store v psu_v unit=V     # save as "psu_v"
psu1 meas_store i psu_i unit=A     # save as "psu_i"
dmm1 config vdc
dmm1 meas_store dmm_v unit=V       # save as "dmm_v"

# 3. Derive values
calc power       m["psu_v"] * m["psu_i"] unit=W
calc v_error     m["dmm_v"] - m["psu_v"] unit=V
calc v_error_pct m["v_error"] / m["psu_v"] * 100 unit=%

# 4. Review and export
log print
log save results.csv
```
