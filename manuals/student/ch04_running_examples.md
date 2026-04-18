# Chapter 4: Finding and Running Examples

The toolkit ships with 15 bundled example scripts that demonstrate common lab workflows. You can run them as-is, customize them with parameters, or use them as starting points for your own scripts.

## Listing Available Examples

    examples

This prints all 15 examples with their descriptions:

    psu_dmm_test         Set PSU to a voltage, measure with DMM, log result
    voltage_sweep        Sweep PSU through a list of voltages, log DMM reading at each step
    awg_scope_check      Output a sine wave on AWG, measure frequency and PK2PK on scope
    freq_sweep           Sweep AWG through frequencies, scope measures each
    psu_ramp             Ramp PSU voltage from start to end in steps
    live_voltage_sweep   Voltage sweep with live plot
    live_multi_plot      Multi-channel live plot
    live_freq_sweep      Frequency sweep with live plot
    live_combined_plot   Combined live plot with PSU and DMM
    cross_script_demo    Cross-script demo calling Python from SCPI
    conditional_psu_check  PSU check with if/elif/else branching
    assert_limits        Assert and check with pass/fail limits
    while_counter        While loop with counter and accumulator
    syntax_reference     Full syntax tour of all scripting features
    complete_cross_script  Complete cross-script demo

## Loading an Example

    examples load psu_dmm_test

This copies the example script into your session. You can now see its source:

    script show psu_dmm_test

Output shows every line of the script with syntax highlighting.

To load all examples at once:

    examples load all

## Running an Example

    script run psu_dmm_test

This runs the script from top to bottom. In mock mode, you will see:

    === PSU/DMM Voltage Test ===
    Target: 5.0V
    [SUCCESS] Output enabled
    [SUCCESS] Set 1: 5.0V
    [INFO] Sleeping 0.5s...
    psu_v = 5.001753 V
    [SUCCESS] Configured for dc_voltage
    vtest = 5.000241 V
    === Test complete ===
    Label      Value       Unit   Source
    psu_v      5.001753    V      psu1
    vtest      5.000241    V      dmm1

## Using Parameter Overrides

Many examples define default variables at the top (like `voltage = 5.0`). You can override these when running:

    script run psu_dmm_test voltage=3.3 label=v3v3

This sets `voltage` to 3.3 and `label` to "v3v3" before running the script. The log entry will use your custom label:

    Label      Value       Unit   Source
    psu_v      3.298176    V      psu1
    v3v3       3.300122    V      dmm1

## Walkthrough: psu_dmm_test

This is the simplest example. Here is what each line does:

    voltage = 5.0                    # default voltage (overridable)
    label = vtest                    # default label (overridable)

    print "=== PSU/DMM Voltage Test ==="
    print "Target: {voltage}V"       # prints with variable substitution

    psu1 chan 1 on                   # enable PSU output
    psu1 set 1 {voltage}            # set PSU to target voltage
    sleep 0.5                        # wait 500ms for output to settle

    psu_v = psu1 meas v unit=V      # measure PSU's own output
    dmm1 config vdc                  # configure DMM for DC voltage
    {label} = dmm1 meas unit=V      # measure with DMM, use custom label

    print "=== Test complete ==="
    log print                        # show all measurements

After running, you can compute the error between PSU setpoint and DMM reading:

<!-- doc-test: skip reason="depends on the vtest label recorded by the preceding script" -->

    calc error = {vtest} - 5.0 unit=V
    calc error_pct = ({vtest} - 5.0) / 5.0 * 100 unit=%

## Walkthrough: voltage_sweep

This example sweeps through multiple voltages and records the DMM reading at each step:

    examples load voltage_sweep
    script run voltage_sweep

What it does:
1. Turns on PSU channel 1
2. Configures the DMM for DC voltage
3. For each voltage in the list (1.0, 2.0, 3.3, 5.0, 9.0, 12.0):
   - Sets the PSU to that voltage
   - Waits 500ms for settling
   - Records the DMM reading as `v_1.0`, `v_2.0`, etc.
4. Turns off the PSU
5. Prints the log and saves to CSV

The log will have entries like:

    Label      Value       Unit   Source
    v_1.0      0.999847    V      dmm1
    v_2.0      1.999623    V      dmm1
    v_3.3      3.299814    V      dmm1
    v_5.0      4.999952    V      dmm1
    v_9.0      8.999431    V      dmm1
    v_12.0     11.999684   V      dmm1

## Modifying an Example

To customize an example, edit it after loading:

    examples load psu_dmm_test
    script edit psu_dmm_test

This opens the script in your system text editor. Make changes, save, and close. Then run:

    script run psu_dmm_test

## Saving Custom Scripts

If you modify an example and want to keep it:

    script save

This writes all in-memory scripts to the scripts directory as `.scpi` files. They will be automatically loaded next time you start the REPL.

## Try It

1. Launch mock mode: `scpi-repl --mock`
2. Load and run the psu_dmm_test: `examples load psu_dmm_test` then `script run psu_dmm_test`
3. Run it again with different parameters: `script run psu_dmm_test voltage=3.3 label=v3v3`
4. Load the voltage_sweep: `examples load voltage_sweep` then `script run voltage_sweep`
5. View the CSV output: `log save sweep_results.csv`
6. Try the syntax_reference example to see every scripting feature: `examples load syntax_reference` then `script run syntax_reference`
