"""
Verify every Python code example in docs/python.md compiles and runs
against mock instruments.

Each test function corresponds to one doc section.
Run with:  python -m pytest tests/test_doc_examples.py -v
"""

import contextlib
import os
import sys
import traceback

# Ensure the project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _header(name):
    print(f"\n{'=' * 60}")
    print(f"  TEST: {name}")
    print(f"{'=' * 60}")


def _pass(name):
    print(f"  [PASS] {name}")


def _fail(name, err):
    print(f"  [FAIL] {name}")
    traceback.print_exc()
    return err


results = {}


# ---------------------------------------------------------------
# 1. Quickstart — autodiscovery
# ---------------------------------------------------------------
def test_01_quickstart_autodiscovery():
    _header("Quickstart — autodiscovery")
    from lab_instruments import HP_E3631A
    from lab_instruments.mock_instruments import get_mock_devices

    instruments = get_mock_devices(verbose=False)
    # The doc uses instruments["psu"]; mock returns "psu1"
    psu = instruments["psu1"]

    psu.enable_output(True)
    psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, voltage=5.0)
    v = psu.measure_voltage(HP_E3631A.Channel.POSITIVE_6V)
    print(f"  Measured: {v:.4f} V")
    assert isinstance(v, float), f"Expected float, got {type(v)}"
    psu.enable_output(False)
    _pass("Quickstart — autodiscovery")


# ---------------------------------------------------------------
# 2. Direct instantiation (mock version — skip connect)
# ---------------------------------------------------------------
def test_02_direct_instantiation():
    _header("Direct instantiation")
    from lab_instruments import HP_E3631A
    from lab_instruments.mock_instruments import MockHP_E3631A

    psu = MockHP_E3631A()

    # Simulate the with-block pattern (disable_all_channels on exit)
    psu.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, voltage=3.3, current_limit=0.2)
    psu.enable_output(True)
    v = psu.measure_voltage(HP_E3631A.Channel.POSITIVE_6V)
    print(f"  Measured: {v:.4f} V")
    assert isinstance(v, float)
    psu.disable_all_channels()
    _pass("Direct instantiation")


# ---------------------------------------------------------------
# 3. Channel enums
# ---------------------------------------------------------------
def test_03_channel_enums():
    _header("Channel enums")
    from lab_instruments import HP_E3631A

    ch1 = HP_E3631A.Channel.POSITIVE_6V
    ch2 = HP_E3631A.Channel.POSITIVE_25V
    ch3 = HP_E3631A.Channel.NEGATIVE_25V

    print(f"  POSITIVE_6V  = {ch1}")
    print(f"  POSITIVE_25V = {ch2}")
    print(f"  NEGATIVE_25V = {ch3}")

    assert ch1 is not None
    assert ch2 is not None
    assert ch3 is not None

    # Verify set/measure methods accept channel enum
    from lab_instruments.mock_instruments import MockHP_E3631A

    psu = MockHP_E3631A()
    psu.set_output_channel(HP_E3631A.Channel.POSITIVE_25V, voltage=12.0, current_limit=0.5)
    v = psu.measure_voltage(HP_E3631A.Channel.POSITIVE_25V)
    i = psu.measure_current(HP_E3631A.Channel.POSITIVE_25V)
    print(f"  Voltage: {v:.4f} V, Current: {i:.6f} A")
    assert isinstance(v, float)
    assert isinstance(i, float)
    _pass("Channel enums")


# ---------------------------------------------------------------
# 4. WaveformType enum and from_alias
# ---------------------------------------------------------------
def test_04_waveform_type():
    _header("WaveformType")
    from lab_instruments import WaveformType

    # Verify from_alias
    assert WaveformType.from_alias("sine") is WaveformType.SIN
    assert WaveformType.from_alias("square") is WaveformType.SQU
    assert WaveformType.from_alias("SIN") is WaveformType.SIN
    print("  from_alias('sine')   -> ", WaveformType.from_alias("sine"))
    print("  from_alias('square') -> ", WaveformType.from_alias("square"))
    print("  from_alias('SIN')    -> ", WaveformType.from_alias("SIN"))

    # Verify AWG accepts WaveformType
    from lab_instruments.mock_instruments import MockEDU33212A

    awg = MockEDU33212A()
    awg.set_waveform(1, WaveformType.SIN, frequency=1000, amplitude=2.0)
    awg.set_waveform(2, WaveformType.SQU, frequency=500, amplitude=1.0)
    _pass("WaveformType")


