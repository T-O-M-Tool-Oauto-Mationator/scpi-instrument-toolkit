"""Automated tests for PSU REPL commands using mock instruments."""
import pytest
import os
import sys
import random

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


class MockMultiChannelPSU(MockHP_E3631A):
    """Multi-channel PSU mock — set_voltage has a channel parameter."""

    def set_voltage(self, channel, v):
        pass

    def set_current_limit(self, channel, i):
        pass

    def measure_voltage(self, channel=None):
        return round(random.uniform(4.985, 5.015), 6)

    def measure_current(self, channel=None):
        return round(random.uniform(0.099, 0.101), 6)


@pytest.fixture
def repl():
    devices = {"psu1": MockHP_E3631A()}
    return make_repl(devices)


@pytest.fixture
def repl_multi():
    devices = {"psu1": MockMultiChannelPSU()}
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


class TestPsuMeasureMultiChannel:
    def test_meas_channel_v(self, repl_multi):
        repl_multi.onecmd("psu meas 1 v")

    def test_meas_channel_i(self, repl_multi):
        repl_multi.onecmd("psu meas 2 i")

    def test_meas_store_channel(self, repl_multi):
        repl_multi.onecmd("psu meas_store 1 v ch1_v unit=V")
        assert len(repl_multi.measurements) == 1

    def test_meas_store_channel_current(self, repl_multi):
        repl_multi.onecmd("psu meas_store 2 i ch2_i unit=A")
        assert len(repl_multi.measurements) == 1


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
