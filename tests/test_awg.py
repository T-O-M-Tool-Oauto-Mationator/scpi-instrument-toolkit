"""tests/test_awg.py — Driver-level unit tests for AWG drivers (no hardware required).

Replaces the previous non-pytest manual script.
"""
import pytest


def _writes(mock_inst):
    """Return all SCPI strings passed to instrument.write() in call order."""
    return [c.args[0] for c in mock_inst.write.call_args_list]


# ===========================================================================
# Keysight_EDU33212A
# ===========================================================================

class TestKeysight_EnableOutput:
    def test_enable_ch1_on(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.enable_output(1, True)
        mi.write.assert_called_with("OUTPut1 ON")

    def test_enable_ch2_off(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.enable_output(2, False)
        mi.write.assert_called_with("OUTPut2 OFF")

    def test_disable_all_channels(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.disable_all_channels()
        cmds = _writes(mi)
        assert "OUTPut1 OFF" in cmds
        assert "OUTPut2 OFF" in cmds


class TestKeysight_SetFunction:
    def test_set_sin(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_function(1, "SIN")
        mi.write.assert_called_with("SOURce1:FUNCtion SIN")

    def test_invalid_function_raises(self, keysight_edu33212a):
        awg, _ = keysight_edu33212a
        with pytest.raises(ValueError):
            awg.set_function(1, "TRIANGLE")


class TestKeysight_BasicParams:
    def test_set_frequency(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_frequency(1, 1000)
        mi.write.assert_called_with("SOURce1:FREQuency 1000")

    def test_set_amplitude_ch2(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_amplitude(2, 2.5)
        mi.write.assert_called_with("SOURce2:VOLTage 2.5")

    def test_set_offset(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_offset(1, 1.65)
        mi.write.assert_called_with("SOURce1:VOLTage:OFFSet 1.65")

    def test_set_square_duty(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_square_duty(1, 25)
        mi.write.assert_called_with("SOURce1:FUNCtion:SQUare:DCYCle 25")

    def test_set_output_load_inf(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_output_load(1, "INF")
        mi.write.assert_called_with("OUTPut1:LOAD INFinity")

    def test_set_output_load_numeric(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_output_load(1, 50)
        mi.write.assert_called_with("OUTPut1:LOAD 50")


class TestKeysight_SetWaveform:
    def test_sin_waveform(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_waveform(1, "SIN", frequency=1000, amplitude=2.0, offset=0.0)
        cmds = _writes(mi)
        assert "SOURce1:FUNCtion SIN" in cmds
        assert "SOURce1:FREQuency 1000" in cmds
        assert "SOURce1:VOLTage 2.0" in cmds

    def test_square_with_duty(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_waveform(1, "SQU", duty=25)
        cmds = _writes(mi)
        assert "SOURce1:FUNCtion SQU" in cmds
        assert "SOURce1:FUNCtion:SQUare:DCYCle 25" in cmds

    def test_nois_no_frequency(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_waveform(1, "NOIS", amplitude=1.0)
        cmds = _writes(mi)
        # NOIS waveform should NOT send FREQuency
        assert not any("FREQuency" in c for c in cmds)


class TestKeysight_Modulation_AM:
    def test_am_on(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_am(1, True, depth=100, mod_freq=10, mod_func="SIN")
        cmds = _writes(mi)
        assert "SOURce1:AM:STATe ON" in cmds
        assert "SOURce1:AM:DEPTh 100" in cmds
        assert "SOURce1:AM:INTernal:FUNCtion SIN" in cmds
        assert "SOURce1:AM:INTernal:FREQuency 10" in cmds

    def test_am_off_no_params(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_am(1, False)
        cmds = _writes(mi)
        assert "SOURce1:AM:STATe OFF" in cmds
        # No depth/function/frequency commands when disabling
        assert not any("DEPTh" in c for c in cmds)


class TestKeysight_Sweep:
    def test_sweep_on(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_sweep(1, True, start=100, stop=10000, time=2.0)
        cmds = _writes(mi)
        assert "SOURce1:SWEep:STATe ON" in cmds
        assert "SOURce1:FREQuency:STARt 100" in cmds
        assert "SOURce1:FREQuency:STOP 10000" in cmds
        assert "SOURce1:SWEep:TIME 2.0" in cmds

    def test_sweep_off_no_extra(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_sweep(1, False)
        cmds = _writes(mi)
        assert "SOURce1:SWEep:STATe OFF" in cmds
        assert not any("STARt" in c for c in cmds)


class TestKeysight_Burst:
    def test_burst_on(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.set_burst(1, True, n_cycles=5, period=0.01)
        cmds = _writes(mi)
        assert "SOURce1:BURSt:STATe ON" in cmds
        assert "SOURce1:BURSt:NCYCles 5" in cmds
        assert "SOURce1:BURSt:INTernal:PERiod 0.01" in cmds


class TestKeysight_SaveRecall:
    def test_save_0(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.save_state(0)
        mi.write.assert_called_with("*SAV 0")

    def test_save_4(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        awg.save_state(4)
        mi.write.assert_called_with("*SAV 4")

    def test_save_5_raises(self, keysight_edu33212a):
        awg, _ = keysight_edu33212a
        with pytest.raises(ValueError):
            awg.save_state(5)


class TestKeysight_GetError:
    def test_queries_system_error(self, keysight_edu33212a):
        awg, mi = keysight_edu33212a
        mi.query.return_value = '+0,"No error"'
        awg.get_error()
        mi.query.assert_called_with("SYSTem:ERRor?")


# ===========================================================================
# BK_4063
# ===========================================================================

class TestBK4063_EnableOutput:
    def test_enable_ch1_on(self, bk_4063):
        awg, mi = bk_4063
        awg.enable_output(1, True)
        mi.write.assert_called_with("C1:OUTPut ON")

    def test_enable_ch2_off(self, bk_4063):
        awg, mi = bk_4063
        awg.enable_output(2, False)
        mi.write.assert_called_with("C2:OUTPut OFF")

    def test_invalid_channel_raises(self, bk_4063):
        awg, _ = bk_4063
        with pytest.raises(ValueError):
            awg.enable_output(3, True)


class TestBK4063_SetOutputImpedance:
    def test_numeric_load(self, bk_4063):
        awg, mi = bk_4063
        awg.set_output_impedance(1, 50)
        mi.write.assert_called_with("C1:OUTPut LOAD,50")

    def test_high_z(self, bk_4063):
        awg, mi = bk_4063
        awg.set_output_impedance(1, "HZ")
        mi.write.assert_called_with("C1:OUTPut LOAD,HZ")


class TestBK4063_SetWaveform:
    def test_sine_all_params(self, bk_4063):
        awg, mi = bk_4063
        awg.set_waveform(1, "SINE", 1000, 2.0, 0.5, 0, 50, 50)
        mi.write.assert_called_with(
            "C1:BSWV WVTP,SINE,FRQ,1000,AMP,2.0,OFST,0.5,PHSE,0,DUTY,50,SYM,50"
        )

    def test_alias_sin_to_sine(self, bk_4063):
        awg, mi = bk_4063
        awg.set_waveform(1, "SIN", frequency=1000)
        cmds = _writes(mi)
        assert any("WVTP,SINE" in c for c in cmds)

    def test_alias_squ_to_square(self, bk_4063):
        awg, mi = bk_4063
        awg.set_waveform(1, "SQU", frequency=1000)
        cmds = _writes(mi)
        assert any("WVTP,SQUARE" in c for c in cmds)

    def test_alias_tri_to_ramp(self, bk_4063):
        awg, mi = bk_4063
        awg.set_waveform(1, "TRI", frequency=1000)
        cmds = _writes(mi)
        assert any("WVTP,RAMP" in c for c in cmds)

    def test_alias_triangle_to_ramp(self, bk_4063):
        awg, mi = bk_4063
        awg.set_waveform(1, "TRIANGLE", frequency=1000)
        cmds = _writes(mi)
        assert any("WVTP,RAMP" in c for c in cmds)

    def test_invalid_waveform_raises(self, bk_4063):
        awg, _ = bk_4063
        with pytest.raises(ValueError):
            awg.set_waveform(1, "UNKNOWN")


class TestBK4063_CopyChannel:
    def test_copy_ch1_to_ch2(self, bk_4063):
        awg, mi = bk_4063
        # copy_channel(dest, src): dest=1→C1, src=2→C2
        awg.copy_channel(1, 2)
        mi.write.assert_called_with("PACP C1,C2")


class TestBK4063_GetError:
    def test_queries_system_error(self, bk_4063):
        awg, mi = bk_4063
        mi.query.return_value = '+0,"No error"'
        awg.get_error()
        mi.query.assert_called_with("SYSTem:ERRor?")


# ===========================================================================
# JDS6600_Generator
# ===========================================================================

class TestJDS6600_EnableOutput:
    def test_both_on(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.enable_output(ch1=True, ch2=True)
        mi.write.assert_called_with(":w20=1,1.")

    def test_ch1_on_ch2_off(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.enable_output(ch1=True, ch2=False)
        mi.write.assert_called_with(":w20=1,0.")

    def test_both_off(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.enable_output(ch1=False, ch2=False)
        mi.write.assert_called_with(":w20=0,0.")


class TestJDS6600_SetWaveform:
    def test_sine_ch1(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_waveform(1, "sine")
        mi.write.assert_called_with(":w21=0.")

    def test_square_ch1(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_waveform(1, "square")
        mi.write.assert_called_with(":w21=1.")

    def test_sine_ch2(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_waveform(2, "sine")
        mi.write.assert_called_with(":w22=0.")

    def test_invalid_waveform_raises(self, jds6600_generator):
        gen, _ = jds6600_generator
        with pytest.raises(ValueError):
            gen.set_waveform(1, "bogus")


@pytest.mark.parametrize("freq_hz,expected_write", [
    (100,         ":w23=10000,0."),
    (1_000,       ":w23=100000,0."),
    (19_999_999,  ":w23=1999999900,0."),
    (20_000_000,  ":w23=2000,2."),
    (60_000_000,  ":w23=6000,2."),
])
class TestJDS6600_SetFrequency:
    def test_ch1_encoding(self, jds6600_generator, freq_hz, expected_write):
        gen, mi = jds6600_generator
        gen.set_frequency(1, freq_hz)
        mi.write.assert_called_with(expected_write)

    def test_ch2_uses_reg24(self, jds6600_generator, freq_hz, expected_write):
        gen, mi = jds6600_generator
        gen.set_frequency(2, 1000)
        mi.write.assert_called_with(":w24=100000,0.")


class TestJDS6600_SetAmplitude:
    def test_ch1_2v5(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_amplitude(1, 2.5)
        mi.write.assert_called_with(":w25=2500.")

    def test_ch2_1v(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_amplitude(2, 1.0)
        mi.write.assert_called_with(":w26=1000.")

    def test_ch1_0v5(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_amplitude(1, 0.5)
        mi.write.assert_called_with(":w25=500.")


class TestJDS6600_SetOffset:
    @pytest.mark.parametrize("offset_v,expected_write", [
        (-5.0, ":w27=500."),
        (0.0,  ":w27=1000."),
        (5.0,  ":w27=1500."),
    ])
    def test_ch1_encoding(self, jds6600_generator, offset_v, expected_write):
        gen, mi = jds6600_generator
        gen.set_offset(1, offset_v)
        mi.write.assert_called_with(expected_write)

    def test_ch2_uses_reg28(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_offset(2, 0.0)
        mi.write.assert_called_with(":w28=1000.")


class TestJDS6600_SetDutyCycle:
    def test_50_percent(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_duty_cycle(1, 50.0)
        mi.write.assert_called_with(":w29=500.")

    def test_min_boundary(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_duty_cycle(1, 0.1)
        mi.write.assert_called_with(":w29=1.")

    def test_max_boundary(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_duty_cycle(1, 99.9)
        mi.write.assert_called_with(":w29=999.")

    def test_zero_raises(self, jds6600_generator):
        gen, _ = jds6600_generator
        with pytest.raises(ValueError):
            gen.set_duty_cycle(1, 0.0)

    def test_100_raises(self, jds6600_generator):
        gen, _ = jds6600_generator
        with pytest.raises(ValueError):
            gen.set_duty_cycle(1, 100.0)

    def test_ch2_uses_reg30(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_duty_cycle(2, 50.0)
        mi.write.assert_called_with(":w30=500.")


class TestJDS6600_SetPhase:
    def test_90_degrees(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_phase(1, 90.0)
        mi.write.assert_called_with(":w31=900.")

    def test_zero_degrees(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_phase(1, 0.0)
        mi.write.assert_called_with(":w31=0.")

    def test_max_boundary(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_phase(1, 359.9)
        mi.write.assert_called_with(":w31=3599.")

    def test_360_raises(self, jds6600_generator):
        gen, _ = jds6600_generator
        with pytest.raises(ValueError):
            gen.set_phase(1, 360.0)

    def test_ch2_uses_reg32(self, jds6600_generator):
        gen, mi = jds6600_generator
        gen.set_phase(2, 90.0)
        mi.write.assert_called_with(":w32=900.")
