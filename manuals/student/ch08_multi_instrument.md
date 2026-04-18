# Chapter 8: Multi-Instrument Workflows

Real lab tests often involve multiple instruments working together. This chapter shows common multi-instrument patterns.

## Addressing Multiple Instruments

When you have multiple instruments of the same type, they are numbered:

    list
    # psu1: HP E3631A
    # psu2: Matrix MPS-6010H
    # dmm1: HP 34401A
    # dmm2: OWON XDM1041
    # scope1: Rigol DHO804

Address any instrument directly by prefixing its name:

<!-- doc-test: skip reason="reference example -- requires a multi-PSU / multi-DMM lab setup (psu2, dmm2)" -->

    psu1 set 1 5.0
    psu2 set 1 12.0
    dmm1 config vdc
    dmm2 config idc

Or use `use` to switch the active instrument for short commands:

    use psu1
    psu set 1 5.0       # acts on psu1

    use psu2
    psu set 1 12.0      # acts on psu2

## Pattern 1: PSU + DMM Voltage Verification

Verify that the PSU is outputting the correct voltage using an independent DMM measurement.

    # Set the PSU
    psu1 chan 1 on
    psu1 set 1 5.0
    sleep 0.5

    # Measure with both instruments
    psu_v = psu1 meas v unit=V
    dmm1 config vdc
    dmm_v = dmm1 meas unit=V

    # Compare
    calc error = psu_v - dmm_v unit=V
    calc error_pct = (psu_v - dmm_v) / psu_v * 100 unit=%
    print "PSU reads {psu_v} V, DMM reads {dmm_v} V"
    print "Error: {error_pct}%"

    log print

## Pattern 2: AWG + Scope Signal Check

Generate a waveform with the AWG and verify it on the scope.

    # Configure AWG
    awg1 chan 1 on
    awg1 wave 1 sine freq=1000 amp=2.0 offset=0
    sleep 0.5

    # Configure and capture on scope
    scope1 autoset
    sleep 1.0

    # Measure signal characteristics
    freq = scope1 meas 1 FREQUENCY unit=Hz
    pk2pk = scope1 meas 1 PK2PK unit=V

    # Verify
    calc freq_error = (freq - 1000) / 1000 * 100 unit=%
    calc amp_error = (pk2pk - 2.0) / 2.0 * 100 unit=%

    print "Frequency: {freq} Hz (error: {freq_error}%)"
    print "Amplitude: {pk2pk} Vpp (error: {amp_error}%)"

    # Cleanup
    awg1 chan 1 off
    log print

## Pattern 3: PSU Voltage Sweep with DMM Readback

Sweep the PSU through a range of voltages and record DMM readings at each step.

    log clear
    psu1 chan 1 on
    dmm1 config vdc

    for v 1.0 2.0 3.3 5.0 9.0 12.0
      psu1 set 1 {v}
      sleep 0.5
      psu_v = psu1 meas v unit=V
      dmm_v = dmm1 meas unit=V
      calc error_{v} = psu_v - dmm_v unit=V
    end

    psu1 chan 1 off
    log print
    log save voltage_sweep.csv

## Pattern 4: AWG Frequency Sweep with Scope Measurement

Characterize frequency response by sweeping the AWG and measuring on the scope.

    awg1 chan 1 on
    awg1 wave 1 sine amp=2.0 offset=0

    for f 100 500 1000 5000 10000 50000
      awg1 freq 1 {f}
      sleep 0.5
      freq_{f} = scope1 meas 1 FREQUENCY unit=Hz
      pk2pk_{f} = scope1 meas 1 PK2PK unit=V
    end

    awg1 chan 1 off
    log print
    log save freq_response.csv

## Pattern 5: Power Measurement (PSU + DMM)

Measure both voltage and current to compute power dissipation.

    psu1 chan 1 on
    psu1 set 1 5.0

    # Use PSU for voltage, DMM for current
    v = psu1 meas v unit=V
    dmm1 config idc
    i = dmm1 meas unit=A

    calc power = v * i unit=W
    calc resistance = v / i unit=ohms

    print "V = {v} V, I = {i} A"
    print "P = {power} W, R = {resistance} ohms"
    log print

## Pattern 6: Dual-Supply Configuration

Set up positive and negative rails for an op-amp circuit.

<!-- doc-test: skip reason="requires dual-PSU lab setup; psu1 track + psu2 not present in single-PSU mock" -->

    # Positive rail
    psu1 chan 1 on
    psu1 set 1 12.0

    # Negative rail (if using tracking mode)
    psu1 track on          # channels mirror: +12V and -12V

    # Or use two separate PSUs
    psu1 chan 1 on
    psu1 set 1 12.0        # +12V rail
    psu2 chan 1 on
    psu2 set 1 12.0        # -12V rail (wire negative)

    # Verify both rails
    pos_v = psu1 meas v unit=V
    neg_v = psu2 meas v unit=V
    print "Positive rail: {pos_v} V"
    print "Negative rail: {neg_v} V"

## Pattern 7: Full V&V Test Sequence

A complete validation test that uses multiple instruments:

<!-- doc-test: skip reason="requires 2x DMM lab setup and a real DUT at 3.3 V (check fails against unconfigured mock)" -->

    set -e
    log clear

    print "=== V&V Test: DUT Power-Up Sequence ==="

    # Step 1: Power up DUT
    psu1 chan 1 on
    psu1 set 1 3.3 0.5
    sleep 1.0

    # Step 2: Verify supply voltage
    dmm1 config vdc
    v_supply = dmm1 meas unit=V
    check v_supply 3.135 3.465 "supply within 5% of 3.3V"

    # Step 3: Check quiescent current
    dmm2 config idc
    i_quiescent = dmm2 meas unit=A
    check i_quiescent 0 0.050 "quiescent current < 50mA"

    # Step 4: Apply test signal
    awg1 chan 1 on
    awg1 wave 1 sine freq=1000 amp=1.0 offset=1.65
    sleep 0.5

    # Step 5: Verify output
    scope1 autoset
    sleep 1.0
    out_freq = scope1 meas 1 FREQUENCY unit=Hz
    out_pk2pk = scope1 meas 2 PK2PK unit=V

    # Step 6: Cleanup and report
    awg1 chan 1 off
    psu1 chan 1 off

    log print
    log report
    log save vv_test_results.csv
    print "=== Test Complete ==="

## Safe Shutdown

Always shut down instruments at the end of a test:

    all off          # disables all outputs on all instruments

Or shut down individually:

<!-- doc-test: skip reason="references psu2 which isn't in the single-PSU mock" -->

    psu1 chan 1 off
    awg1 off
    psu2 chan 1 off

## Try It

1. In mock mode, run Pattern 1 (PSU + DMM verification)
2. Run Pattern 2 (AWG + scope signal check)
3. Try the full V&V test sequence
4. Export results and review the CSV
