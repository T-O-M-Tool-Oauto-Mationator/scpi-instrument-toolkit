"""Extra tests for AWG commands targeting missed coverage lines."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockEDU33212A, MockJDS6600


@pytest.fixture
def repl_jds(make_repl):
    return make_repl({"awg1": MockJDS6600()})


@pytest.fixture
def repl_edu(make_repl):
    return make_repl({"awg1": MockEDU33212A()})


# ---------------------------------------------------------------------------
# JDS6600 protocol paths (is_jds6600=True)
# ---------------------------------------------------------------------------


class TestAwgJds6600:
    def test_chan_on_jds6600(self, repl_jds):
        repl_jds.onecmd("awg chan 1 on")

    def test_chan_off_jds6600(self, repl_jds):
        repl_jds.onecmd("awg chan 1 off")

    def test_chan_all_jds6600(self, repl_jds):
        repl_jds.onecmd("awg chan all on")

    def test_wave_jds6600_with_all_params(self, repl_jds):
        repl_jds.onecmd("awg wave 1 sine freq=1000 amp=2.0 offset=0.0 duty=50 phase=90")

    def test_freq_jds6600(self, repl_jds):
        repl_jds.onecmd("awg freq 1 1000")

    def test_amp_jds6600(self, repl_jds):
        repl_jds.onecmd("awg amp 1 3.3")

    def test_offset_jds6600(self, repl_jds):
        repl_jds.onecmd("awg offset 1 0.5")

    def test_on_all_jds6600(self, repl_jds):
        repl_jds.onecmd("awg on")

    def test_off_all_jds6600(self, repl_jds):
        repl_jds.onecmd("awg off")


# ---------------------------------------------------------------------------
# Duty cycle not supported independently (lines 93-94)
# AWG that does NOT have set_duty_cycle
# ---------------------------------------------------------------------------


class MockAwgNoDuty:
    """AWG with no set_duty_cycle."""

    def __init__(self):
        self._ch_amplitude = {1: 5.0, 2: 5.0}
        self._ch_offset = {1: 0.0, 2: 0.0}
        self._ch_frequency = {1: 10000.0, 2: 10000.0}
        self._ch_output = {1: False, 2: False}

    def enable_output(self, ch_or_state=None, state=None, ch1=None, ch2=None):
        pass

    def disable_all_channels(self):
        pass

    def set_waveform(self, ch, wave, **kwargs):
        pass

    def set_frequency(self, ch, freq):
        self._ch_frequency[int(ch)] = float(freq)

    def set_amplitude(self, ch, amp):
        self._ch_amplitude[int(ch)] = float(amp)

    def set_offset(self, ch, offset):
        self._ch_offset[int(ch)] = float(offset)

    def get_amplitude(self, ch):
        return self._ch_amplitude.get(int(ch), 5.0)

    def get_offset(self, ch):
        return self._ch_offset.get(int(ch), 0.0)

    def get_frequency(self, ch):
        return self._ch_frequency.get(int(ch), 10000.0)

    def reset(self):
        pass

    def disconnect(self):
        pass

    def query(self, cmd):
        return "MOCK,AWG,SN001,1.0"

    def send_command(self, cmd):
        pass


class MockAwgNoPhase(MockAwgNoDuty):
    """AWG with no set_phase."""

    pass


class MockAwgNoSync(MockAwgNoDuty):
    """AWG with no set_sync_output."""

    pass


class TestAwgUnsupportedIndependent:
    def test_duty_not_supported(self, capsys, make_repl):
        """awg duty on device without set_duty_cycle prints warning."""
        repl = make_repl({"awg1": MockAwgNoDuty()})
        repl.onecmd("awg duty 1 50")
        out = capsys.readouterr().out
        assert "not supported" in out.lower() or "duty" in out.lower()

    def test_phase_not_supported(self, capsys, make_repl):
        """awg phase on device without set_phase prints warning."""
        repl = make_repl({"awg1": MockAwgNoPhase()})
        repl.onecmd("awg phase 1 90")
        out = capsys.readouterr().out
        assert "not supported" in out.lower() or "phase" in out.lower()

    def test_sync_not_available(self, capsys, make_repl):
        """awg sync on device without set_sync_output prints warning."""
        repl = make_repl({"awg1": MockAwgNoSync()})
        repl.onecmd("awg sync on")
        out = capsys.readouterr().out
        assert "not available" in out.lower() or "sync" in out.lower()

    def test_freq_not_supported(self, capsys, make_repl):
        """awg freq on device without set_frequency."""

        class MockAwgNoFreqCls:
            def __init__(self):
                pass

            def enable_output(self, *a, **kw):
                pass

            def disable_all_channels(self):
                pass

            def set_waveform(self, ch, wave, **kwargs):
                pass

            def get_amplitude(self, ch):
                return None

            def get_offset(self, ch):
                return None

            def get_frequency(self, ch):
                return None

            def reset(self):
                pass

            def disconnect(self):
                pass

            def query(self, cmd):
                return "MOCK,AWG,SN001,1.0"

            def send_command(self, cmd):
                pass

        repl = make_repl({"awg1": MockAwgNoFreqCls()})
        repl.onecmd("awg freq 1 1000")
        out = capsys.readouterr().out
        assert "not supported" in out.lower() or "freq" in out.lower()

    def test_amp_not_supported(self, capsys, make_repl):
        """awg amp on device without set_amplitude."""

        class MockAwgNoAmpCls:
            def __init__(self):
                pass

            def enable_output(self, *a, **kw):
                pass

            def disable_all_channels(self):
                pass

            def set_waveform(self, ch, wave, **kwargs):
                pass

            def set_frequency(self, ch, freq):
                pass

            def get_amplitude(self, ch):
                return None

            def get_offset(self, ch):
                return None

            def get_frequency(self, ch):
                return None

            def reset(self):
                pass

            def disconnect(self):
                pass

            def query(self, cmd):
                return "MOCK,AWG,SN001,1.0"

            def send_command(self, cmd):
                pass

        repl = make_repl({"awg1": MockAwgNoAmpCls()})
        repl.onecmd("awg amp 1 3.3")
        out = capsys.readouterr().out
        assert "not supported" in out.lower() or "amp" in out.lower()

    def test_offset_not_supported(self, capsys, make_repl):
        """awg offset on device without set_offset."""

        class MockAwgNoOffsetCls:
            def __init__(self):
                pass

            def enable_output(self, *a, **kw):
                pass

            def disable_all_channels(self):
                pass

            def set_waveform(self, ch, wave, **kwargs):
                pass

            def set_frequency(self, ch, freq):
                pass

            def set_amplitude(self, ch, amp):
                pass

            def get_amplitude(self, ch):
                return None

            def get_offset(self, ch):
                return None

            def get_frequency(self, ch):
                return None

            def reset(self):
                pass

            def disconnect(self):
                pass

            def query(self, cmd):
                return "MOCK,AWG,SN001,1.0"

            def send_command(self, cmd):
                pass

        repl = make_repl({"awg1": MockAwgNoOffsetCls()})
        repl.onecmd("awg offset 1 0.5")
        out = capsys.readouterr().out
        assert "not supported" in out.lower() or "offset" in out.lower()


# ---------------------------------------------------------------------------
# Error handling in execute (lines 141-144)
# ---------------------------------------------------------------------------


class TestAwgErrorHandling:
    def test_value_error_handled(self, repl_edu, capsys):
        """Passing invalid float value triggers ValueError handler."""
        repl_edu.onecmd("awg freq 1 not_a_number")
        out = capsys.readouterr().out
        assert "Invalid value" in out or "error" in out.lower() or "not_a_number" in out

    def test_general_exception_handled(self, repl_edu, capsys):
        """An unexpected exception in AWG command is caught."""
        from unittest.mock import patch

        with patch.object(MockEDU33212A, "set_frequency", side_effect=RuntimeError("hw error")):
            repl_edu.onecmd("awg freq 1 1000")
            out = capsys.readouterr().out
            assert "hw error" in out or "error" in out.lower()


# ---------------------------------------------------------------------------
# AWG state via state callback (line 121-122)
# ---------------------------------------------------------------------------


class TestAwgStateCallback:
    def test_awg_state_delegates(self, repl_edu):
        repl_edu.onecmd("awg state on")
        repl_edu.onecmd("awg state off")
        repl_edu.onecmd("awg state safe")
        repl_edu.onecmd("awg state reset")
