# Scripts & Directives

Scripts are named sequences of REPL commands stored in the session. They support variables, loops, sub-scripts, and operator interaction — letting you automate full test sequences.

Script directives (`set`, `array`, `print`, `pause`, `input`, `sleep`, `repeat`, `for`, `call`, `import`, `export`, `breakpoint`) are also valid as **interactive REPL commands** — you can test them at the prompt before putting them in a script.

---

## Script Management

### script new

Create a new script and open it in your editor.

```
script new <name>
```

Opens your system editor (`$EDITOR` / `$VISUAL`). Write one command per line. Save and close to finish.

```
script new my_psu_test
```

### script run

Execute a script with optional parameter overrides.

```
script run <name|path> [key=value ...]
```

| Parameter   | Required | Description                                                                                |
| ----------- | -------- | ------------------------------------------------------------------------------------------ |
| `name`      | required | Script name (from `script list`) **or** a file path (absolute or relative to cwd).        |
| `key=value` | optional | Override script variables. Replaces the default values from `set` lines inside the script. |

Pass a file path — with `/`, `\`, a leading `.`, or a `.scpi` extension — to run a script directly from disk without copying it to the scripts library:

```
script run my_psu_test                     # named script in scripts dir
script run my_psu_test voltage=3.3         # with parameter override
script run ./lab3.scpi                     # run by relative path
script run ../tests/sweep.scpi             # run by relative path
script run /home/user/projects/lab3.scpi   # run by absolute path
script run C:/projects/lab3.scpi           # Windows absolute path
```

### script debug

Run a script in the **interactive debugger** — step through commands one at a time, set breakpoints, and inspect state at any point.

```
script debug <name|path> [key=value ...]
```

Accepts the same name-or-path syntax as `script run`. See [Debugger](#debugger) for the full reference.

```
script debug lab3
script debug ./lab3.scpi
script debug my_test voltage=3.3
```

### script dir

Get or set the directory where named scripts are stored for this session.

```
script dir           # print current scripts directory
script dir <path>    # switch to a different directory
script dir reset     # go back to the default
```

| Example | Effect |
|---------|--------|
| `script dir .` | Load named scripts from the current working directory |
| `script dir ./scripts` | Load from a `scripts/` subfolder of cwd |
| `script dir /path/to/scripts` | Load from an absolute path |
| `script dir reset` | Restore default (`~/Documents/scpi-instrument-toolkit/scripts/`) |

Changing the scripts dir immediately reloads all named scripts from the new location. This is useful when your project keeps its `.scpi` files alongside its source code:

```
script dir .                # point at the project folder
script list                 # see what's available
script run lab3             # run lab3.scpi from the project folder
```

!!! note
    `script dir` affects named scripts (used by `script run <name>`). To run a one-off file anywhere on disk without changing the scripts dir, use `script run ./path/to/file.scpi` instead.

### script edit

Open an existing script in your editor.

```
script edit <name>
```

### script show

Print a script's lines to the terminal with syntax highlighting.

```
script show <name>
```

### script list

Show all saved scripts with their line counts.

```
script list
```

### script rm

Delete a script.

```
script rm <name>
```

### script import

Load script lines from a plain-text file.

```
script import <name> <path>
```

### script load / save

Reload scripts from disk, or show the current scripts directory.

```
script save [path]         # save (default: .repl_scripts.json)
script load [path]         # load (default: .repl_scripts.json)
```

Scripts persist between REPL sessions via `.repl_scripts.json`. Use `script save` before exiting and `script load` on next launch, or let the REPL do it automatically.

---

## Variables

Variables let you parameterize scripts so the same script works for different test conditions.

### set — define a variable

```
set <varname> <expression>
```

Defines a variable accessible as `${varname}` in all subsequent lines. Evaluated at **script expansion time** (before execution begins), so arithmetic using other variables works.

| Parameter    | Required | Description                                 |
| ------------ | -------- | ------------------------------------------- |
| `varname`    | required | Variable name. No spaces — use underscores. |
| `expression` | required | Value, string, or arithmetic expression.    |

```
set voltage 5.0           # ${voltage} = 5.0
set label vtest           # ${label} = "vtest"
set doubled ${voltage} * 2    # ${doubled} = 10.0
set offset ${voltage} - 0.5   # ${offset} = 4.5
```

#### Error handling: set -e / set +e

Control whether a script stops when a command fails (like bash's `set -e`).

```
set -e    # Enable exit-on-error: stop script on first command failure
set +e    # Disable exit-on-error: continue despite errors
```

**Example: stop on error**

```
set -e
psu1 set 5.0           # if this fails, script stops here
dmm1 config vdc        # this won't run if PSU command failed
print Done             # this won't run either
```

**Example: continue on error**

```
set +e
psu1 set 5.0           # if this fails, continue anyway
dmm1 config vdc        # this runs regardless
print Done             # always executes
```

!!! tip
Use `set -e` for critical test sequences where a single failure should abort the entire test. Use `set +e` when you want to collect partial results even if some commands fail.

### Variable substitution

Use `${varname}` anywhere in a script line and it will be replaced with the variable's value before the command runs:

```
set voltage 5.0
set label my_run

