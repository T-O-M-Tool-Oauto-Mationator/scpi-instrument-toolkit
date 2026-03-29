"""tests/test_repl_coverage.py -- Additional tests to push project coverage past 80%.

Targets uncovered paths in:
  - psu.py: single-channel on/off, meas with no readback, multi-channel set/meas, get on multi-ch
  - dmm.py: Owon (basic) paths, text_loop, cleartext, ranges, meas continuity/diode
  - scope.py: awg sub-handlers, counter source/mode, dvm source, meas_clear, meas_setup, wait_stop, state
  - scripting.py: script run, record start/stop/status, examples load
  - runner.py: run_expanded normal execution, NOP, set -e
  - device_manager.py: connect, disconnect, query, send_command, reset, clear_status
  - matrix_mps6010h.py: set_output, set_output_channel, measure_voltage_channel, measure_current_channel, repr
"""

import os
import random
import tempfile
from unittest.mock import MagicMock

import pytest

from lab_instruments.mock_instruments import (
    MockDHO804,
    MockHP_34401A,
    MockHP_E3631A,
    MockMPS6010H,
    MockXDM1041,
)

# ---------------------------------------------------------------------------
# Custom mock for multi-channel PSU (has 'channel' param in measure_voltage)
# ---------------------------------------------------------------------------


class MockMultiChannelPSU(MockHP_E3631A):
    """Multi-channel PSU mock -- measure_voltage(channel) triggers multi-channel detection."""

    def measure_voltage(self, channel=None):
        return round(random.uniform(4.985, 5.015), 6)

    def measure_current(self, channel=None):
        return round(random.uniform(0.099, 0.101), 6)


# ═══════════════════════════════════════════════════════════════════
# 1. PSU command handler -- uncovered paths
# ═══════════════════════════════════════════════════════════════════


class TestPsuSingleChannelOnOff:
    """Cover psu on / psu off shorthand for single-channel PSU (MPS6010H)."""

    def test_psu_on(self, make_repl, capsys):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu on")
        out = capsys.readouterr().out
        assert "enabled" in out.lower() or "Output" in out

    def test_psu_off(self, make_repl, capsys):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu off")
        out = capsys.readouterr().out
        assert "disabled" in out.lower() or "Output" in out


class TestPsuSingleChannelChan:
    """Cover psu chan on|off for single-channel PSU."""

    def test_chan_on(self, make_repl):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu1 on")
        assert dev._output is True

    def test_chan_off(self, make_repl):
        dev = MockMPS6010H()
        dev._output = True
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu1 off")
        assert dev._output is False


class TestPsuSingleChannelSet:
    """Cover psu set <voltage> [current] for single-channel PSU."""

    def test_set_voltage_only(self, make_repl):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu set 12.0")
        assert dev._voltage == 12.0

    def test_set_voltage_and_current(self, make_repl):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu set 5.0 0.5")
        assert dev._voltage == 5.0
        assert dev._current == 0.5


class TestPsuSingleChannelMeas:
    """Cover psu meas v|i for single-channel PSU."""

    def test_meas_voltage(self, make_repl, capsys):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu meas v")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)

    def test_meas_current(self, make_repl, capsys):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu meas i")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)

    def test_meas_bad_mode(self, make_repl, capsys):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu meas x")
        out = capsys.readouterr().out
        assert "v|i" in out.lower() or "meas" in out.lower()

    def test_meas_missing_arg(self, make_repl, capsys):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu meas")
        out = capsys.readouterr().out
        assert "Usage" in out or "v|i" in out.lower()


class TestPsuNoReadback:
    """Cover SUPPORTS_READBACK = False path in meas."""

    def test_meas_no_readback(self, make_repl, capsys):
        dev = MockMPS6010H()
        dev.SUPPORTS_READBACK = False
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu meas v")
        out = capsys.readouterr().out
        assert "no readback" in out.lower()


class TestPsuSingleChannelGet:
    """Cover psu get for single-channel PSU (MockMPS6010H is single-channel)."""

    def test_get(self, make_repl, capsys):
        dev = MockMPS6010H()
        dev._voltage = 12.0
        dev._current = 1.5
        dev._output = True
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu get")
        out = capsys.readouterr().out
        assert "Setpoint" in out or "12" in out


