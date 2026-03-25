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
    repl._scan_done.set()
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