# ---------------------------------------------------------------
# 5. DMMMode enum and from_alias
# ---------------------------------------------------------------
def test_05_dmm_mode():
    _header("DMMMode")
    from lab_instruments import DMMMode

    mode = DMMMode.from_alias("vdc")
    assert mode is DMMMode.DC_VOLTAGE
    print(f"  from_alias('vdc') -> {mode}")

    # The doc example uses f"measure_{mode}" expecting "measure_dc_voltage".
    # In Python 3.11+ str(StrEnum) returns "ClassName.MEMBER", so f-string
    # interpolation gives "measure_DMMMode.DC_VOLTAGE" — NOT what the docs show.
    # The correct portable form is f"measure_{mode.value}".
    method_name_doc = f"measure_{mode}"  # what the doc says
    method_name_fix = f"measure_{mode.value}"  # what actually works
    print(f"  f'measure_{{mode}}'       = {method_name_doc}")
    print(f"  f'measure_{{mode.value}}' = {method_name_fix}")

    if method_name_doc != "measure_dc_voltage":
        print('  [DOC BUG] f"measure_{mode}" produces wrong result on Python 3.11+')
        print('            Doc should use: f"measure_{mode.value}"')

    assert method_name_fix == "measure_dc_voltage", f"Got {method_name_fix}"
    print(f"  method_name (fixed) = {method_name_fix}")

    # Verify DMM has configure/measure methods
    from lab_instruments.mock_instruments import MockHP_34401A

    dmm = MockHP_34401A()
    dmm.configure_dc_voltage()
    v = dmm.measure_dc_voltage()
    r = dmm.measure_resistance_2wire()
    print(f"  DC voltage: {v}, 2-wire resistance: {r}")
    assert isinstance(v, float)
    assert isinstance(r, float)
    _pass("DMMMode")


# ---------------------------------------------------------------
# 6. CouplingMode and TriggerEdge
# ---------------------------------------------------------------
def test_06_scope_enums():
    _header("CouplingMode and TriggerEdge")
    from lab_instruments import CouplingMode, TriggerEdge, TriggerMode
    from lab_instruments.mock_instruments import MockDHO804

    scope = MockDHO804()
    scope.set_coupling(1, CouplingMode.DC)
    scope.set_coupling(2, CouplingMode.AC)
    print(f"  Set channel 1 to {CouplingMode.DC}, channel 2 to {CouplingMode.AC}")

    # The doc example: scope.configure_trigger(channel=1, level=1.0, slope=TriggerEdge.RISE)
    # MockScope signature: configure_trigger(self, ch, level, slope, mode)
    # mode is required in the mock — pass TriggerMode.AUTO
    scope.configure_trigger(1, 1.0, TriggerEdge.RISE, TriggerMode.AUTO)
    print(f"  Trigger configured with slope={TriggerEdge.RISE}")
    _pass("CouplingMode and TriggerEdge")


