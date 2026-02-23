"""Automated tests for AWG REPL commands using mock instruments."""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockEDU33212A, MockJDS6600


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
    devices = {"awg1": MockEDU33212A()}
    return make_repl(devices)


class TestAwgChannel:
    def test_chan_on(self, repl):
        repl.onecmd("awg chan 1 on")

    def test_chan_off(self, repl):
        repl.onecmd("awg chan 1 off")

    def test_chan_all_off(self, repl):
        repl.onecmd("awg chan all off")


class TestAwgWaveform:
    def test_wave_sine(self, repl):
        repl.onecmd("awg wave 1 sine freq=1000 amp=2.0")

    def test_wave_square(self, repl):
        repl.onecmd("awg wave 1 square freq=500 duty=25")

    def test_wave_ramp(self, repl):
        repl.onecmd("awg wave 1 ramp freq=100")

    def test_wave_all(self, repl):
        repl.onecmd("awg wave all sine freq=1000")


class TestAwgParameters:
    def test_freq(self, repl):
        repl.onecmd("awg freq 1 1000")

    def test_amp(self, repl):
        repl.onecmd("awg amp 1 3.3")

    def test_offset(self, repl):
        repl.onecmd("awg offset 1 1.65")

    def test_duty(self, repl):
        repl.onecmd("awg duty 1 25")

    def test_phase(self, repl):
        repl.onecmd("awg phase 1 180")


class TestAwgSync:
    def test_sync_on(self, repl):
        repl.onecmd("awg sync on")

    def test_sync_off(self, repl):
        repl.onecmd("awg sync off")


class TestAwgState:
    def test_state_on(self, repl):
        repl.onecmd("awg state on")

    def test_state_off(self, repl):
        repl.onecmd("awg state off")

    def test_state_safe(self, repl):
        repl.onecmd("awg state safe")

    def test_state_reset(self, repl):
        repl.onecmd("awg state reset")


class TestAwgHelp:
    def test_help_no_args(self, repl):
        repl.onecmd("awg")

    def test_unknown_cmd(self, repl):
        repl.onecmd("awg nonexistent")
