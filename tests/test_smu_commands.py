"""Tests for SMU REPL commands using MockNI_PXIe_4139."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockNI_PXIe_4139


def make_repl(devices):
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl()
    repl._scan_thread.join(timeout=5.0)
    repl._scan_done.wait(timeout=5.0)
    repl.devices = devices
    return repl


@pytest.fixture
def repl():
    devices = {"smu": MockNI_PXIe_4139()}
    return make_repl(devices)


class TestSmuOnOff:
    def test_on(self, repl):
        repl.onecmd("smu on")

    def test_off(self, repl):
        repl.onecmd("smu off")

    def test_on_off_sequence(self, repl):
        repl.onecmd("smu on")
        repl.onecmd("smu off")


class TestSmuSet:
    def test_set_voltage_only(self, repl):
        repl.onecmd("smu set 5.0")

    def test_set_voltage_and_current(self, repl):
        repl.onecmd("smu set 3.3 0.01")

    def test_set_zero(self, repl):
        repl.onecmd("smu set 0.0 0.001")

    def test_set_missing_args(self, repl, capsys):
        repl.onecmd("smu set")
        out = capsys.readouterr().out
        assert out != ""

    def test_set_negative_voltage(self, repl):
        repl.onecmd("smu set -5.0 0.1")


class TestSmuMeas:
    def test_meas_voltage(self, repl):
        repl.onecmd("smu meas v")

    def test_meas_voltage_long(self, repl):
        repl.onecmd("smu meas voltage")

    def test_meas_current(self, repl):
        repl.onecmd("smu meas i")

    def test_meas_current_long(self, repl):
        repl.onecmd("smu meas current")

    def test_meas_volt_alias(self, repl):
        repl.onecmd("smu meas volt")

    def test_meas_curr_alias(self, repl):
        repl.onecmd("smu meas curr")

    def test_meas_missing_arg(self, repl, capsys):
        repl.onecmd("smu meas")
        out = capsys.readouterr().out
        assert out != ""

    def test_meas_unknown_mode(self, repl, capsys):
        repl.onecmd("smu meas x")
        out = capsys.readouterr().out
        assert out != ""


class TestSmuMeasStore:
    def test_meas_store_voltage(self, repl):
        repl.onecmd("smu meas_store v vout")
        assert len(repl.measurements) == 1
        assert repl.measurements[0]["label"] == "vout"

    def test_meas_store_current(self, repl):
        repl.onecmd("smu meas_store i iout")
        assert len(repl.measurements) == 1
        assert repl.measurements[0]["label"] == "iout"

    def test_meas_store_with_unit(self, repl):
        repl.onecmd("smu meas_store v vout unit=mV")
        assert len(repl.measurements) == 1

    def test_meas_store_missing_args(self, repl, capsys):
        repl.onecmd("smu meas_store v")
        out = capsys.readouterr().out
        assert out != ""

    def test_meas_store_unknown_mode(self, repl, capsys):
        repl.onecmd("smu meas_store x label")
        out = capsys.readouterr().out
        assert out != ""


class TestSmuGet:
    def test_get(self, repl):
        repl.onecmd("smu get")


class TestSmuState:
    def test_state_on(self, repl):
        devices = repl.devices
        repl.onecmd("smu state on")
        assert not repl._command_had_error
        assert devices["smu"].get_output_state() is True

    def test_state_off(self, repl):
        devices = repl.devices
        repl.onecmd("smu state on")
        repl.onecmd("smu state off")
        assert not repl._command_had_error
        assert devices["smu"].get_output_state() is False

    def test_state_safe(self, repl):
        devices = repl.devices
        repl.onecmd("smu state on")
        repl.onecmd("smu state safe")
        assert not repl._command_had_error
        assert devices["smu"].get_output_state() is False

    def test_state_reset(self, repl):
        repl.onecmd("smu state reset")
        assert not repl._command_had_error

    def test_state_no_args_shows_help(self, repl, capsys):
        repl.onecmd("smu state")
        out = capsys.readouterr().out
        assert "state" in out.lower()
        assert not repl._command_had_error


class TestSmuHelp:
    def test_help_no_args(self, repl, capsys):
        repl.onecmd("smu")
        out = capsys.readouterr().out
        assert out != ""

    def test_unknown_cmd(self, repl, capsys):
        repl.onecmd("smu nonexistent_cmd")
        out = capsys.readouterr().out
        assert out != ""


class TestSmuSafety:
    def test_on_with_safety_limit(self, repl):
        """SMU on with a voltage safety limit that should be blocked."""
        repl.onecmd("upper_limit smu voltage 0.0")
        repl.onecmd("smu on")

    def test_set_with_safety_limit_exceeded(self, repl, capsys):
        """smu set exceeding safety limit should be rejected."""
        repl.onecmd("upper_limit smu voltage 3.0")
        repl.onecmd("smu set 5.0")
        out = capsys.readouterr().out
        assert out != ""


class TestSmuMeasVI:
    def test_no_arg_gives_vi(self, repl, capsys):
        # smu meas with no argument now gives atomic V+I output
        repl.onecmd("smu meas")
        out = capsys.readouterr().out
        assert "V=" in out
        assert "I=" in out

    def test_vi_subcommand(self, repl, capsys):
        repl.onecmd("smu meas vi")
        out = capsys.readouterr().out
        assert "V=" in out
        assert "I=" in out

    def test_v_still_works(self, repl, capsys):
        repl.onecmd("smu meas v")
        out = capsys.readouterr().out
        assert "V" in out

    def test_i_still_works(self, repl, capsys):
        repl.onecmd("smu meas i")
        out = capsys.readouterr().out
        assert "A" in out

    def test_compliance_annotation_when_set(self, repl, capsys):
        repl.devices["smu"]._set_mock_compliance(True)
        repl.onecmd("smu meas vi")
        out = capsys.readouterr().out
        assert "COMPLIANCE" in out

    def test_no_compliance_annotation_when_clear(self, repl, capsys):
        repl.devices["smu"]._set_mock_compliance(False)
        repl.onecmd("smu meas vi")
        out = capsys.readouterr().out
        assert "COMPLIANCE" not in out


class TestSmuCompliance:
    def test_not_in_compliance(self, repl, capsys):
        repl.devices["smu"]._set_mock_compliance(False)
        repl.onecmd("smu compliance")
        out = capsys.readouterr().out
        assert out != ""

    def test_in_compliance_shows_warning(self, repl, capsys):
        repl.devices["smu"]._set_mock_compliance(True)
        repl.onecmd("smu compliance")
        out = capsys.readouterr().out
        assert "COMPLIANCE" in out.upper()


class TestSmuSourceDelay:
    def test_set_source_delay(self, repl):
        repl.onecmd("smu source_delay 0.5")
        assert repl.devices["smu"]._source_delay == pytest.approx(0.5)

    def test_get_source_delay(self, repl, capsys):
        repl.devices["smu"]._source_delay = 0.25
        repl.onecmd("smu source_delay")
        out = capsys.readouterr().out
        assert "0.25" in out

    def test_source_delay_zero(self, repl):
        repl.onecmd("smu source_delay 0")
        assert repl.devices["smu"]._source_delay == pytest.approx(0.0)

    def test_source_delay_negative_shows_error(self, repl, capsys):
        repl.onecmd("smu source_delay -0.1")
        out = capsys.readouterr().out
        assert out != ""


class TestSmuSetMode:
    def test_set_mode_current(self, repl):
        repl.onecmd("smu set_mode current 0.05 5.0")
        dev = repl.devices["smu"]
        assert dev._output_mode == "current"
        assert dev._current_level == pytest.approx(0.05)
        assert dev._voltage_limit == pytest.approx(5.0)

    def test_set_mode_current_no_voltage_limit(self, repl):
        repl.onecmd("smu set_mode current 0.01")
        assert repl.devices["smu"]._output_mode == "current"

    def test_set_mode_voltage_switches_back(self, repl):
        repl.onecmd("smu set_mode current 0.05")
        repl.onecmd("smu set_mode voltage 3.3 0.1")
        dev = repl.devices["smu"]
        assert dev._output_mode == "voltage"
        assert dev._voltage == pytest.approx(3.3)

    def test_set_mode_missing_args_shows_help(self, repl, capsys):
        repl.onecmd("smu set_mode")
        out = capsys.readouterr().out
        assert out != ""

    def test_set_mode_unknown_mode_shows_warning(self, repl, capsys):
        repl.onecmd("smu set_mode dc 0.05")
        out = capsys.readouterr().out
        assert out != ""


class TestSmuAvg:
    def test_set_avg(self, repl):
        repl.onecmd("smu avg 10")
        assert repl.devices["smu"]._samples_to_average == 10

    def test_get_avg(self, repl, capsys):
        repl.devices["smu"]._samples_to_average = 5
        repl.onecmd("smu avg")
        out = capsys.readouterr().out
        assert "5" in out

    def test_avg_one(self, repl):
        repl.onecmd("smu avg 1")
        assert repl.devices["smu"]._samples_to_average == 1

    def test_avg_zero_shows_error(self, repl, capsys):
        repl.onecmd("smu avg 0")
        out = capsys.readouterr().out
        assert out != ""


class TestSmuTemp:
    def test_temp_shows_degrees(self, repl, capsys):
        repl.onecmd("smu temp")
        out = capsys.readouterr().out
        assert "degrees C" in out

    def test_temp_value_in_range(self, repl, capsys):
        repl.onecmd("smu temp")
        out = capsys.readouterr().out
        import re

        match = re.search(r"(\d+\.\d+)", out)
        assert match is not None
        val = float(match.group(1))
        assert 10.0 <= val <= 100.0