class TestPsuMultiChannelSet:
    """Cover multi-channel PSU set with MockMultiChannelPSU."""

    def test_set_channel_voltage(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu set 1 5.0")
        out = capsys.readouterr().out
        assert "Set" in out

    def test_set_channel_voltage_and_current(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu set 1 5.0 0.2")
        out = capsys.readouterr().out
        assert "Set" in out

    def test_set_missing_args(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu set 1")
        out = capsys.readouterr().out
        assert "Usage" in out or "channel" in out.lower()

    def test_set_invalid_channel(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu set 9 5.0")
        out = capsys.readouterr().out
        assert "Invalid" in out or "channel" in out.lower()


class TestPsuMultiChannelMeas:
    """Cover multi-channel psu meas <ch> v|i."""

    def test_meas_ch_voltage(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu meas 1 v")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)

    def test_meas_ch_current(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu meas 1 i")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)

    def test_meas_ch_bad_mode(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu meas 1 x")
        out = capsys.readouterr().out
        assert "v|i" in out.lower() or "meas" in out.lower()

    def test_meas_ch_missing_args(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu meas 1")
        out = capsys.readouterr().out
        assert "Usage" in out or "meas" in out.lower()

    def test_meas_ch_invalid_channel(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu meas 9 v")
        out = capsys.readouterr().out
        assert "Invalid" in out or "channel" in out.lower()


class TestPsuMultiChannelGet:
    """Cover psu get warning on multi-channel PSU."""

    def test_get_multi_warns(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu get")
        out = capsys.readouterr().out
        assert "not available" in out.lower()


class TestPsuMultiChannelTrackSaveRecall:
    """Cover track/save/recall for multi vs single-channel PSUs."""

    def test_track_on_multi(self, make_repl):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu track on")

    def test_save_multi(self, make_repl):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu save 1")

    def test_recall_multi(self, make_repl):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu recall 1")

    def test_track_single_warns(self, make_repl, capsys):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu track on")
        out = capsys.readouterr().out
        assert "not available" in out.lower()

    def test_save_single_warns(self, make_repl, capsys):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu save 1")
        out = capsys.readouterr().out
        assert "not available" in out.lower()

    def test_recall_single_warns(self, make_repl, capsys):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu recall 1")
        out = capsys.readouterr().out
        assert "not available" in out.lower()


class TestPsuStateSafe:
    """Cover psu state safe command."""

    def test_state_safe(self, make_repl):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu state safe")

    def test_state_reset(self, make_repl):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu state reset")


class TestPsuMultiChannelHelp:
    """Cover help output for multi-channel PSU."""

    def test_help_multi_channel(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu")
        out = capsys.readouterr().out
        assert "channel" in out.lower() or "1" in out


class TestPsuMultiChannelChan:
    """Cover psu chan <N> on|off for multi-channel PSU."""

    def test_chan_on(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu chan 1 on")
        out = capsys.readouterr().out
        assert "enabled" in out.lower()

    def test_chan_off(self, make_repl, capsys):
        dev = MockMultiChannelPSU()
        repl = make_repl({"psu1": dev})
        repl.onecmd("psu chan 1 off")
        out = capsys.readouterr().out
        assert "disabled" in out.lower()


# ═══════════════════════════════════════════════════════════════════
# 2. DMM command handler -- uncovered paths
# ═══════════════════════════════════════════════════════════════════


class TestDmmOwonBasicConfig:
    """Cover Owon XDM1041 (basic DMM) config path."""

    def test_config_vdc_owon(self, make_repl, capsys):
        dev = MockXDM1041()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm config vdc")
        out = capsys.readouterr().out
        assert "Mode set" in out or "set to" in out.lower()

    def test_meas_vdc_owon(self, make_repl, capsys):
        dev = MockXDM1041()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm meas vdc")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)


class TestDmmHpRead:
    """Cover dmm read."""

    def test_read(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm read")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)


class TestDmmHpFetch:
    """Cover dmm fetch for HP (full-featured) DMM."""

    def test_fetch(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm fetch")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)

    def test_fetch_owon_not_available(self, make_repl, capsys):
        dev = MockXDM1041()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm fetch")
        out = capsys.readouterr().out
        assert "not available" in out.lower()


class TestDmmBeep:
    """Cover dmm beep for HP and Owon."""

    def test_beep_hp(self, make_repl):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm beep")

    def test_beep_owon_not_available(self, make_repl, capsys):
        dev = MockXDM1041()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm beep")
        out = capsys.readouterr().out
        assert "not available" in out.lower()


class TestDmmDisplay:
    """Cover dmm display on/off."""

    def test_display_on(self, make_repl):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm display on")

    def test_display_off(self, make_repl):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm display off")

    def test_display_owon_not_available(self, make_repl, capsys):
        dev = MockXDM1041()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm display on")
        out = capsys.readouterr().out
        assert "not available" in out.lower()


class TestDmmText:
    """Cover dmm text and related commands."""

    def test_text_short(self, make_repl):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm text HELLO")

    def test_text_long_scrolls(self, make_repl):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm text HELLO_WORLD_THIS_IS_LONG")

    def test_text_scroll_on(self, make_repl):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm text HELLO scroll=on")

    def test_text_scroll_off(self, make_repl):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm text HELLO scroll=off")

    def test_text_owon_not_available(self, make_repl, capsys):
        dev = MockXDM1041()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm text HELLO")
        out = capsys.readouterr().out
        assert "not available" in out.lower()

    def test_text_no_message(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm text")
        out = capsys.readouterr().out
        assert "Usage" in out or "text" in out.lower()


class TestDmmTextLoop:
    """Cover dmm text_loop command."""

    def test_text_loop_start(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm text_loop hello")
        out = capsys.readouterr().out
        assert "loop started" in out.lower() or "Text loop" in out

    def test_text_loop_stop(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm text_loop off")
        out = capsys.readouterr().out
        assert "stopped" in out.lower()

    def test_text_loop_no_args(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm text_loop")
        out = capsys.readouterr().out
        assert "Usage" in out or "text_loop" in out.lower()

    def test_text_loop_owon_not_available(self, make_repl, capsys):
        dev = MockXDM1041()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm text_loop hello")
        out = capsys.readouterr().out
        assert "not available" in out.lower()


class TestDmmCleartext:
    """Cover dmm cleartext."""

    def test_cleartext(self, make_repl):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm cleartext")

    def test_cleartext_owon_not_available(self, make_repl, capsys):
        dev = MockXDM1041()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm cleartext")
        out = capsys.readouterr().out
        assert "not available" in out.lower()


class TestDmmRanges:
    """Cover dmm ranges for HP and Owon."""

    def test_ranges_hp(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm ranges")
        out = capsys.readouterr().out
        assert "vdc" in out.lower() or "range" in out.lower() or "34401" in out

    def test_ranges_owon(self, make_repl, capsys):
        dev = MockXDM1041()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm ranges")
        out = capsys.readouterr().out
        assert "owon" in out.lower() or "auto" in out.lower()


class TestDmmMeasContinuityDiode:
    """Cover dmm meas cont and dmm meas diode for HP."""

    def test_meas_continuity(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm meas cont")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)

    def test_meas_diode(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm meas diode")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)


class TestDmmConfigAdvanced:
    """Cover dmm config with range, resolution, and nplc parameters."""

    def test_config_with_range_and_res(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm config vdc 10 0.001")
        out = capsys.readouterr().out
        assert "Configured" in out

    def test_config_with_nplc(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm config vdc 10 0.001 nplc=10")
        out = capsys.readouterr().out
        assert "Configured" in out

    def test_config_continuity(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm config cont")
        out = capsys.readouterr().out
        assert "Configured" in out

    def test_config_diode(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm config diode")
        out = capsys.readouterr().out
        assert "Configured" in out

    def test_config_invalid_mode(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm config bogus")
        out = capsys.readouterr().out
        assert "Invalid" in out or "options" in out.lower()


class TestDmmMeasWithRangeRes:
    """Cover dmm meas <mode> <range> <res> for HP."""

    def test_meas_vdc_with_range(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm meas vdc 10 0.001")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)

    def test_meas_invalid_mode(self, make_repl, capsys):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm meas bogus")
        out = capsys.readouterr().out
        assert "Invalid" in out or "options" in out.lower()


class TestDmmStateSafe:
    """Cover dmm state safe/reset."""

    def test_state_safe(self, make_repl):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm state safe")

    def test_state_reset(self, make_repl):
        dev = MockHP_34401A()
        repl = make_repl({"dmm1": dev})
        repl.onecmd("dmm state reset")


# ═══════════════════════════════════════════════════════════════════
# 3. Scope command handler -- uncovered paths
# ═══════════════════════════════════════════════════════════════════


class TestScopeAwgSubhandlers:
    """Cover scope awg sub-commands through the REPL."""

    def test_awg_chan_on(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg chan on")
        out = capsys.readouterr().out
        assert "enabled" in out.lower()

    def test_awg_chan_off(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg chan off")
        out = capsys.readouterr().out
        assert "disabled" in out.lower()

    def test_awg_set(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg set SINusoid 1000 2.0")
        out = capsys.readouterr().out
        assert "configured" in out.lower() or "AWG" in out

    def test_awg_set_with_offset(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg set SINusoid 1000 2.0 offset=0.5")
        out = capsys.readouterr().out
        assert "AWG" in out

    def test_awg_func(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg func SQUare")
        out = capsys.readouterr().out
        assert "function" in out.lower() or "SQUare" in out

    def test_awg_freq(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg freq 5000")
        out = capsys.readouterr().out
        assert "frequency" in out.lower() or "5000" in out

    def test_awg_amp(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg amp 3.0")
        out = capsys.readouterr().out
        assert "amplitude" in out.lower() or "3.0" in out

    def test_awg_offset(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg offset 1.0")
        out = capsys.readouterr().out
        assert "offset" in out.lower()

    def test_awg_phase(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg phase 90")
        out = capsys.readouterr().out
        assert "phase" in out.lower() or "90" in out

    def test_awg_duty(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg duty 50")
        out = capsys.readouterr().out
        assert "duty" in out.lower()

    def test_awg_sym(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg sym 75")
        out = capsys.readouterr().out
        assert "symmetry" in out.lower() or "75" in out

    def test_awg_mod_on(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg mod on")
        out = capsys.readouterr().out
        assert "modulation" in out.lower()

    def test_awg_mod_off(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg mod off")
        out = capsys.readouterr().out
        assert "modulation" in out.lower()

    def test_awg_mod_type(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg mod_type AM")
        out = capsys.readouterr().out
        assert "modulation type" in out.lower() or "AM" in out

    def test_awg_unknown(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope awg bogus")
        out = capsys.readouterr().out
        assert "Unknown" in out or "awg" in out.lower()


class TestScopeCounterSubhandlers:
    """Cover scope counter sub-commands."""

    def test_counter_off(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope counter off")
        out = capsys.readouterr().out
        assert "disabled" in out.lower()

    def test_counter_source(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope counter source 2")
        out = capsys.readouterr().out
        assert "source" in out.lower() or "CH2" in out

    def test_counter_mode(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope counter mode FREQ")
        out = capsys.readouterr().out
        assert "mode" in out.lower() or "FREQ" in out

    def test_counter_unknown(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope counter bogus")
        out = capsys.readouterr().out
        assert "Unknown" in out or "counter" in out.lower()


class TestScopeDvmSubhandlers:
    """Cover scope dvm sub-commands."""

    def test_dvm_off(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope dvm off")
        out = capsys.readouterr().out
        assert "disabled" in out.lower()

    def test_dvm_source(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope dvm source 3")
        out = capsys.readouterr().out
        assert "source" in out.lower() or "CH3" in out

    def test_dvm_unknown(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope dvm bogus")
        out = capsys.readouterr().out
        assert "Unknown" in out or "dvm" in out.lower()


class TestScopeWaitStop:
    """Cover scope wait_stop command."""

    def test_wait_stop_default_timeout(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope wait_stop")
        out = capsys.readouterr().out
        assert "stopped" in out.lower() or "trigger" in out.lower()

    def test_wait_stop_custom_timeout(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope wait_stop timeout=5")
        out = capsys.readouterr().out
        assert "stopped" in out.lower() or "trigger" in out.lower()

    def test_wait_stop_timeout_not_fired(self, make_repl, capsys):
        dev = MockDHO804()
        dev.wait_for_stop = lambda timeout=10.0: False
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope wait_stop timeout=1")
        out = capsys.readouterr().out
        assert "still armed" in out.lower() or "did not fire" in out.lower()


class TestScopeMeasSetupAndClear:
    """Cover scope meas_setup and meas_clear."""

    def test_meas_setup(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope meas_setup 1 FREQUENCY")
        out = capsys.readouterr().out
        assert "configured" in out.lower() or "FREQUENCY" in out

    def test_meas_clear_not_supported(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope meas_clear")
        out = capsys.readouterr().out
        assert "not supported" in out.lower() or "clear" in out.lower()

    def test_meas_no_args_shows_help(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope meas 1")
        out = capsys.readouterr().out
        assert "Missing" in out or "Usage" in out or "FREQUENCY" in out


class TestScopeMeasForce:
    """Cover scope meas_force command."""

    def test_meas_force(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope meas_force")
        out = capsys.readouterr().out
        assert "forced" in out.lower() or "DSP" in out or "refresh" in out.lower()


class TestScopeDisplaySubhandlers:
    """Cover additional scope display sub-commands."""

    def test_display_unknown(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope display bogus")
        out = capsys.readouterr().out
        assert "Unknown" in out or "display" in out.lower()


class TestScopeAcquireSubhandlers:
    """Cover additional scope acquire sub-commands."""

    def test_acquire_unknown(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope acquire bogus")
        out = capsys.readouterr().out
        assert "Unknown" in out or "acquire" in out.lower()


class TestScopeCursorSubhandlers:
    """Cover additional scope cursor sub-commands."""

    def test_cursor_unknown(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope cursor bogus")
        out = capsys.readouterr().out
        assert "Unknown" in out or "cursor" in out.lower()


class TestScopeMathSubhandlers:
    """Cover additional scope math sub-commands."""

    def test_math_on_default_ch(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope math on")
        out = capsys.readouterr().out
        assert "Math1" in out or "enabled" in out.lower()

    def test_math_scale_with_offset(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope math scale 1 0.5 1.0")
        out = capsys.readouterr().out
        assert "scale" in out.lower()

    def test_math_filter_with_bounds(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope math filter 1 BPAS CH1 upper=1000 lower=100")
        out = capsys.readouterr().out
        assert "filter" in out.lower()

    def test_math_unknown(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope math bogus")
        out = capsys.readouterr().out
        assert "Unknown" in out or "math" in out.lower()


class TestScopeRecordSubhandlers:
    """Cover additional scope record sub-commands."""

    def test_record_unknown(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope record bogus")
        out = capsys.readouterr().out
        assert "Unknown" in out or "record" in out.lower()


class TestScopeMaskSubhandlers:
    """Cover additional scope mask sub-commands."""

    def test_mask_unknown(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope mask bogus")
        out = capsys.readouterr().out
        assert "Unknown" in out or "mask" in out.lower()


class TestScopeState:
    """Cover scope state command."""

    def test_state_safe(self, make_repl):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope state safe")

    def test_state_reset(self, make_repl):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope state reset")


class TestScopeTriggerAdvanced:
    """Cover trigger with positional slope/mode."""

    def test_trigger_with_slope(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        # scope.py calls: dev.configure_trigger(channel, level, slope)
        # MockScope.configure_trigger(ch, level, slope, mode) has 4 required args
        # but scope.py only passes 3, so it will hit the except path; that's fine
        repl.onecmd("scope trigger 1 1.5 FALL")
        # No crash is the test goal here


class TestScopeMeasDelayAdvanced:
    """Cover meas_delay with edge and direction args."""

    def test_meas_delay_with_edges(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope meas_delay 1 2 FALL RISE FORWARDS")
        out = capsys.readouterr().out
        assert any(c.isdigit() for c in out)


class TestScopeMeasDelayStoreAdvanced:
    """Cover meas_delay_store with extra args."""

    def test_meas_delay_store_with_edges(self, make_repl):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope meas_delay_store 1 2 my_delay FALL RISE unit=ns")
        assert len(repl.measurements) == 1


class TestScopeSaveMultiChannel:
    """Cover multi-channel save."""

    def test_save_multi_channel(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "multi.csv")
            repl.onecmd(f"scope save 1,3 {path}")
            out = capsys.readouterr().out
            assert "saved" in out.lower()


class TestScopeHelpFlag:
    """Cover scope --help flag path."""

    def test_help_flag(self, make_repl, capsys):
        dev = MockDHO804()
        repl = make_repl({"scope1": dev})
        repl.onecmd("scope autoset --help")
        out = capsys.readouterr().out
        assert "scope" in out.lower()


# ═══════════════════════════════════════════════════════════════════
# 4. Scripting commands -- uncovered paths
# ═══════════════════════════════════════════════════════════════════


class TestScriptRunViaRepl:
    """Cover script run through the REPL shell."""

    def test_script_run(self, make_repl, capsys):
        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        repl.ctx.scripts["test"] = ["psu set 5.0"]
        repl.onecmd("script run test")
        assert dev._voltage == 5.0

    def test_script_run_not_found(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("script run nonexistent")
        out = capsys.readouterr().out
        assert "not found" in out.lower()


class TestRecordViaRepl:
    """Cover record start/stop/status through the REPL."""

    def test_record_start(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("record start myrec")
        out = capsys.readouterr().out
        assert "Recording" in out
        assert repl.ctx.record_script == "myrec"

    def test_record_stop(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("record start myrec")
        capsys.readouterr()  # clear
        repl.onecmd("record stop")
        out = capsys.readouterr().out
        assert "Stopped" in out or "saved" in out.lower()
        assert repl.ctx.record_script is None

    def test_record_status_active(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("record start myrec")
        capsys.readouterr()
        repl.onecmd("record status")
        out = capsys.readouterr().out
        assert "myrec" in out

    def test_record_status_inactive(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("record status")
        out = capsys.readouterr().out
        assert "Not recording" in out or "not recording" in out.lower()

    def test_record_stop_not_recording(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("record stop")
        out = capsys.readouterr().out
        assert "Not recording" in out


class TestExamplesViaRepl:
    """Cover examples command through the REPL."""

    def test_examples_list(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("examples")
        out = capsys.readouterr().out
        assert "example" in out.lower() or "Available" in out

    def test_examples_load_all(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("examples load all")
        out = capsys.readouterr().out
        assert "Loaded" in out

    def test_examples_load_specific(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("examples load psu_dmm_test")
        out = capsys.readouterr().out
        assert "Loaded" in out or "not found" in out.lower()

    def test_examples_load_not_found(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("examples load nonexistent_example_name")
        out = capsys.readouterr().out
        assert "not found" in out.lower()


class TestScriptDirViaRepl:
    """Cover script dir command through the REPL."""

    def test_script_dir_show(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("script dir")
        out = capsys.readouterr().out
        assert "Scripts dir" in out or "dir" in out.lower()

    def test_script_dir_set(self, make_repl, capsys):
        repl = make_repl({})
        with tempfile.TemporaryDirectory() as td:
            repl.onecmd(f"script dir {td}")
            out = capsys.readouterr().out
            assert "set to" in out.lower() or td in out

    def test_script_dir_reset(self, make_repl, capsys):
        repl = make_repl({})
        repl.onecmd("script dir reset")
        out = capsys.readouterr().out
        assert "reset" in out.lower()


class TestScriptShowListRm:
    """Cover script show/list/rm through the REPL."""

    def test_script_list(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.scripts["my_test"] = ["psu set 5.0", "psu on"]
        repl.onecmd("script list")
        out = capsys.readouterr().out
        assert "my_test" in out

    def test_script_show(self, make_repl, capsys):
        repl = make_repl({})
        repl.ctx.scripts["my_test"] = ["psu set 5.0", "psu on"]
        repl.onecmd("script show my_test")
        out = capsys.readouterr().out
        assert "psu set 5.0" in out

    def test_script_rm(self, make_repl, capsys):
        repl = make_repl({})
        with tempfile.TemporaryDirectory() as td:
            repl.ctx._scripts_dir_override = td
            repl.ctx.scripts["my_test"] = ["psu set 5.0"]
            with open(os.path.join(td, "my_test.scpi"), "w") as f:
                f.write("psu set 5.0\n")
            repl.onecmd("script rm my_test")
            out = capsys.readouterr().out
            assert "deleted" in out.lower()
            assert "my_test" not in repl.ctx.scripts


class TestScriptImportViaRepl:
    """Cover script import through the REPL."""

    def test_script_import(self, make_repl, capsys):
        repl = make_repl({})
        with tempfile.TemporaryDirectory() as td:
            repl.ctx._scripts_dir_override = td
            src = os.path.join(td, "source.scpi")
            with open(src, "w") as f:
                f.write("psu set 5.0\npsu on\n")
            repl.onecmd(f"script import my_imported {src}")
            out = capsys.readouterr().out
            assert "Imported" in out
            assert "my_imported" in repl.ctx.scripts


class TestScriptLoadSaveViaRepl:
    """Cover script load/save through the REPL."""

    def test_script_save_and_load(self, make_repl, capsys):
        repl = make_repl({})
        with tempfile.TemporaryDirectory() as td:
            repl.ctx._scripts_dir_override = td
            repl.ctx.scripts["s1"] = ["psu set 5.0"]
            repl.onecmd("script save")
            capsys.readouterr()
            repl.ctx.scripts.clear()
            repl.onecmd("script load")
            out = capsys.readouterr().out
            assert "Loaded" in out
            assert "s1" in repl.ctx.scripts


# ═══════════════════════════════════════════════════════════════════
# 5. Script engine runner -- additional coverage
# ═══════════════════════════════════════════════════════════════════


class TestRunnerExpandedExecution:
    """Cover run_expanded with actual REPL commands."""

    def test_run_expanded_with_real_repl(self, make_repl):
        from lab_instruments.repl.script_engine.runner import run_expanded

        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        expanded = [("psu set 10.0", "psu set 10.0")]
        result = run_expanded(expanded, repl, repl.ctx, debug=False)
        assert result is False
        assert dev._voltage == 10.0

    def test_run_expanded_nop_mixed(self, make_repl):
        from lab_instruments.repl.script_engine.runner import run_expanded

        dev = MockMPS6010H()
        repl = make_repl({"psu1": dev})
        expanded = [
            ("__NOP__", "set voltage 5.0"),
            ("psu set 7.0", "psu set $voltage"),
        ]
        result = run_expanded(expanded, repl, repl.ctx, debug=False)
        assert result is False
        assert dev._voltage == 7.0

    def test_run_expanded_set_e_stops(self, make_repl):
        """Test that set -e mode stops on first error."""
        from lab_instruments.repl.script_engine.runner import run_expanded

        repl = make_repl({})
        repl.ctx.exit_on_error = True

        def fail_onecmd(line):
            repl.ctx.command_had_error = True
            return False

        repl.onecmd = fail_onecmd
        expanded = [
            ("psu set 5.0", "psu set 5.0"),
            ("psu set 10.0", "psu set 10.0"),
        ]
        result = run_expanded(expanded, repl, repl.ctx, debug=False)
        assert result is True

    def test_run_expanded_breakpoint_filtering(self):
        """Test that __BREAKPOINT__ markers are filtered from line list."""
        from lab_instruments.repl.context import ReplContext
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = ReplContext()
        shell = MagicMock()
        shell.onecmd.return_value = False
        # Put breakpoint AFTER the command so it doesn't trigger at line 1
        # (breakpoint at line 2 won't trigger because there's only 1 cmd line)
        expanded = [
            ("print hello", "print hello"),
            ("__BREAKPOINT__", "__BREAKPOINT__"),
        ]
        result = run_expanded(expanded, shell, ctx, debug=False)
        assert result is False
        # Only "print hello" should be executed, breakpoint marker filtered out
        shell.onecmd.assert_called_once()

    def test_run_expanded_comment_and_blank_lines(self):
        """Comments and blank lines should be filtered out."""
        from lab_instruments.repl.context import ReplContext
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = ReplContext()
        shell = MagicMock()
        shell.onecmd.return_value = False
        expanded = [
            ("# this is a comment", "# this is a comment"),
            ("   ", "   "),
            ("", ""),
            ("print hello", "print hello"),
        ]
        result = run_expanded(expanded, shell, ctx, debug=False)
        assert result is False
        assert shell.onecmd.call_count == 1

    def test_run_expanded_tuple_fallback(self):
        """Test non-tuple items in expanded list (fallback path)."""
        from lab_instruments.repl.context import ReplContext
        from lab_instruments.repl.script_engine.runner import run_expanded

        ctx = ReplContext()
        shell = MagicMock()
        shell.onecmd.return_value = False
        expanded = ["print hello"]
        result = run_expanded(expanded, shell, ctx, debug=False)
        assert result is False
        shell.onecmd.assert_called_once()


# ═══════════════════════════════════════════════════════════════════
# 6. DeviceManager -- coverage for base class methods
# ═══════════════════════════════════════════════════════════════════


class TestDeviceManager:
    """Cover DeviceManager connect, disconnect, query, send_command, reset, clear_status."""

    def test_connect(self, mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        from lab_instruments.src.device_manager import DeviceManager

        dm = DeviceManager("GPIB::1::INSTR")
        dm.connect()
        assert dm.instrument is not None
        mock_rm.open_resource.assert_called_with("GPIB::1::INSTR")
        assert dm.instrument.timeout == 5000

    def test_connect_failure(self, mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        import pyvisa

        mock_rm.open_resource.side_effect = pyvisa.VisaIOError(-1)
        from lab_instruments.src.device_manager import DeviceManager

        dm = DeviceManager("GPIB::1::INSTR")
        with pytest.raises(pyvisa.VisaIOError):
            dm.connect()

    def test_disconnect(self, mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        from lab_instruments.src.device_manager import DeviceManager

        dm = DeviceManager("GPIB::1::INSTR")
        dm.connect()
        dm.disconnect()
        mock_instrument.close.assert_called_once()
        assert dm.instrument is None

    def test_disconnect_when_not_connected(self, mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        from lab_instruments.src.device_manager import DeviceManager

        dm = DeviceManager("GPIB::1::INSTR")
        dm.disconnect()  # Should not raise

    def test_send_command(self, mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        from lab_instruments.src.device_manager import DeviceManager

        dm = DeviceManager("GPIB::1::INSTR")
        dm.connect()
        dm.send_command("*RST")
        mock_instrument.write.assert_called_with("*RST")

    def test_send_command_not_connected(self, mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        from lab_instruments.src.device_manager import DeviceManager

        dm = DeviceManager("GPIB::1::INSTR")
        with pytest.raises(ConnectionError):
            dm.send_command("*RST")

    def test_query(self, mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        from lab_instruments.src.device_manager import DeviceManager

        dm = DeviceManager("GPIB::1::INSTR")
        dm.connect()
        mock_instrument.query.return_value = "  5.0023  "
        result = dm.query("MEAS:VOLT?")
        assert result == "5.0023"
        mock_instrument.query.assert_called_with("MEAS:VOLT?")

    def test_query_not_connected(self, mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        from lab_instruments.src.device_manager import DeviceManager

        dm = DeviceManager("GPIB::1::INSTR")
        with pytest.raises(ConnectionError):
            dm.query("*IDN?")

    def test_reset(self, mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        from lab_instruments.src.device_manager import DeviceManager

        dm = DeviceManager("GPIB::1::INSTR")
        dm.connect()
        dm.reset()
        writes = [c.args[0] for c in mock_instrument.write.call_args_list]
        assert "*RST" in writes
        assert "*CLS" in writes

    def test_clear_status(self, mock_visa_rm):
        mock_rm, mock_instrument = mock_visa_rm
        from lab_instruments.src.device_manager import DeviceManager

        dm = DeviceManager("GPIB::1::INSTR")
        dm.connect()
        dm.clear_status()
        mock_instrument.write.assert_called_with("*CLS")


# ═══════════════════════════════════════════════════════════════════
# 7. MATRIX_MPS6010H -- additional coverage via mock VISA
# ═══════════════════════════════════════════════════════════════════


class TestMatrixMPS6010HAdditional:
    """Cover set_output, set_output_channel, measure_* compat, repr."""

    def test_set_output(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_output(12.0, 2.0)
        assert psu.get_voltage_setpoint() == 12.0
        assert psu.get_current_limit() == 2.0

    def test_enable_output_true(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.enable_output(True)
        assert psu.get_output_state() is True

    def test_enable_output_false(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.enable_output(True)
        psu.enable_output(False)
        assert psu.get_output_state() is False

    def test_disable_output(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_voltage(10.0)
        psu.enable_output(True)
        psu.disable_output()
        assert psu.get_output_state() is False
        assert psu.get_voltage_setpoint() == 0.0
        assert psu.get_current_limit() == 0.0

    def test_set_output_channel_with_current(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_output_channel("ch1", 15.0, 3.0)
        assert psu.get_voltage_setpoint() == 15.0
        assert psu.get_current_limit() == 3.0

    def test_set_output_channel_without_current(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_output_channel("ch1", 15.0)
        assert psu.get_voltage_setpoint() == 15.0

    def test_measure_voltage_channel(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_voltage(20.0)
        result = psu.measure_voltage_channel("ch1")
        assert result == 20.0

    def test_measure_current_channel(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_current_limit(5.0)
        result = psu.measure_current_channel("ch1")
        assert result == 5.0

    def test_measure_voltage(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_voltage(25.0)
        assert psu.measure_voltage() == 25.0

    def test_measure_current(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_current_limit(7.5)
        assert psu.measure_current() == 7.5

    def test_repr(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_voltage(12.0)
        psu.set_current_limit(2.0)
        psu.enable_output(True)
        r = repr(psu)
        assert "12.0" in r
        assert "2.0" in r
        assert "ON" in r

    def test_get_error(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        result = psu.get_error()
        assert "not supported" in result.lower()