psu1 set ${voltage}               # → psu1 set 5.0
dmm1 meas_store ${label} unit=V   # → dmm1 meas_store my_run unit=V
print Setting ${voltage}V         # → prints "Setting 5.0V"
```

### Overriding variables at run time

Variables defined with `set` can be overridden when running the script from the command line:

```
# Script has:  set voltage 5.0
script run my_test voltage=3.3    # runs with voltage=3.3 instead of 5.0
script run my_test voltage=12.0 label=high_v
```

This is how you reuse the same script for different test conditions without editing it.

**Priority order:** command-line params > `set` defaults in the script.

---

## Measurements in scripts

Scripts use the same `meas_store`, `calc`, and `log` commands as the interactive REPL. Understanding how they fit together is key to writing useful test scripts.

### How meas_store works in a script

`meas_store` saves a measurement to the **measurement log** with a name (the label) so you can retrieve it later. The label is just a string you choose — it becomes the row name in the log table.

```
psu1 meas_store v output_v unit=V   # measure voltage, save as "output_v"
dmm1 config vdc                     # set DMM to DC voltage mode
dmm1 meas_store dmm_v unit=V        # measure DMM, save as "dmm_v"
calc error m["output_v"] - m["dmm_v"] unit=V   # subtract them
log print                           # show the full table
```

After running this, `log print` shows:

```
Label       Value       Unit   Source
output_v    4.9987      V      psu.meas
dmm_v       4.9992      V      dmm.read
error      -0.0005      V      calc
```

See [Log & Calc](logging.md) for the full reference.

### Using variables as log labels

Script variables and log labels are **two separate things**:

- **Script variable** (`${var}`) — substituted into command text before the command runs
- **Log label** — the name given to a stored measurement row

You can use a script variable _as_ the log label — this is how you make labels dynamic:

```
set meas_name output_v         # script variable: meas_name = "output_v"
psu1 meas_store v ${meas_name} unit=V
#                  └─ expands to: psu1 meas_store v output_v unit=V
#                     log label = "output_v"
```

This is especially useful in loops — each iteration gets a different label:

```
dmm1 config vdc
for v 3.3 5.0 12.0
  psu1 set ${v}
  sleep 0.5
  dmm1 meas_store dmm_${v} unit=V   # labels: dmm_3.3, dmm_5.0, dmm_12.0
end
log print    # all three rows appear in the log
```

### A complete measurement script

```
# my_test — measure PSU accuracy at a target voltage
set voltage 5.0
set test_name vout_5v

print === Starting test: ${test_name} ===
psu1 chan 1 on
psu1 set ${voltage}
sleep 0.5

psu1 meas_store v psu_v unit=V         # save PSU reading as "psu_v"
dmm1 config vdc                        # set DMM to DC voltage mode
dmm1 meas_store dmm_v unit=V           # save DMM reading as "dmm_v"

calc error     m["dmm_v"] - m["psu_v"] unit=V
calc error_pct m["error"] / m["psu_v"] * 100 unit=%

log print
log save ${test_name}.csv