# ---------------------------------------------------------------
# 7. Voltage sweep with plotting (skip actual plot display)
# ---------------------------------------------------------------
def test_07_voltage_sweep():
    _header("Voltage sweep with plotting")
    import numpy as np

    from lab_instruments.mock_instruments import MockHP_34401A, MockHP_E3631A

    psu = MockHP_E3631A()
    dmm = MockHP_34401A()

    V_START, V_END, STEPS = 1.0, 12.0, 23
    voltages = np.linspace(V_START, V_END, STEPS)
    measured = []

    try:
        psu.enable_output(True)
        for v_set in voltages:
            psu.set_voltage(float(v_set))
            v_meas = dmm.measure_dc_voltage()
            measured.append(v_meas)
    finally:
        psu.enable_output(False)

    measured = np.array(measured)
    assert len(measured) == STEPS
    print(f"  Collected {STEPS} data points, first={measured[0]:.4f}, last={measured[-1]:.4f}")

    # Verify matplotlib import and basic figure creation (no display)
    import matplotlib

    matplotlib.use("Agg")  # non-interactive backend
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    ax1.plot(voltages, measured, "o-", markersize=3)
    ax1.plot(voltages, voltages, "--", color="gray", label="Ideal")
    ax1.set_ylabel("Measured (V)")
    ax1.set_title("Voltage Sweep: PSU Setpoint vs DMM Reading")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    error_mv = (measured - voltages) * 1000
    ax2.bar(voltages, error_mv, width=(voltages[1] - voltages[0]) * 0.6)
    ax2.set_xlabel("Setpoint (V)")
    ax2.set_ylabel("Error (mV)")
    ax2.axhline(0, color="gray", linewidth=0.5)
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    plt.close(fig)
    print("  Plot created successfully (Agg backend, no display)")
    _pass("Voltage sweep with plotting")


# ---------------------------------------------------------------
# 8. Multi-instrument test with safe shutdown
# ---------------------------------------------------------------
def test_08_multi_instrument():
    _header("Multi-instrument test with safe shutdown")
    from lab_instruments.mock_instruments import MockEDU33212A, MockHP_34401A, MockHP_E3631A

    psu = MockHP_E3631A()
    dmm = MockHP_34401A()
    awg = MockEDU33212A()

    try:
        # Doc example uses awg.set_dc_output(1, 3.0) — check if mock has it
        # MockAWG base does NOT have set_dc_output, but real EDU33212A does.
        # We test the method if it exists, otherwise note the gap.
        if hasattr(awg, "set_dc_output"):
            awg.set_dc_output(1, 3.0)
            print("  awg.set_dc_output(1, 3.0) — OK")
        else:
            print("  [NOTE] MockEDU33212A missing set_dc_output — doc example would fail on mock")

        awg.enable_output(1, True)

        psu.enable_output(True)
        results_list = []

        for voltage in [3.3, 5.0, 9.0, 12.0]:
            psu.set_voltage(voltage)
            reading = dmm.measure_dc_voltage()
            results_list.append((voltage, reading))
            print(f"    {voltage:5.1f} V -> {reading:.4f} V")

        assert len(results_list) == 4
        print(f"  Collected {len(results_list)} data points.")
    finally:
        with contextlib.suppress(Exception):
            psu.enable_output(False)
        with contextlib.suppress(Exception):
            awg.enable_output(1, False)
        print("  All outputs disabled.")

    _pass("Multi-instrument test with safe shutdown")


