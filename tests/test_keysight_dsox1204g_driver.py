"""tests/test_keysight_dsox1204g_driver.py — Driver-level unit tests for Keysight DSOX1204G oscilloscope."""

import pytest
from unittest.mock import call


def _writes(mock_inst):
    """Return all SCPI strings passed to instrument.write() in call order."""
    return [c.args[0] for c in mock_inst.write.call_args_list]


# ===========================================================================
# Fixture
# ===========================================================================


@pytest.fixture
def scope(mock_visa_rm):
    mock_rm, mock_instrument = mock_visa_rm
    from lab_instruments.src.keysight_dsox1204g import Keysight_DSOX1204G

    dev = Keysight_DSOX1204G("USB::0x2A8D::0x0396::CN63347188::INSTR")
    dev.instrument = mock_instrument
    mock_instrument.reset_mock()
    return dev, mock_instrument


# ===========================================================================
# 1. TestBasicControl
# ===========================================================================


class TestBasicControl:
    def test_run(self, scope):
        dev, mi = scope
        dev.run()
        mi.write.assert_called_with(":RUN")

    def test_stop(self, scope):
        dev, mi = scope
        dev.stop()
        mi.write.assert_called_with(":STOP")

    def test_single(self, scope):
        dev, mi = scope
        dev.single()
        mi.write.assert_called_with(":SINGle")

    def test_autoset_sends_autoscale_not_autoset(self, scope):
        """Keysight uses :AUToscale, NOT :AUToset."""
        dev, mi = scope
        dev.autoset()
        mi.write.assert_called_with(":AUToscale")
        # Make sure we did NOT send :AUToset
        cmds = _writes(mi)
        assert ":AUToset" not in cmds

    def test_force_trigger_sends_trigger_force(self, scope):
        """Keysight uses :TRIGger:FORCe, NOT :TFORce."""
        dev, mi = scope
        dev.force_trigger()
        mi.write.assert_called_with(":TRIGger:FORCe")
        cmds = _writes(mi)
        assert ":TFORce" not in cmds


# ===========================================================================
# 2. TestChannelControl
# ===========================================================================


class TestChannelControl:
    def test_enable_ch1(self, scope):
        dev, mi = scope
        dev.enable_channel(1)
        mi.write.assert_called_with(":CHANnel1:DISPlay ON")

    def test_disable_ch3(self, scope):
        dev, mi = scope
        dev.disable_channel(3)
        mi.write.assert_called_with(":CHANnel3:DISPlay OFF")

    def test_enable_all_channels(self, scope):
        dev, mi = scope
        dev.enable_all_channels()
        cmds = _writes(mi)
        for ch in range(1, 5):
            assert f":CHANnel{ch}:DISPlay ON" in cmds

    def test_disable_all_channels(self, scope):
        dev, mi = scope
        dev.disable_all_channels()
        cmds = _writes(mi)
        for ch in range(1, 5):
            assert f":CHANnel{ch}:DISPlay OFF" in cmds

    def test_invalid_channel_0_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.enable_channel(0)

    def test_invalid_channel_5_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.enable_channel(5)


# ===========================================================================
# 3. TestVerticalScale
# ===========================================================================


class TestVerticalScale:
    def test_scale_and_offset(self, scope):
        dev, mi = scope
        dev.set_vertical_scale(2, 0.5, offset=1.5)
        cmds = _writes(mi)
        assert ":CHANnel2:SCALe 0.5" in cmds
        assert ":CHANnel2:OFFSet 1.5" in cmds

    def test_scale_default_offset(self, scope):
        dev, mi = scope
        dev.set_vertical_scale(1, 1.0)
        cmds = _writes(mi)
        assert ":CHANnel1:SCALe 1.0" in cmds
        assert ":CHANnel1:OFFSet 0.0" in cmds


# ===========================================================================
# 4. TestCoupling
# ===========================================================================


