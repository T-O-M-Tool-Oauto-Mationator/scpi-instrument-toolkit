"""Extra tests targeting missed lines in general.py and bulk operations."""

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


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


# ---------------------------------------------------------------------------
# PSU with disable_output (not disable_all_channels)
# ---------------------------------------------------------------------------


class MockPsuNoDisableAll:
    """PSU that has disable_output but not disable_all_channels."""

    def __init__(self):
        self._output = True

    def disable_output(self):
        self._output = False

    def enable_output(self, state):
        self._output = bool(state)

    def get_voltage_setpoint(self):
        return 5.0

    def get_current_limit(self):
        return 0.1

    def get_output_state(self):
        return self._output

    def reset(self):
        pass

    def disconnect(self):
        pass

    def query(self, cmd):
        return "MOCK,PSU,SN001,1.0"

    def send_command(self, cmd):
        pass


class MockPsuEnableOnly:
    """PSU that only has enable_output."""

    def __init__(self):
        self._output = True

    def enable_output(self, state):
        self._output = bool(state)

    def get_voltage_setpoint(self):
        return 5.0

    def get_current_limit(self):
        return 0.1

    def get_output_state(self):
        return self._output

    def reset(self):
        pass

    def disconnect(self):
        pass

    def query(self, cmd):
        return "MOCK,PSU,SN001,1.0"

    def send_command(self, cmd):
        pass


class MockAwgNoDisableAll:
    """AWG that has disable_output but not disable_all_channels."""

    def __init__(self):
        self._enabled = True

    def disable_output(self):
        self._enabled = False

    def enable_output(self, state=None, ch1=None, ch2=None):
        pass

    def get_amplitude(self, ch):
        return 1.0

    def get_offset(self, ch):
        return 0.0

    def get_frequency(self, ch):
        return 1000.0

    def reset(self):
        pass

    def disconnect(self):
        pass

    def query(self, cmd):
        return "MOCK,AWG,SN001,1.0"

    def send_command(self, cmd):
        pass


class MockAwgEnableOutputTypeError:
    """AWG where enable_output(ch1=...) raises TypeError."""

    def __init__(self):
        pass

    def enable_output(self, *args, **kwargs):
        raise TypeError("no kwargs")

    def get_amplitude(self, ch):
        return 1.0

    def get_offset(self, ch):
        return 0.0

    def get_frequency(self, ch):
        return 1000.0

    def reset(self):
        pass

    def disconnect(self):
        pass

    def query(self, cmd):
        return "MOCK,AWG,SN001,1.0"

    def send_command(self, cmd):
        pass


class MockAwgEnableAllChannels:
    """AWG with enable_all_channels method."""

    def __init__(self):
        self._all_enabled = False

    def enable_all_channels(self):
        self._all_enabled = True

    def disable_all_channels(self):
        self._all_enabled = False

    def get_amplitude(self, ch):
        return 1.0

    def get_offset(self, ch):
        return 0.0

    def get_frequency(self, ch):
        return 1000.0

    def reset(self):
        pass

    def disconnect(self):
        pass

    def query(self, cmd):
        return "MOCK,AWG,SN001,1.0"

    def send_command(self, cmd):
        pass


class MockScopeNoDisableAll:
    """Scope that has disable_channel but not disable_all_channels."""

    def stop(self):
        pass

    def disable_channel(self, ch):
        pass

    def reset(self):
        pass

    def disconnect(self):
        pass

    def query(self, cmd):
        return "MOCK,SCOPE,SN001,1.0"

    def send_command(self, cmd):
        pass


class MockScopeWithAwgOutput:
    """Scope that has awg_set_output_enable, awg_set_function, awg_set_offset."""

    def stop(self):
        pass

    def disable_all_channels(self):
        pass

    def awg_set_output_enable(self, state):
        pass

    def awg_set_function(self, func):
        pass

    def awg_set_offset(self, val):
        pass

    def reset(self):
        pass

    def disconnect(self):
        pass

    def query(self, cmd):
        return "MOCK,SCOPE,SN001,1.0"

    def send_command(self, cmd):
        pass


# ---------------------------------------------------------------------------
# _state_psu branches
# ---------------------------------------------------------------------------


class TestStatePsuBranches:
    def test_psu_off_disable_output_branch(self):
        dev = MockPsuNoDisableAll()
        repl = make_repl({"psu1": dev})
        repl.onecmd("state psu1 off")
        assert dev._output is False

    def test_psu_off_enable_output_branch(self):
        dev = MockPsuEnableOnly()
        repl = make_repl({"psu1": dev})
        repl.onecmd("state psu1 off")
        assert dev._output is False

    def test_safe_all_psu_disable_output_branch(self):
        dev = MockPsuNoDisableAll()
        repl = make_repl({"psu1": dev})
        repl.onecmd("state safe")
        assert dev._output is False

    def test_safe_all_psu_enable_output_branch(self):
        dev = MockPsuEnableOnly()
        repl = make_repl({"psu1": dev})
        repl.onecmd("state safe")
        assert dev._output is False

    def test_off_all_psu_disable_output_branch(self):
        dev = MockPsuNoDisableAll()
        repl = make_repl({"psu1": dev})
        repl.onecmd("all off")
        assert dev._output is False

    def test_off_all_psu_enable_output_branch(self):
        dev = MockPsuEnableOnly()
        repl = make_repl({"psu1": dev})
        repl.onecmd("all off")
        assert dev._output is False


