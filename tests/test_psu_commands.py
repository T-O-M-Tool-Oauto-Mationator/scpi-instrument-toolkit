"""Automated tests for PSU REPL commands using mock instruments."""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockHP_E3631A, MockMPS6010H


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
    devices = {"psu1": MockHP_E3631A()}
    return make_repl(devices)


class TestPsuChannel:
    def test_chan_on(self, repl):
        repl.onecmd("psu chan 1 on")

    def test_chan_off(self, repl):
        repl.onecmd("psu chan 1 off")


class TestPsuSet:
    def test_set_voltage(self, repl):
        repl.onecmd("psu set 5.0")

    def test_set_voltage_current(self, repl):
        repl.onecmd("psu set 5.0 0.5")


class TestPsuMeasure:
    def test_meas_v(self, repl):
        repl.onecmd("psu meas v")

    def test_meas_i(self, repl):
        repl.onecmd("psu meas i")

    def test_meas_store(self, repl):
        repl.onecmd("psu meas_store v test_v unit=V")
        assert len(repl.measurements) == 1


class TestPsuGet:
    def test_get(self, repl):
        repl.onecmd("psu get")


class TestPsuTrack:
    def test_track_on(self, repl):
        repl.onecmd("psu track on")

    def test_track_off(self, repl):
        repl.onecmd("psu track off")


class TestPsuSaveRecall:
    def test_save(self, repl):
        repl.onecmd("psu save 1")

    def test_recall(self, repl):
        repl.onecmd("psu recall 1")


class TestPsuState:
    def test_state_on(self, repl):
        repl.onecmd("psu state on")

    def test_state_off(self, repl):
        repl.onecmd("psu state off")

    def test_state_safe(self, repl):
        repl.onecmd("psu state safe")

    def test_state_reset(self, repl):
        repl.onecmd("psu state reset")


class TestPsuHelp:
    def test_help_no_args(self, repl):
        repl.onecmd("psu")

    def test_unknown_cmd(self, repl):
        repl.onecmd("psu nonexistent")
