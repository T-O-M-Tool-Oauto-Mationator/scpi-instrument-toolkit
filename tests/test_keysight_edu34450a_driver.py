"""Tests for Keysight EDU34450A DMM driver."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def dmm(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.keysight_edu34450a import Keysight_EDU34450A

    dev = Keysight_EDU34450A("USB::0x2A8D::0x8E01::INSTR")
    dev.instrument = mock_instrument
    mock_instrument.reset_mock()
    mock_instrument.query.return_value = "5.000000E+00"
    return dev, mock_instrument


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
# Configure modes
# ---------------------------------------------------------------------------


class TestConfigureModes:
    def test_configure_dc_voltage(self, dmm):
        device, mock_inst = dmm
        device.configure_dc_voltage()
        mock_inst.write.assert_called_with("CONFigure:VOLTage:DC DEF,DEF")

    def test_configure_dc_voltage_with_range(self, dmm):
        device, mock_inst = dmm
        device.configure_dc_voltage(range_val=10, resolution=0.001)
        mock_inst.write.assert_called_with("CONFigure:VOLTage:DC 10,0.001")

    def test_configure_ac_voltage(self, dmm):
        device, mock_inst = dmm
        device.configure_ac_voltage()
        mock_inst.write.assert_called_with("CONFigure:VOLTage:AC DEF,DEF")

    def test_configure_dc_current(self, dmm):
        device, mock_inst = dmm
        device.configure_dc_current()
        mock_inst.write.assert_called_with("CONFigure:CURRent:DC DEF,DEF")

    def test_configure_ac_current(self, dmm):
        device, mock_inst = dmm
        device.configure_ac_current()
        mock_inst.write.assert_called_with("CONFigure:CURRent:AC DEF,DEF")

    def test_configure_resistance_2wire(self, dmm):
        device, mock_inst = dmm
        device.configure_resistance_2wire()
        mock_inst.write.assert_called_with("CONFigure:RESistance DEF,DEF")

    def test_configure_resistance_4wire(self, dmm):
        device, mock_inst = dmm
        device.configure_resistance_4wire()
        mock_inst.write.assert_called_with("CONFigure:FRESistance DEF,DEF")

    def test_configure_frequency(self, dmm):
        device, mock_inst = dmm
        device.configure_frequency()
        mock_inst.write.assert_called_with("CONFigure:FREQuency DEF,DEF")

    def test_configure_period(self, dmm):
        device, mock_inst = dmm
        device.configure_period()
        mock_inst.write.assert_called_with("CONFigure:PERiod DEF,DEF")

    def test_configure_continuity(self, dmm):
        device, mock_inst = dmm
        device.configure_continuity()
        mock_inst.write.assert_called_with("CONFigure:CONTinuity")

    def test_configure_diode(self, dmm):
        device, mock_inst = dmm
        device.configure_diode()
        mock_inst.write.assert_called_with("CONFigure:DIODe")

    def test_configure_capacitance_default(self, dmm):
        device, mock_inst = dmm
        device.configure_capacitance()
        mock_inst.write.assert_called_with("CONFigure:CAPacitance DEF")

    def test_configure_capacitance_with_range(self, dmm):
        device, mock_inst = dmm
        device.configure_capacitance(range_val=1e-6)
        mock_inst.write.assert_called_with("CONFigure:CAPacitance 1e-06")

    def test_configure_temperature(self, dmm):
        device, mock_inst = dmm
        device.configure_temperature()
        mock_inst.write.assert_called_with("CONFigure:TEMPerature")


# ---------------------------------------------------------------------------
# Read / Fetch
# ---------------------------------------------------------------------------


class TestReadFetch:
    def test_read_single(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "5.000000E+00"
        val = device.read()
        assert isinstance(val, float)
        assert val == pytest.approx(5.0)

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
        assert val == pytest.approx(3.3)

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
# Measure modes
# ---------------------------------------------------------------------------


class TestMeasureModes:
    def test_measure_dc_voltage(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "5.0"
        result = device.measure_dc_voltage()
        assert isinstance(result, float)
        assert result == pytest.approx(5.0)

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


class TestTriggerConfig:
    def test_set_trigger_source_imm(self, dmm):
        device, mock_inst = dmm
        device.set_trigger_source("IMM")
        mock_inst.write.assert_called_with("TRIGger:SOURce IMM")

    def test_set_trigger_source_bus(self, dmm):
        device, mock_inst = dmm
        device.set_trigger_source("BUS")
        mock_inst.write.assert_called_with("TRIGger:SOURce BUS")

    def test_set_trigger_source_ext(self, dmm):
        device, mock_inst = dmm
        device.set_trigger_source("EXT")
        mock_inst.write.assert_called_with("TRIGger:SOURce EXT")

    def test_set_trigger_source_invalid(self, dmm):
        device, mock_inst = dmm
        with pytest.raises(ValueError):
            device.set_trigger_source("INVALID")

    def test_set_trigger_delay(self, dmm):
        device, mock_inst = dmm
        device.set_trigger_delay(0.1)
        mock_inst.write.assert_called_with("TRIGger:DELay 0.1")

    def test_set_trigger_delay_default(self, dmm):
        device, mock_inst = dmm
        device.set_trigger_delay()
        mock_inst.write.assert_called_with("TRIGger:DELay MIN")

    def test_set_sample_count(self, dmm):
        device, mock_inst = dmm
        device.set_sample_count(10)
        mock_inst.write.assert_called_with("SAMPle:COUNt 10")

    def test_set_sample_count_default(self, dmm):
        device, mock_inst = dmm
        device.set_sample_count()
        mock_inst.write.assert_called_with("SAMPle:COUNt 1")

    def test_trigger(self, dmm):
        device, mock_inst = dmm
        device.trigger()
        mock_inst.write.assert_called_with("*TRG")

    def test_init(self, dmm):
        device, mock_inst = dmm
        device.init()
        mock_inst.write.assert_called_with("INITiate")


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------


class TestDisplay:
    def test_set_display_on(self, dmm):
        device, mock_inst = dmm
        device.set_display(True)
        mock_inst.write.assert_called_with("DISPlay ON")

    def test_set_display_off(self, dmm):
        device, mock_inst = dmm
        device.set_display(False)
        mock_inst.write.assert_called_with("DISPlay OFF")

    def test_display_text(self, dmm):
        device, mock_inst = dmm
        device.display_text("HELLO WORLD")
        mock_inst.write.assert_called_with('DISPlay:TEXT "HELLO WORLD"')

    def test_display_text_truncation(self, dmm):
        device, mock_inst = dmm
        device.display_text("THIS IS TOO LONG FOR DISPLAY")
        mock_inst.write.assert_called_with('DISPlay:TEXT "THIS IS TOO "')

    def test_clear_display_text(self, dmm):
        device, mock_inst = dmm
        device.clear_display_text()
        mock_inst.write.assert_called_with("DISPlay:TEXT:CLEar")

    def test_clear_display_alias(self, dmm):
        device, mock_inst = dmm
        device.clear_display()
        mock_inst.write.assert_called_with("DISPlay:TEXT:CLEar")


# ---------------------------------------------------------------------------
# Beeper
# ---------------------------------------------------------------------------


class TestBeeper:
    def test_set_beeper_on(self, dmm):
        device, mock_inst = dmm
        device.set_beeper(True)
        mock_inst.write.assert_called_with("SYSTem:BEEPer:STATe ON")

    def test_set_beeper_off(self, dmm):
        device, mock_inst = dmm
        device.set_beeper(False)
        mock_inst.write.assert_called_with("SYSTem:BEEPer:STATe OFF")

    def test_beep(self, dmm):
        device, mock_inst = dmm
        device.beep()
        mock_inst.write.assert_called_with("SYSTem:BEEPer")


# ---------------------------------------------------------------------------
# Get error
# ---------------------------------------------------------------------------


class TestGetError:
    def test_get_error(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = '+0,"No error"'
        err = device.get_error()
        assert "error" in err.lower() or err != ""

    def test_get_error_with_error(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = '-100,"Command error"'
        err = device.get_error()
        assert "-100" in err


# ---------------------------------------------------------------------------
# Set mode
# ---------------------------------------------------------------------------


class TestSetMode:
    def test_set_mode_vdc(self, dmm):
        device, mock_inst = dmm
        device.set_mode("vdc")
        mock_inst.write.assert_called_with("CONFigure:VOLTage:DC DEF,DEF")

    def test_set_mode_dc_voltage(self, dmm):
        device, mock_inst = dmm
        device.set_mode("dc_voltage")
        mock_inst.write.assert_called_with("CONFigure:VOLTage:DC DEF,DEF")

    def test_set_mode_vac(self, dmm):
        device, mock_inst = dmm
        device.set_mode("vac")
        mock_inst.write.assert_called_with("CONFigure:VOLTage:AC DEF,DEF")

    def test_set_mode_ac_voltage(self, dmm):
        device, mock_inst = dmm
        device.set_mode("ac_voltage")
        mock_inst.write.assert_called_with("CONFigure:VOLTage:AC DEF,DEF")

    def test_set_mode_idc(self, dmm):
        device, mock_inst = dmm
        device.set_mode("idc")
        mock_inst.write.assert_called_with("CONFigure:CURRent:DC DEF,DEF")

    def test_set_mode_iac(self, dmm):
        device, mock_inst = dmm
        device.set_mode("iac")
        mock_inst.write.assert_called_with("CONFigure:CURRent:AC DEF,DEF")

    def test_set_mode_res(self, dmm):
        device, mock_inst = dmm
        device.set_mode("res")
        mock_inst.write.assert_called_with("CONFigure:RESistance DEF,DEF")

    def test_set_mode_fres(self, dmm):
        device, mock_inst = dmm
        device.set_mode("fres")
        mock_inst.write.assert_called_with("CONFigure:FRESistance DEF,DEF")

    def test_set_mode_freq(self, dmm):
        device, mock_inst = dmm
        device.set_mode("freq")
        mock_inst.write.assert_called_with("CONFigure:FREQuency DEF,DEF")

    def test_set_mode_period(self, dmm):
        device, mock_inst = dmm
        device.set_mode("period")
        mock_inst.write.assert_called_with("CONFigure:PERiod DEF,DEF")

    def test_set_mode_cont(self, dmm):
        device, mock_inst = dmm
        device.set_mode("cont")
        mock_inst.write.assert_called_with("CONFigure:CONTinuity")

    def test_set_mode_diode(self, dmm):
        device, mock_inst = dmm
        device.set_mode("diode")
        mock_inst.write.assert_called_with("CONFigure:DIODe")

    def test_set_mode_cap(self, dmm):
        device, mock_inst = dmm
        device.set_mode("cap")
        mock_inst.write.assert_called_with("CONFigure:CAPacitance DEF")

    def test_set_mode_capacitance(self, dmm):
        device, mock_inst = dmm
        device.set_mode("capacitance")
        mock_inst.write.assert_called_with("CONFigure:CAPacitance DEF")

    def test_set_mode_temp(self, dmm):
        device, mock_inst = dmm
        device.set_mode("temp")
        mock_inst.write.assert_called_with("CONFigure:TEMPerature")

    def test_set_mode_temperature(self, dmm):
        device, mock_inst = dmm
        device.set_mode("temperature")
        mock_inst.write.assert_called_with("CONFigure:TEMPerature")

    def test_set_mode_case_insensitive(self, dmm):
        device, mock_inst = dmm
        device.set_mode("VDC")
        mock_inst.write.assert_called_with("CONFigure:VOLTage:DC DEF,DEF")

    def test_set_mode_invalid(self, dmm):
        device, mock_inst = dmm
        with pytest.raises(ValueError, match="Unknown mode"):
            device.set_mode("invalid_mode")


# ---------------------------------------------------------------------------
# Capacitance
# ---------------------------------------------------------------------------


class TestCapacitance:
    def test_configure_capacitance_default(self, dmm):
        device, mock_inst = dmm
        device.configure_capacitance()
        mock_inst.write.assert_called_with("CONFigure:CAPacitance DEF")

    def test_configure_capacitance_with_range(self, dmm):
        device, mock_inst = dmm
        device.configure_capacitance(range_val=1e-9)
        mock_inst.write.assert_called_with("CONFigure:CAPacitance 1e-09")

    def test_measure_capacitance_default(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "1.5e-09"
        result = device.measure_capacitance()
        assert isinstance(result, float)
        assert result == pytest.approx(1.5e-9)

    def test_measure_capacitance_with_range(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "4.7e-06"
        result = device.measure_capacitance(range_val=10e-6)
        assert isinstance(result, float)
        assert result == pytest.approx(4.7e-6)

    def test_measure_capacitance_invalid(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "BAD"
        with pytest.raises(ValueError):
            device.measure_capacitance()


# ---------------------------------------------------------------------------
# Temperature
# ---------------------------------------------------------------------------


class TestTemperature:
    def test_configure_temperature(self, dmm):
        device, mock_inst = dmm
        device.configure_temperature()
        mock_inst.write.assert_called_with("CONFigure:TEMPerature")

    def test_measure_temperature(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "25.3"
        result = device.measure_temperature()
        assert isinstance(result, float)
        assert result == pytest.approx(25.3)

    def test_measure_temperature_negative(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "-10.5"
        result = device.measure_temperature()
        assert isinstance(result, float)
        assert result == pytest.approx(-10.5)

    def test_measure_temperature_invalid(self, dmm):
        device, mock_inst = dmm
        mock_inst.query.return_value = "BAD"
        with pytest.raises(ValueError):
            device.measure_temperature()
