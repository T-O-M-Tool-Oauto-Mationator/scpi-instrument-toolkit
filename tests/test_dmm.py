"""tests/test_dmm.py — Driver-level unit tests for DMM drivers (no hardware required).

Replaces the previous all-skipped hardware integration test file.
"""
import pytest
from unittest.mock import patch


def _writes(mock_inst):
    """Return all SCPI strings passed to instrument.write() in call order."""
    return [c.args[0] for c in mock_inst.write.call_args_list]


# ===========================================================================
# HP_34401A
# ===========================================================================

class TestHP34401A_Configure:
    def test_configure_dc_voltage_defaults(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.configure_dc_voltage()
        mi.write.assert_called_with("CONFigure:VOLTage:DC DEF,DEF")

    def test_configure_dc_voltage_with_nplc(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.configure_dc_voltage(10, 0.001, nplc=10)
        cmds = _writes(mi)
        assert "CONFigure:VOLTage:DC 10,0.001" in cmds
        assert "SENSe:VOLTage:DC:NPLCycles 10" in cmds

    def test_configure_ac_voltage(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.configure_ac_voltage()
        mi.write.assert_called_with("CONFigure:VOLTage:AC DEF,DEF")

    def test_configure_dc_current(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.configure_dc_current()
        mi.write.assert_called_with("CONFigure:CURRent:DC DEF,DEF")

    def test_configure_resistance_2wire(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.configure_resistance_2wire()
        mi.write.assert_called_with("CONFigure:RESistance DEF,DEF")

    def test_configure_resistance_4wire(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.configure_resistance_4wire()
        mi.write.assert_called_with("CONFigure:FRESistance DEF,DEF")

    def test_configure_continuity(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.configure_continuity()
        mi.write.assert_called_with("CONFigure:CONTinuity")

    def test_configure_diode(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.configure_diode()
        mi.write.assert_called_with("CONFigure:DIODe")


class TestHP34401A_Read:
    def test_single_reading(self, hp_34401a):
        dmm, mi = hp_34401a
        mi.query.return_value = "5.0023"
        result = dmm.read()
        assert result == pytest.approx(5.0023)
        mi.query.assert_called_with("READ?")

    def test_multiple_readings_averaged(self, hp_34401a):
        dmm, mi = hp_34401a
        mi.query.return_value = "5.0, 5.1, 4.9"
        result = dmm.read()
        assert result == pytest.approx((5.0 + 5.1 + 4.9) / 3)

    def test_malformed_response_raises(self, hp_34401a):
        dmm, mi = hp_34401a
        mi.query.return_value = "GARBAGE"
        with pytest.raises(ValueError):
            dmm.read()


class TestHP34401A_Fetch:
    def test_fetch_returns_float(self, hp_34401a):
        dmm, mi = hp_34401a
        mi.query.return_value = "3.3"
        result = dmm.fetch()
        assert result == pytest.approx(3.3)
        mi.query.assert_called_with("FETCh?")


class TestHP34401A_Measure:
    def test_measure_dc_voltage(self, hp_34401a):
        dmm, mi = hp_34401a
        mi.query.return_value = "10.0"
        dmm.measure_dc_voltage(10, 0.001)
        mi.query.assert_called_with("MEASure:VOLTage:DC? 10,0.001")

    def test_measure_continuity(self, hp_34401a):
        dmm, mi = hp_34401a
        mi.query.return_value = "0.5"
        dmm.measure_continuity()
        mi.query.assert_called_with("MEASure:CONTinuity?")

    def test_measure_diode(self, hp_34401a):
        dmm, mi = hp_34401a
        mi.query.return_value = "0.65"
        dmm.measure_diode()
        mi.query.assert_called_with("MEASure:DIODe?")


class TestHP34401A_Display:
    def test_display_on(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.set_display(True)
        mi.write.assert_called_with("DISPlay ON")

    def test_display_off(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.set_display(False)
        mi.write.assert_called_with("DISPlay OFF")

    def test_display_text(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.display_text("TEST")
        mi.write.assert_called_with('DISPlay:TEXT "TEST"')

    def test_display_text_truncated(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.display_text("X" * 15)
        # Driver truncates to 12 characters
        mi.write.assert_called_with('DISPlay:TEXT "XXXXXXXXXXXX"')

    def test_clear_display_text(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.clear_display_text()
        mi.write.assert_called_with("DISPlay:TEXT:CLEar")


class TestHP34401A_Trigger:
    @pytest.mark.parametrize("src", ["IMM", "BUS", "EXT"])
    def test_valid_trigger_sources(self, hp_34401a, src):
        dmm, mi = hp_34401a
        dmm.set_trigger_source(src)
        mi.write.assert_called_with(f"TRIGger:SOURce {src}")

    def test_immediate_alias(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.set_trigger_source("IMMEDIATE")
        mi.write.assert_called_with("TRIGger:SOURce IMMEDIATE")

    def test_invalid_source_raises(self, hp_34401a):
        dmm, _ = hp_34401a
        with pytest.raises(ValueError):
            dmm.set_trigger_source("BOGUS")

    def test_trigger(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.trigger()
        mi.write.assert_called_with("*TRG")

    def test_init(self, hp_34401a):
        dmm, mi = hp_34401a
        dmm.init()
        mi.write.assert_called_with("INITiate")


class TestHP34401A_GetError:
    def test_queries_system_error(self, hp_34401a):
        dmm, mi = hp_34401a
        mi.query.return_value = '+0,"No error"'
        dmm.get_error()
        mi.query.assert_called_with("SYSTem:ERRor?")


# ===========================================================================
# Owon_XDM1041
# ===========================================================================

class TestOwon_Configure:
    def test_configure_dc_voltage_auto(self, owon_xdm1041):
        dmm, mi = owon_xdm1041
        dmm.configure_dc_voltage()
        mi.write.assert_called_with("CONFigure:VOLTage:DC AUTO")

    def test_configure_dc_voltage_range(self, owon_xdm1041):
        dmm, mi = owon_xdm1041
        dmm.configure_dc_voltage(5)
        mi.write.assert_called_with("CONFigure:VOLTage:DC 5")

    def test_configure_temperature_kits90(self, owon_xdm1041):
        dmm, mi = owon_xdm1041
        dmm.configure_temperature("KITS90")
        mi.write.assert_called_with("CONFigure:TEMPerature:RTD KITS90")

    def test_configure_temperature_pt100(self, owon_xdm1041):
        dmm, mi = owon_xdm1041
        dmm.configure_temperature("PT100")
        mi.write.assert_called_with("CONFigure:TEMPerature:RTD PT100")

    def test_configure_temperature_no_validation(self, owon_xdm1041):
        dmm, mi = owon_xdm1041
        # No ValueError — driver passes RTD type through without validation
        dmm.configure_temperature("BOGUS")
        mi.write.assert_called_with("CONFigure:TEMPerature:RTD BOGUS")


class TestOwon_Measure:
    def test_measure_queries_meas(self, owon_xdm1041, monkeypatch):
        dmm, mi = owon_xdm1041
        # measure() imports time inside the function body — patch the module globally
        import time as _time
        monkeypatch.setattr(_time, "sleep", lambda _: None)
        mi.query.return_value = "5.0"
        result = dmm.measure()
        assert result == pytest.approx(5.0)
        mi.query.assert_called_with("MEAS?")

    def test_get_error_not_supported(self, owon_xdm1041):
        dmm, mi = owon_xdm1041
        result = dmm.get_error()
        mi.query.assert_not_called()
        assert "not supported" in result.lower()


class TestOwon_SetMode:
    def test_set_mode_vdc(self, owon_xdm1041):
        dmm, mi = owon_xdm1041
        dmm.set_mode("vdc")
        mi.write.assert_called_with("CONFigure:VOLTage:DC AUTO")

    def test_set_mode_res(self, owon_xdm1041):
        dmm, mi = owon_xdm1041
        dmm.set_mode("res")
        mi.write.assert_called_with("CONFigure:RESistance AUTO")

    def test_set_mode_cont(self, owon_xdm1041):
        dmm, mi = owon_xdm1041
        dmm.set_mode("cont")
        mi.write.assert_called_with("CONFigure:CONTinuity")

    def test_set_mode_temp(self, owon_xdm1041):
        dmm, mi = owon_xdm1041
        dmm.set_mode("temp")
        # configure_temperature() called with default "KITS90"
        mi.write.assert_called_with("CONFigure:TEMPerature:RTD KITS90")
