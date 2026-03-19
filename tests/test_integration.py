"""tests/test_integration.py — End-to-end REPL workflows using mock devices only.

All tests in this module are marked @pytest.mark.integration and require no
physical instruments. They exercise the full REPL command path using mock classes.
"""

import csv

import pytest

from lab_instruments.mock_instruments import (
    MockDHO804,
    MockEDU33212A,
    MockHP_34401A,
    MockHP_E3631A,
    MockMPS6010H,
    get_mock_devices,
)

pytestmark = pytest.mark.integration


class TestFullWorkflow_PSU:
    def test_set_measure_store_check_pass(self, make_repl):
        devices = {"psu1": MockHP_E3631A()}
        repl = make_repl(devices)
        repl.onecmd("psu set 5.0 0.1")
        repl.onecmd("psu meas_store v vout unit=V")
        assert len(repl.measurements) == 1

    def test_check_passes(self, make_repl):
        devices = {"psu1": MockHP_E3631A()}
        repl = make_repl(devices)
        repl.onecmd("psu meas_store v vout unit=V")
        repl.onecmd("check vout 4.9 5.1")
        assert len(repl.test_results) == 1
        assert repl.test_results[-1]["passed"] is True

    def test_injected_out_of_range_fails(self, make_repl):
        devices = {"psu1": MockHP_E3631A()}
        repl = make_repl(devices)
        # Directly inject an out-of-range measurement
        repl.measurements.append({"label": "vbad", "value": 3.0, "unit": "V"})
        repl.onecmd("check vbad 4.9 5.1")
        assert len(repl.test_results) == 1
        assert repl.test_results[-1]["passed"] is False


class TestFullWorkflow_AWG:
    def test_wave_then_enable(self, make_repl):
        devices = {"awg1": MockEDU33212A()}
        repl = make_repl(devices)
        repl.onecmd("awg wave 1 sine freq=1000 amp=2.0")
        repl.onecmd("awg chan 1 on")
        assert not repl._command_had_error


class TestFullWorkflow_AWGScope:
    def test_wave_and_scope_measure(self, make_repl):
        devices = {"awg1": MockEDU33212A(), "scope1": MockDHO804()}
        repl = make_repl(devices)
        repl.onecmd("awg wave 1 sine freq=1000 amp=2.0")
        repl.onecmd("scope meas_store 1 FREQUENCY freq_out unit=Hz")
        assert len(repl.measurements) == 1


class TestFullWorkflow_DMM:
    def test_meas_store_and_check(self, make_repl):
        devices = {"dmm1": MockHP_34401A()}
        repl = make_repl(devices)
        repl.onecmd("dmm config vdc")
        repl.onecmd("dmm meas_store label unit=V")
        repl.onecmd("check label 4.9 5.1")
        assert len(repl.test_results) >= 1
        assert repl.test_results[-1]["passed"] is True


class TestFullWorkflow_SafetyLimits:
    def test_upper_limit_blocks_awg(self, make_repl):
        devices = {"awg1": MockEDU33212A()}
        repl = make_repl(devices)
        repl.onecmd("upper_limit awg vpeak 3.3")
        repl.onecmd("awg wave 1 sine amp=10.0")
        assert repl._command_had_error is True


class TestFullWorkflow_MultiDevice:
    def test_two_psus_independent_measurements(self, make_repl):
        devices = {
            "psu1": MockHP_E3631A(),
            "psu2": MockMPS6010H(),
        }
        repl = make_repl(devices)
        repl.onecmd("psu1 meas_store v p1 unit=V")
        repl.onecmd("psu2 meas_store v p2 unit=V")
        labels = [m["label"] for m in repl.measurements]
        assert "p1" in labels
        assert "p2" in labels


class TestFullWorkflow_Report:
    def test_accumulate_and_report(self, make_repl):
        devices = {"psu1": MockHP_E3631A()}
        repl = make_repl(devices)
        # Inject two measurements and check both
        repl.measurements.append({"label": "v1", "value": 5.0, "unit": "V"})
        repl.measurements.append({"label": "v2", "value": 3.3, "unit": "V"})
        repl.onecmd("check v1 4.9 5.1")
        repl.onecmd("check v2 3.2 3.4")
        assert len(repl.test_results) == 2
        # Print report without error
        repl.onecmd("report")


class TestFullWorkflow_AllMocks:
    def test_basic_command_per_device(self, make_repl):
        devices = get_mock_devices(verbose=False)
        repl = make_repl(devices)
        repl.onecmd("psu1 set 5.0")
        repl.onecmd("awg1 wave 1 sine freq=1000 amp=2.0")
        repl.onecmd("dmm1 config vdc")
        repl.onecmd("dmm1 meas_store reading unit=V")
        repl.onecmd("scope1 meas_store 1 FREQUENCY f_out unit=Hz")
        assert len(repl.measurements) >= 2


