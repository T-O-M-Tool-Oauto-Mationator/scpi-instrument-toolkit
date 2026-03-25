"""Tests for JDS6600 Generator driver — targeting missed coverage lines."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def gen(jds6600_generator):
    device, mock_inst = jds6600_generator
    mock_inst.read.return_value = ":ok."
    return device, mock_inst


# ---------------------------------------------------------------------------
# enable_output
# ---------------------------------------------------------------------------


class TestEnableOutput:
    def test_enable_both_on(self, gen):
        device, mock_inst = gen
        device.enable_output(ch1=True, ch2=True)
        mock_inst.write.assert_called()

    def test_disable_both(self, gen):
        device, mock_inst = gen
        device.enable_output(ch1=False, ch2=False)
        mock_inst.write.assert_called()

    def test_enable_ch1_only(self, gen):
        device, mock_inst = gen
        device.enable_output(ch1=True)
        mock_inst.write.assert_called()

    def test_enable_ch2_only(self, gen):
        device, mock_inst = gen
        device.enable_output(ch2=True)
        mock_inst.write.assert_called()

    def test_enable_defaults_preserve_state(self, gen):
        """Calling enable_output() with no args preserves current state."""
        device, mock_inst = gen
        device._ch1_enabled = True
        device._ch2_enabled = False
        device.enable_output()
        mock_inst.write.assert_called()


# ---------------------------------------------------------------------------
# set_waveform
# ---------------------------------------------------------------------------


class TestSetWaveform:
    def test_set_sine_ch1(self, gen):
        device, mock_inst = gen
        device.set_waveform(1, "sine")
        mock_inst.write.assert_called()

    def test_set_square_ch2(self, gen):
        device, mock_inst = gen
        device.set_waveform(2, "square")
        mock_inst.write.assert_called()

    def test_set_triangle(self, gen):
        device, mock_inst = gen
        device.set_waveform(1, "triangle")
        mock_inst.write.assert_called()

    def test_set_noise(self, gen):
        device, mock_inst = gen
        device.set_waveform(1, "noise")
        mock_inst.write.assert_called()

    def test_set_dc(self, gen):
        device, mock_inst = gen
        device.set_waveform(1, "dc")
        mock_inst.write.assert_called()

    def test_invalid_channel(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_waveform(3, "sine")

    def test_invalid_waveform(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_waveform(1, "invalid_wave_xyz")


# ---------------------------------------------------------------------------
# set_frequency
# ---------------------------------------------------------------------------


class TestSetFrequency:
    def test_set_100hz(self, gen):
        device, mock_inst = gen
        device.set_frequency(1, 100.0)
        assert device._ch_frequency[1] == 100.0

    def test_set_1khz(self, gen):
        device, mock_inst = gen
        device.set_frequency(1, 1000.0)
        assert device._ch_frequency[1] == 1000.0

    def test_set_1mhz(self, gen):
        device, mock_inst = gen
        device.set_frequency(1, 1_000_000.0)
        assert device._ch_frequency[1] == 1_000_000.0

    def test_set_20mhz_high_freq_mode(self, gen):
        device, mock_inst = gen
        device.set_frequency(1, 25_000_000.0)
        assert device._ch_frequency[1] == 25_000_000.0

    def test_set_ch2(self, gen):
        device, mock_inst = gen
        device.set_frequency(2, 500.0)
        assert device._ch_frequency[2] == 500.0

    def test_invalid_channel(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_frequency(3, 1000.0)


# ---------------------------------------------------------------------------
# set_amplitude
# ---------------------------------------------------------------------------


class TestSetAmplitude:
    def test_set_1vpp(self, gen):
        device, mock_inst = gen
        device.set_amplitude(1, 1.0)
        assert device._ch_amplitude[1] == 1.0

    def test_set_5vpp(self, gen):
        device, mock_inst = gen
        device.set_amplitude(2, 5.0)
        assert device._ch_amplitude[2] == 5.0

    def test_invalid_channel(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_amplitude(3, 1.0)


# ---------------------------------------------------------------------------
# set_offset
# ---------------------------------------------------------------------------


class TestSetOffset:
    def test_set_zero_offset(self, gen):
        device, mock_inst = gen
        device.set_offset(1, 0.0)
        assert device._ch_offset[1] == 0.0

    def test_set_positive_offset(self, gen):
        device, mock_inst = gen
        device.set_offset(1, 2.5)
        assert device._ch_offset[1] == 2.5

    def test_set_negative_offset(self, gen):
        device, mock_inst = gen
        device.set_offset(1, -3.0)
        assert device._ch_offset[1] == -3.0

    def test_clamp_high(self, gen):
        device, mock_inst = gen
        device.set_offset(1, 100.0)  # clamps to valid range
        mock_inst.write.assert_called()

    def test_invalid_channel(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_offset(3, 0.0)


# ---------------------------------------------------------------------------
# set_duty_cycle
# ---------------------------------------------------------------------------


class TestSetDutyCycle:
    def test_set_50_percent(self, gen):
        device, mock_inst = gen
        device.set_duty_cycle(1, 50.0)
        mock_inst.write.assert_called()

    def test_set_10_percent(self, gen):
        device, mock_inst = gen
        device.set_duty_cycle(1, 10.0)
        mock_inst.write.assert_called()

    def test_invalid_channel(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_duty_cycle(3, 50.0)

    def test_out_of_range_low(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_duty_cycle(1, 0.0)

    def test_out_of_range_high(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_duty_cycle(1, 100.0)


# ---------------------------------------------------------------------------
# set_phase
# ---------------------------------------------------------------------------


class TestSetPhase:
    def test_set_90_degrees(self, gen):
        device, mock_inst = gen
        device.set_phase(1, 90.0)
        mock_inst.write.assert_called()

    def test_set_zero_degrees(self, gen):
        device, mock_inst = gen
        device.set_phase(1, 0.0)
        mock_inst.write.assert_called()

    def test_invalid_channel(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_phase(3, 90.0)

    def test_invalid_phase_negative(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_phase(1, -10.0)

    def test_invalid_phase_360(self, gen):
        device, mock_inst = gen
        with pytest.raises(ValueError):
            device.set_phase(1, 360.0)


# ---------------------------------------------------------------------------
# set_sync
# ---------------------------------------------------------------------------


class TestSetSync:
    def test_sync_all_enabled(self, gen):
        device, mock_inst = gen
        device.set_sync(freq=True, waveform=True, amplitude=True, offset=True, duty=True)
        mock_inst.write.assert_called()

    def test_sync_all_disabled(self, gen):
        device, mock_inst = gen
        device.set_sync()
        mock_inst.write.assert_called()

    def test_sync_freq_only(self, gen):
        device, mock_inst = gen
        device.set_sync(freq=True)
        mock_inst.write.assert_called()


# ---------------------------------------------------------------------------
# get_amplitude / get_offset / get_frequency
# ---------------------------------------------------------------------------


class TestGetters:
    def test_get_amplitude_cached(self, gen):
        device, mock_inst = gen
        device.set_amplitude(1, 3.0)
        val = device.get_amplitude(1)
        assert val == 3.0

    def test_get_amplitude_not_set(self, gen):
        device, mock_inst = gen
        val = device.get_amplitude(1)
        assert val is None

    def test_get_offset_cached(self, gen):
        device, mock_inst = gen
        device.set_offset(1, 0.5)
        val = device.get_offset(1)
        assert val == 0.5

    def test_get_offset_not_set(self, gen):
        device, mock_inst = gen
        val = device.get_offset(1)
        assert val is None

    def test_get_frequency_cached(self, gen):
        device, mock_inst = gen
        device.set_frequency(1, 1000.0)
        val = device.get_frequency(1)
        assert val == 1000.0
