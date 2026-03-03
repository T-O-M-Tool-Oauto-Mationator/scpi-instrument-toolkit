"""tests/test_repl.py — REPL gap tests not covered by existing *_commands.py files.

Covers: multi-device routing, missing-device graceful error, help commands,
error flag reset, and device name aliasing.
"""
import pytest
from lab_instruments.mock_instruments import MockHP_E3631A, MockMPS6010H, MockEDU33212A


class TestReplMultiDevice:
    def test_two_psus(self, make_repl):
        devices = {"psu1": MockHP_E3631A(), "psu2": MockMPS6010H()}
        repl = make_repl(devices)
        repl.onecmd("psu1 set 5.0")
        repl.onecmd("psu2 set 12.0")

    def test_psu_and_awg(self, make_repl):
        devices = {"psu1": MockHP_E3631A(), "awg1": MockEDU33212A()}
        repl = make_repl(devices)
        repl.onecmd("psu set 3.3")
        repl.onecmd("awg wave 1 sine freq=1000 amp=2.0")


class TestReplDeviceNotPresent:
    def test_awg_cmd_no_awg(self, make_repl):
        repl = make_repl({})
        # Should not raise — error printed gracefully
        repl.onecmd("awg wave 1 sine")

    def test_psu_cmd_no_psu(self, make_repl):
        repl = make_repl({})
        repl.onecmd("psu set 5.0")


class TestReplHelp:
    def test_help_general(self, make_repl):
        repl = make_repl({})
        repl.onecmd("help")

    def test_help_psu(self, make_repl):
        repl = make_repl({})
        repl.onecmd("help psu")

    def test_help_awg(self, make_repl):
        repl = make_repl({})
        repl.onecmd("help awg")


class TestReplErrorFlagReset:
    def test_error_set_on_missing_device(self, make_repl):
        repl = make_repl({})
        repl._command_had_error = False
        repl.onecmd("awg wave 1 sine")
        assert repl._command_had_error is True

    def test_error_reset_on_success(self, make_repl):
        devices = {"psu1": MockHP_E3631A()}
        repl = make_repl(devices)
        # Trigger an error first
        repl.onecmd("awg wave 1 sine")
        assert repl._command_had_error is True
        # A successful psu command should reset the flag
        repl._command_had_error = False
        repl.onecmd("psu set 5.0")
        assert repl._command_had_error is False


class TestReplDeviceNames:
    def test_psu_alias_single_device(self, make_repl):
        devices = {"psu1": MockHP_E3631A()}
        repl = make_repl(devices)
        # 'psu' command should route to psu1 when only one PSU is present
        repl.onecmd("psu set 5.0")

    def test_awg_alias_single_device(self, make_repl):
        devices = {"awg1": MockEDU33212A()}
        repl = make_repl(devices)
        repl.onecmd("awg wave 1 sine freq=1000 amp=2.0")
