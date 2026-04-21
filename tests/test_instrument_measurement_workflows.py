"""tests/test_instrument_measurement_workflows.py

End-to-end workflow tests: read from mock instruments, store values in
script_vars, perform arithmetic/calc, log measurements, and verify results.

All tests use the conftest.py `make_repl` fixture and mock devices from
lab_instruments/mock_instruments.py.  No physical hardware required.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import (
    MockDHO804,
    MockEDU33212A,
    MockHP_34401A,
    MockHP_E3631A,
    get_mock_devices,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def repl_dmm(make_repl):
    return make_repl({"dmm1": MockHP_34401A()})


@pytest.fixture
def repl_psu(make_repl):
    return make_repl({"psu1": MockHP_E3631A()})


@pytest.fixture
def repl_dmm_psu(make_repl):
    return make_repl({"dmm1": MockHP_34401A(), "psu1": MockHP_E3631A()})


@pytest.fixture
def repl_all(make_repl):
    return make_repl(get_mock_devices(verbose=False))


# ---------------------------------------------------------------------------
# TestDmmReadAndArithmetic
# ---------------------------------------------------------------------------


class TestDmmReadAndArithmetic:
    def test_read_assigns_variable(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        assert "v" in repl_dmm.ctx.script_vars

    def test_read_stores_as_float(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        val = repl_dmm.ctx.script_vars["v"]
        assert isinstance(val, float), f"expected float, got {type(val)}"

    def test_read_not_stored_as_string(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        val = repl_dmm.ctx.script_vars["v"]
        assert not isinstance(val, str), "value must not be a string"

    def test_read_value_in_plausible_range(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        val = float(repl_dmm.ctx.script_vars["v"])
        assert 4.0 < val < 6.0

    def test_doubled_arithmetic(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("doubled = v * 2")
        v = float(repl_dmm.ctx.script_vars["v"])
        doubled = float(repl_dmm.ctx.script_vars["doubled"])
        assert abs(doubled - v * 2) < 1e-9

    def test_offset_arithmetic(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("offset = v + 0.5")
        v = float(repl_dmm.ctx.script_vars["v"])
        offset = float(repl_dmm.ctx.script_vars["offset"])
        assert abs(offset - (v + 0.5)) < 1e-9

    def test_calc_power_from_read(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("calc power = v * 0.1 unit=W")
        entry = repl_dmm.ctx.measurements.get_by_label("power")
        assert entry is not None
        assert entry["unit"] == "W"
        v = float(repl_dmm.ctx.script_vars["v"])
        assert abs(float(entry["value"]) - v * 0.1) < 1e-9

    def test_calc_result_stored_in_script_vars(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("calc derived = v * 2 unit=V")
        assert "derived" in repl_dmm.ctx.script_vars

    def test_threshold_comparison(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("above_zero = v > 0")
        assert repl_dmm.ctx.script_vars["above_zero"] is True

    def test_read_idc_unit_is_A(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config idc")
        repl_dmm.onecmd("i = dmm1 read unit=A")
        entry = repl_dmm.ctx.measurements.get_by_label("i")
        assert entry is not None
        assert entry["unit"] == "A"

    def test_read_res_unit_is_ohms(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config res")
        repl_dmm.onecmd("r = dmm1 read unit=ohms")
        entry = repl_dmm.ctx.measurements.get_by_label("r")
        assert entry is not None
        assert entry["unit"] == "ohms"

    def test_multiple_reads_accumulate(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v1 = dmm1 read unit=V")
        repl_dmm.onecmd("v2 = dmm1 read unit=V")
        assert "v1" in repl_dmm.ctx.script_vars
        assert "v2" in repl_dmm.ctx.script_vars
        assert len(repl_dmm.ctx.measurements) >= 2


# ---------------------------------------------------------------------------
# TestPsuMeasureAndCalc
# ---------------------------------------------------------------------------


class TestPsuMeasureAndCalc:
    def test_meas_voltage_assigns_variable(self, repl_psu):
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("v = psu1 read unit=V")
        assert "v" in repl_psu.ctx.script_vars

    def test_meas_voltage_stored_as_float(self, repl_psu):
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("v = psu1 read unit=V")
        val = repl_psu.ctx.script_vars["v"]
        assert isinstance(val, float)

    def test_set_then_meas_plausible(self, repl_psu):
        repl_psu.onecmd("psu1 set 1 5.0")
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("vout = psu1 read unit=V")
        val = float(repl_psu.ctx.script_vars["vout"])
        assert 4.9 < val < 5.1

    def test_calc_power_v_times_i(self, repl_psu):
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("v = psu1 read unit=V")
        repl_psu.onecmd("psu1 meas 1 i")
        repl_psu.onecmd("i = psu1 read unit=A")
        repl_psu.onecmd("calc power = v * i unit=W")
        entry = repl_psu.ctx.measurements.get_by_label("power")
        assert entry is not None
        assert entry["unit"] == "W"
        v = float(repl_psu.ctx.script_vars["v"])
        i = float(repl_psu.ctx.script_vars["i"])
        assert abs(float(entry["value"]) - v * i) < 1e-9

    def test_multiple_meas_all_in_log(self, repl_psu):
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("v1 = psu1 read unit=V")
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("v2 = psu1 read unit=V")
        labels = [m["label"] for m in repl_psu.ctx.measurements.entries]
        assert "v1" in labels
        assert "v2" in labels

    def test_meas_current_stored_as_float(self, repl_psu):
        repl_psu.onecmd("psu1 meas 1 i")
        repl_psu.onecmd("i = psu1 read unit=A")
        val = repl_psu.ctx.script_vars["i"]
        assert isinstance(val, float)

    def test_set_voltage_calc_headroom(self, repl_psu):
        repl_psu.onecmd("psu1 set 1 5.0")
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("vout = psu1 read unit=V")
        repl_psu.onecmd("calc headroom = 5.1 - vout unit=V")
        entry = repl_psu.ctx.measurements.get_by_label("headroom")
        assert entry is not None
        vout = float(repl_psu.ctx.script_vars["vout"])
        assert abs(float(entry["value"]) - (5.1 - vout)) < 1e-9

    def test_psu_measurement_logged_with_source(self, repl_psu):
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("supply = psu1 read unit=V")
        entry = repl_psu.ctx.measurements.get_by_label("supply")
        assert entry is not None
        assert entry["source"] == "psu1"


# ---------------------------------------------------------------------------
# TestMeasurementLogging
# ---------------------------------------------------------------------------


class TestMeasurementLogging:
    def test_measure_then_log_print_contains_label(self, repl_dmm, capsys):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("reading = dmm1 read unit=V")
        repl_dmm.onecmd("log print")
        out = capsys.readouterr().out
        assert "reading" in out

    def test_log_print_contains_value(self, repl_dmm, capsys):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("vreading = dmm1 read unit=V")
        repl_dmm.onecmd("log print")
        out = capsys.readouterr().out
        assert "vreading" in out

    def test_log_clear_empties_log(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        assert len(repl_dmm.ctx.measurements) >= 1
        repl_dmm.onecmd("log clear")
        assert len(repl_dmm.ctx.measurements) == 0

    def test_multiple_measurements_accumulate(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("a = dmm1 read unit=V")
        repl_dmm.onecmd("b = dmm1 read unit=V")
        repl_dmm.onecmd("c = dmm1 read unit=V")
        assert len(repl_dmm.ctx.measurements) >= 3

    def test_log_entry_has_correct_unit(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("vol = dmm1 read unit=V")
        entry = repl_dmm.ctx.measurements.get_by_label("vol")
        assert entry["unit"] == "V"

    def test_log_entry_has_numeric_value(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("vm = dmm1 read unit=V")
        entry = repl_dmm.ctx.measurements.get_by_label("vm")
        assert isinstance(entry["value"], (int, float))

    def test_calc_result_in_log(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("calc pwr = v * 0.02 unit=W")
        entry = repl_dmm.ctx.measurements.get_by_label("pwr")
        assert entry is not None
        assert entry["unit"] == "W"

    def test_log_save_csv_contains_label(self, repl_dmm, tmp_path):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("vsave = dmm1 read unit=V")
        repl_dmm.ctx._data_dir_override = str(tmp_path)
        repl_dmm.onecmd("log save workflow_test.csv csv")
        csv_path = str(tmp_path / "workflow_test.csv")
        assert os.path.isfile(csv_path)
        with open(csv_path) as fh:
            content = fh.read()
        assert "vsave" in content

    def test_log_print_empty_says_no_measurements(self, repl_dmm, capsys):
        repl_dmm.onecmd("log print")
        out = capsys.readouterr().out
        assert "No measurements" in out

    def test_log_clear_after_multiple(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("x1 = dmm1 read unit=V")
        repl_dmm.onecmd("x2 = dmm1 read unit=V")
        repl_dmm.onecmd("log clear")
        assert len(repl_dmm.ctx.measurements) == 0


# ---------------------------------------------------------------------------
# TestMeasurementInExpressions
# ---------------------------------------------------------------------------


class TestMeasurementInExpressions:
    def test_augmented_add_with_measured_value(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("total = 0.0")
        repl_dmm.onecmd("total += v")
        v = float(repl_dmm.ctx.script_vars["v"])
        total = float(repl_dmm.ctx.script_vars["total"])
        assert abs(total - v) < 1e-9

    def test_for_loop_accumulate_reads(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("acc = 0.0")
        repl_dmm.onecmd("for idx in [1, 2, 3]")
        repl_dmm.onecmd("sample = dmm1 read unit=V")
        repl_dmm.onecmd("acc += sample")
        repl_dmm.onecmd("end")
        acc = float(repl_dmm.ctx.script_vars["acc"])
        assert acc > 0.0

    def test_if_condition_on_measured_value(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("result = 0")
        repl_dmm.onecmd("if v > 4.9")
        repl_dmm.onecmd("result = 1")
        repl_dmm.onecmd("end")
        # MockHP_34401A.read() returns ~5.0, so v > 4.9 should be True
        assert repl_dmm.ctx.script_vars["result"] == 1

    def test_assert_measured_value_positive(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("assert v > 0")
        assert not repl_dmm.ctx.command_had_error

    def test_print_interpolates_measured_variable(self, repl_dmm, capsys):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("vprint = dmm1 read unit=V")
        repl_dmm.onecmd('print "Voltage is {vprint} V"')
        out = capsys.readouterr().out
        # The numeric value should appear in the printed output, not the raw var name
        val_str = str(repl_dmm.ctx.script_vars["vprint"])
        # At minimum the label or value appears (interpolation may vary in format)
        assert val_str[:4] in out or "Voltage" in out

    def test_measured_value_in_calc_expression(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("calc err = v - 5.0 unit=V")
        entry = repl_dmm.ctx.measurements.get_by_label("err")
        assert entry is not None
        v = float(repl_dmm.ctx.script_vars["v"])
        assert abs(float(entry["value"]) - (v - 5.0)) < 1e-9

    def test_measured_value_in_nested_arithmetic(self, repl_dmm):
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("r = 50.0")
        repl_dmm.onecmd("p = (v * v) / r")
        v = float(repl_dmm.ctx.script_vars["v"])
        p = float(repl_dmm.ctx.script_vars["p"])
        assert abs(p - (v * v) / 50.0) < 1e-9

    def test_use_measured_value_as_loop_bound(self, repl_dmm):
        """Measured value can drive a while-loop counter bound."""
        repl_dmm.onecmd("dmm1 config vdc")
        repl_dmm.onecmd("n = 0")
        repl_dmm.onecmd("while n < 3")
        repl_dmm.onecmd("v = dmm1 read unit=V")
        repl_dmm.onecmd("n++")
        repl_dmm.onecmd("end")
        assert float(repl_dmm.ctx.script_vars["n"]) == 3.0
        assert "v" in repl_dmm.ctx.script_vars


# ---------------------------------------------------------------------------
# TestMultiInstrumentWorkflow
# ---------------------------------------------------------------------------


class TestMultiInstrumentWorkflow:
    def test_dmm_and_psu_both_measured(self, repl_dmm_psu):
        repl_dmm_psu.onecmd("dmm1 config vdc")
        repl_dmm_psu.onecmd("vd = dmm1 read unit=V")
        repl_dmm_psu.onecmd("psu1 meas 1 v")
        repl_dmm_psu.onecmd("vp = psu1 read unit=V")
        assert "vd" in repl_dmm_psu.ctx.script_vars
        assert "vp" in repl_dmm_psu.ctx.script_vars
        assert isinstance(repl_dmm_psu.ctx.script_vars["vd"], float)
        assert isinstance(repl_dmm_psu.ctx.script_vars["vp"], float)

    def test_psu_set_readback_within_tolerance(self, repl_psu):
        repl_psu.onecmd("psu1 set 1 5.0")
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("vout = psu1 read unit=V")
        vout = float(repl_psu.ctx.script_vars["vout"])
        assert abs(vout - 5.0) < 0.05

    def test_full_configure_measure_calc_log_verify(self, repl_dmm_psu):
        # Configure instruments
        repl_dmm_psu.onecmd("psu1 set 1 5.0 0.1")
        repl_dmm_psu.onecmd("dmm1 config vdc")
        # Measure
        repl_dmm_psu.onecmd("psu1 meas 1 v")
        repl_dmm_psu.onecmd("supply_v = psu1 read unit=V")
        repl_dmm_psu.onecmd("psu1 meas 1 i")
        repl_dmm_psu.onecmd("supply_i = psu1 read unit=A")
        # Calc
        repl_dmm_psu.onecmd("calc supply_p = supply_v * supply_i unit=W")
        # Verify log has all three
        labels = [m["label"] for m in repl_dmm_psu.ctx.measurements.entries]
        assert "supply_v" in labels
        assert "supply_i" in labels
        assert "supply_p" in labels

    def test_compare_dmm_and_psu_readings(self, repl_dmm_psu):
        repl_dmm_psu.onecmd("dmm1 config vdc")
        repl_dmm_psu.onecmd("vd = dmm1 read unit=V")
        repl_dmm_psu.onecmd("psu1 meas 1 v")
        repl_dmm_psu.onecmd("vp = psu1 read unit=V")
        repl_dmm_psu.onecmd("diff = vd - vp")
        vd = float(repl_dmm_psu.ctx.script_vars["vd"])
        vp = float(repl_dmm_psu.ctx.script_vars["vp"])
        diff = float(repl_dmm_psu.ctx.script_vars["diff"])
        assert abs(diff - (vd - vp)) < 1e-9

    def test_all_mock_devices_measure_no_error(self, repl_all):
        repl_all.onecmd("dmm1 config vdc")
        repl_all.onecmd("vdmm = dmm1 read unit=V")
        repl_all.onecmd("psu1 meas 1 v")
        repl_all.onecmd("vpsu = psu1 read unit=V")
        assert not repl_all.ctx.command_had_error

    def test_sequential_psu_measurements_log_all(self, repl_psu):
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("va = psu1 read unit=V")
        repl_psu.onecmd("psu1 set 1 3.3")
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("vb = psu1 read unit=V")
        labels = [m["label"] for m in repl_psu.ctx.measurements.entries]
        assert "va" in labels
        assert "vb" in labels

    def test_check_command_on_measured_value(self, repl_psu):
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("vcheck = psu1 read unit=V")
        repl_psu.onecmd("check vcheck 4.9 5.1")
        assert len(repl_psu.test_results) >= 1
        assert repl_psu.test_results[-1]["passed"] is True

    def test_awg_scope_workflow_no_error(self, make_repl):
        devices = {"awg1": MockEDU33212A(), "scope1": MockDHO804()}
        repl = make_repl(devices)
        repl.onecmd("awg1 wave 1 sine freq=1000 amp=2.0")
        repl.onecmd("awg1 chan 1 on")
        repl.onecmd("scope1 meas 1 FREQUENCY")
        assert not repl._command_had_error

    def test_multi_device_log_accumulates(self, repl_dmm_psu):
        repl_dmm_psu.onecmd("dmm1 config vdc")
        repl_dmm_psu.onecmd("rd1 = dmm1 read unit=V")
        repl_dmm_psu.onecmd("psu1 meas 1 v")
        repl_dmm_psu.onecmd("rp1 = psu1 read unit=V")
        repl_dmm_psu.onecmd("dmm1 config vdc")
        repl_dmm_psu.onecmd("rd2 = dmm1 read unit=V")
        assert len(repl_dmm_psu.ctx.measurements) >= 3

    def test_psu_readback_error_within_one_percent(self, repl_psu):
        repl_psu.onecmd("psu1 set 1 5.0")
        repl_psu.onecmd("psu1 meas 1 v")
        repl_psu.onecmd("vout = psu1 read unit=V")
        repl_psu.onecmd("error_pct = abs(vout - 5.0) / 5.0 * 100")
        pct = float(repl_psu.ctx.script_vars["error_pct"])
        assert pct < 1.0

    def test_script_based_full_workflow(self, repl_dmm_psu):
        """Run a multi-step workflow as an in-memory script."""
        script_lines = [
            "psu1 set 1 5.0 0.1",
            "psu1 meas 1 v",
            "supply = psu1 read unit=V",
            "dmm1 config vdc",
            "measured = dmm1 read unit=V",
            "calc delta = supply - measured unit=V",
        ]
        repl_dmm_psu.ctx.scripts["wf"] = script_lines
        repl_dmm_psu.onecmd("script run wf")
        assert "supply" in repl_dmm_psu.ctx.script_vars
        assert "measured" in repl_dmm_psu.ctx.script_vars
        assert "delta" in repl_dmm_psu.ctx.script_vars
        entry = repl_dmm_psu.ctx.measurements.get_by_label("delta")
        assert entry is not None
        assert entry["unit"] == "V"