class TestTestParamCommand:
    """Tests for the test_param / log integration feature."""

    def test_param_registers_without_evaluating(self, make_repl):
        repl = make_repl({})
        repl.onecmd("test_param v_out 4500 5500 unit=mV")
        assert "v_out" in repl.test_params
        assert repl.test_params["v_out"]["min"] == 4500.0
        assert repl.test_params["v_out"]["max"] == 5500.0
        assert repl.test_results == []

    def test_param_pass_on_log_print(self, make_repl):
        repl = make_repl({})
        repl.measurements.append({"label": "vout", "value": 5000.0, "unit": "mV", "source": "test"})
        repl.onecmd("test_param vout 4500 5500 unit=mV")
        repl.onecmd("log print")
        assert repl.test_results[-1]["passed"] is True
        assert repl.test_results[-1]["label"] == "vout"

    def test_param_fail_on_log_print(self, make_repl):
        repl = make_repl({})
        repl.measurements.append({"label": "vout", "value": 3000.0, "unit": "mV", "source": "test"})
        repl.onecmd("test_param vout 4500 5500 unit=mV")
        repl.onecmd("log print")
        assert repl.test_results[-1]["passed"] is False

    def test_param_missing_measurement_is_fail(self, make_repl):
        repl = make_repl({})
        repl.onecmd("test_param ron_t1 0 50 unit=mOhm")
        repl.onecmd("log print")
        result = next(r for r in repl.test_results if r["label"] == "ron_t1")
        assert result["passed"] is False
        assert result["value"] is None

    def test_param_no_double_count_with_check(self, make_repl):
        repl = make_repl({})
        repl.measurements.append({"label": "vout", "value": 5.0, "unit": "V", "source": "test"})
        repl.onecmd("check vout 4.9 5.1")
        repl.onecmd("test_param vout 4.9 5.1 unit=V")
        repl.onecmd("log print")
        matching = [r for r in repl.test_results if r["label"] == "vout"]
        assert len(matching) == 1

    def test_log_clear_clears_test_params(self, make_repl):
        repl = make_repl({})
        repl.onecmd("test_param vout 4500 5500 unit=mV")
        assert repl.test_params != {}
        repl.onecmd("log clear")
        assert repl.test_params == {}

    def test_log_save_includes_passfail_columns(self, make_repl, tmp_path):
        repl = make_repl({})
        repl.measurements.append({"label": "vout", "value": 5000.0, "unit": "mV", "source": "test"})
        repl.onecmd("test_param vout 4500 5500 unit=mV")
        csv_path = str(tmp_path / "results.csv")
        repl._data_dir_override = str(tmp_path)
        repl.onecmd(f"log save {csv_path} csv")
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader if row.get("label") == "vout"]
        assert rows, "No vout row in CSV"
        assert rows[0]["pass_fail"] in ("PASS", "FAIL")
        assert "expected_min" in rows[0]
        assert "expected_max" in rows[0]

    def test_param_min_gte_max_sets_error_flag(self, make_repl):
        repl = make_repl({})
        repl._command_had_error = False
        repl.onecmd("test_param label 5.0 3.0")
        assert repl._command_had_error is True

    def test_param_overwrites_on_duplicate_label(self, make_repl):
        repl = make_repl({})
        repl.onecmd("test_param vout 0 10 unit=V")
        repl.onecmd("test_param vout 0 20 unit=V")
        assert repl.test_params["vout"]["max"] == 20.0

    def test_overall_verdict_all_pass(self, make_repl, capsys):
        repl = make_repl({})
        repl.measurements.append({"label": "v1", "value": 5.0, "unit": "V", "source": "test"})
        repl.measurements.append({"label": "v2", "value": 3.3, "unit": "V", "source": "test"})
        repl.onecmd("test_param v1 4.9 5.1 unit=V")
        repl.onecmd("test_param v2 3.2 3.4 unit=V")
        capsys.readouterr()
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "ALL TEST PARAMETERS PASSED" in out

    def test_overall_verdict_some_fail(self, make_repl, capsys):
        repl = make_repl({})
        repl.measurements.append({"label": "v1", "value": 5.0, "unit": "V", "source": "test"})
        repl.measurements.append({"label": "v2", "value": 9.9, "unit": "V", "source": "test"})
        repl.onecmd("test_param v1 4.9 5.1 unit=V")
        repl.onecmd("test_param v2 3.2 3.4 unit=V")
        capsys.readouterr()
        repl.onecmd("log print")
        out = capsys.readouterr().out
        assert "TEST PARAMETER(S) FAILED" in out