psu1 chan 1 off
print === Done ===
```

Run it with different voltages without editing the script:

```
script run my_test voltage=3.3 test_name=vout_3v3
script run my_test voltage=12.0 test_name=vout_12v
```

---

## Output and Operator Interaction

### print — display a message

```
print <message>
```

Prints a message to the terminal. Variable substitution works.

```
print === PSU/DMM Test ===
print Setting ${voltage}V to ${label}
print Test complete. Check log print for results.
```

Use `print` to add section headers, progress updates, and instructions in your scripts.

### pause — wait for operator

```
pause [message]
```

Stops script execution and waits for the operator to press **Enter**. Use for manual steps — connecting probes, changing the DUT, verifying wiring — before the script continues.

| Parameter | Required | Description                                                     |
| --------- | -------- | --------------------------------------------------------------- |
| `message` | optional | Prompt shown to operator. Default: "Press Enter to continue..." |

```
pause
pause Connect probe to TP1 then press Enter
pause Swap DUT before continuing
```

### input — prompt for a value

```
input <varname> [prompt text]
```

Prompts the operator to type a value at runtime. The entered text is stored as `${varname}` and substituted into all subsequent lines.

| Parameter     | Required | Description                                                                                           |
| ------------- | -------- | ----------------------------------------------------------------------------------------------------- |
| `varname`     | required | Variable name. The entered value will be available as `${varname}` in all lines after this directive. |
| `prompt text` | optional | Text shown to operator. Default: the variable name.                                                   |

```
input voltage Enter target voltage (V):
input dut_id DUT serial number:
input operator_name Operator name:
```

After `input voltage`, you can use `${voltage}` anywhere:

```
input voltage Enter target voltage (V):
psu1 set ${voltage}
print Voltage set to ${voltage}V
dmm1 config vdc
dmm1 meas_store output_${voltage} unit=V
```

!!! note
Unlike `set`, values captured by `input` **cannot** be overridden from the command line at `script run` time. They are always prompted interactively.

---

## Timing

### sleep — pause inside a script

```
sleep <seconds>
```

Pauses execution for the given duration. Variable substitution works:

```
sleep 0.5              # pause 500 ms
sleep ${delay}         # pause using a variable
sleep 1.0              # wait 1 second for signal to settle
```

Use `sleep` after `psu set` or `awg wave` to let the output settle before measuring.

---

## Loops

### repeat — fixed number of repetitions

```
repeat <N>
  <commands>
end
```

Executes the enclosed commands exactly N times.

| Parameter | Required | Description                         |
| --------- | -------- | ----------------------------------- |
| `N`       | required | Number of repetitions. Integer ≥ 1. |

```
repeat 5
  psu1 meas_store v sample unit=V
  sleep 0.2
end
```

```
repeat 3
  dmm1 meas vdc
  sleep 0.5
end
```

### for — loop over a list of values

```
for <var> <val1> <val2> ... <valN>
  <commands>
end
```

Iterates over a whitespace-separated list of values. On each iteration, `${var}` is set to the next value in the list.

| Parameter       | Required | Description                                                 |
| --------------- | -------- | ----------------------------------------------------------- |
| `var`           | required | Loop variable name. Available as `${var}` inside the block. |
| `val1 val2 ...` | required | Space-separated list of values to iterate over.             |

**Sweep PSU through voltages:**

```
dmm1 config vdc
for v 1.0 2.0 3.3 5.0 9.0 12.0
  print Setting ${v}V...
  psu1 set ${v}
  sleep 0.5
  dmm1 meas_store v_${v} unit=V
end
```

**Enable each scope channel in turn:**

```
for ch 1 2 3 4
  scope1 chan ${ch} on
end
```

**Frequency sweep:**

```
for f 100 500 1000 5000 10000 50000
  awg1 freq 1 ${f}
  sleep 0.4
  scope1 meas_store 1 FREQUENCY freq_${f} unit=Hz
  scope1 meas_store 1 PK2PK pk2pk_${f} unit=V
end
```

#### Multi-variable loops

Loop over multiple variables at once by separating them with commas. Values in the list are also comma-separated:

```
for VIN,VSCALE,LABEL 5.0,1.0,five 3.3,0.5,three 2.5,0.5,two
  print Testing ${VIN}V with scale ${VSCALE} (${LABEL})
  psu1 set ${VIN}
  sleep 0.5
