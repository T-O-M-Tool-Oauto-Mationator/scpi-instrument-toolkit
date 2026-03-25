"""Tests for HP 34401A DMM driver — targeting missed lines."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def dmm(hp_34401a):
    device, mock_inst = hp_34401a
    mock_inst.query.return_value = "5.000000E+00"
    return device, mock_inst


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestContextManager:
    def test_enter_exit(self, dmm):
        device, mock_inst = dmm
        with device:
            pass
        # Should call reset on exit
        mock_inst.write.assert_called()


# ---------------------------------------------------------------------------
# configure methods
# ---------------------------------------------------------------------------


class TestConfigure:
    def test_configure_dc_voltage(self, dmm):
        device, mock_inst = dmm
        device.configure_dc_voltage()
        mock_inst.write.assert_called()

    def test_configure_dc_voltage_with_nplc(self, dmm):
        device, mock_inst = dmm
        device.configure_dc_voltage(range_val=10, resolution=0.001, nplc=1)
        assert mock_inst.write.call_count >= 2

    def test_configure_ac_voltage(self, dmm):
        device, mock_inst = dmm
        device.configure_ac_voltage()
        mock_inst.write.assert_called()

    def test_configure_dc_current(self, dmm):
        device, mock_inst = dmm
        device.configure_dc_current()
        mock_inst.write.assert_called()

    def test_configure_dc_current_with_nplc(self, dmm):
        device, mock_inst = dmm
        device.configure_dc_current(nplc=10)
        assert mock_inst.write.call_count >= 2

    def test_configure_ac_current(self, dmm):
        device, mock_inst = dmm
        device.configure_ac_current()
        mock_inst.write.assert_called()

    def test_configure_resistance_2wire(self, dmm):
        device, mock_inst = dmm
        device.configure_resistance_2wire()
        mock_inst.write.assert_called()

    def test_configure_resistance_2wire_nplc(self, dmm):
        device, mock_inst = dmm
        device.configure_resistance_2wire(nplc=0.2)
        assert mock_inst.write.call_count >= 2

    def test_configure_resistance_4wire(self, dmm):
        device, mock_inst = dmm
        device.configure_resistance_4wire()
        mock_inst.write.assert_called()

    def test_configure_resistance_4wire_nplc(self, dmm):
        device, mock_inst = dmm
        device.configure_resistance_4wire(nplc=100)
        assert mock_inst.write.call_count >= 2

    def test_configure_frequency(self, dmm):
        device, mock_inst = dmm
        device.configure_frequency()
        mock_inst.write.assert_called()

    def test_configure_period(self, dmm):
        device, mock_inst = dmm
        device.configure_period()
        mock_inst.write.assert_called()

    def test_configure_continuity(self, dmm):
        device, mock_inst = dmm
        device.configure_continuity()
        mock_inst.write.assert_called()

    def test_configure_diode(self, dmm):
        device, mock_inst = dmm
        device.configure_diode()
        mock_inst.write.assert_called()


# ---------------------------------------------------------------------------
# read / fetch
# ---------------------------------------------------------------------------


class TestReadFetch:
    def test_read_single(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "5.000000E+00"
        val = device.read()
        assert isinstance(val, float)

    def test_read_multiple(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "5.0,4.9,5.1"
        val = device.read()
        assert abs(val - 5.0) < 0.5

    def test_read_invalid_raises(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "NOT_A_NUMBER"
        with pytest.raises(ValueError):
            device.read()

    def test_fetch_single(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "3.300000E+00"
        val = device.fetch()
        assert isinstance(val, float)

    def test_fetch_multiple(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "1.0,2.0,3.0"
        val = device.fetch()
        assert abs(val - 2.0) < 0.01

    def test_fetch_invalid_raises(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "INVALID"
        with pytest.raises(ValueError):
            device.fetch()


# ---------------------------------------------------------------------------
# measure methods
# ---------------------------------------------------------------------------


class TestMeasure:
    def test_measure_dc_voltage(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "5.0"
        result = device.measure_dc_voltage()
        assert isinstance(result, float)

    def test_measure_ac_voltage(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "3.3"
        result = device.measure_ac_voltage()
        assert isinstance(result, float)

    def test_measure_dc_current(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "0.01"
        result = device.measure_dc_current()
        assert isinstance(result, float)

    def test_measure_ac_current(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "0.05"
        result = device.measure_ac_current()
        assert isinstance(result, float)

    def test_measure_resistance_2wire(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "100.0"
        result = device.measure_resistance_2wire()
        assert isinstance(result, float)

    def test_measure_resistance_4wire(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "99.5"
        result = device.measure_resistance_4wire()
        assert isinstance(result, float)

    def test_measure_frequency(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "1000.0"
        result = device.measure_frequency()
        assert isinstance(result, float)

    def test_measure_period(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "0.001"
        result = device.measure_period()
        assert isinstance(result, float)

    def test_measure_continuity(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "5.0"
        result = device.measure_continuity()
        assert isinstance(result, float)

    def test_measure_continuity_invalid(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "BAD"
        with pytest.raises(ValueError):
            device.measure_continuity()

    def test_measure_diode(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "0.6"
        result = device.measure_diode()
        assert isinstance(result, float)

    def test_measure_diode_invalid(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "BAD"
        with pytest.raises(ValueError):
            device.measure_diode()


# ---------------------------------------------------------------------------
# Trigger configuration
# ---------------------------------------------------------------------------


class TestTrigger:
    def test_set_trigger_source_imm(self, dmm):
        device, mock_inst = dmm
        device.set_trigger_source("IMM")
        mock_inst.write.assert_called()

    def test_set_trigger_source_bus(self, dmm):
        device, mock_inst = dmm
        device.set_trigger_source("BUS")
        mock_inst.write.assert_called()

    def test_set_trigger_source_ext(self, dmm):
        device, mock_inst = dmm
        device.set_trigger_source("EXT")
        mock_inst.write.assert_called()

    def test_set_trigger_source_invalid(self, dmm):
        device, mock_inst = dmm
        with pytest.raises(ValueError):
            device.set_trigger_source("INVALID")

    def test_set_trigger_delay(self, dmm):
        device, mock_inst = dmm
        device.set_trigger_delay(0.1)
        mock_inst.write.assert_called()

    def test_set_sample_count(self, dmm):
        device, mock_inst = dmm
        device.set_sample_count(10)
        mock_inst.write.assert_called()

    def test_set_trigger_count(self, dmm):
        device, mock_inst = dmm
        device.set_trigger_count(5)
        mock_inst.write.assert_called()

    def test_trigger(self, dmm):
        device, mock_inst = dmm
        device.trigger()
        mock_inst.write.assert_called()

    def test_init(self, dmm):
        device, mock_inst = dmm
        device.init()
        mock_inst.write.assert_called()


# ---------------------------------------------------------------------------
# System & utility
# ---------------------------------------------------------------------------


class TestSystemUtility:
    def test_get_error(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = '+0,"No error"'
        err = device.get_error()
        assert "error" in err.lower() or err != ""

    def test_set_display_on(self, dmm):
        device, mock_inst = dmm
        device.set_display(True)
        mock_inst.write.assert_called()

    def test_set_display_off(self, dmm):
        device, mock_inst = dmm
        device.set_display(False)
        mock_inst.write.assert_called()

    def test_display_text(self, dmm):
        device, mock_inst = dmm
        device.display_text("HELLO WORLD")
        mock_inst.write.assert_called()

    def test_clear_display_text(self, dmm):
        device, mock_inst = dmm
        device.clear_display_text()
        mock_inst.write.assert_called()

    def test_clear_display(self, dmm):
        device, mock_inst = dmm
        device.clear_display()
        mock_inst.write.assert_called()

    def test_set_beeper_on(self, dmm):
        device, mock_inst = dmm
        device.set_beeper(True)
        mock_inst.write.assert_called()

    def test_set_beeper_off(self, dmm):
        device, mock_inst = dmm
        device.set_beeper(False)
        mock_inst.write.assert_called()

    def test_beep(self, dmm):
        device, mock_inst = dmm
        device.beep()
        mock_inst.write.assert_called()

    def test_display_text_rolling_short(self, dmm, monkeypatch):
        """Short text: calls display_text directly."""
        import lab_instruments.src.hp_34401a as mod

        monkeypatch.setattr(mod.time, "sleep", lambda _: None)
        device, mock_inst = dmm
        device.display_text_rolling("HI", width=12)
        mock_inst.write.assert_called()

    def test_display_text_rolling_long(self, dmm, monkeypatch):
        """Long text: scrolls through frames."""
        import lab_instruments.src.hp_34401a as mod

        monkeypatch.setattr(mod.time, "sleep", lambda _: None)
        device, mock_inst = dmm
        device.display_text_rolling("THIS IS A LONG MESSAGE", width=12, delay=0, loops=1)
        mock_inst.write.assert_called()

    def test_display_text_rolling_invalid_width(self, dmm):
        device, mock_inst = dmm
        with pytest.raises(ValueError):
            device.display_text_rolling("text", width=0)

    def test_display_text_scroll(self, dmm, monkeypatch):
        import lab_instruments.src.hp_34401a as mod

        monkeypatch.setattr(mod.time, "sleep", lambda _: None)
        device, mock_inst = dmm
        device.display_text_scroll("HELLO WORLD EXTENDED")
        mock_inst.write.assert_called()
