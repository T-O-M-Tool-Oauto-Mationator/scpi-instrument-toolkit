"""tests/test_psu.py — Driver-level unit tests for PSU drivers (no hardware required)."""
import pytest


def _writes(mock_inst):
    """Return all SCPI strings passed to instrument.write() in call order."""
    return [c.args[0] for c in mock_inst.write.call_args_list]


# ===========================================================================
# HP_E3631A
# ===========================================================================

class TestHPE3631A_EnableOutput:
    def test_enable_on(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.enable_output(True)
        mi.write.assert_called_with("OUTPUT:STATE ON")

    def test_enable_off(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.enable_output(False)
        mi.write.assert_called_with("OUTPUT:STATE OFF")


class TestHPE3631A_SelectChannel:
    def test_select_p6v(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.select_channel("positive_6_volts_channel")
        mi.write.assert_called_with("INSTRUMENT:SELECT P6V")

    def test_select_p25v(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.select_channel("positive_25_volts_channel")
        mi.write.assert_called_with("INSTRUMENT:SELECT P25V")

    def test_select_n25v(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.select_channel("negative_25_volts_channel")
        mi.write.assert_called_with("INSTRUMENT:SELECT N25V")

    def test_invalid_channel_raises(self, hp_e3631a):
        psu, mi = hp_e3631a
        with pytest.raises(ValueError):
            psu.select_channel("bad")


class TestHPE3631A_SetOutputChannel:
    def test_explicit_current(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.set_output_channel("positive_6_volts_channel", 3.3, 0.5)
        mi.write.assert_called_with("APPLY P6V, 3.3, 0.5")

    def test_default_current_p6v(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.set_output_channel("positive_6_volts_channel", 5.0)
        # Default current limit for P6V is 1
        mi.write.assert_called_with("APPLY P6V, 5.0, 1")


class TestHPE3631A_SetVoltage:
    def test_select_before_voltage(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.set_voltage("positive_6_volts_channel", 3.3)
        cmds = _writes(mi)
        assert "INSTRUMENT:SELECT P6V" in cmds
        assert "VOLTAGE 3.3" in cmds
        assert cmds.index("INSTRUMENT:SELECT P6V") < cmds.index("VOLTAGE 3.3")


class TestHPE3631A_MeasureVoltage:
    def test_returns_float(self, hp_e3631a):
        psu, mi = hp_e3631a
        mi.query.return_value = "5.0023"
        result = psu.measure_voltage("positive_6_volts_channel")
        assert result == pytest.approx(5.0023, rel=1e-6)

    def test_select_before_query(self, hp_e3631a):
        psu, mi = hp_e3631a
        mi.query.return_value = "5.0"
        psu.measure_voltage("positive_6_volts_channel")
        # select_channel sends a write, measure_voltage sends a query
        assert "INSTRUMENT:SELECT P6V" in _writes(mi)
        mi.query.assert_called_with("MEASURE:VOLTAGE?")


class TestHPE3631A_SaveRecall:
    def test_save_1(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.save_state(1)
        mi.write.assert_called_with("*SAV 1")

    def test_save_3(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.save_state(3)
        mi.write.assert_called_with("*SAV 3")

    def test_save_0_raises(self, hp_e3631a):
        psu, _ = hp_e3631a
        with pytest.raises(ValueError):
            psu.save_state(0)

    def test_save_4_raises(self, hp_e3631a):
        psu, _ = hp_e3631a
        with pytest.raises(ValueError):
            psu.save_state(4)

    def test_recall_2(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.recall_state(2)
        mi.write.assert_called_with("*RCL 2")


class TestHPE3631A_DisableAllChannels:
    def test_output_off_and_zero_all(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.disable_all_channels()
        cmds = _writes(mi)
        assert "OUTPUT:STATE OFF" in cmds
        assert "APPLY P6V, 0.0, 0.0" in cmds
        assert "APPLY P25V, 0.0, 0.0" in cmds
        assert "APPLY N25V, 0.0, 0.0" in cmds


class TestHPE3631A_SetTracking:
    def test_tracking_on(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.set_tracking(True)
        mi.write.assert_called_with("OUTPUT:TRACK ON")

    def test_tracking_off(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.set_tracking(False)
        mi.write.assert_called_with("OUTPUT:TRACK OFF")


class TestHPE3631A_GetError:
    def test_queries_system_error(self, hp_e3631a):
        psu, mi = hp_e3631a
        mi.query.return_value = '+0,"No error"'
        psu.get_error()
        mi.query.assert_called_with("SYSTEM:ERROR?")


class TestHPE3631A_ContextManager:
    def test_enter_disables_all(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.__enter__()
        cmds = _writes(mi)
        assert "OUTPUT:STATE OFF" in cmds
        assert "APPLY P6V, 0.0, 0.0" in cmds

    def test_exit_disables_all(self, hp_e3631a):
        psu, mi = hp_e3631a
        psu.__exit__(None, None, None)
        cmds = _writes(mi)
        assert "OUTPUT:STATE OFF" in cmds

    def test_exit_called_after_exception(self, hp_e3631a):
        psu, mi = hp_e3631a
        try:
            with psu:
                raise RuntimeError("test error")
        except RuntimeError:
            pass
        cmds = _writes(mi)
        assert "OUTPUT:STATE OFF" in cmds
        assert "APPLY P6V, 0.0, 0.0" in cmds


# ===========================================================================
# MATRIX_MPS6010H
# ===========================================================================

class TestMATRIX_SetVoltage:
    def test_normal(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_voltage(12.5)
        mi.write.assert_called_with("VOLT 12.500")

    def test_zero_boundary(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_voltage(0.0)
        mi.write.assert_called_with("VOLT 0.000")

    def test_max_boundary(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_voltage(60.0)
        mi.write.assert_called_with("VOLT 60.000")

    def test_over_max_raises(self, matrix_mps6010h):
        psu, _ = matrix_mps6010h
        with pytest.raises(ValueError):
            psu.set_voltage(60.001)

    def test_negative_raises(self, matrix_mps6010h):
        psu, _ = matrix_mps6010h
        with pytest.raises(ValueError):
            psu.set_voltage(-0.001)

    def test_cache_updated(self, matrix_mps6010h):
        psu, _ = matrix_mps6010h
        psu.set_voltage(15.0)
        assert psu.get_voltage_setpoint() == 15.0


class TestMATRIX_SetCurrentLimit:
    def test_normal(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_current_limit(2.5)
        mi.write.assert_called_with("CURR 2.500")

    def test_zero_boundary(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_current_limit(0.0)
        mi.write.assert_called_with("CURR 0.000")

    def test_max_boundary(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.set_current_limit(10.0)
        mi.write.assert_called_with("CURR 10.000")

    def test_over_max_raises(self, matrix_mps6010h):
        psu, _ = matrix_mps6010h
        with pytest.raises(ValueError):
            psu.set_current_limit(10.001)

    def test_negative_raises(self, matrix_mps6010h):
        psu, _ = matrix_mps6010h
        with pytest.raises(ValueError):
            psu.set_current_limit(-0.001)


class TestMATRIX_EnableOutput:
    def test_enable_on(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.enable_output(True)
        mi.write.assert_called_with("OUTP 1")

    def test_enable_off(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.enable_output(False)
        mi.write.assert_called_with("OUTP 0")


class TestMATRIX_CachedReadback:
    def test_measure_voltage_returns_setpoint(self, matrix_mps6010h):
        psu, _ = matrix_mps6010h
        psu.set_voltage(15.0)
        assert psu.measure_voltage() == 15.0

    def test_get_voltage_setpoint(self, matrix_mps6010h):
        psu, _ = matrix_mps6010h
        psu.set_voltage(15.0)
        assert psu.get_voltage_setpoint() == 15.0

    def test_get_current_limit(self, matrix_mps6010h):
        psu, _ = matrix_mps6010h
        psu.set_current_limit(2.5)
        assert psu.get_current_limit() == 2.5

    def test_get_error_not_supported(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        result = psu.get_error()
        # No query should be issued — stub only
        mi.query.assert_not_called()
        assert "not supported" in result.lower() or "not supported" in result


class TestMATRIX_ContextManager:
    def test_enter_sequence(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.__enter__()
        cmds = _writes(mi)
        assert cmds == ["*CLS", "OUTP 0", "VOLT 0.000", "CURR 0.000"]

    def test_exit_sequence(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        psu.__exit__(None, None, None)
        cmds = _writes(mi)
        assert cmds == ["OUTP 0", "VOLT 0.000", "CURR 0.000", "REM:OFF"]

    def test_exit_called_after_exception(self, matrix_mps6010h):
        psu, mi = matrix_mps6010h
        with pytest.raises(RuntimeError):
            with psu:
                raise RuntimeError("test")
        cmds = _writes(mi)
        assert "REM:OFF" in cmds
