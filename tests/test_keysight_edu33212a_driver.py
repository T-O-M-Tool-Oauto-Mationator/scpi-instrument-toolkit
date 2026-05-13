"""Tests for Keysight EDU33212A AWG driver — targeting missed coverage lines."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def awg(keysight_edu33212a):
    device, mock_inst = keysight_edu33212a
    mock_inst.query.return_value = "1.000000E+00"
    return device, mock_inst


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestContextManager:
    def test_enter_exit(self, awg):
        device, mock_inst = awg
        with device:
            pass
        mock_inst.write.assert_called()


# ---------------------------------------------------------------------------
# Output control
# ---------------------------------------------------------------------------


class TestOutputControl:
    def test_enable_output_ch1(self, awg):
        device, mock_inst = awg
        device.enable_output(1, True)
        mock_inst.write.assert_called()

    def test_disable_output_ch2(self, awg):
        device, mock_inst = awg
        device.enable_output(2, False)
        mock_inst.write.assert_called()

    def test_enable_invalid_channel(self, awg):
        device, mock_inst = awg
        with pytest.raises(ValueError):
            device.enable_output(3, True)

    def test_disable_all_channels(self, awg):
        device, mock_inst = awg
        device.disable_all_channels()
        assert mock_inst.write.call_count > 0

    def test_disable_all_channels_uses_MIN_not_zero(self, awg):
        """Regression: previously wrote FREQuency 0.0 / VOLTage 0.0 which the
        instrument silently clipped, polluting the error queue with -222.
        The fix uses SCPI MINimum so the parked values are documented-valid."""
        device, mock_inst = awg
        device.disable_all_channels()
        cmds = [c.args[0] for c in mock_inst.write.call_args_list]
        # Each channel must park freq and amplitude at MINimum, not 0.0
        for ch in (1, 2):
            assert f"SOURce{ch}:FREQuency MINimum" in cmds
            assert f"SOURce{ch}:VOLTage MINimum" in cmds
            # And must NOT have written the old 0.0 forms
            assert f"SOURce{ch}:FREQuency 0.0" not in cmds
            assert f"SOURce{ch}:VOLTage 0.0" not in cmds
            # Output must be disabled at the end
            assert f"OUTPut{ch} OFF" in cmds

    def test_set_output_load_inf(self, awg):
        device, mock_inst = awg
        device.set_output_load(1, "INF")
        mock_inst.write.assert_called()

    def test_set_output_load_50(self, awg):
        device, mock_inst = awg
        device.set_output_load(1, 50)
        mock_inst.write.assert_called()

    def test_set_output_load_infinity_string(self, awg):
        device, mock_inst = awg
        device.set_output_load(1, "INFINITY")
        mock_inst.write.assert_called()

    def test_set_output_polarity_normal(self, awg):
        device, mock_inst = awg
        device.set_output_polarity(1, True)
        mock_inst.write.assert_called()

    def test_set_output_polarity_inverted(self, awg):
        device, mock_inst = awg
        device.set_output_polarity(1, False)
        mock_inst.write.assert_called()

    def test_set_sync_output(self, awg):
        device, mock_inst = awg
        device.set_sync_output(True)
        mock_inst.write.assert_called()


# ---------------------------------------------------------------------------
# Query methods
# ---------------------------------------------------------------------------


class TestQueryMethods:
    def test_get_amplitude(self, awg):
        device, mock_inst = awg
        mock_inst.query.return_value = "2.0"
        val = device.get_amplitude(1)
        assert isinstance(val, float)

    def test_get_offset(self, awg):
        device, mock_inst = awg
        mock_inst.query.return_value = "0.5"
        val = device.get_offset(1)
        assert isinstance(val, float)

    def test_get_frequency(self, awg):
        device, mock_inst = awg
        mock_inst.query.return_value = "1000.0"
        val = device.get_frequency(1)
        assert isinstance(val, float)

    def test_get_output_state_on(self, awg):
        device, mock_inst = awg
        mock_inst.query.return_value = "1"
        assert device.get_output_state(1) is True

    def test_get_output_state_off(self, awg):
        device, mock_inst = awg
        mock_inst.query.return_value = "0"
        assert device.get_output_state(1) is False


# ---------------------------------------------------------------------------
# Waveform config
# ---------------------------------------------------------------------------


class TestWaveformConfig:
    def test_set_function_sin(self, awg):
        device, mock_inst = awg
        device.set_function(1, "SIN")
        mock_inst.write.assert_called()

    def test_set_function_invalid(self, awg):
        device, mock_inst = awg
        with pytest.raises(ValueError):
            device.set_function(1, "INVALID_WAVE")

    def test_set_frequency(self, awg):
        device, mock_inst = awg
        device.set_frequency(1, 1000.0)
        mock_inst.write.assert_called()

    def test_set_amplitude(self, awg):
        device, mock_inst = awg
        device.set_amplitude(1, 2.0)
        mock_inst.write.assert_called()

    def test_set_offset(self, awg):
        device, mock_inst = awg
        device.set_offset(1, 0.5)
        mock_inst.write.assert_called()

    def test_set_high_low(self, awg):
        device, mock_inst = awg
        device.set_high_low(1, 2.5, 0.5)
        assert mock_inst.write.call_count >= 2

    def test_set_voltage_unit_vpp(self, awg):
        device, mock_inst = awg
        device.set_voltage_unit(1, "VPP")
        mock_inst.write.assert_called()

    def test_set_voltage_unit_invalid(self, awg):
        device, mock_inst = awg
        with pytest.raises(ValueError):
            device.set_voltage_unit(1, "INVALID")

    def test_set_square_duty(self, awg):
        device, mock_inst = awg
        device.set_square_duty(1, 50.0)
        mock_inst.write.assert_called()

    def test_set_ramp_symmetry(self, awg):
        device, mock_inst = awg
        device.set_ramp_symmetry(1, 50.0)
        mock_inst.write.assert_called()

    def test_set_dc_output(self, awg):
        device, mock_inst = awg
        device.set_dc_output(1, 1.0)
        assert mock_inst.write.call_count >= 1


# ---------------------------------------------------------------------------
# set_waveform convenience method
# ---------------------------------------------------------------------------


class TestSetWaveform:
    def test_set_waveform_sin(self, awg):
        device, mock_inst = awg
        device.set_waveform(1, "SIN", frequency=1000, amplitude=1.0, offset=0.0)
        mock_inst.write.assert_called()

    def test_set_waveform_square_duty(self, awg):
        device, mock_inst = awg
        device.set_waveform(1, "SQU", frequency=1000, amplitude=1.0, duty=50)
        mock_inst.write.assert_called()

    def test_set_waveform_ramp_symmetry(self, awg):
        device, mock_inst = awg
        device.set_waveform(1, "RAMP", frequency=500, amplitude=1.0, symmetry=50)
        mock_inst.write.assert_called()

    def test_set_waveform_pulse_duty(self, awg):
        device, mock_inst = awg
        device.set_waveform(1, "PULS", frequency=1000, amplitude=1.0, duty=10)
        mock_inst.write.assert_called()

    def test_set_waveform_noise(self, awg):
        device, mock_inst = awg
        device.set_waveform(1, "NOIS", amplitude=1.0)
        mock_inst.write.assert_called()

    def test_set_waveform_dc(self, awg):
        device, mock_inst = awg
        device.set_waveform(1, "DC")
        mock_inst.write.assert_called()

    def test_set_waveform_invalid(self, awg):
        device, mock_inst = awg
        with pytest.raises(ValueError):
            device.set_waveform(1, "INVALID_WAVE")

    def test_set_waveform_ch2(self, awg):
        device, mock_inst = awg
        device.set_waveform(2, "SIN", frequency=2000, amplitude=0.5)
        mock_inst.write.assert_called()


# ---------------------------------------------------------------------------
# Modulation
# ---------------------------------------------------------------------------


class TestModulation:
    def test_set_am_on(self, awg):
        device, mock_inst = awg
        device.set_am(1, True, depth=100, mod_freq=10, mod_func="SIN")
        assert mock_inst.write.call_count >= 2

    def test_set_am_off(self, awg):
        device, mock_inst = awg
        device.set_am(1, False)
        mock_inst.write.assert_called()

    def test_set_fm_on(self, awg):
        device, mock_inst = awg
        device.set_fm(1, True, deviation=100, mod_freq=10)
        mock_inst.write.assert_called()

    def test_set_fm_off(self, awg):
        device, mock_inst = awg
        device.set_fm(1, False)
        mock_inst.write.assert_called()

    def test_set_fsk_on(self, awg):
        device, mock_inst = awg
        device.set_fsk(1, True, hop_freq=500, rate=5)
        mock_inst.write.assert_called()

    def test_set_fsk_off(self, awg):
        device, mock_inst = awg
        device.set_fsk(1, False)
        mock_inst.write.assert_called()


# ---------------------------------------------------------------------------
# Numeric validation (Rule 5) — bounds taken from EDU33210 Series User's Guide
# ---------------------------------------------------------------------------


class TestNumericValidation:
    def test_set_square_duty_below_min_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r"out of range"):
            device.set_square_duty(1, 0.0)

    def test_set_square_duty_above_max_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError):
            device.set_square_duty(1, 100.0)

    def test_set_square_duty_at_edges_passes(self, awg):
        device, mock_inst = awg
        device.set_square_duty(1, 0.01)
        device.set_square_duty(1, 99.99)
        assert mock_inst.write.call_count >= 2

    def test_set_ramp_symmetry_below_min_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError):
            device.set_ramp_symmetry(1, -1.0)

    def test_set_ramp_symmetry_above_max_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError):
            device.set_ramp_symmetry(1, 100.1)

    def test_set_pulse_width_below_min_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r">= 16 ns"):
            device.set_pulse_width(1, 10e-9)

    def test_set_pulse_width_at_min_passes(self, awg):
        device, mock_inst = awg
        device.set_pulse_width(1, 16e-9)
        mock_inst.write.assert_called_with("SOURce1:FUNCtion:PULSe:WIDTh 1.6e-08")

    def test_set_pulse_duty_out_of_range_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError):
            device.set_pulse_duty(1, 100.0)

    def test_set_pulse_edge_leading_too_short_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r"leading edge .* out of range"):
            device.set_pulse_edge(1, leading=1e-9)

    def test_set_pulse_edge_trailing_too_long_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r"trailing edge .* out of range"):
            device.set_pulse_edge(1, trailing=10e-6)

    def test_set_pulse_edge_within_range_passes(self, awg):
        device, mock_inst = awg
        device.set_pulse_edge(1, leading=10e-9, trailing=500e-9)
        cmds = [c.args[0] for c in mock_inst.write.call_args_list]
        assert any("LEADing 1e-08" in c for c in cmds)
        assert any("TRAiling 5e-07" in c for c in cmds)

    def test_set_am_depth_above_120_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r"AM depth"):
            device.set_am(1, True, depth=121.0)

    def test_set_am_depth_state_off_skips_validation(self, awg):
        # When state=False, depth is unused so validation is skipped.
        device, mock_inst = awg
        device.set_am(1, False, depth=999.0)
        mock_inst.write.assert_called_with("SOURce1:AM:STATe OFF")

    def test_set_pm_deviation_above_360_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r"PM deviation"):
            device.set_pm(1, True, deviation=361.0)

    def test_set_burst_n_cycles_zero_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r"n_cycles"):
            device.set_burst(1, True, n_cycles=0)

    def test_set_burst_n_cycles_above_max_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError):
            device.set_burst(1, True, n_cycles=100_000_001)

    def test_set_burst_phase_out_of_range_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r"phase"):
            device.set_burst(1, True, n_cycles=3, phase=361.0)

    def test_set_burst_state_off_skips_validation(self, awg):
        # When state=False, n_cycles/phase are unused.
        device, mock_inst = awg
        device.set_burst(1, False, n_cycles=99999999999, phase=999)
        mock_inst.write.assert_called_with("SOURce1:BURSt:STATe OFF")

    def test_set_pulse_period_below_min_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r"out of range"):
            device.set_pulse_period(1, 1e-9)  # 1 ns < 33 ns min

    def test_set_pulse_period_at_min_passes(self, awg):
        device, mock_inst = awg
        device.set_pulse_period(1, 33e-9)
        cmds = [c.args[0] for c in mock_inst.write.call_args_list]
        assert any("PULSe:PERiod" in c for c in cmds)

    def test_set_fm_zero_deviation_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r"FM deviation"):
            device.set_fm(1, True, deviation=0.0)

    def test_set_fm_negative_deviation_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError):
            device.set_fm(1, True, deviation=-10.0)

    def test_set_pwm_negative_deviation_raises(self, awg):
        device, _ = awg
        with pytest.raises(ValueError, match=r"PWM deviation"):
            device.set_pwm(1, True, deviation=-1e-6)


# ---------------------------------------------------------------------------
# Context manager — Rule 7: __exit__ must not mask in-block exceptions.
# ---------------------------------------------------------------------------


class TestExitDoesNotMaskExceptions:
    def test_exit_swallows_cleanup_error_so_user_exception_propagates(self, awg):
        device, mock_inst = awg
        # Enter normally; arm the side_effect just before user code raises so
        # only __exit__'s cleanup writes will fail.
        with pytest.raises(ZeroDivisionError), device:
            mock_inst.write.side_effect = RuntimeError("instrument unresponsive")
            _ = 1 / 0  # noqa: B018  user code raises
