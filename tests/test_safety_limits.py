"""Tests for the safety limit system (lower_limit/upper_limit directives, AWG/PSU guards)."""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockEDU33212A, MockHP_E3631A, MockMPS6010H


def make_repl(devices):
    from lab_instruments.src import discovery as _disc
    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices
    from lab_instruments.repl import InstrumentRepl
    repl = InstrumentRepl()
    repl._scan_done.set()
    repl.devices = devices
    return repl


@pytest.fixture
def awg_repl():
    return make_repl({"awg1": MockEDU33212A()})


@pytest.fixture
def psu_repl():
    return make_repl({"psu1": MockHP_E3631A()})


@pytest.fixture
def two_psu_repl():
    return make_repl({"psu1": MockHP_E3631A(), "psu2": MockMPS6010H()})


# ---------------------------------------------------------------------------
# Limit parsing — new lower_limit / upper_limit syntax
# ---------------------------------------------------------------------------

class TestLowerUpperParsing:
    def test_upper_limit_awg_vpeak(self, awg_repl):
        awg_repl._expand_script_lines(["upper_limit awg vpeak 5.0"], {})
        assert awg_repl._safety_limits[("awg", None)]["vpeak_upper"] == 5.0

    def test_lower_limit_awg_vtrough(self, awg_repl):
        awg_repl._expand_script_lines(["lower_limit awg vtrough -5.0"], {})
        assert awg_repl._safety_limits[("awg", None)]["vtrough_lower"] == -5.0

    def test_upper_limit_awg_vpp(self, awg_repl):
        awg_repl._expand_script_lines(["upper_limit awg vpp 10.0"], {})
        assert awg_repl._safety_limits[("awg", None)]["vpp_upper"] == 10.0

    def test_upper_limit_awg_freq(self, awg_repl):
        awg_repl._expand_script_lines(["upper_limit awg freq 1000000"], {})
        assert awg_repl._safety_limits[("awg", None)]["freq_upper"] == 1_000_000.0

    def test_upper_limit_psu_voltage(self, psu_repl):
        psu_repl._expand_script_lines(["upper_limit psu voltage 15.0"], {})
        assert psu_repl._safety_limits[("psu", None)]["voltage_upper"] == 15.0

    def test_upper_limit_psu_current(self, psu_repl):
        psu_repl._expand_script_lines(["upper_limit psu current 2.0"], {})
        assert psu_repl._safety_limits[("psu", None)]["current_upper"] == 2.0

    def test_no_chan_stores_none_channel(self, awg_repl):
        awg_repl._expand_script_lines(["upper_limit awg vpeak 5.0"], {})
        assert ("awg", None) in awg_repl._safety_limits

    def test_chan_explicit_stores_integer_channel(self, awg_repl):
        awg_repl._expand_script_lines(["upper_limit awg chan 1 vpeak 5.0"], {})
        assert awg_repl._safety_limits[("awg", 1)]["vpeak_upper"] == 5.0

    def test_named_device_psu1(self, psu_repl):
        psu_repl._expand_script_lines(["upper_limit psu1 voltage 3.3"], {})
        assert psu_repl._safety_limits[("psu1", None)]["voltage_upper"] == 3.3

    def test_named_device_with_chan(self, psu_repl):
        psu_repl._expand_script_lines(["upper_limit psu1 chan 1 voltage 3.3"], {})
        assert psu_repl._safety_limits[("psu1", 1)]["voltage_upper"] == 3.3

    def test_unknown_param_sets_error(self, awg_repl):
        awg_repl._expand_script_lines(["upper_limit awg bogus_key 1.0"], {})
        assert awg_repl._command_had_error

    def test_unknown_device_sets_error(self, awg_repl):
        awg_repl._expand_script_lines(["upper_limit osc vpeak 1.0"], {})
        assert awg_repl._command_had_error

    def test_bad_value_sets_error(self, awg_repl):
        awg_repl._expand_script_lines(["upper_limit awg vpeak notanumber"], {})
        assert awg_repl._command_had_error


# ---------------------------------------------------------------------------
# AWG amp limits
# ---------------------------------------------------------------------------

