# Example Workflows

These bundled examples demonstrate common lab measurement workflows. Load any example into your session and run it, or use it as a starting point for your own scripts.

```
examples                        # list all bundled examples
examples load <name>            # load a specific example
examples load all               # load all examples at once
script run <name> [params]      # run a loaded example
```

---

## psu_dmm_test

**Set PSU to a voltage, measure with DMM, log result.**

This is the simplest useful workflow: power a DUT at a target voltage and record what the DMM actually measures.

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `voltage` | `5.0` | Target PSU voltage in volts. |
| `label` | `vtest` | Label for the DMM measurement in the log. |

**Load and run:**

```
examples load psu_dmm_test
script run psu_dmm_test voltage=5.0 label=vtest
script run psu_dmm_test voltage=3.3 label=v3v3
```

**What it does:**

1. Turns on PSU channel 1
2. Sets the voltage to `${voltage}` V
3. Waits 500 ms for the output to settle
4. Records the PSU's measured output as `psu_v`
5. Takes a DC voltage reading from the DMM, records as `${label}`
6. Prints the log

**Script source:**

```
# psu_dmm_test
set voltage 5.0
set label vtest

print === PSU/DMM Voltage Test ===
print Target: ${voltage}V

psu1 chan 1 on
psu1 set ${voltage}
sleep 0.5

psu1 meas_store v psu_v unit=V

dmm1 config vdc
dmm1 meas_store ${label} unit=V

print === Test complete ===
log print
```

**Interpreting results:**

After running, `log print` shows:

```
Label      Value      Unit   Source
psu_v      4.9987     V      psu.meas
vtest      4.9992     V      dmm.read
```

Compute the error between PSU setpoint and DMM reading:

```
calc error m["vtest"] - 5.0 unit=V
calc error_pct (m["vtest"] - 5.0) / 5.0 * 100 unit=%
```

---

## voltage_sweep

**Sweep PSU through a list of voltages, log DMM reading at each step.**

Tests how a DUT responds across a range of supply voltages.

**Load and run:**

```
examples load voltage_sweep
script run voltage_sweep
```

**What it does:**

1. Turns on PSU channel 1
2. For each voltage in the list: sets PSU → waits 500 ms → records DMM reading
3. Turns off PSU
4. Prints and saves the log to `voltage_sweep.csv`

**Default voltage list:** `1.0 2.0 3.3 5.0 9.0 12.0`

**To change the voltage list:** load the example, then `script edit voltage_sweep` and modify the `for` line.

**Script source:**

```
# voltage_sweep
print === Voltage Sweep ===
psu1 chan 1 on
sleep 0.3
dmm1 config vdc

for v 1.0 2.0 3.3 5.0 9.0 12.0
  print Setting ${v}V...
  psu1 set ${v}
  sleep 0.5
  dmm1 meas_store v_${v} unit=V
end

psu1 chan 1 off
print === Sweep complete ===
log print
log save voltage_sweep.csv
```

**Analyzing results:**

After running, each voltage step is recorded as `v_1.0`, `v_2.0`, `v_3.3`, etc. You can compute differences:

```
calc delta_3v3_5v m["v_5.0"] - m["v_3.3"] unit=V
```

---

## awg_scope_check

**Output a sine wave on AWG ch1, measure frequency and PK2PK on the scope.**

A basic signal integrity check — verify the AWG is outputting what you expect.

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `freq` | `1000` | Target frequency in Hz. |
| `amp` | `2.0` | Target amplitude in Vpp. |

**Load and run:**

```
examples load awg_scope_check
script run awg_scope_check freq=1000 amp=2.0
script run awg_scope_check freq=10000 amp=1.0
```

**What it does:**

1. Enables AWG channel 1
2. Configures a sine wave at `${freq}` Hz, `${amp}` Vpp
3. Waits 500 ms for signal to stabilize
4. Runs `scope autoset` to auto-configure the scope
5. Waits 1 s for autoset to settle
6. Records: FREQUENCY, PK2PK, and RMS from scope channel 1

**Script source:**

