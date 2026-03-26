"""tests/test_integration.py — End-to-end REPL workflows using mock devices only.

All tests in this module are marked @pytest.mark.integration and require no
physical instruments. They exercise the full REPL command path using mock classes.
"""

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


class TestFullWorkflow_SMU:
    def test_smu_state_delegation(self, make_repl):
        from lab_instruments.mock_instruments import MockNI_PXIe_4139

        devices = {"smu": MockNI_PXIe_4139()}
        repl = make_repl(devices)
        # This exercises the delegation from 'smu state on' to shell.do_state('smu on')
        repl.onecmd("smu state on")
        assert not repl._command_had_error
        assert devices["smu"].get_output_state() is True

    def test_smu_set_and_meas(self, make_repl):
        from lab_instruments.mock_instruments import MockNI_PXIe_4139

        devices = {"smu": MockNI_PXIe_4139()}
        repl = make_repl(devices)
        repl.onecmd("smu set 5.0 0.01")
        repl.onecmd("smu meas v")
        assert not repl._command_had_error


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
