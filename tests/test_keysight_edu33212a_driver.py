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