```
# awg_scope_check
set freq 1000
set amp 2.0

print === AWG + Scope Signal Check ===
print Frequency: ${freq} Hz   Amplitude: ${amp} Vpp

awg1 chan 1 on
awg1 wave 1 sine freq=${freq} amp=${amp} offset=0
sleep 0.5

scope1 autoset
sleep 1.0

scope1 meas_store 1 FREQUENCY meas_freq unit=Hz
scope1 meas_store 1 PK2PK     meas_pk2pk unit=V
scope1 meas_store 1 RMS       meas_rms unit=V

print === Results ===
log print
```

**Check accuracy:**

```
calc freq_error (m["meas_freq"] - 1000) / 1000 * 100 unit=%
calc amp_error (m["meas_pk2pk"] - 2.0) / 2.0 * 100 unit=%
```

---

## freq_sweep

**Sweep AWG through a list of frequencies, scope measures each.**

Characterize frequency response — useful for testing filters, amplifiers, and signal paths.

**Load and run:**

```
examples load freq_sweep
script run freq_sweep
```

**What it does:**

1. Enables AWG ch1, sets sine wave with fixed amplitude
2. For each frequency in the list: sets frequency → waits 400 ms → records FREQUENCY and PK2PK from scope
3. Disables AWG
4. Prints and saves log to `freq_sweep.csv`

**Default frequency list:** `100 500 1000 5000 10000 50000 100000` (Hz)

**Script source:**

```
# freq_sweep
print === Frequency Sweep ===
awg1 chan 1 on
awg1 wave 1 sine amp=2.0 offset=0
sleep 0.3

for f 100 500 1000 5000 10000 50000 100000
  print Testing ${f} Hz...
  awg1 freq 1 ${f}
  sleep 0.4
  scope1 meas_store 1 FREQUENCY freq_${f} unit=Hz
  scope1 meas_store 1 PK2PK     pk2pk_${f} unit=V
end

awg1 chan 1 off
print === Sweep complete ===
log print
log save freq_sweep.csv
```

**Computing gain:**

If you're testing a filter or amplifier, measure the input and output simultaneously:

```
# Modify the loop to capture both channels:
for f 100 500 1000 5000 10000 50000
  awg1 freq 1 ${f}
  sleep 0.4
  scope1 meas_store 1 PK2PK in_${f} unit=V
  scope1 meas_store 2 PK2PK out_${f} unit=V
  calc gain_${f} m["out_${f}"] / m["in_${f}"]
end
```

---

## psu_ramp

**Ramp PSU voltage from start to end in N equal steps.**

Useful for gradually bringing up power to a DUT and logging the response at each step.

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `v_start` | `0` | Starting voltage. |
| `v_end` | `12.0` | Ending voltage. |
| `steps` | `7` | Number of steps (informational — edit the `for` line to change the actual list). |
| `delay` | `0.5` | Seconds to wait at each step. |

**Load and run:**

```
examples load psu_ramp
script run psu_ramp v_start=0 v_end=12.0 delay=1.0
```

**Script source:**

```
# psu_ramp
set v_start 0
set v_end 12.0
set steps 7
set delay 0.5

print === PSU Voltage Ramp ===
print ${v_start}V → ${v_end}V in ${steps} steps

psu1 chan 1 on

for v ${v_start} 2.0 4.0 6.0 8.0 10.0 ${v_end}
  print Ramping to ${v}V
  psu1 set ${v}
  sleep ${delay}
  psu1 meas_store v ramp_${v} unit=V
end

print === Ramp complete ===
log print
```

!!! tip "Customizing the step list"
    The `for` loop hardcodes the voltage steps (`2.0 4.0 6.0 ...`). To change the actual step values, load the example with `examples load psu_ramp`, then `script edit psu_ramp` and modify the `for` line directly.

---

## Building your own

Use these examples as templates. The general pattern for any measurement script is:

```
# 1. Set defaults (overridable at run time)
set voltage 5.0
set label my_test
set delay 0.5

# 2. Operator setup
print === My Test ===
pause Connect hardware, then press Enter

# 3. Configure instruments
psu1 chan 1 on
psu1 set ${voltage}
sleep ${delay}

# 4. Measure and store
psu1 meas_store v psu_out unit=V
dmm1 config vdc
dmm1 meas_store dmm_out unit=V

# 5. Derived calculations
calc error m["dmm_out"] - m["psu_out"] unit=V

# 6. Export
log print
log save ${label}_results.csv

# 7. Safe state
psu1 chan 1 off
```

See [Scripting](scripting.md) for the complete directive reference.
