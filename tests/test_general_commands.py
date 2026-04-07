"""Tests for general REPL commands: scan, list, use, status, idn, raw, state, etc."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockAWG, MockDHO804, MockHP_34401A, MockHP_E3631A, MockNI_PXIe_4139


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
def repl_empty():
    return make_repl({})


@pytest.fixture
def repl_psu():
    return make_repl({"psu1": MockHP_E3631A()})


@pytest.fixture
def repl_multi():
    return make_repl(
        {
            "psu1": MockHP_E3631A(),
            "awg1": MockAWG(),
            "dmm1": MockHP_34401A(),
            "scope1": MockDHO804(),
            "smu": MockNI_PXIe_4139(),
        }
    )


# ---------------------------------------------------------------------------
# list / status
# ---------------------------------------------------------------------------


class TestList:
    def test_list_empty(self, repl_empty, capsys):
        repl_empty.onecmd("list")
        out = capsys.readouterr().out
        assert "No instruments" in out

    def test_list_with_devices(self, repl_psu, capsys):
        repl_psu.onecmd("list")
        out = capsys.readouterr().out
        assert "psu1" in out

    def test_list_help(self, repl_empty, capsys):
        repl_empty.onecmd("list --help")
        out = capsys.readouterr().out
        assert out != ""

    def test_status_delegates(self, repl_psu, capsys):
        repl_psu.onecmd("status")
        out = capsys.readouterr().out
        assert "psu1" in out


# ---------------------------------------------------------------------------
# use
# ---------------------------------------------------------------------------


class TestUse:
    def test_use_valid_device(self, repl_psu):
        repl_psu.onecmd("use psu1")
        assert repl_psu.selected == "psu1"

    def test_use_invalid_device(self, repl_psu, capsys):
        repl_psu.onecmd("use nonexistent")
        out = capsys.readouterr().out
        assert "Unknown" in out or "nonexistent" in out

    def test_use_no_args_shows_help(self, repl_psu, capsys):
        repl_psu.onecmd("use")
        out = capsys.readouterr().out
        assert out != ""

    def test_use_help_flag(self, repl_psu, capsys):
        repl_psu.onecmd("use --help")
        out = capsys.readouterr().out
        assert out != ""


# ---------------------------------------------------------------------------
# scan
# ---------------------------------------------------------------------------


class TestScan:
    def test_scan_help(self, repl_empty, capsys):
        repl_empty.onecmd("scan --help")
        out = capsys.readouterr().out
        assert out != ""

    def test_scan_while_done(self, repl_empty, capsys):
        """When scan_done is set, re-runs discovery."""
        repl_empty.onecmd("scan")
        # No crash is sufficient — devices may be empty

    def test_scan_not_done_waits(self, repl_empty):
        """When scan not done yet, it waits — we just make sure it doesn't hang."""
        repl_empty._scan_done.clear()
        # Set the event from a thread quickly so wait() returns
        import threading

        threading.Timer(0.01, repl_empty._scan_done.set).start()
        repl_empty.onecmd("scan")


# ---------------------------------------------------------------------------
# idn
# ---------------------------------------------------------------------------


class TestIdn:
    def test_idn_no_device_selected(self, repl_empty, capsys):
        repl_empty.onecmd("idn")
        # Should print error about no device
        out = capsys.readouterr().out
        assert out != "" or repl_empty.ctx.command_had_error

    def test_idn_named_device(self, repl_psu, capsys):
        repl_psu.onecmd("idn psu1")
        out = capsys.readouterr().out
        assert out != ""

    def test_idn_unknown_device(self, repl_psu):
        repl_psu.onecmd("idn nonexistent")
        assert repl_psu.ctx.command_had_error

    def test_idn_help(self, repl_empty, capsys):
        repl_empty.onecmd("idn --help")
        out = capsys.readouterr().out
        assert out != ""

    def test_idn_active_device(self, repl_psu, capsys):
        repl_psu.onecmd("use psu1")
        repl_psu.ctx.command_had_error = False
        repl_psu.onecmd("idn")
        out = capsys.readouterr().out
        assert out != ""


# ---------------------------------------------------------------------------
# raw
# ---------------------------------------------------------------------------