class TestCoupling:
    def test_dc_coupling(self, scope):
        dev, mi = scope
        dev.set_coupling(1, "DC")
        mi.write.assert_called_with(":CHANnel1:COUPling DC")

    def test_ac_coupling(self, scope):
        dev, mi = scope
        dev.set_coupling(1, "AC")
        mi.write.assert_called_with(":CHANnel1:COUPling AC")

    def test_gnd_raises_valueerror(self, scope):
        """Keysight 1000X does NOT support GND coupling."""
        dev, _ = scope
        with pytest.raises(ValueError, match="GND"):
            dev.set_coupling(1, "GND")

    def test_invalid_coupling_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_coupling(1, "BOGUS")


# ===========================================================================
# 5. TestBandwidthLimit
# ===========================================================================


class TestBandwidthLimit:
    def test_20m_maps_to_on(self, scope):
        """Keysight maps '20M' to 'ON'."""
        dev, mi = scope
        dev.set_bandwidth_limit(1, "20M")
        mi.write.assert_called_with(":CHANnel1:BWLimit ON")

    def test_off(self, scope):
        dev, mi = scope
        dev.set_bandwidth_limit(1, "OFF")
        mi.write.assert_called_with(":CHANnel1:BWLimit OFF")


# ===========================================================================
# 6. TestInvert
# ===========================================================================


class TestInvert:
    def test_invert_on(self, scope):
        dev, mi = scope
        dev.invert_channel(1, True)
        mi.write.assert_called_with(":CHANnel1:INVert ON")

    def test_invert_off(self, scope):
        dev, mi = scope
        dev.invert_channel(2, False)
        mi.write.assert_called_with(":CHANnel2:INVert OFF")


# ===========================================================================
# 7. TestLabel
# ===========================================================================


class TestLabel:
    def test_set_label(self, scope):
        dev, mi = scope
        dev.set_channel_label(3, "Clock")
        mi.write.assert_called_with(':CHANnel3:LABel "Clock"')


# ===========================================================================
# 8. TestProbe
# ===========================================================================


class TestProbe:
    def test_probe_10x(self, scope):
        dev, mi = scope
        dev.set_probe_attenuation(2, 10)
        mi.write.assert_called_with(":CHANnel2:PROBe 10")


# ===========================================================================
# 9. TestHorizontal
# ===========================================================================


class TestHorizontal:
    def test_set_horizontal_scale(self, scope):
        dev, mi = scope
        dev.set_horizontal_scale(0.001)
        mi.write.assert_called_with(":TIMebase:SCALe 0.001")

    def test_set_horizontal_offset_uses_position(self, scope):
        """Keysight uses :TIMebase:POSition, NOT :TIMebase:MAIN:OFFSet."""
        dev, mi = scope
        dev.set_horizontal_offset(0.005)
        mi.write.assert_called_with(":TIMebase:POSition 0.005")
        cmds = _writes(mi)
        # Ensure we did NOT use the Rigol-style offset command
        for cmd in cmds:
            assert "TIMebase:MAIN:OFFSet" not in cmd

    def test_set_horizontal_position_alias(self, scope):
        dev, mi = scope
        dev.set_horizontal_position(0.002)
        mi.write.assert_called_with(":TIMebase:POSition 0.002")

    def test_get_horizontal_offset(self, scope):
        dev, mi = scope
        mi.query.return_value = "0.003"
        result = dev.get_horizontal_offset()
        mi.query.assert_called_with(":TIMebase:POSition?")
        assert result == pytest.approx(0.003)

    def test_move_horizontal(self, scope):
        dev, mi = scope
        mi.query.return_value = "0.001"
        dev.move_horizontal(0.002)
        # Should query current position then write new position
        mi.query.assert_called_with(":TIMebase:POSition?")
        mi.write.assert_called_with(":TIMebase:POSition 0.003")


# ===========================================================================
# 10. TestTrigger
# ===========================================================================