end
```

#### Interactive for/repeat loops

You can enter `for` and `repeat` blocks directly in the interactive REPL. The prompt will change to show indentation, and you type `end` when finished:

```
eset> for VIN 5.0 3.3 2.5
  > print Testing VIN=${VIN}
  > psu1 set ${VIN}
  > sleep 0.5
  > end
Testing VIN=5.0
Testing VIN=3.3
Testing VIN=2.5
eset>
```

This works exactly the same as in scripts — all variable substitution and nesting work the same way.

!!! tip
The loop variable is substituted in all lines inside the block — including labels, print messages, and sub-command parameters.

**Variable references in the value list:**

```
set v_start 1.0
set v_mid 5.0
set v_end 12.0

for v ${v_start} ${v_mid} ${v_end}
  psu1 set ${v}
  sleep 0.5
end
```

### array — multi-line value list

```
array <varname>
  <value1>
  <value2>
  ...
end
```

Builds a variable from a list of values, one per line. Comment out any line with `#` to exclude it from the list. The result is stored as a space-separated string compatible with `for`.

This is the preferred way to define a sweep table — it's easy to read and you can disable individual points by commenting them out.

| Parameter  | Required | Description        |
| ---------- | -------- | ------------------ |
| `varname`  | required | Variable name.     |
| each line  | —        | One element per line. Lines starting with `#` are skipped. |

```
array SWEEP
  5.0,0.001,1.0
  3.3,0.001,0.5
  # 2.5,0.001,0.5   <- commented out, skipped
  1.8,0.0005,0.5
  1.5,0.0005,0.2
end

for VIN,HSCALE,VSCALE ${SWEEP}
  psu set ${VIN} 0.5
  scope hscale ${HSCALE}
  scope vscale 1 ${VSCALE} 0
end
```

This is equivalent to writing all values inline on the `for` line — but much easier to manage.

---

## Variable Scope

By default, each script runs in its own isolated variable scope. Variables defined inside a script do not leak into the REPL, and REPL variables are not automatically visible inside scripts. Use `import` and `export` to explicitly cross the boundary.

### import — pull a variable from the parent scope

```
import <varname> [varname2 ...]
```

Copies a variable from the calling scope (REPL or parent script) into the current script's scope. If the variable does not exist in the parent scope, an error is raised.

```
import FREQ VREF    # bring FREQ and VREF in from the REPL
psu set ${VREF} 0.5
awg freq 1 ${FREQ}
```

### export — push a variable back to the parent scope

```
export <varname> [varname2 ...]
```

When the script finishes, copies the named variable back to the calling scope (REPL or parent script). Only explicitly exported variables survive — everything else stays local.

```
set result 42.0
export result    # ${result} becomes available in the REPL after the script runs
```

**Example: script that returns a computed value**

```
# measure_vout — measures PSU output, exports result
set VOUT 0.0
psu meas_store v psu_reading unit=V
set VOUT m["psu_reading"]
export VOUT
```

After `script run measure_vout`, `${VOUT}` is available in the REPL.

---

## Sub-scripts

### call — run another script inline

```
call <name> [key=value ...]
```

Executes another script as a sub-routine. The called script runs in its own variable scope. Variables from the current script can be passed as parameters.

| Parameter   | Required | Description                                                   |
| ----------- | -------- | ------------------------------------------------------------- |
| `name`      | required | Name of the script to call.                                   |
| `key=value` | optional | Parameters to pass. Supports variable substitution in values. |

```
call set_psu voltage=5.0
call set_psu voltage=${target_v}     # pass a variable from current script
```

**Example: reusable sub-script pattern**

Create a script `set_psu`:

```
# set_psu — sets PSU to a voltage and verifies
# Params: voltage, label
set voltage 5.0
set label psu_out

psu1 chan 1 on
psu1 set ${voltage}
sleep 0.5
psu1 meas_store v ${label} unit=V
```

Call it from another script:

```
# main test
dmm1 config vdc
for v 3.3 5.0 12.0
  call set_psu voltage=${v} label=psu_${v}
  dmm1 meas_store dmm_${v} unit=V
end
log print
```

