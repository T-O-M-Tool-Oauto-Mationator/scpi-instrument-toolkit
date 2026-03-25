"""Tests for SafetySystem — limit checking, output guards, retroactive checks."""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockAWG, MockHP_E3631A
from lab_instruments.repl.commands.safety import SafetySystem
from lab_instruments.repl.context import ReplContext


def make_ctx_with_devices(devices):
    ctx = ReplContext()
    ctx.registry.devices = devices
    return ctx


# ---------------------------------------------------------------------------
# collect_limits
# ---------------------------------------------------------------------------


class TestCollectLimits:
    def test_no_limits_returns_empty(self):
        ctx = make_ctx_with_devices({})
        safety = SafetySystem(ctx)
        limits = safety.collect_limits("psu1", "psu", None)
        assert limits == {}

    def test_device_name_limits(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu1", None)] = {"voltage_upper": 5.0}
        safety = SafetySystem(ctx)
        limits = safety.collect_limits("psu1", "psu", None)
        assert limits["voltage_upper"] == 5.0

    def test_device_type_limits(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu", None)] = {"voltage_upper": 12.0}
        safety = SafetySystem(ctx)
        limits = safety.collect_limits("psu1", "psu", None)
        assert limits["voltage_upper"] == 12.0

    def test_device_name_takes_priority_for_upper(self):
        """More restrictive (lower) upper limit wins."""
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu1", None)] = {"voltage_upper": 5.0}
        ctx.safety_limits[("psu", None)] = {"voltage_upper": 12.0}
        safety = SafetySystem(ctx)
        limits = safety.collect_limits("psu1", "psu", None)
        assert limits["voltage_upper"] == 5.0

    def test_channel_specific_limits(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu1", 1)] = {"voltage_upper": 3.3}
        safety = SafetySystem(ctx)
        limits = safety.collect_limits("psu1", "psu", 1)
        assert limits["voltage_upper"] == 3.3

    def test_lower_limit_more_restrictive(self):
        """Higher lower limit wins (more restrictive)."""
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu1", None)] = {"voltage_lower": 1.0}
        ctx.safety_limits[("psu", None)] = {"voltage_lower": 0.5}
        safety = SafetySystem(ctx)
        limits = safety.collect_limits("psu1", "psu", None)
        assert limits["voltage_lower"] == 1.0


# ---------------------------------------------------------------------------
# check_psu_limits
# ---------------------------------------------------------------------------


class TestCheckPsuLimits:
    def test_no_limits_returns_true(self):
        ctx = make_ctx_with_devices({})
        safety = SafetySystem(ctx)
        assert safety.check_psu_limits("psu1", None, voltage=5.0) is True

    def test_voltage_within_limit(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu1", None)] = {"voltage_upper": 12.0}
        safety = SafetySystem(ctx)
        assert safety.check_psu_limits("psu1", None, voltage=5.0) is True

    def test_voltage_exceeds_upper_limit(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu1", None)] = {"voltage_upper": 5.0}
        safety = SafetySystem(ctx)
        assert safety.check_psu_limits("psu1", None, voltage=10.0) is False

    def test_voltage_below_lower_limit(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu1", None)] = {"voltage_lower": 1.0}
        safety = SafetySystem(ctx)
        assert safety.check_psu_limits("psu1", None, voltage=0.5) is False

    def test_current_exceeds_upper(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu1", None)] = {"current_upper": 0.1}
        safety = SafetySystem(ctx)
        assert safety.check_psu_limits("psu1", None, current=1.0) is False

    def test_current_below_lower(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu1", None)] = {"current_lower": 0.01}
        safety = SafetySystem(ctx)
        assert safety.check_psu_limits("psu1", None, current=0.001) is False

    def test_with_channel(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("psu1", 1)] = {"voltage_upper": 3.3}
        safety = SafetySystem(ctx)
        assert safety.check_psu_limits("psu1", 1, voltage=5.0) is False
        assert safety.check_psu_limits("psu1", 1, voltage=3.0) is True


# ---------------------------------------------------------------------------
# check_awg_limits
# ---------------------------------------------------------------------------


class TestCheckAwgLimits:
    def test_no_limits_returns_true(self):
        ctx = make_ctx_with_devices({})
        safety = SafetySystem(ctx)
        assert safety.check_awg_limits("awg1", 1, new_vpp=5.0) is True

    def test_vpp_exceeds_upper(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("awg1", 1)] = {"vpp_upper": 3.0}
        safety = SafetySystem(ctx)
        assert safety.check_awg_limits("awg1", 1, new_vpp=5.0) is False

    def test_vpp_within_limit(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("awg1", 1)] = {"vpp_upper": 10.0}
        safety = SafetySystem(ctx)
        assert safety.check_awg_limits("awg1", 1, new_vpp=5.0) is True

    def test_freq_exceeds_upper(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("awg1", 1)] = {"freq_upper": 1000.0}
        safety = SafetySystem(ctx)
        assert safety.check_awg_limits("awg1", 1, new_freq=5000.0) is False

    def test_freq_below_lower(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("awg1", 1)] = {"freq_lower": 100.0}
        safety = SafetySystem(ctx)
        assert safety.check_awg_limits("awg1", 1, new_freq=10.0) is False

    def test_vpeak_upper_exceeded(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("awg1", 1)] = {"vpeak_upper": 2.0}
        safety = SafetySystem(ctx)
        # vpp=4.0, offset=0 => peak = 2.0, trough = -2.0
        assert safety.check_awg_limits("awg1", 1, new_vpp=5.0, new_offset=0.0) is False

    def test_vtrough_lower_exceeded(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("awg1", 1)] = {"vtrough_lower": -1.0}
        safety = SafetySystem(ctx)
        # vpp=5.0, offset=0 => trough = -2.5 < -1.0
        assert safety.check_awg_limits("awg1", 1, new_vpp=5.0, new_offset=0.0) is False

    def test_vpp_unknown_with_peak_limit(self):
        ctx = make_ctx_with_devices({})
        ctx.safety_limits[("awg1", 1)] = {"vpeak_upper": 2.0}
        ctx.registry.devices["awg1"] = MockAWG()
        safety = SafetySystem(ctx)
        # No vpp known — should be blocked
        assert safety.check_awg_limits("awg1", 1, new_vpp=None) is False


# ---------------------------------------------------------------------------
# check_psu_output_allowed
# ---------------------------------------------------------------------------


class TestCheckPsuOutputAllowed:
    def test_no_limits_allows(self):
        ctx = make_ctx_with_devices({})
        safety = SafetySystem(ctx)
        assert safety.check_psu_output_allowed("psu1") is True

    def test_voltage_known_within_limits(self):
        dev = MockHP_E3631A()
        dev._voltage = 3.0
        dev._current = 0.1
        ctx = make_ctx_with_devices({"psu1": dev})
        ctx.safety_limits[("psu1", None)] = {"voltage_upper": 5.0}
        safety = SafetySystem(ctx)
        assert safety.check_psu_output_allowed("psu1") is True

    def test_voltage_exceeds_limit_blocked(self):
        dev = MockHP_E3631A()
        dev._voltage = 10.0
        dev._current = 0.1
        ctx = make_ctx_with_devices({"psu1": dev})
        ctx.safety_limits[("psu1", None)] = {"voltage_upper": 5.0}
        safety = SafetySystem(ctx)
        assert safety.check_psu_output_allowed("psu1") is False

    def test_unknown_state_blocked_when_limits_set(self):
        """Device with no get_voltage_setpoint — state unknown."""
        dev = MagicMock(spec=[])  # no methods
        ctx = make_ctx_with_devices({"psu1": dev})
        ctx.safety_limits[("psu1", None)] = {"voltage_upper": 5.0}
        safety = SafetySystem(ctx)
        assert safety.check_psu_output_allowed("psu1") is False


# ---------------------------------------------------------------------------
# check_awg_output_allowed
# ---------------------------------------------------------------------------


class TestCheckAwgOutputAllowed:
    def test_no_limits_allows(self):
        ctx = make_ctx_with_devices({})
        safety = SafetySystem(ctx)
        assert safety.check_awg_output_allowed("awg1", 1) is True

    def test_vpp_within_limits(self):
        dev = MockAWG()
        ctx = make_ctx_with_devices({"awg1": dev})
        ctx.safety_limits[("awg1", 1)] = {"vpp_upper": 10.0}
        ctx.awg_channel_state[("awg1", 1)] = {"vpp": 2.0, "offset": 0.0}
        safety = SafetySystem(ctx)
        assert safety.check_awg_output_allowed("awg1", 1) is True

    def test_vpp_exceeds_limit(self):
        dev = MockAWG()
        ctx = make_ctx_with_devices({"awg1": dev})
        ctx.safety_limits[("awg1", 1)] = {"vpp_upper": 2.0}
        ctx.awg_channel_state[("awg1", 1)] = {"vpp": 5.0, "offset": 0.0}
        safety = SafetySystem(ctx)
        assert safety.check_awg_output_allowed("awg1", 1) is False

    def test_unknown_state_blocked_when_limits_set(self):
        dev = MagicMock(spec=[])
        ctx = make_ctx_with_devices({"awg1": dev})
        ctx.safety_limits[("awg1", 1)] = {"vpp_upper": 5.0}
        safety = SafetySystem(ctx)
        assert safety.check_awg_output_allowed("awg1", 1) is False


# ---------------------------------------------------------------------------
# retroactive_limit_check_all
# ---------------------------------------------------------------------------


class TestRetroactiveLimitCheckAll:
    def test_no_devices_no_crash(self):
        ctx = make_ctx_with_devices({})
        safety = SafetySystem(ctx)
        safety.retroactive_limit_check_all()

    def test_psu_violation_output_on_auto_disabled(self, capsys):
        dev = MockHP_E3631A()
        dev._voltage = 10.0
        dev._current = 0.1
        dev._output = True
        ctx = make_ctx_with_devices({"psu1": dev})
        ctx.safety_limits[("psu1", None)] = {"voltage_upper": 5.0}
        safety = SafetySystem(ctx)
        safety.retroactive_limit_check_all()
        # Output should be auto-disabled
        assert dev._output is False

    def test_psu_violation_output_off_warning(self, capsys):
        dev = MockHP_E3631A()
        dev._voltage = 10.0
        dev._current = 0.1
        dev._output = False
        ctx = make_ctx_with_devices({"psu1": dev})
        ctx.safety_limits[("psu1", None)] = {"voltage_upper": 5.0}
        safety = SafetySystem(ctx)
        safety.retroactive_limit_check_all()
        out = capsys.readouterr().out
        assert "Retroactive" in out or "exceeds" in out

    def test_psu_current_violation(self, capsys):
        dev = MockHP_E3631A()
        dev._voltage = 3.0
        dev._current = 2.0
        dev._output = True
        ctx = make_ctx_with_devices({"psu1": dev})
        ctx.safety_limits[("psu1", None)] = {"current_upper": 0.5}
        safety = SafetySystem(ctx)
        safety.retroactive_limit_check_all()
        assert dev._output is False

    def test_psu_lower_violation(self, capsys):
        dev = MockHP_E3631A()
        dev._voltage = 0.5
        dev._current = 0.1
        dev._output = True
        ctx = make_ctx_with_devices({"psu1": dev})
        ctx.safety_limits[("psu1", None)] = {"voltage_lower": 1.0}
        safety = SafetySystem(ctx)
        safety.retroactive_limit_check_all()
        assert dev._output is False

    def test_awg_no_state_skipped(self):
        dev = MockAWG()
        ctx = make_ctx_with_devices({"awg1": dev})
        ctx.safety_limits[("awg1", 1)] = {"vpp_upper": 5.0}
        # No awg_channel_state set, no get_amplitude/offset/frequency — state unknown
        safety = SafetySystem(ctx)
        # Should complete without crash
        safety.retroactive_limit_check_all()

    def test_awg_vpp_violation(self, capsys):
        dev = MockAWG()
        dev._ch_output = {1: True, 2: False}
        ctx = make_ctx_with_devices({"awg1": dev})
        ctx.safety_limits[("awg1", 1)] = {"vpp_upper": 1.0}
        ctx.awg_channel_state[("awg1", 1)] = {"vpp": 5.0, "offset": 0.0}
        safety = SafetySystem(ctx)
        safety.retroactive_limit_check_all()
        out = capsys.readouterr().out
        assert "SAFETY" in out or "Retroactive" in out

    def test_awg_freq_limit_but_unknown(self, capsys):
        dev = MockAWG()
        ctx = make_ctx_with_devices({"awg1": dev})
        ctx.safety_limits[("awg1", 1)] = {"freq_upper": 1000.0}
        ctx.awg_channel_state[("awg1", 1)] = {"vpp": 1.0, "offset": 0.0}
        safety = SafetySystem(ctx)
        safety.retroactive_limit_check_all()
        out = capsys.readouterr().out
        assert "freq" in out.lower() or "manually" in out.lower()


# ---------------------------------------------------------------------------
# query_awg_state / query_psu_state
# ---------------------------------------------------------------------------


class TestQueryState:
    def test_query_psu_state_no_device(self):
        ctx = make_ctx_with_devices({})
        safety = SafetySystem(ctx)
        state = safety.query_psu_state("nonexistent")
        assert state["voltage"] is None
        assert state["current"] is None

    def test_query_psu_state_mock(self):
        dev = MockHP_E3631A()
        dev._voltage = 5.0
        dev._current = 0.1
        ctx = make_ctx_with_devices({"psu1": dev})
        safety = SafetySystem(ctx)
        state = safety.query_psu_state("psu1")
        assert state["voltage"] == 5.0
        assert state["current"] == 0.1

    def test_query_awg_state_no_device(self):
        ctx = make_ctx_with_devices({})
        safety = SafetySystem(ctx)
        state = safety.query_awg_state("nonexistent", 1)
        assert state["vpp"] is None

    def test_query_awg_state_with_cached(self):
        dev = MockAWG()
        ctx = make_ctx_with_devices({"awg1": dev})
        ctx.awg_channel_state[("awg1", 1)] = {"vpp": 3.0, "offset": 0.5}
        safety = SafetySystem(ctx)
        state = safety.query_awg_state("awg1", 1)
        assert state["vpp"] is not None

    def test_update_awg_state(self):
        ctx = make_ctx_with_devices({})
        safety = SafetySystem(ctx)
        safety.update_awg_state("awg1", 1, vpp=3.0, offset=0.5)
        assert ctx.awg_channel_state[("awg1", 1)]["vpp"] == 3.0
        assert ctx.awg_channel_state[("awg1", 1)]["offset"] == 0.5


# ---------------------------------------------------------------------------
# REPL-level safety commands via make_repl
# ---------------------------------------------------------------------------


def make_repl(devices=None):
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices or {}
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl()
    repl._scan_thread.join(timeout=5.0)
    repl._scan_done.wait(timeout=5.0)
    repl.devices = devices or {}
    return repl


class TestSafetyViaRepl:
    def test_upper_limit_psu(self, capsys):
        repl = make_repl({"psu1": MockHP_E3631A()})
        repl.onecmd("upper_limit psu1 voltage 5.0")
        out = capsys.readouterr().out
        assert "Limit" in out or "limit" in out.lower()

    def test_lower_limit_psu(self, capsys):
        repl = make_repl({"psu1": MockHP_E3631A()})
        repl.onecmd("lower_limit psu1 voltage 0.0")
        out = capsys.readouterr().out
        assert out != ""

    def test_upper_limit_awg(self, capsys):
        repl = make_repl({"awg1": MockAWG()})
        repl.onecmd("upper_limit awg1 vpp 5.0")
        out = capsys.readouterr().out
        assert out != ""

    def test_upper_limit_awg_freq(self, capsys):
        repl = make_repl({"awg1": MockAWG()})
        repl.onecmd("upper_limit awg1 freq 10000")
        out = capsys.readouterr().out
        assert out != ""

    def test_upper_limit_chan(self, capsys):
        repl = make_repl({"awg1": MockAWG()})
        repl.onecmd("upper_limit awg1 chan 1 vpp 5.0")
        out = capsys.readouterr().out
        assert out != ""
