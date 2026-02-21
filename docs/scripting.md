# Scripts & Directives

Scripts are named sequences of REPL commands stored in the session. They support variables, loops, sub-scripts, and operator interaction — letting you automate full test sequences.

Script directives (`set`, `print`, `pause`, `input`, `sleep`, `repeat`, `for`, `call`) are also valid as **interactive REPL commands** — you can test them at the prompt before putting them in a script.

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
script run <name> [key=value ...]
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | required | Script name (as shown by `script list`). |
| `key=value` | optional | Override script variables. Replaces the default values from `set` lines inside the script. |

```
script run my_psu_test
script run my_psu_test voltage=3.3 label=test_3v3
```

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

Save or restore the entire script library as a JSON file.

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

| Parameter | Required | Description |
|-----------|----------|-------------|
| `varname` | required | Variable name. No spaces — use underscores. |
| `expression` | required | Value, string, or arithmetic expression. |

```
set voltage 5.0           # ${voltage} = 5.0
set label vtest           # ${label} = "vtest"
set doubled ${voltage} * 2    # ${doubled} = 10.0
set offset ${voltage} - 0.5   # ${offset} = 4.5
```

### Variable substitution

Use `${varname}` anywhere in a script line and it will be replaced with the variable's value before the command runs:

```
set voltage 5.0
set label my_run

psu1 set ${voltage}               # → psu1 set 5.0
dmm1 meas_store vdc ${label} unit=V   # → dmm1 meas_store vdc my_run unit=V
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
dmm1 meas_store vdc dmm_v unit=V   # measure DMM, save as "dmm_v"
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

You can use a script variable *as* the log label — this is how you make labels dynamic:

```
set meas_name output_v         # script variable: meas_name = "output_v"
psu1 meas_store v ${meas_name} unit=V
#                  └─ expands to: psu1 meas_store v output_v unit=V
#                     log label = "output_v"
```

This is especially useful in loops — each iteration gets a different label:

```
for v 3.3 5.0 12.0
  psu1 set ${v}
  sleep 0.5
  dmm1 meas_store vdc dmm_${v} unit=V   # labels: dmm_3.3, dmm_5.0, dmm_12.0
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
dmm1 meas_store vdc dmm_v unit=V       # save DMM reading as "dmm_v"

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

| Parameter | Required | Description |
|-----------|----------|-------------|
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

| Parameter | Required | Description |
|-----------|----------|-------------|
| `varname` | required | Variable name. The entered value will be available as `${varname}` in all lines after this directive. |
| `prompt text` | optional | Text shown to operator. Default: the variable name. |

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
dmm1 meas_store vdc output_${voltage} unit=V
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

| Parameter | Required | Description |
|-----------|----------|-------------|
| `N` | required | Number of repetitions. Integer ≥ 1. |

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

| Parameter | Required | Description |
|-----------|----------|-------------|
| `var` | required | Loop variable name. Available as `${var}` inside the block. |
| `val1 val2 ...` | required | Space-separated list of values to iterate over. |

**Sweep PSU through voltages:**

```
for v 1.0 2.0 3.3 5.0 9.0 12.0
  print Setting ${v}V...
  psu1 set ${v}
  sleep 0.5
  dmm1 meas_store vdc v_${v} unit=V
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

---

## Sub-scripts

### call — run another script inline

```
call <name> [key=value ...]
```

Executes another script as a sub-routine. The called script runs in its own variable scope. Variables from the current script can be passed as parameters.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | required | Name of the script to call. |
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
for v 3.3 5.0 12.0
  call set_psu voltage=${v} label=psu_${v}
  dmm1 meas_store vdc dmm_${v} unit=V
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

# ── Sweep ────────────────────────────────────
for v 1.0 2.0 3.3 5.0 9.0 12.0
  print Testing ${v}V...
  psu1 set ${v}
  sleep ${delay}
  psu1 meas_store v psu_${v} unit=V
  dmm1 meas_store vdc dmm_${v} unit=V
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