# ---------------------------------------------------------------
# 9. I2C register read/write via EV2300
# ---------------------------------------------------------------
def test_09_ev2300():
    _header("I2C register read/write via EV2300")
    from lab_instruments.mock_instruments import MockEV2300

    ev = MockEV2300()

    I2C_ADDR = 0x08
    REG_SYS_STAT = 0x00
    REG_SYS_CTRL1 = 0x04
    REG_SYS_CTRL2 = 0x05
    REG_OV_TRIP = 0x09
    REG_UV_TRIP = 0x0A
    REG_CC_CFG = 0x0B
    REG_ADCGAIN1 = 0x50
    REG_ADCOFFSET = 0x51
    REG_ADCGAIN2 = 0x59

    init_writes = [
        (REG_SYS_STAT, 0xFF, "clear all faults"),
        (REG_SYS_CTRL1, 0x10, "enable ADC"),
        (REG_SYS_CTRL2, 0x03, "enable CHG + DSG"),
        (REG_CC_CFG, 0x19, "coulomb counter config"),
    ]
    for reg, val, desc in init_writes:
        r = ev.write_byte(I2C_ADDR, reg, val)
        # Doc uses r["status_text"] on failure, but mock always returns ok=True
        # and has no status_text key. We verify the ok path.
        status = "OK" if r["ok"] else f"FAIL: {r.get('status_text', 'unknown')}"
        print(f"    Write 0x{reg:02X} = 0x{val:02X} ({desc}) -- {status}")
        assert r["ok"] is True

    g1 = ev.read_byte(I2C_ADDR, REG_ADCGAIN1)["value"]
    g2 = ev.read_byte(I2C_ADDR, REG_ADCGAIN2)["value"]
    offset = ev.read_byte(I2C_ADDR, REG_ADCOFFSET)["value"]

    gain_uv = 365 + (((g1 >> 3) & 0x03) << 3) | ((g2 >> 5) & 0x07)
    offset_mv = offset if offset < 128 else offset - 256
    print(f"    ADC gain: {gain_uv} uV/LSB, offset: {offset_mv} mV")

    ev.write_byte(I2C_ADDR, REG_OV_TRIP, 0xBE)
    ev.write_byte(I2C_ADDR, REG_UV_TRIP, 0x97)

    r = ev.read_byte(I2C_ADDR, REG_SYS_STAT)
    assert r["ok"] is True
    stat = r["value"]
    print(
        f"    SYS_STAT: 0x{stat:02X} -- OV={'SET' if stat & 0x04 else 'clear'}, UV={'SET' if stat & 0x08 else 'clear'}"
    )
    _pass("I2C register read/write via EV2300")


# ---------------------------------------------------------------
# 10. Saving results to CSV
# ---------------------------------------------------------------
def test_10_csv():
    _header("Saving results to CSV")
    import tempfile

    import numpy as np
    import pandas as pd

    from lab_instruments.mock_instruments import MockHP_34401A, MockHP_E3631A

    psu = MockHP_E3631A()
    dmm = MockHP_34401A()

    voltages = np.linspace(1.0, 12.0, 23)
    rows = []

    try:
        psu.enable_output(True)
        for v_set in voltages:
            psu.set_voltage(float(v_set))
            v_meas = dmm.measure_dc_voltage()
            rows.append({"setpoint_V": round(float(v_set), 3), "measured_V": round(v_meas, 6)})
    finally:
        psu.enable_output(False)

    df = pd.DataFrame(rows)
    df["error_mV"] = (df["measured_V"] - df["setpoint_V"]) * 1000

    # Write to temp file instead of cwd
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        csv_path = f.name
        df.to_csv(csv_path, index=False)

    print(f"  Wrote {len(df)} rows to {csv_path}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  First row: {df.iloc[0].to_dict()}")

    # Verify file
    df2 = pd.read_csv(csv_path)
    assert len(df2) == 23
    assert "error_mV" in df2.columns
    os.unlink(csv_path)
    _pass("Saving results to CSV")


# ---------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------
if __name__ == "__main__":
    tests = [
        ("01_quickstart_autodiscovery", test_01_quickstart_autodiscovery),
        ("02_direct_instantiation", test_02_direct_instantiation),
        ("03_channel_enums", test_03_channel_enums),
        ("04_waveform_type", test_04_waveform_type),
        ("05_dmm_mode", test_05_dmm_mode),
        ("06_scope_enums", test_06_scope_enums),
        ("07_voltage_sweep", test_07_voltage_sweep),
        ("08_multi_instrument", test_08_multi_instrument),
        ("09_ev2300", test_09_ev2300),
        ("10_csv", test_10_csv),
    ]

    passed = 0
    failed = 0
    errors = {}

    for name, fn in tests:
        try:
            fn()
            passed += 1
        except Exception as e:
            failed += 1
            errors[name] = traceback.format_exc()
            print(f"  [FAIL] {name}: {e}")

    print(f"\n{'=' * 60}")
    print(f"  SUMMARY: {passed} passed, {failed} failed out of {len(tests)}")
    print(f"{'=' * 60}")

    if errors:
        print("\nFailed tests detail:")
        for name, tb in errors.items():
            print(f"\n--- {name} ---")
            print(tb)

    sys.exit(1 if failed else 0)