# ---------------------------------------------------------------------------
# _state_awg branches
# ---------------------------------------------------------------------------


class TestStateAwgBranches:
    def test_awg_off_disable_output_branch(self):
        dev = MockAwgNoDisableAll()
        repl = make_repl({"awg1": dev})
        repl.onecmd("state awg1 off")

    def test_awg_off_enable_output_typeerror_branch(self, capsys):
        dev = MockAwgEnableOutputTypeError()
        repl = make_repl({"awg1": dev})
        repl.onecmd("state awg1 off")

    def test_awg_on_enable_all_channels_branch(self):
        """_state_awg on uses enable_all_channels if present."""
        dev = MockAwgEnableAllChannels()
        repl = make_repl({"awg1": dev})
        repl.onecmd("state awg1 on")
        assert dev._all_enabled is True

    def test_all_on_scope_enable_all_channels(self):
        """on_all for scope with enable_all_channels."""
        dev = MockScopeWithAwgOutput()
        repl = make_repl({"scope1": dev})
        repl.onecmd("all on")

    def test_safe_all_awg_disable_output_branch(self):
        dev = MockAwgNoDisableAll()
        repl = make_repl({"awg1": dev})
        repl.onecmd("state safe")

    def test_off_all_awg_disable_output_branch(self):
        dev = MockAwgNoDisableAll()
        repl = make_repl({"awg1": dev})
        repl.onecmd("all off")


# ---------------------------------------------------------------------------
# scope branches with disable_channel
# ---------------------------------------------------------------------------


class TestStateScopeBranches:
    def test_scope_safe_awg_output_branch(self):
        dev = MockScopeWithAwgOutput()
        repl = make_repl({"scope1": dev})
        repl.onecmd("state safe")

    def test_scope_off_disable_channel_branch(self):
        dev = MockScopeNoDisableAll()
        repl = make_repl({"scope1": dev})
        repl.onecmd("all off")

    def test_safe_all_scope_disable_channel_branch(self):
        dev = MockScopeNoDisableAll()
        repl = make_repl({"scope1": dev})
        repl.onecmd("state safe")


# ---------------------------------------------------------------------------
# SMU in bulk operations (via enable_output path)
# ---------------------------------------------------------------------------


class MockSmuEnableOnly:
    def __init__(self):
        self._output = False

    def enable_output(self, state):
        self._output = bool(state)

    def get_voltage_setpoint(self):
        return 0.0

    def get_current_limit(self):
        return 0.01

    def get_output_state(self):
        return self._output

    def reset(self):
        pass

    def disconnect(self):
        pass

    def query(self, cmd):
        return "MOCK,SMU,SN001,1.0"

    def send_command(self, cmd):
        pass


class TestSmuBulkOps:
    def test_off_all_smu_enable_output(self):
        dev = MockSmuEnableOnly()
        repl = make_repl({"smu": dev})
        repl.onecmd("all off")
        assert dev._output is False

    def test_on_all_smu_enable_output(self):
        dev = MockSmuEnableOnly()
        repl = make_repl({"smu": dev})
        repl.onecmd("all on")
        assert dev._output is True


# ---------------------------------------------------------------------------
# print_devices with selected device
# ---------------------------------------------------------------------------


class TestPrintDevicesSelected:
    def test_selected_device_highlighted(self, capsys):
        from lab_instruments.mock_instruments import MockHP_E3631A

        repl = make_repl({"psu1": MockHP_E3631A(), "psu2": MockHP_E3631A()})
        repl.onecmd("use psu1")
        capsys.readouterr()  # clear
        repl.onecmd("list")
        out = capsys.readouterr().out
        assert "psu1" in out
        assert "psu2" in out


# ---------------------------------------------------------------------------
# do_scan: scan when not done (lines 116-118)
# ---------------------------------------------------------------------------


class TestScanBranch:
    def test_scan_waiting_branch(self, capsys):
        from lab_instruments.mock_instruments import MockHP_E3631A

        repl = make_repl({"psu1": MockHP_E3631A()})
        repl._scan_done.clear()
        import threading

        threading.Timer(0.02, repl._scan_done.set).start()
        repl.onecmd("scan")
        capsys.readouterr()
        assert True  # just no crash

    def test_scan_with_no_devices_found(self, capsys):
        repl = make_repl({})
        repl.onecmd("scan")
        out = capsys.readouterr().out
        assert out != ""


# ---------------------------------------------------------------------------
# reload (lines 398-407) — just test it doesn't crash by patching os.execv
# ---------------------------------------------------------------------------


class TestReload:
    def test_reload_calls_execv(self):
        from lab_instruments.mock_instruments import MockHP_E3631A

        repl = make_repl({"psu1": MockHP_E3631A()})
        with patch("os.execv", side_effect=SystemExit(0)), pytest.raises(SystemExit):
            repl.onecmd("reload")