class TestRaw:
    def test_raw_no_args_shows_help(self, repl_psu, capsys):
        repl_psu.onecmd("raw")
        out = capsys.readouterr().out
        assert out != ""

    def test_raw_help_flag(self, repl_psu, capsys):
        repl_psu.onecmd("raw --help")
        out = capsys.readouterr().out
        assert out != ""

    def test_raw_write_command(self, repl_psu, capsys):
        repl_psu.onecmd("use psu1")
        repl_psu.onecmd("raw *RST")
        out = capsys.readouterr().out
        assert out != ""

    def test_raw_query_command(self, repl_psu, capsys):
        repl_psu.onecmd("use psu1")
        repl_psu.onecmd("raw *IDN?")
        out = capsys.readouterr().out
        assert out != ""

    def test_raw_named_device_query(self, repl_psu, capsys):
        repl_psu.onecmd("raw psu1 *IDN?")
        out = capsys.readouterr().out
        assert out != ""

    def test_raw_named_device_write(self, repl_psu, capsys):
        repl_psu.onecmd("raw psu1 OUTPUT:STATE OFF")
        out = capsys.readouterr().out
        assert out != ""

    def test_raw_no_device_selected(self, repl_empty):
        repl_empty.onecmd("raw *IDN?")
        assert repl_empty.ctx.command_had_error


# ---------------------------------------------------------------------------
# version
# ---------------------------------------------------------------------------


class TestVersion:
    def test_version_prints(self, repl_empty, capsys):
        repl_empty.onecmd("version")
        out = capsys.readouterr().out
        assert "scpi-instrument-toolkit" in out


# ---------------------------------------------------------------------------
# close
# ---------------------------------------------------------------------------


class TestClose:
    def test_close_disconnects_all(self, repl_psu, capsys):
        repl_psu.onecmd("close")
        out = capsys.readouterr().out
        assert "disconnect" in out.lower()
        assert len(repl_psu.devices) == 0

    def test_close_help(self, repl_empty, capsys):
        repl_empty.onecmd("close --help")
        out = capsys.readouterr().out
        assert out != ""

    def test_close_empty(self, repl_empty, capsys):
        repl_empty.onecmd("close")
        out = capsys.readouterr().out
        assert out != ""


# ---------------------------------------------------------------------------
# state
# ---------------------------------------------------------------------------


class TestState:
    def test_state_help(self, repl_multi, capsys):
        repl_multi.onecmd("state")
        out = capsys.readouterr().out
        assert out != ""

    def test_state_list(self, repl_multi, capsys):
        repl_multi.onecmd("state list")
        out = capsys.readouterr().out
        assert out != ""

    def test_state_safe_all(self, repl_multi):
        repl_multi.onecmd("state safe")

    def test_state_off_all(self, repl_multi):
        repl_multi.onecmd("state off")

    def test_state_on_all(self, repl_multi):
        repl_multi.onecmd("state on")

    def test_state_reset_all(self, repl_multi):
        repl_multi.onecmd("state reset")

    def test_state_psu_off(self, repl_psu):
        repl_psu.onecmd("state psu1 off")

    def test_state_psu_safe(self, repl_psu):
        repl_psu.onecmd("state psu1 safe")

    def test_state_psu_on(self, repl_psu):
        repl_psu.onecmd("state psu1 on")

    def test_state_psu_reset(self, repl_psu):
        repl_psu.onecmd("state psu1 reset")

    def test_state_psu_unknown_state(self, repl_psu, capsys):
        repl_psu.onecmd("state psu1 xyz")
        out = capsys.readouterr().out
        assert out != ""

    def test_state_awg_off(self, repl_multi):
        repl_multi.onecmd("state awg1 off")

    def test_state_awg_on(self, repl_multi):
        repl_multi.onecmd("state awg1 on")

    def test_state_awg_reset(self, repl_multi):
        repl_multi.onecmd("state awg1 reset")

    def test_state_awg_unknown(self, repl_multi, capsys):
        repl_multi.onecmd("state awg1 xyz")
        out = capsys.readouterr().out
        assert out != ""

    def test_state_scope_off(self, repl_multi):
        repl_multi.onecmd("state scope1 off")

    def test_state_scope_on(self, repl_multi):
        repl_multi.onecmd("state scope1 on")

    def test_state_scope_reset(self, repl_multi):
        repl_multi.onecmd("state scope1 reset")

    def test_state_dmm_safe(self, repl_multi):
        repl_multi.onecmd("state dmm1 safe")

    def test_state_dmm_reset(self, repl_multi):
        repl_multi.onecmd("state dmm1 reset")

    def test_state_unknown_device(self, repl_psu):
        repl_psu.onecmd("state nonexistent off")
        assert repl_psu.ctx.command_had_error

    def test_state_missing_arg(self, repl_psu, capsys):
        repl_psu.onecmd("state psu1")
        out = capsys.readouterr().out
        assert out != ""

    def test_state_help_flag(self, repl_psu, capsys):
        repl_psu.onecmd("state --help")
        out = capsys.readouterr().out
        assert out != ""


