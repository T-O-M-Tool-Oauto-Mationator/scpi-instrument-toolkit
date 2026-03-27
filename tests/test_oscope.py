"""Oscilloscope driver tests using mock instruments.

Exercises channel control, measurements, scales, triggers, waveform capture,
and delay measurements through the MockScope/MockDHO804 mock layer.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockDHO804, MockEDU33212A


@pytest.fixture
def oscope():
    return MockDHO804()


@pytest.fixture
def awg():
    return MockEDU33212A()


class TestChannelControl:
    def test_enable_channel(self, oscope):
        for ch in [1, 2, 3, 4]:
            oscope.enable_channel(ch)

    def test_disable_channel(self, oscope):
        for ch in [1, 2, 3, 4]:
            oscope.disable_channel(ch)

    def test_enable_disable_all(self, oscope):
        oscope.enable_all_channels()
        oscope.disable_all_channels()


class TestBasicMeasurements:
    def test_frequency_measurement(self, oscope):
        oscope.enable_channel(1)
        freq = oscope.measure_frequency(1)
        assert 900 < freq < 1100

    def test_pk2pk_measurement(self, oscope):
        oscope.enable_channel(1)
        pk2pk = oscope.measure_peak_to_peak(1)
        assert 1.5 < pk2pk < 2.5

    def test_rms_measurement(self, oscope):
        oscope.enable_channel(1)
        rms = oscope.measure_rms(1)
        assert 0.5 < rms < 1.0


class TestMeasurementTypes:
    def test_all_measurement_types(self, oscope):
        oscope.enable_channel(1)
        measurements = {
            "Frequency": oscope.measure_frequency(1),
            "Period": oscope.measure_period(1),
            "Peak-to-Peak": oscope.measure_peak_to_peak(1),
            "RMS": oscope.measure_rms(1),
            "Mean": oscope.measure_mean(1),
            "Maximum": oscope.measure_max(1),
            "Minimum": oscope.measure_min(1),
        }
        for name, value in measurements.items():
            assert isinstance(value, float), f"{name} should be a float"

    def test_measure_bnf_fallback(self, oscope):
        val = oscope.measure_bnf(1, "UNKNOWN_TYPE")
        assert isinstance(val, float)


class TestScales:
    def test_vertical_scales(self, oscope):
        for scale in [0.5, 1.0, 2.0]:
            oscope.set_vertical_scale(1, scale)

    def test_horizontal_scales(self, oscope):
        for scale in [0.0001, 0.001, 0.01]:
            oscope.set_horizontal_scale(scale)

    def test_probe_attenuation(self, oscope):
        oscope.set_probe_attenuation(1, 10.0)
        oscope.set_probe_attenuation(1, 1.0)

    def test_coupling(self, oscope):
        oscope.set_coupling(1, "DC")
        oscope.set_coupling(1, "AC")


class TestTrigger:
    def test_configure_trigger_rising(self, oscope):
        oscope.configure_trigger(1, level=0.5, slope="RISE", mode="NORMAL")

    def test_configure_trigger_falling(self, oscope):
        oscope.configure_trigger(1, level=0.5, slope="FALL", mode="NORMAL")


class TestWaveformCapture:
    def test_get_waveform_data(self, oscope):
        oscope.enable_channel(1)
        raw_data = oscope.get_waveform_data(1)
        assert len(raw_data) > 0

    def test_get_waveform_scaled(self, oscope):
        oscope.enable_channel(1)
        time_vals, volt_vals = oscope.get_waveform_scaled(1)
        assert len(time_vals) == len(volt_vals)
        assert len(time_vals) > 0
        assert min(volt_vals) < 0 < max(volt_vals)


class TestDelayMeasurement:
    def test_delay_between_channels(self, oscope):
        oscope.enable_channel(1)
        oscope.enable_channel(2)
        delay = oscope.measure_delay(1, 2)
        assert isinstance(delay, float)
        assert abs(delay) < 1e-3  # should be microsecond-scale