class TestTrigger:
    def test_configure_trigger_rise_maps_to_positive(self, scope):
        dev, mi = scope
        dev.configure_trigger(1, 0.5, slope="RISE", mode="AUTO")
        cmds = _writes(mi)
        assert ":TRIGger:MODE EDGE" in cmds
        assert ":TRIGger:EDGE:SOURce CHANnel1" in cmds
        assert ":TRIGger:EDGE:SLOPe POSitive" in cmds
        assert ":TRIGger:EDGE:LEVel 0.5,CHANnel1" in cmds
        assert ":TRIGger:SWEep AUTO" in cmds

    def test_configure_trigger_fall_maps_to_negative(self, scope):
        dev, mi = scope
        dev.configure_trigger(2, 1.0, slope="FALL")
        cmds = _writes(mi)
        assert ":TRIGger:EDGE:SLOPe NEGative" in cmds

    def test_configure_trigger_rfall_maps_to_either(self, scope):
        dev, mi = scope
        dev.configure_trigger(1, 0.0, slope="RFALL")
        cmds = _writes(mi)
        assert ":TRIGger:EDGE:SLOPe EITHer" in cmds

    def test_configure_trigger_either_maps_to_either(self, scope):
        dev, mi = scope
        dev.configure_trigger(1, 0.0, slope="EITHER")
        cmds = _writes(mi)
        assert ":TRIGger:EDGE:SLOPe EITHer" in cmds

    def test_set_trigger_sweep_auto(self, scope):
        dev, mi = scope
        dev.set_trigger_sweep("AUTO")
        mi.write.assert_called_with(":TRIGger:SWEep AUTO")

    def test_set_trigger_sweep_normal(self, scope):
        dev, mi = scope
        dev.set_trigger_sweep("NORMAL")
        mi.write.assert_called_with(":TRIGger:SWEep NORMal")


# ===========================================================================
# 11. TestTriggerStatus
# ===========================================================================


class TestTriggerStatus:
    def test_ter_returns_1_means_td(self, scope):
        """Keysight :TER? returns 1 when triggered."""
        dev, mi = scope
        mi.query.return_value = "1"
        result = dev.get_trigger_status()
        mi.query.assert_called_with(":TER?")
        assert result == "TD"

    def test_ter_returns_0_means_run(self, scope):
        dev, mi = scope
        mi.query.return_value = "0"
        result = dev.get_trigger_status()
        assert result == "RUN"


# ===========================================================================
# 12. TestWaitForStop
# ===========================================================================


class TestWaitForStop:
    def test_wait_success(self, scope, monkeypatch):
        dev, mi = scope
        mi.query.return_value = "1"
        # Patch time.sleep to avoid delays and time.time for predictable flow
        import lab_instruments.src.keysight_dsox1204g as _mod

        monkeypatch.setattr(_mod.time, "sleep", lambda _: None)
        result = dev.wait_for_stop(timeout=2.0)
        assert result is True

    def test_wait_timeout(self, scope, monkeypatch):
        dev, mi = scope
        mi.query.return_value = "0"
        import lab_instruments.src.keysight_dsox1204g as _mod

        call_count = [0]
        start_time = 100.0

        def fake_time():
            call_count[0] += 1
            # After a few iterations, exceed deadline
            return start_time + call_count[0] * 2.0

        monkeypatch.setattr(_mod.time, "sleep", lambda _: None)
        monkeypatch.setattr(_mod.time, "time", fake_time)
        result = dev.wait_for_stop(timeout=1.0)
        assert result is False


# ===========================================================================
# 13. TestMeasurements
# ===========================================================================


class TestMeasurements:
    def test_measure_frequency_format(self, scope):
        """Keysight uses :MEASure:FREQuency? CHANnel1 (NOT :MEASure:ITEM?)."""
        dev, mi = scope
        mi.query.return_value = "1000.0"
        result = dev.measure(1, "frequency")
        mi.query.assert_called_with(":MEASure:FREQuency? CHANnel1")
        assert result == pytest.approx(1000.0)
        # Ensure NOT using Rigol-style :MEASure:ITEM?
        for c in mi.query.call_args_list:
            assert "MEASure:ITEM?" not in c.args[0]

    def test_measure_vpp(self, scope):
        dev, mi = scope
        mi.query.return_value = "3.3"
        result = dev.measure(2, "vpp")
        mi.query.assert_called_with(":MEASure:VPP? CHANnel2")
        assert result == pytest.approx(3.3)

    def test_measure_bnf_alias(self, scope):
        """measure_bnf should be an alias for measure."""
        dev, mi = scope
        mi.query.return_value = "5.0"
        result = dev.measure_bnf(1, "vrms")
        mi.query.assert_called_with(":MEASure:VRMS? CHANnel1")
        assert result == pytest.approx(5.0)

    def test_measure_delay(self, scope):
        dev, mi = scope
        mi.query.return_value = "0.000001"
        result = dev.measure_delay(1, 2)
        mi.query.assert_called_with(":MEASure:DELay? CHANnel1,CHANnel2")
        assert result == pytest.approx(1e-6)

    def test_configure_measurement(self, scope):
        dev, mi = scope
        dev.configure_measurement(1, "frequency")
        mi.write.assert_called_with(":MEASure:FREQuency CHANnel1")