class TestAwgAmpLimits:
    def _set_limits(self, repl, **kw):
        _MAP = {
            "vpp_max":     "upper_limit awg vpp",
            "vpeak_max":   "upper_limit awg vpeak",
            "vtrough_min": "lower_limit awg vtrough",
            "freq_max":    "upper_limit awg freq",
        }
        lines = [f"{_MAP[k]} {v}" for k, v in kw.items()]
        repl._expand_script_lines(lines, {})

    def test_amp_below_vpp_max_passes(self, awg_repl):
        self._set_limits(awg_repl, vpp_max=10.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg amp 1 5.0")
        assert not awg_repl._command_had_error

    def test_amp_exactly_at_vpp_max_passes(self, awg_repl):
        self._set_limits(awg_repl, vpp_max=5.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg amp 1 5.0")
        assert not awg_repl._command_had_error

    def test_amp_over_vpp_max_fails(self, awg_repl):
        self._set_limits(awg_repl, vpp_max=4.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg amp 1 5.0")
        assert awg_repl._command_had_error

    def test_peak_exceeded_via_amp(self, awg_repl):
        # offset=3, vpp=5 → peak=5.5 > 5.0
        self._set_limits(awg_repl, vpeak_max=5.0)
        awg_repl._update_awg_state("awg1", 1, offset=3.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg amp 1 5.0")
        assert awg_repl._command_had_error

    def test_peak_ok_with_pre_tracked_offset(self, awg_repl):
        # offset=1, vpp=4 → peak=3.0 < 5.0
        self._set_limits(awg_repl, vpeak_max=5.0)
        awg_repl._update_awg_state("awg1", 1, offset=1.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg amp 1 4.0")
        assert not awg_repl._command_had_error


# ---------------------------------------------------------------------------
# AWG offset limits
# ---------------------------------------------------------------------------

class TestAwgOffsetLimits:
    def _set_limits(self, repl, **kw):
        _MAP = {
            "vpp_max":     "upper_limit awg vpp",
            "vpeak_max":   "upper_limit awg vpeak",
            "vtrough_min": "lower_limit awg vtrough",
            "freq_max":    "upper_limit awg freq",
        }
        repl._expand_script_lines([f"{_MAP[k]} {v}" for k, v in kw.items()], {})

    def test_offset_pushes_peak_over_limit(self, awg_repl):
        # vpp=4, offset=4 → peak=6.0 > 5.0
        self._set_limits(awg_repl, vpeak_max=5.0)
        awg_repl._update_awg_state("awg1", 1, vpp=4.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg offset 1 4.0")
        assert awg_repl._command_had_error

    def test_offset_pushes_trough_below_limit(self, awg_repl):
        # vpp=4, offset=-4 → trough=-6.0 < -5.0
        self._set_limits(awg_repl, vtrough_min=-5.0)
        awg_repl._update_awg_state("awg1", 1, vpp=4.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg offset 1 -4.0")
        assert awg_repl._command_had_error

    def test_offset_within_limits(self, awg_repl):
        # vpp=2, offset=2 → peak=3, trough=1 — both fine
        self._set_limits(awg_repl, vpeak_max=5.0, vtrough_min=-5.0)
        awg_repl._update_awg_state("awg1", 1, vpp=2.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg offset 1 2.0")
        assert not awg_repl._command_had_error

    def test_offset_exactly_at_boundary(self, awg_repl):
        # vpp=4, offset=3 → peak=5.0 == 5.0 (not exceeded)
        self._set_limits(awg_repl, vpeak_max=5.0)
        awg_repl._update_awg_state("awg1", 1, vpp=4.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg offset 1 3.0")
        assert not awg_repl._command_had_error


# ---------------------------------------------------------------------------
# AWG freq limits
# ---------------------------------------------------------------------------

class TestAwgFreqLimits:
    def _set_limits(self, repl, **kw):
        _MAP = {
            "vpp_max":     "upper_limit awg vpp",
            "vpeak_max":   "upper_limit awg vpeak",
            "vtrough_min": "lower_limit awg vtrough",
            "freq_max":    "upper_limit awg freq",
        }
        repl._expand_script_lines([f"{_MAP[k]} {v}" for k, v in kw.items()], {})

    def test_freq_below_limit_passes(self, awg_repl):
        self._set_limits(awg_repl, freq_max=1000000)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg freq 1 500000")
        assert not awg_repl._command_had_error

    def test_freq_over_limit_fails(self, awg_repl):
        self._set_limits(awg_repl, freq_max=1000000)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg freq 1 2000000")
        assert awg_repl._command_had_error

    def test_freq_exactly_at_limit_passes(self, awg_repl):
        self._set_limits(awg_repl, freq_max=1000000)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg freq 1 1000000")
        assert not awg_repl._command_had_error


# ---------------------------------------------------------------------------
# AWG wave limits
# ---------------------------------------------------------------------------

class TestAwgWaveLimits:
    def _set_limits(self, repl, **kw):
        _MAP = {
            "vpp_max":     "upper_limit awg vpp",
            "vpeak_max":   "upper_limit awg vpeak",
            "vtrough_min": "lower_limit awg vtrough",
            "freq_max":    "upper_limit awg freq",
        }
        repl._expand_script_lines([f"{_MAP[k]} {v}" for k, v in kw.items()], {})

    def test_wave_amp_over_vpp_max_fails(self, awg_repl):
        self._set_limits(awg_repl, vpp_max=4.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg wave 1 sine freq=1000 amp=5.0")
        assert awg_repl._command_had_error

    def test_wave_amp_and_offset_peak_exceeded(self, awg_repl):
        # amp=4, offset=4 → peak=6 > 5
        self._set_limits(awg_repl, vpeak_max=5.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg wave 1 sine freq=1000 amp=4.0 offset=4.0")
        assert awg_repl._command_had_error

    def test_wave_amp_and_offset_trough_exceeded(self, awg_repl):
        # amp=4, offset=-4 → trough=-6 < -5
        self._set_limits(awg_repl, vtrough_min=-5.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg wave 1 sine freq=1000 amp=4.0 offset=-4.0")
        assert awg_repl._command_had_error

    def test_wave_within_limits_passes(self, awg_repl):
        self._set_limits(awg_repl, vpp_max=10.0, vpeak_max=5.0, vtrough_min=-5.0, freq_max=1000000)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg wave 1 sine freq=1000 amp=4.0 offset=0.0")
        assert not awg_repl._command_had_error

    def test_wave_freq_over_limit_fails(self, awg_repl):
        self._set_limits(awg_repl, freq_max=1000)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg wave 1 sine freq=5000 amp=1.0")
        assert awg_repl._command_had_error


# ---------------------------------------------------------------------------
# PSU limits
# ---------------------------------------------------------------------------

class TestPsuLimits:
    def _set_limits(self, repl, **kw):
        _MAP = {
            "voltage_max": "upper_limit psu voltage",
            "current_max": "upper_limit psu current",
        }
        repl._expand_script_lines([f"{_MAP[k]} {v}" for k, v in kw.items()], {})

    def test_voltage_over_limit_fails(self, psu_repl):
        self._set_limits(psu_repl, voltage_max=10.0)
        psu_repl._command_had_error = False
        psu_repl.onecmd("psu set 12.0")
        assert psu_repl._command_had_error

    def test_voltage_at_exact_limit_passes(self, psu_repl):
        self._set_limits(psu_repl, voltage_max=10.0)
        psu_repl._command_had_error = False
        psu_repl.onecmd("psu set 10.0")
        assert not psu_repl._command_had_error

    def test_voltage_under_limit_passes(self, psu_repl):
        self._set_limits(psu_repl, voltage_max=15.0)
        psu_repl._command_had_error = False
        psu_repl.onecmd("psu set 5.0")
        assert not psu_repl._command_had_error

    def test_current_over_limit_fails(self, psu_repl):
        self._set_limits(psu_repl, current_max=1.0)
        psu_repl._command_had_error = False
        psu_repl.onecmd("psu set 5.0 2.0")
        assert psu_repl._command_had_error

    def test_current_at_exact_limit_passes(self, psu_repl):
        self._set_limits(psu_repl, current_max=2.0)
        psu_repl._command_had_error = False
        psu_repl.onecmd("psu set 5.0 2.0")
        assert not psu_repl._command_had_error

    def test_no_limits_always_passes(self, psu_repl):
        # No limit directives — should never block
        psu_repl._command_had_error = False
        psu_repl.onecmd("psu set 99.0 99.0")
        assert not psu_repl._command_had_error


# ---------------------------------------------------------------------------
# Per-channel PSU limits
# ---------------------------------------------------------------------------

class TestPerChannelPsuLimits:
    def test_ch1_upper_blocks_ch1(self, psu_repl):
        psu_repl._expand_script_lines(["upper_limit psu chan 1 voltage 2.1"], {})
        assert not psu_repl._check_psu_limits("psu1", 1, voltage=3.0)

    def test_ch1_limit_does_not_restrict_ch2(self, psu_repl):
        psu_repl._expand_script_lines(["upper_limit psu chan 1 voltage 2.1"], {})
        assert psu_repl._check_psu_limits("psu1", 2, voltage=5.0)

    def test_lower_bound_blocks_voltage_below(self, psu_repl):
        psu_repl._expand_script_lines(["lower_limit psu chan 1 voltage 0.5"], {})
        assert not psu_repl._check_psu_limits("psu1", 1, voltage=0.1)

    def test_value_within_window_passes(self, psu_repl):
        psu_repl._expand_script_lines([
            "lower_limit psu chan 1 voltage 0.5",
            "upper_limit psu chan 1 voltage 2.1",
        ], {})
        assert psu_repl._check_psu_limits("psu1", 1, voltage=1.5)

    def test_value_at_upper_boundary_passes(self, psu_repl):
        psu_repl._expand_script_lines(["upper_limit psu chan 1 voltage 2.1"], {})
        assert psu_repl._check_psu_limits("psu1", 1, voltage=2.1)

    def test_value_at_lower_boundary_passes(self, psu_repl):
        psu_repl._expand_script_lines(["lower_limit psu chan 1 voltage 0.5"], {})
        assert psu_repl._check_psu_limits("psu1", 1, voltage=0.5)


# ---------------------------------------------------------------------------
# Hierarchical limit lookup — tightest bound wins
# ---------------------------------------------------------------------------

class TestHierarchicalLookup:
    def test_channel_limit_tightens_type_wide(self, psu_repl):
        # type-wide: ≤5V; ch1-specific: ≤2.1V → ch1 sees 2.1V cap
        psu_repl._expand_script_lines([
            "upper_limit psu voltage 5.0",
            "upper_limit psu chan 1 voltage 2.1",
        ], {})
        assert not psu_repl._check_psu_limits("psu1", 1, voltage=3.0)

    def test_ch2_still_passes_type_wide(self, psu_repl):
        psu_repl._expand_script_lines([
            "upper_limit psu voltage 5.0",
            "upper_limit psu chan 1 voltage 2.1",
        ], {})
        assert psu_repl._check_psu_limits("psu1", 2, voltage=4.0)

    def test_ch2_blocked_by_type_wide_limit(self, psu_repl):
        psu_repl._expand_script_lines([
            "upper_limit psu voltage 5.0",
            "upper_limit psu chan 1 voltage 2.1",
        ], {})
        assert not psu_repl._check_psu_limits("psu1", 2, voltage=6.0)

    def test_named_device_limit_tightens_type_limit(self, psu_repl):
        # type-wide: ≤5V; named psu1: ≤3.3V → psu1 sees 3.3V cap
        psu_repl._expand_script_lines([
            "upper_limit psu voltage 5.0",
            "upper_limit psu1 voltage 3.3",
        ], {})
        assert not psu_repl._check_psu_limits("psu1", None, voltage=4.0)

    def test_type_wide_limit_still_applies_via_named(self, psu_repl):
        # Only named limit set; type-wide applies too via hierarchy
        psu_repl._expand_script_lines(["upper_limit psu1 voltage 3.3"], {})
        assert not psu_repl._check_psu_limits("psu1", None, voltage=4.0)
        assert psu_repl._check_psu_limits("psu1", None, voltage=3.0)


# ---------------------------------------------------------------------------
# Named-device limits
# ---------------------------------------------------------------------------

class TestNamedDeviceLimits:
    def test_psu1_limit_applies_to_psu1(self, two_psu_repl):
        two_psu_repl._expand_script_lines(["upper_limit psu1 voltage 2.1"], {})
        assert not two_psu_repl._check_psu_limits("psu1", None, voltage=3.0)

    def test_psu1_limit_does_not_affect_psu2(self, two_psu_repl):
        two_psu_repl._expand_script_lines(["upper_limit psu1 voltage 2.1"], {})
        assert two_psu_repl._check_psu_limits("psu2", None, voltage=3.0)

    def test_type_wide_limit_affects_all_devices(self, two_psu_repl):
        two_psu_repl._expand_script_lines(["upper_limit psu voltage 5.0"], {})
        assert not two_psu_repl._check_psu_limits("psu1", None, voltage=6.0)
        two_psu_repl._command_had_error = False
        assert not two_psu_repl._check_psu_limits("psu2", None, voltage=6.0)

    def test_named_awg_limit_does_not_affect_other_awg(self, awg_repl):
        awg_repl._expand_script_lines(["upper_limit awg1 vpeak 3.0"], {})
        # awg2 not in devices but limit key ("awg2", None) simply won't match
        result = awg_repl._check_awg_limits("awg2", 1, new_vpp=2.0, new_offset=2.0)
        assert result  # peak=3.0 — no limit for awg2 → passes


# ---------------------------------------------------------------------------
# Limit reset between scripts
# ---------------------------------------------------------------------------

class TestLimitReset:
    def test_limits_cleared_between_scripts(self, awg_repl):
        # First script sets limits
        awg_repl._expand_script_lines(["upper_limit awg vpp 4.0"], {})
        assert awg_repl._safety_limits.get(("awg", None), {}).get("vpp_upper") == 4.0

        # Second script at depth=0 clears them
        awg_repl._expand_script_lines(["awg amp 1 2.0"], {})
        assert awg_repl._safety_limits == {}

    def test_awg_state_cleared_between_scripts(self, awg_repl):
        # Manually plant some state
        awg_repl._awg_channel_state[("awg1", 1)] = {"vpp": 3.0, "offset": 1.0}

        # New top-level script call clears it
        awg_repl._expand_script_lines(["awg amp 1 1.0"], {})
        assert awg_repl._awg_channel_state == {}

    def test_nested_call_does_not_reset(self, awg_repl):
        # depth > 0 should NOT clear limits
        awg_repl._safety_limits = {("awg", None): {"vpp_upper": 5.0}}
        awg_repl._expand_script_lines(["awg amp 1 1.0"], {}, depth=1)
        assert awg_repl._safety_limits == {("awg", None): {"vpp_upper": 5.0}}


# ---------------------------------------------------------------------------
# Interactive REPL handlers — do_upper_limit / do_lower_limit
# ---------------------------------------------------------------------------

class TestInteractiveLimitCommands:
    """Verify that upper_limit / lower_limit work at the interactive REPL prompt."""

    # --- PSU ---

    def test_interactive_upper_limit_psu_stores_limit(self, psu_repl):
        psu_repl.onecmd("upper_limit psu voltage 5.0")
        assert psu_repl._safety_limits.get(("psu", None), {}).get("voltage_upper") == 5.0

    def test_interactive_lower_limit_psu_stores_limit(self, psu_repl):
        psu_repl.onecmd("lower_limit psu voltage 0.5")
        assert psu_repl._safety_limits.get(("psu", None), {}).get("voltage_lower") == 0.5

    def test_interactive_upper_limit_psu_blocks_command(self, psu_repl):
        psu_repl.onecmd("upper_limit psu voltage 3.0")
        psu_repl._command_had_error = False
        psu_repl.onecmd("psu set 5.0")
        assert psu_repl._command_had_error

    def test_interactive_upper_limit_psu_allows_safe_command(self, psu_repl):
        psu_repl.onecmd("upper_limit psu voltage 10.0")
        psu_repl._command_had_error = False
        psu_repl.onecmd("psu set 5.0")
        assert not psu_repl._command_had_error

    def test_interactive_upper_limit_psu_chan_stores_correctly(self, psu_repl):
        psu_repl.onecmd("upper_limit psu chan 1 voltage 2.1")
        assert psu_repl._safety_limits.get(("psu", 1), {}).get("voltage_upper") == 2.1

    def test_interactive_upper_limit_psu_current(self, psu_repl):
        psu_repl.onecmd("upper_limit psu current 1.5")
        assert psu_repl._safety_limits.get(("psu", None), {}).get("current_upper") == 1.5

    def test_interactive_limit_does_not_bleed_error_state(self, psu_repl):
        # An error in the limit directive itself should NOT permanently set _command_had_error
        psu_repl._command_had_error = False
        psu_repl.onecmd("upper_limit psu voltage notanumber")
        # After the handler returns, the outer error state is restored to False
        assert not psu_repl._command_had_error

    def test_interactive_limits_persist_across_multiple_commands(self, psu_repl):
        psu_repl.onecmd("upper_limit psu voltage 5.0")
        psu_repl.onecmd("upper_limit psu current 1.0")
        assert psu_repl._safety_limits.get(("psu", None), {}).get("voltage_upper") == 5.0
        assert psu_repl._safety_limits.get(("psu", None), {}).get("current_upper") == 1.0

    # --- AWG ---

    def test_interactive_upper_limit_awg_vpeak_stores_limit(self, awg_repl):
        awg_repl.onecmd("upper_limit awg vpeak 5.0")
        assert awg_repl._safety_limits.get(("awg", None), {}).get("vpeak_upper") == 5.0

    def test_interactive_lower_limit_awg_vtrough_stores_limit(self, awg_repl):
        awg_repl.onecmd("lower_limit awg vtrough -0.3")
        assert awg_repl._safety_limits.get(("awg", None), {}).get("vtrough_lower") == -0.3

    def test_interactive_upper_limit_awg_vpp_stores_limit(self, awg_repl):
        awg_repl.onecmd("upper_limit awg vpp 10.0")
        assert awg_repl._safety_limits.get(("awg", None), {}).get("vpp_upper") == 10.0

    def test_interactive_upper_limit_awg_freq_stores_limit(self, awg_repl):
        awg_repl.onecmd("upper_limit awg freq 1e6")
        assert awg_repl._safety_limits.get(("awg", None), {}).get("freq_upper") == 1_000_000.0

    def test_interactive_upper_limit_awg_blocks_amp_command(self, awg_repl):
        awg_repl.onecmd("upper_limit awg vpp 4.0")
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg amp 1 5.0")
        assert awg_repl._command_had_error

    def test_interactive_upper_limit_awg_allows_safe_amp(self, awg_repl):
        awg_repl.onecmd("upper_limit awg vpp 10.0")
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg amp 1 5.0")
        assert not awg_repl._command_had_error

    def test_interactive_lower_limit_awg_blocks_trough(self, awg_repl):
        # offset=-3, vpp=4 → trough=-5 < -3 → blocked
        awg_repl.onecmd("lower_limit awg vtrough -3.0")
        awg_repl._update_awg_state("awg1", 1, vpp=4.0)
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg offset 1 -3.0")
        assert awg_repl._command_had_error

    def test_interactive_upper_limit_awg_chan_stores_correctly(self, awg_repl):
        awg_repl.onecmd("upper_limit awg chan 1 vpeak 3.3")
        assert awg_repl._safety_limits.get(("awg", 1), {}).get("vpeak_upper") == 3.3

    def test_interactive_upper_limit_awg_blocks_wave_command(self, awg_repl):
        awg_repl.onecmd("upper_limit awg freq 1000")
        awg_repl._command_had_error = False
        awg_repl.onecmd("awg wave 1 sine freq=5000 amp=1.0")
        assert awg_repl._command_had_error

    def test_interactive_awg_limits_accumulate(self, awg_repl):
        awg_repl.onecmd("upper_limit awg vpeak 5.0")
        awg_repl.onecmd("lower_limit awg vtrough -0.3")
        awg_repl.onecmd("upper_limit awg freq 1e6")
        assert awg_repl._safety_limits.get(("awg", None), {}).get("vpeak_upper") == 5.0
        assert awg_repl._safety_limits.get(("awg", None), {}).get("vtrough_lower") == -0.3
        assert awg_repl._safety_limits.get(("awg", None), {}).get("freq_upper") == 1_000_000.0
