# Chapter 3: Your First Measurement

This chapter walks through a complete measurement workflow step by step. You will set a PSU voltage, measure it with a DMM, log the result, and shut down safely.

You can follow along in mock mode (`scpi-repl --mock`) or with real instruments in the lab.

## Step 1: Launch the REPL

    scpi-repl --mock

The REPL starts, scans for instruments, and shows the prompt:

    eset>

## Step 2: See What is Connected

    list

This prints all discovered instruments with their names and models:

<!-- doc-test: skip reason="sample `list` output, not runnable REPL input" -->

    Name     Type               Model
    psu1     Power Supply       HP E3631A
    dmm1     Multimeter         HP 34401A
    scope1   Oscilloscope       Rigol DHO804
    ...

The names (psu1, dmm1, scope1) are what you use in commands.

## Step 3: Select a Power Supply

    use psu1

This sets psu1 as the "active" PSU. Now you can type `psu` commands without specifying which PSU:

    [SUCCESS] Active: psu1

Alternatively, you can always prefix commands with the instrument name directly: `psu1 set 1 5.0`.

## Step 4: Enable the Output

    psu chan 1 on

This enables channel 1 of the power supply. The output is now live (or simulated in mock mode).

    [SUCCESS] Output enabled

## Step 5: Set the Voltage

    psu set 1 5.0

This sets channel 1 to 5.0 volts. You can optionally set a current limit:

    psu set 1 5.0 0.5

This sets 5.0 V with a 0.5 A current limit.

    [SUCCESS] Set 1: 5.0V

## Step 6: Measure the PSU Output

    psu meas 1 v

This reads the actual output voltage from the PSU's internal measurement circuitry:

    5.001753 V

Note: the value is slightly different from 5.0 -- this is normal. Real instruments have small measurement variations.

## Step 7: Configure the DMM

    dmm1 config vdc

This configures the DMM (dmm1) for DC voltage measurement. The mode stays active until you change it.

    [SUCCESS] Configured for dc_voltage

## Step 8: Read the DMM and Store the Result

    voltage = dmm1 meas unit=V

This does three things:
1. Takes a DC voltage reading from the DMM
2. Stores the result in a variable called `voltage`
3. Records it in the measurement log with the label "voltage" and unit "V"

Output:

    voltage = 5.000241 V

The variable `voltage` is now available for calculations and print statements.

## Step 9: Print the Result

    print "Measured voltage: {voltage} V"

Output:

    Measured voltage: 5.000241 V

The `{voltage}` placeholder is replaced with the stored value.

## Step 10: View the Measurement Log

    log print

This shows all recorded measurements in a table:

    Label      Value       Unit   Source
    voltage    5.000241    V      dmm1

You can export this to a CSV file:

    log save results.csv

## Step 11: Shut Down Safely

    all off

This disables all instrument outputs at once -- a safe shutdown.

    exit

This closes the REPL and disconnects from all instruments.

## Putting It All Together

Here is the complete sequence you just ran:

    scpi-repl --mock
    list
    use psu1
    psu chan 1 on
    psu set 1 5.0
    psu meas 1 v
    dmm1 config vdc
    voltage = dmm1 meas unit=V
    print "Measured voltage: {voltage} V"
    log print
    all off
    exit

## Common Mistakes

**Forgetting to enable the output.** If you set a voltage but do not run `psu chan 1 on`, the output stays at 0 V. Always enable the channel before setting voltage.

**Forgetting to configure the DMM mode.** If you run `dmm1 meas` without first running `dmm1 config vdc`, the DMM may be in the wrong mode (resistance, frequency, etc.) and return unexpected values.

**Using `psu meas v` instead of the assignment syntax.** Plain `psu meas 1 v` prints the value but does NOT save it. Use `label = psu1 meas v unit=V` to record it in the log.

**Not specifying the channel number.** `psu set 5.0` is ambiguous. Always specify the channel: `psu set 1 5.0`.

## Try It

Run the complete sequence above in mock mode. Then try:

1. Change the voltage to 3.3 V and measure again
2. Measure the current: `current = psu1 meas i unit=A`
3. Calculate power: `calc power = voltage * current unit=W`
4. View the updated log: `log print`