# ===========================================================================
# 14. TestClearMeasurements
# ===========================================================================


class TestClearMeasurements:
    def test_clear(self, scope):
        dev, mi = scope
        dev.clear_measurements()
        mi.write.assert_called_with(":MEASure:CLEar")


# ===========================================================================
# 15. TestDisplay
# ===========================================================================


class TestDisplay:
    def test_screenshot(self, scope):
        dev, mi = scope
        mi.query_binary_values.return_value = b"\x89PNG_DATA"
        dev.get_screenshot()
        mi.query_binary_values.assert_called_once_with(
            ":DISPlay:DATA? PNG,COLor", datatype="B", container=bytes
        )

    def test_clear_display(self, scope):
        dev, mi = scope
        dev.clear_display()
        mi.write.assert_called_with(":DISPlay:CLEar")

    def test_brightness(self, scope):
        dev, mi = scope
        dev.set_waveform_brightness(75)
        mi.write.assert_called_with(":DISPlay:INTensity:WAVeform 75")

    def test_persistence(self, scope):
        dev, mi = scope
        dev.set_persistence("INFinite")
        mi.write.assert_called_with(":DISPlay:PERSistence INFinite")


# ===========================================================================
# 16. TestAcquire
# ===========================================================================


class TestAcquire:
    def test_set_type(self, scope):
        dev, mi = scope
        dev.set_acquisition_type("AVERAGE")
        mi.write.assert_called_with(":ACQuire:TYPE AVERAGE")

    def test_set_average_count(self, scope):
        dev, mi = scope
        dev.set_average_count(64)
        mi.write.assert_called_with(":ACQuire:COUNt 64")

    def test_get_sample_rate(self, scope):
        dev, mi = scope
        mi.query.return_value = "2.0E+09"
        result = dev.get_sample_rate()
        mi.query.assert_called_with(":ACQuire:SRATe?")
        assert result == pytest.approx(2.0e9)


# ===========================================================================
# 17. TestAWG
# ===========================================================================


class TestAWG:
    def test_awg_set_output_enable(self, scope):
        dev, mi = scope
        dev.awg_set_output_enable(True)
        mi.write.assert_called_with(":WGEN:OUTPut 1")

    def test_awg_set_output_disable(self, scope):
        dev, mi = scope
        dev.awg_set_output_enable(False)
        mi.write.assert_called_with(":WGEN:OUTPut 0")

    def test_awg_set_function(self, scope):
        dev, mi = scope
        dev.awg_set_function("SINusoid")
        mi.write.assert_called_with(":WGEN:FUNCtion SINusoid")

    def test_awg_set_frequency(self, scope):
        dev, mi = scope
        dev.awg_set_frequency(1000)
        mi.write.assert_called_with(":WGEN:FREQuency 1000")

    def test_awg_set_amplitude(self, scope):
        dev, mi = scope
        dev.awg_set_amplitude(2.0)
        mi.write.assert_called_with(":WGEN:VOLTage 2.0")

    def test_awg_set_offset(self, scope):
        dev, mi = scope
        dev.awg_set_offset(0.5)
        mi.write.assert_called_with(":WGEN:VOLTage:OFFSet 0.5")

    def test_awg_set_square_duty(self, scope):
        dev, mi = scope
        dev.awg_set_square_duty(50)
        mi.write.assert_called_with(":WGEN:FUNCtion:SQUare:DCYCle 50")

    def test_awg_set_ramp_symmetry(self, scope):
        dev, mi = scope
        dev.awg_set_ramp_symmetry(75)
        mi.write.assert_called_with(":WGEN:FUNCtion:RAMP:SYMMetry 75")


