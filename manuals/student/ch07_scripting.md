# Chapter 7: Scripting Mastery

Scripts let you automate entire test sequences. Instead of typing commands one at a time, you write them in a file and run them with one command.

## Creating Scripts

### Method 1: Script Editor

    script new my_test

This opens your system text editor. Write commands, one per line. Save and close.

### Method 2: Record from Interactive Session

    record start my_test
    psu1 chan 1 on
    psu1 set 1 5.0
    sleep 0.5
    v = psu1 meas v unit=V
    log print
    record stop

Every command you type between `record start` and `record stop` is saved to the script.

### Method 3: Load from File

    script run ./my_test.scpi

Run a `.scpi` file directly from disk without copying it to the scripts library.

## Running Scripts

    script run my_test                    # run by name
    script run my_test voltage=3.3       # with parameter override
    script run ./lab3.scpi                # run by file path

## Variables in Scripts

Define default values at the top of your script. Users can override them with `key=value` on the command line.

    # my_test.scpi
    voltage = 5.0
    label = vtest

    psu1 chan 1 on
    psu1 set 1 {voltage}
    sleep 0.5
    {label} = dmm1 meas unit=V
    log print

Run with defaults:

    script run my_test

Run with overrides:

    script run my_test voltage=3.3 label=v3v3

## For Loops

Repeat a block of commands for each value in a list:

    for v 1.0 2.0 3.3 5.0
      psu1 set 1 {v}
      sleep 0.5
      v_{v} = dmm1 meas unit=V
    end

The loop variable `{v}` takes each value in order: 1.0, then 2.0, then 3.3, then 5.0.

### Linspace for Smooth Sweeps

Generate evenly spaced values:

    RAMP = linspace 0 5.0 11

This creates 11 values from 0 to 5.0: `0 0.5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5 5.0`

Use it in a for loop:

    RAMP = linspace 0 5.0 11
    for v RAMP
      psu1 set 1 {v}
      sleep 0.3
      v_{v} = dmm1 meas unit=V
    end

### Multi-Variable For Loops

Iterate over paired values:

    for ch,v 1,5.0 2,12.0 3,3.3
      psu1 set {ch} {v}
    end

## While Loops

Repeat until a condition is false:

    i = 0
    total = 0
    while i < 5
      i++
      total += i
    end
    print "Sum 1..5 = {total}"

### While with Break and Continue

    j = 0
    while j < 20
      j++
      if j == 3
        continue       # skip iteration 3
      end
      if j > 6
        break          # stop after 6
      end
      print "j = {j}"
    end

## If / Elif / Else

Conditional branching:

    voltage = 5.05
    if voltage > 5.1
      verdict = "OVER"
    elif voltage < 4.9
      verdict = "UNDER"
    else
      verdict = "OK"
    end
    print "Voltage {voltage} V: {verdict}"

## Assert (Hard Stop)

Assert stops the script immediately if the condition is false:

<!-- doc-test: skip reason="reference example -- voltage not set in this block" -->

    assert voltage > 0 "voltage must be positive"
    assert voltage < 6.0 "voltage below safety limit"

Use assert for safety-critical checks that must pass before continuing.

## Check (Soft Test)

Check records a PASS or FAIL result but does NOT stop the script:

<!-- doc-test: skip reason="reference example -- voltage not set in this block" -->

    check voltage > 4.9 "above lower bound"
    check voltage < 5.1 "below upper bound"

View results with:

    log report

Check is useful for validation testing where you want to run all tests and report results at the end.

## Sleep and Pause

<!-- doc-test: skip reason="pause prompts operator for interactive Enter" -->

    sleep 0.5              # wait 500ms (for instrument settling)
    sleep 2                # wait 2 seconds
    pause                  # wait for user to press Enter
    pause "Connect DUT"    # wait with custom message

## Repeat

Repeat a block a fixed number of times:

    repeat 5
      v = dmm1 meas unit=V
      sleep 1
    end

## Calling Sub-Scripts

<!-- doc-test: skip reason="requires a saved sub-script named other_script on disk" -->

    call other_script

Runs `other_script` from within the current script. Variables are shared between caller and callee.

## The Debugger

Step through a script one command at a time:

    script debug my_test

Debugger commands:

| Command  | Action                        |
|----------|-------------------------------|
| n / next | Execute next line             |
| c / cont | Continue to next breakpoint   |
| s / step | Same as next                  |
| p / print | Show all variables           |
| q / quit | Stop debugging                |

### Breakpoints

Add a breakpoint in your script:

<!-- doc-test: skip reason="breakpoint only fires under `script debug`, not at the onecmd prompt" -->

    psu1 set 1 5.0
    breakpoint                # debugger stops here
    v = dmm1 meas unit=V

When running with `script debug`, execution pauses at each breakpoint so you can inspect variables.

## Error Handling

    set -e            # stop script on any error
    set +e            # continue despite errors (default)

With `set -e`, the script stops at the first error (failed measurement, invalid command, etc.). Without it, errors are printed but the script continues.

## Example: Complete Test Script

    # lab3_full_test.scpi
    set -e
    log clear
    voltage = 5.0
    tolerance = 5

    print "=== Lab 3: Voltage Accuracy Test ==="
    print "Target: {voltage} V, Tolerance: {tolerance}%"

    psu1 chan 1 on
    psu1 set 1 {voltage}
    sleep 1.0

    dmm1 config vdc
    measured = dmm1 meas unit=V
    calc error_pct = (measured - {voltage}) / {voltage} * 100 unit=%

    check error_pct -5 5 "within {tolerance}% tolerance"

    psu1 chan 1 off
    log print
    log save lab3_results.csv
    log report

    print "=== Test Complete ==="

## Try It

1. Create a script with `script new my_sweep`
2. Write a for loop that sweeps voltage and measures
3. Run it in mock mode
4. Try the debugger: `script debug my_sweep`
5. Add a breakpoint and inspect variables