!!! note
Parameters passed via `call` override `set` defaults in the called script — same priority rules as `script run`.

---

## Comments

Lines beginning with `#` are ignored during execution.

```
# This is a comment
set voltage 5.0     # inline comments work too
```

Use comments liberally to document what each section does, expected values, and any hardware setup required.

---

## Debugger

The script debugger lets you step through a script one command at a time, set breakpoints, jump around, and run live REPL commands while paused. Because all loops and variables are fully expanded before the debugger starts, every iteration of a `for` loop appears as a separate numbered line — you can set a breakpoint on exactly the one point you care about.

### Starting the debugger

```
script debug <name> [key=value ...]
```

```
script debug lab3
script debug my_sweep voltage=3.3
```

### In-script breakpoints

Add `breakpoint` anywhere in a script file to automatically pause there, even when running with `script run`:

```
psu set ${VIN} 0.5
psu chan on
breakpoint          ← execution pauses here; drops into debugger
scope single
```

### Debugger display

When paused, the debugger shows a context window around the current line. The current line is highlighted in cyan. Lines with breakpoints are marked with `●`:

```
  ────────────────────────────────────────────────────────────
      12     psu chan off
      13     sleep 0.5
  →   14     psu set 5.0 0.5
  ●   15     psu chan on
      16     sleep 0.3
  ────────────────────────────────────────────────────────────
  14/42  │  n=step  c=continue  back  goto N  b N=break  d N=del  l=list  q=quit

(dbg) _
```

### Debugger commands

| Command      | Action                                                                                 |
| ------------ | -------------------------------------------------------------------------------------- |
| Enter / `n`  | Execute the current line and advance to the next                                       |
| `c`          | Continue running until the next breakpoint or end of script                            |
| `back`       | Move pointer back one line without executing — lets you re-run a command               |
| `goto N`     | Jump the pointer to line N — lines in between are **not** executed or reversed        |
| `b N`        | Set a breakpoint at line N                                                              |
| `d N`        | Delete the breakpoint at line N                                                        |
| `l`          | Show a wider context window (±8 lines)                                                 |
| `info`       | Show current line number and all active breakpoints                                    |
| `q`          | Abort the script and return to the REPL                                                |
| _any command_ | Type any REPL command (e.g. `psu meas v`, `scope meas 1 FREQ`) to run it live        |

!!! note
    `back` moves the execution pointer but does **not** reverse any instrument state. Use it when you want to re-execute a command, not to undo it.

!!! tip
    Because the full script is expanded before the debugger starts, line numbers are stable for the entire session. A `for` loop with 7 iterations appears as 7×N separate lines — you can set a breakpoint at exactly the iteration you want to inspect.

---

## Complete Example

A script combining all features:

```
# full_test.repl
# Full voltage characterization test
# Params: dut_name, v_min, v_max, steps

# ── Defaults ────────────────────────────────
set dut_name my_dut
set v_min 1.0
set v_max 5.0
set steps 5
set delay 0.5

# ── Operator setup ───────────────────────────
print === Voltage Characterization Test ===
print DUT: ${dut_name}
pause Connect DUT and DMM probes, then press Enter

# ── Optional runtime input ────────────────────
input operator Operator initials:

# ── PSU on ───────────────────────────────────
psu1 chan 1 on
print PSU enabled
dmm1 config vdc

# ── Sweep ────────────────────────────────────
for v 1.0 2.0 3.3 5.0 9.0 12.0
  print Testing ${v}V...
  psu1 set ${v}
  sleep ${delay}
  psu1 meas_store v psu_${v} unit=V
  dmm1 meas_store dmm_${v} unit=V
  calc err_${v} (m["dmm_${v}"] - m["psu_${v}"]) / m["psu_${v}"] * 100 unit=%
end

# ── Results ────────────────────────────────────
print === Test complete ===
log print
log save ${dut_name}_results.csv

# ── Safe state ────────────────────────────────
psu1 chan 1 off
print PSU off — done
```

Run it:

```
script run full_test dut_name=widget_rev2 delay=1.0
```