# ===========================================================================
# 18. TestDVM
# ===========================================================================


class TestDVM:
    def test_set_dvm_enable(self, scope):
        dev, mi = scope
        dev.set_dvm_enable(True)
        mi.write.assert_called_with(":DVM:ENABle ON")

    def test_get_dvm_current(self, scope):
        dev, mi = scope
        mi.query.return_value = "3.141"
        result = dev.get_dvm_current()
        mi.query.assert_called_with(":DVM:CURRent?")
        assert result == pytest.approx(3.141)

    def test_set_dvm_source(self, scope):
        dev, mi = scope
        dev.set_dvm_source(2)
        mi.write.assert_called_with(":DVM:SOURce CHANnel2")


# ===========================================================================
# 19. TestMaskTest
# ===========================================================================


class TestMaskTest:
    def test_set_mask_enable(self, scope):
        dev, mi = scope
        dev.set_mask_enable(True)
        mi.write.assert_called_with(":MTESt:ENABle ON")

    def test_set_mask_source(self, scope):
        dev, mi = scope
        dev.set_mask_source(1)
        mi.write.assert_called_with(":MTESt:SOURce CHANnel1")

    def test_create_mask(self, scope):
        dev, mi = scope
        dev.create_mask()
        mi.write.assert_called_with(":MTESt:AMASk:CREate")

    def test_start_mask_test(self, scope):
        dev, mi = scope
        dev.start_mask_test()
        mi.write.assert_called_with(":MTESt:ENABle ON")

    def test_stop_mask_test(self, scope):
        dev, mi = scope
        dev.stop_mask_test()
        mi.write.assert_called_with(":MTESt:ENABle OFF")

    def test_get_mask_statistics(self, scope):
        dev, mi = scope
        mi.query.side_effect = ["100", "5"]
        stats = dev.get_mask_statistics()
        assert stats["total"] == 100
        assert stats["failed"] == 5
        assert stats["passed"] == 95

    def test_reset_mask_statistics(self, scope):
        dev, mi = scope
        dev.reset_mask_statistics()
        mi.write.assert_called_with(":MTESt:COUNt:RESet")

    def test_set_mask_tolerance_x(self, scope):
        dev, mi = scope
        dev.set_mask_tolerance_x(0.3)
        mi.write.assert_called_with(":MTESt:AMASk:XDELta 0.3")

    def test_set_mask_tolerance_y(self, scope):
        dev, mi = scope
        dev.set_mask_tolerance_y(0.5)
        mi.write.assert_called_with(":MTESt:AMASk:YDELta 0.5")


# ===========================================================================
# 20. TestMath
# ===========================================================================


class TestMath:
    def test_enable_math_channel(self, scope):
        """Keysight 1000X uses :FUNCtion:DISPlay, NOT :MATH{n}:DISPlay."""
        dev, mi = scope
        dev.enable_math_channel(1, True)
        mi.write.assert_called_with(":FUNCtion:DISPlay ON")

    def test_disable_math_channel(self, scope):
        dev, mi = scope
        dev.enable_math_channel(1, False)
        mi.write.assert_called_with(":FUNCtion:DISPlay OFF")

    def test_configure_fft(self, scope):
        dev, mi = scope
        dev.configure_fft(1, "CHAN1", "RECT")
        cmds = _writes(mi)
        assert ":FUNCtion:OPERation FFT" in cmds
        assert ":FUNCtion:SOURce1 CHANnel1" in cmds

    def test_set_math_scale(self, scope):
        dev, mi = scope
        dev.set_math_scale(1, 0.5, offset=1.0)
        cmds = _writes(mi)
        assert ":FUNCtion:SCALe 0.5" in cmds
        assert ":FUNCtion:OFFSet 1.0" in cmds