# ---------------------------------------------------------------------------
# all
# ---------------------------------------------------------------------------


class TestAll:
    def test_all_help(self, repl_multi, capsys):
        repl_multi.onecmd("all")
        out = capsys.readouterr().out
        assert out != ""

    def test_all_on(self, repl_multi):
        repl_multi.onecmd("all on")

    def test_all_off(self, repl_multi):
        repl_multi.onecmd("all off")

    def test_all_safe(self, repl_multi):
        repl_multi.onecmd("all safe")

    def test_all_reset(self, repl_multi):
        repl_multi.onecmd("all reset")

    def test_all_unknown(self, repl_multi, capsys):
        repl_multi.onecmd("all xyz")
        out = capsys.readouterr().out
        assert out != ""

    def test_all_help_flag(self, repl_multi, capsys):
        repl_multi.onecmd("all --help")
        out = capsys.readouterr().out
        assert out != ""


# ---------------------------------------------------------------------------
# disconnect
# ---------------------------------------------------------------------------


class TestUnscan:
    def test_disconnect_no_args_shows_help(self, repl_psu, capsys):
        repl_psu.onecmd("disconnect")
        out = capsys.readouterr().out
        assert out != ""

    def test_disconnect_help_flag(self, repl_psu, capsys):
        repl_psu.onecmd("disconnect --help")
        out = capsys.readouterr().out
        assert out != ""

    def test_disconnect_removes_device(self, repl_psu):
        assert "psu1" in repl_psu.devices
        repl_psu.onecmd("disconnect psu1")
        assert "psu1" not in repl_psu.devices

    def test_disconnect_unknown_warns(self, repl_psu, capsys):
        repl_psu.onecmd("disconnect nonexistent")
        out = capsys.readouterr().out
        assert "nonexistent" in out or "No device" in out

    def test_disconnect_active_device_clears_selection(self, repl_psu):
        repl_psu.onecmd("use psu1")
        assert repl_psu.selected == "psu1"
        repl_psu.onecmd("disconnect psu1")
        assert repl_psu.selected is None

    def test_disconnect_non_active_preserves_selection(self):
        repl = make_repl({"psu1": MockHP_E3631A(), "psu2": MockHP_E3631A()})
        repl.onecmd("use psu1")
        repl.onecmd("disconnect psu2")
        assert repl.selected == "psu1"
        assert "psu2" not in repl.devices

    def test_disconnect_one_of_two_leaves_other(self):
        repl = make_repl({"psu1": MockHP_E3631A(), "psu2": MockHP_E3631A()})
        repl.onecmd("disconnect psu1")
        assert "psu1" not in repl.devices
        assert "psu2" in repl.devices

    def test_disconnect_unnumbered_device(self):
        repl = make_repl({"awg": MockAWG()})
        repl.onecmd("disconnect awg")
        assert "awg" not in repl.devices

    def test_disconnect_high_numbered_device(self):
        repl = make_repl({"dmm3": MockHP_34401A()})
        repl.onecmd("disconnect dmm3")
        assert "dmm3" not in repl.devices

    def test_disconnect_leaves_other_types_intact(self, repl_multi):
        repl_multi.onecmd("disconnect psu1")
        assert "psu1" not in repl_multi.devices
        assert "awg1" in repl_multi.devices
        assert "dmm1" in repl_multi.devices
        assert "scope1" in repl_multi.devices

    def test_disconnect_prints_removed_message(self, repl_psu, capsys):
        repl_psu.onecmd("disconnect psu1")
        out = capsys.readouterr().out
        assert "psu1" in out

    def test_disconnect_on_empty_repl_warns(self, repl_empty, capsys):
        repl_empty.onecmd("disconnect psu1")
        out = capsys.readouterr().out
        assert out != ""
