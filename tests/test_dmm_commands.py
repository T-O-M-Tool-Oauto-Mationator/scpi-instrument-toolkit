"""Automated tests for DMM REPL commands using mock instruments."""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockHP_34401A, MockXDM1041


def make_repl(devices):
    """Create an InstrumentRepl with mock devices pre-loaded."""
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
    devices = {"dmm1": MockHP_34401A()}
    return make_repl(devices)


class TestDmmConfig:
    def test_config_vdc(self, repl):
        repl.onecmd("dmm config vdc")

    def test_config_vac(self, repl):
        repl.onecmd("dmm config vac")

    def test_config_idc(self, repl):
        repl.onecmd("dmm config idc")

    def test_config_res(self, repl):
        repl.onecmd("dmm config res")

    def test_config_freq(self, repl):
        repl.onecmd("dmm config freq")

    def test_config_cont(self, repl):
        repl.onecmd("dmm config cont")

    def test_config_diode(self, repl):
        repl.onecmd("dmm config diode")


class TestDmmRead:
    def test_read(self, repl):
        repl.onecmd("dmm read")


class TestDmmMeasure:
    def test_meas_vdc(self, repl):
        repl.onecmd("dmm meas vdc")

    def test_meas_res(self, repl):
        repl.onecmd("dmm meas res")

    def test_meas_freq(self, repl):
        repl.onecmd("dmm meas freq")


class TestDmmMeasStore:
    def test_meas_store(self, repl):
        repl.onecmd("dmm config vdc")
        repl.onecmd("dmm meas_store test_v unit=V")
        assert len(repl.measurements) == 1

    def test_meas_store_with_scale(self, repl):
        repl.onecmd("dmm config vdc")
        repl.onecmd("dmm meas_store test_mv scale=1000 unit=mV")
        assert len(repl.measurements) == 1


class TestDmmFetch:
    def test_fetch(self, repl):
        repl.onecmd("dmm fetch")


class TestDmmBeep:
    def test_beep(self, repl):
        repl.onecmd("dmm beep")


class TestDmmDisplay:
    def test_display_on(self, repl):
        repl.onecmd("dmm display on")

    def test_display_off(self, repl):
        repl.onecmd("dmm display off")


class TestDmmText:
    def test_text(self, repl):
        repl.onecmd("dmm text HELLO")


class TestDmmState:
    def test_state_safe(self, repl):
        repl.onecmd("dmm state safe")

    def test_state_reset(self, repl):
        repl.onecmd("dmm state reset")


class TestDmmHelp:
    def test_help_no_args(self, repl):
        repl.onecmd("dmm")

    def test_unknown_cmd(self, repl):
        repl.onecmd("dmm nonexistent")
