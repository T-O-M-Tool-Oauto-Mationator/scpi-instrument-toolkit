"""tests/test_keysight_dsox1204g_driver.py — Driver-level unit tests for Keysight DSOX1204G oscilloscope."""

import pytest


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
        mi.query_binary_values.assert_called_once_with(":DISPlay:DATA? PNG,COLor", datatype="B", container=bytes)

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


# ===========================================================================
# 21. TestContextManager
# ===========================================================================


class TestContextManager:
    def test_enter_clears_and_disables(self, scope):
        dev, mi = scope
        dev.__enter__()
        cmds = _writes(mi)
        assert "*CLS" in cmds
        for ch in range(1, 5):
            assert f":CHANnel{ch}:DISPlay OFF" in cmds
        assert ":WGEN:OUTPut 0" in cmds

    def test_exit_disables_channels_and_awg(self, scope):
        dev, mi = scope
        dev.__exit__(None, None, None)
        cmds = _writes(mi)
        for ch in range(1, 5):
            assert f":CHANnel{ch}:DISPlay OFF" in cmds
        assert ":WGEN:OUTPut 0" in cmds

    def test_exit_fires_on_exception(self, scope):
        dev, mi = scope
        try:
            with dev:
                mi.reset_mock()
                raise RuntimeError("test exception")
        except RuntimeError:
            pass
        cmds = _writes(mi)
        for ch in range(1, 5):
            assert f":CHANnel{ch}:DISPlay OFF" in cmds
        assert ":WGEN:OUTPut 0" in cmds


# ===========================================================================
# 22. TestCache
# ===========================================================================


class TestCache:
    def test_cache_initialized_empty(self, scope):
        dev, _ = scope
        assert dev._cache == {}

    def test_cache_updated_on_channel_enable(self, scope):
        dev, _ = scope
        dev.enable_channel(1)
        assert dev._cache["ch1_display"] is True

    def test_cache_updated_on_channel_disable(self, scope):
        dev, _ = scope
        dev.disable_channel(3)
        assert dev._cache["ch3_display"] is False

    def test_cache_updated_on_set_vertical_scale(self, scope):
        dev, _ = scope
        dev.set_vertical_scale(2, 0.5, offset=1.5)
        assert dev._cache["ch2_scale"] == 0.5
        assert dev._cache["ch2_offset"] == 1.5

    def test_cache_updated_on_coupling(self, scope):
        dev, _ = scope
        dev.set_coupling(1, "AC")
        assert dev._cache["ch1_coupling"] == "AC"

    def test_cache_updated_on_timebase(self, scope):
        dev, _ = scope
        dev.set_horizontal_scale(0.001)
        assert dev._cache["timebase_scale"] == 0.001

    def test_cache_updated_on_awg(self, scope):
        dev, _ = scope
        dev.awg_set_output_enable(True)
        assert dev._cache["awg_output"] is True
        dev.awg_set_frequency(1000)
        assert dev._cache["awg_frequency"] == 1000

    def test_cache_cleared_on_reset(self, scope):
        dev, _ = scope
        dev.enable_channel(1)
        assert dev._cache != {}
        dev.reset()
        assert dev._cache == {}


# ===========================================================================
# 23. TestAllowlists
# ===========================================================================


class TestAllowlists:
    def test_coupling_allowlist(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError, match="COUPLING_ALLOWLIST|one of"):
            dev.set_coupling(1, "BOGUS")

    def test_acq_type_allowlist(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError, match="ACQ_TYPE_ALLOWLIST|one of"):
            dev.set_acquisition_type("BOGUS")

    def test_trigger_sweep_allowlist(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError, match="TRIGGER_SWEEP_ALLOWLIST|one of"):
            dev.set_trigger_sweep("BOGUS")

    def test_awg_func_allowlist(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError, match="AWG_FUNC_ALLOWLIST|one of"):
            dev.awg_set_function("BOGUS")

    def test_bw_limit_allowlist(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError, match="BW_LIMIT_MAP|one of"):
            dev.set_bandwidth_limit(1, "BOGUS")


# ===========================================================================
# 24. TestDigitize
# ===========================================================================


class TestDigitize:
    def test_digitize_channel(self, scope):
        dev, mi = scope
        mi.timeout = 10000
        dev.digitize(1)
        mi.write.assert_called_with(":DIGitize CHANnel1")

    def test_digitize_all(self, scope):
        dev, mi = scope
        mi.timeout = 10000
        dev.digitize()
        mi.write.assert_called_with(":DIGitize")

    def test_digitize_invalid_channel(self, scope):
        dev, mi = scope
        mi.timeout = 10000
        with pytest.raises(ValueError):
            dev.digitize(5)

    def test_digitize_restores_timeout(self, scope):
        dev, mi = scope
        mi.timeout = 10000
        dev.digitize(1)
        assert mi.timeout == 10000


# ===========================================================================
# 25. TestHardwareCounter
# ===========================================================================


class TestHardwareCounter:
    def test_counter_with_channel(self, scope):
        dev, mi = scope
        mi.query.return_value = "1000.123"
        result = dev.measure_counter(1)
        mi.query.assert_called_with(":MEASure:COUNter? CHANnel1")
        assert result == pytest.approx(1000.123)

    def test_counter_default_source(self, scope):
        dev, mi = scope
        mi.query.return_value = "50000.0"
        result = dev.measure_counter()
        mi.query.assert_called_with(":MEASure:COUNter?")
        assert result == pytest.approx(50000.0)

    def test_counter_invalid_channel(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.measure_counter(5)


# ===========================================================================
# 26. TestConvenienceMeasurements
# ===========================================================================


class TestConvenienceMeasurements:
    def test_measure_peak_to_peak(self, scope):
        dev, mi = scope
        mi.query.return_value = "3.3"
        result = dev.measure_peak_to_peak(1)
        mi.query.assert_called_with(":MEASure:VPP? CHANnel1")
        assert result == pytest.approx(3.3)

    def test_measure_rms(self, scope):
        dev, mi = scope
        mi.query.return_value = "1.1"
        result = dev.measure_rms(2)
        mi.query.assert_called_with(":MEASure:VRMS? CHANnel2")
        assert result == pytest.approx(1.1)

    def test_measure_mean(self, scope):
        dev, mi = scope
        mi.query.return_value = "0.5"
        result = dev.measure_mean(1)
        mi.query.assert_called_with(":MEASure:VAVerage? CHANnel1")
        assert result == pytest.approx(0.5)

    def test_measure_rise_time(self, scope):
        dev, mi = scope
        mi.query.return_value = "0.000001"
        result = dev.measure_rise_time(1)
        mi.query.assert_called_with(":MEASure:RISetime? CHANnel1")
        assert result == pytest.approx(1e-6)

    def test_measure_fall_time(self, scope):
        dev, mi = scope
        mi.query.return_value = "0.000002"
        result = dev.measure_fall_time(1)
        mi.query.assert_called_with(":MEASure:FALLtime? CHANnel1")
        assert result == pytest.approx(2e-6)

    def test_measure_duty_cycle(self, scope):
        dev, mi = scope
        mi.query.return_value = "50.0"
        result = dev.measure_duty_cycle(1)
        mi.query.assert_called_with(":MEASure:DUTYcycle? CHANnel1")
        assert result == pytest.approx(50.0)

    def test_measure_pos_width(self, scope):
        dev, mi = scope
        mi.query.return_value = "0.0005"
        result = dev.measure_pos_width(1)
        mi.query.assert_called_with(":MEASure:PWIDth? CHANnel1")
        assert result == pytest.approx(0.0005)

    def test_measure_neg_width(self, scope):
        dev, mi = scope
        mi.query.return_value = "0.0005"
        result = dev.measure_neg_width(1)
        mi.query.assert_called_with(":MEASure:NWIDth? CHANnel1")
        assert result == pytest.approx(0.0005)

    def test_measure_overshoot(self, scope):
        dev, mi = scope
        mi.query.return_value = "5.0"
        result = dev.measure_overshoot(1)
        mi.query.assert_called_with(":MEASure:OVERshoot? CHANnel1")
        assert result == pytest.approx(5.0)

    def test_measure_preshoot(self, scope):
        dev, mi = scope
        mi.query.return_value = "2.0"
        result = dev.measure_preshoot(1)
        mi.query.assert_called_with(":MEASure:PREShoot? CHANnel1")
        assert result == pytest.approx(2.0)


# ===========================================================================
# 27. TestCursorCommands
# ===========================================================================


class TestCursorCommands:
    def test_set_cursor_mode_manual(self, scope):
        dev, mi = scope
        dev.set_cursor_mode("MANual")
        mi.write.assert_called_with(":MARKer:MODE MANual")

    def test_set_cursor_mode_off(self, scope):
        dev, mi = scope
        dev.set_cursor_mode("OFF")
        mi.write.assert_called_with(":MARKer:MODE OFF")

    def test_set_cursor_mode_invalid_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_cursor_mode("BOGUS")

    def test_set_cursor_source(self, scope):
        dev, mi = scope
        dev.set_cursor_source(2)
        cmds = _writes(mi)
        assert ":MARKer:X1Y1source CHANnel2" in cmds
        assert ":MARKer:X2Y2source CHANnel2" in cmds

    def test_set_cursor_x_positions(self, scope):
        dev, mi = scope
        dev.set_cursor_x1_position(0.001)
        mi.write.assert_called_with(":MARKer:X1Position 0.001")
        mi.reset_mock()
        dev.set_cursor_x2_position(0.002)
        mi.write.assert_called_with(":MARKer:X2Position 0.002")

    def test_set_cursor_y_positions(self, scope):
        dev, mi = scope
        dev.set_cursor_y1_position(1.5)
        mi.write.assert_called_with(":MARKer:Y1Position 1.5")
        mi.reset_mock()
        dev.set_cursor_y2_position(3.0)
        mi.write.assert_called_with(":MARKer:Y2Position 3.0")

    def test_get_cursor_x_delta(self, scope):
        dev, mi = scope
        mi.query.return_value = "0.001"
        result = dev.get_cursor_x_delta()
        mi.query.assert_called_with(":MARKer:XDELta?")
        assert result == pytest.approx(0.001)

    def test_get_cursor_y_delta(self, scope):
        dev, mi = scope
        mi.query.return_value = "1.5"
        result = dev.get_cursor_y_delta()
        mi.query.assert_called_with(":MARKer:YDELta?")
        assert result == pytest.approx(1.5)

    def test_set_manual_cursor_positions(self, scope):
        dev, mi = scope
        dev.set_manual_cursor_positions(x1=0.001, x2=0.002)
        cmds = _writes(mi)
        assert ":MARKer:X1Position 0.001" in cmds
        assert ":MARKer:X2Position 0.002" in cmds

    def test_get_manual_cursor_values(self, scope):
        dev, mi = scope
        mi.query.side_effect = ["0.001", "1.0", "0.002", "2.0", "0.001", "1.0"]
        result = dev.get_manual_cursor_values()
        assert result["x1"] == pytest.approx(0.001)
        assert result["y1"] == pytest.approx(1.0)
        assert result["x2"] == pytest.approx(0.002)
        assert result["y2"] == pytest.approx(2.0)
        assert result["dx"] == pytest.approx(0.001)
        assert result["dy"] == pytest.approx(1.0)


# ===========================================================================
# 28. TestTimebaseMode
# ===========================================================================


class TestTimebaseMode:
    def test_set_timebase_mode_main(self, scope):
        dev, mi = scope
        dev.set_timebase_mode("MAIN")
        mi.write.assert_called_with(":TIMebase:MODE MAIN")

    def test_set_timebase_mode_xy(self, scope):
        dev, mi = scope
        dev.set_timebase_mode("XY")
        mi.write.assert_called_with(":TIMebase:MODE XY")

    def test_set_timebase_mode_roll(self, scope):
        dev, mi = scope
        dev.set_timebase_mode("ROLL")
        mi.write.assert_called_with(":TIMebase:MODE ROLL")

    def test_set_timebase_mode_invalid_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_timebase_mode("BOGUS")

    def test_get_timebase_mode(self, scope):
        dev, mi = scope
        mi.query.return_value = "MAIN"
        result = dev.get_timebase_mode()
        mi.query.assert_called_with(":TIMebase:MODE?")
        assert result == "MAIN"

    def test_set_timebase_reference_left(self, scope):
        dev, mi = scope
        dev.set_timebase_reference("LEFT")
        mi.write.assert_called_with(":TIMebase:REFerence LEFT")

    def test_set_timebase_reference_center(self, scope):
        dev, mi = scope
        dev.set_timebase_reference("CENTER")
        mi.write.assert_called_with(":TIMebase:REFerence CENTer")

    def test_set_timebase_reference_right(self, scope):
        dev, mi = scope
        dev.set_timebase_reference("RIGHT")
        mi.write.assert_called_with(":TIMebase:REFerence RIGHt")

    def test_set_timebase_reference_invalid_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_timebase_reference("BOGUS")

    def test_get_timebase_reference(self, scope):
        dev, mi = scope
        mi.query.return_value = "LEFT"
        result = dev.get_timebase_reference()
        mi.query.assert_called_with(":TIMebase:REFerence?")
        assert result == "LEFT"


# ===========================================================================
# 29. TestTriggerEnhancements
# ===========================================================================


class TestTriggerEnhancements:
    def test_set_trigger_holdoff(self, scope):
        dev, mi = scope
        dev.set_trigger_holdoff(0.0001)
        mi.write.assert_called_with(":TRIGger:HOLDoff 0.0001")

    def test_set_trigger_holdoff_minimum_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_trigger_holdoff(1e-9)

    def test_get_trigger_holdoff(self, scope):
        dev, mi = scope
        mi.query.return_value = "0.0001"
        result = dev.get_trigger_holdoff()
        mi.query.assert_called_with(":TRIGger:HOLDoff?")
        assert result == pytest.approx(0.0001)

    def test_set_trigger_noise_reject_on(self, scope):
        dev, mi = scope
        dev.set_trigger_noise_reject(True)
        mi.write.assert_called_with(":TRIGger:NREJect 1")

    def test_set_trigger_noise_reject_off(self, scope):
        dev, mi = scope
        dev.set_trigger_noise_reject(False)
        mi.write.assert_called_with(":TRIGger:NREJect 0")

    def test_set_trigger_hf_reject_on(self, scope):
        dev, mi = scope
        dev.set_trigger_hf_reject(True)
        mi.write.assert_called_with(":TRIGger:HFReject 1")

    def test_set_trigger_coupling_dc(self, scope):
        dev, mi = scope
        dev.set_trigger_coupling("DC")
        mi.write.assert_called_with(":TRIGger:EDGE:COUPling DC")

    def test_set_trigger_coupling_ac(self, scope):
        dev, mi = scope
        dev.set_trigger_coupling("AC")
        mi.write.assert_called_with(":TRIGger:EDGE:COUPling AC")

    def test_set_trigger_coupling_lfreject(self, scope):
        dev, mi = scope
        dev.set_trigger_coupling("LFReject")
        mi.write.assert_called_with(":TRIGger:EDGE:COUPling LFReject")

    def test_set_trigger_coupling_invalid_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_trigger_coupling("BOGUS")


# ===========================================================================
# 30. TestMeasurementStatistics
# ===========================================================================


class TestMeasurementStatistics:
    def test_set_statistics_on(self, scope):
        dev, mi = scope
        dev.set_measurement_statistics(True)
        mi.write.assert_called_with(":MEASure:STATistics ON")

    def test_set_statistics_off(self, scope):
        dev, mi = scope
        dev.set_measurement_statistics(False)
        mi.write.assert_called_with(":MEASure:STATistics OFF")

    def test_reset_statistics(self, scope):
        dev, mi = scope
        dev.reset_measurement_statistics()
        mi.write.assert_called_with(":MEASure:STATistics:RESet")

    def test_get_results(self, scope):
        dev, mi = scope
        mi.query.return_value = "freq,1000.0,1001.0,999.0,1.0"
        result = dev.get_measurement_results()
        mi.query.assert_called_with(":MEASure:RESults?")
        assert "freq" in result


# ===========================================================================
# 31. TestAWGModulation
# ===========================================================================


class TestAWGModulation:
    def test_awg_modulation_enable(self, scope):
        dev, mi = scope
        dev.awg_set_modulation_enable(True)
        mi.write.assert_called_with(":WGEN:MODulation:STATe 1")

    def test_awg_modulation_disable(self, scope):
        dev, mi = scope
        dev.awg_set_modulation_enable(False)
        mi.write.assert_called_with(":WGEN:MODulation:STATe 0")

    def test_awg_modulation_type_am(self, scope):
        dev, mi = scope
        dev.awg_set_modulation_type("AM")
        mi.write.assert_called_with(":WGEN:MODulation:TYPE AM")

    def test_awg_modulation_type_fm(self, scope):
        dev, mi = scope
        dev.awg_set_modulation_type("FM")
        mi.write.assert_called_with(":WGEN:MODulation:TYPE FM")

    def test_awg_modulation_type_fsk(self, scope):
        dev, mi = scope
        dev.awg_set_modulation_type("FSK")
        mi.write.assert_called_with(":WGEN:MODulation:TYPE FSK")

    def test_awg_modulation_type_invalid_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.awg_set_modulation_type("BOGUS")

    def test_awg_pulse_width(self, scope):
        dev, mi = scope
        dev.awg_set_pulse_width(0.0001)
        mi.write.assert_called_with(":WGEN:FUNCtion:PULSe:WIDTh 0.0001")

    def test_awg_pulse_width_invalid_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.awg_set_pulse_width(0)
        with pytest.raises(ValueError):
            dev.awg_set_pulse_width(-1)


# ===========================================================================
# 32. TestSegmentedAcquisition
# ===========================================================================


class TestSegmentedAcquisition:
    def test_set_acquisition_mode_rtim(self, scope):
        dev, mi = scope
        dev.set_acquisition_mode("RTIM")
        mi.write.assert_called_with(":ACQuire:MODE RTIM")

    def test_set_acquisition_mode_segm(self, scope):
        dev, mi = scope
        dev.set_acquisition_mode("SEGM")
        mi.write.assert_called_with(":ACQuire:MODE SEGM")

    def test_set_acquisition_mode_invalid_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_acquisition_mode("BOGUS")

    def test_set_segment_count(self, scope):
        dev, mi = scope
        dev.set_segment_count(100)
        mi.write.assert_called_with(":ACQuire:SEGMented:COUNt 100")

    def test_set_segment_count_minimum_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_segment_count(1)

    def test_get_segment_count(self, scope):
        dev, mi = scope
        mi.query.return_value = "100"
        result = dev.get_segment_count()
        mi.query.assert_called_with(":ACQuire:SEGMented:COUNt?")
        assert result == 100

    def test_set_segment_index(self, scope):
        dev, mi = scope
        dev.set_segment_index(5)
        mi.write.assert_called_with(":ACQuire:SEGMented:INDex 5")

    def test_set_segment_index_minimum_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_segment_index(0)

    def test_get_segment_index(self, scope):
        dev, mi = scope
        mi.query.return_value = "5"
        result = dev.get_segment_index()
        mi.query.assert_called_with(":ACQuire:SEGMented:INDex?")
        assert result == 5


# ===========================================================================
# 33. TestSystemExtras
# ===========================================================================


class TestSystemExtras:
    def test_save_setup(self, scope):
        dev, mi = scope
        dev.save_setup(3)
        mi.write.assert_called_with("*SAV 3")

    def test_save_setup_invalid_slot_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.save_setup(10)
        with pytest.raises(ValueError):
            dev.save_setup(-1)

    def test_recall_setup(self, scope):
        dev, mi = scope
        dev.recall_setup(3)
        mi.write.assert_called_with("*RCL 3")

    def test_recall_setup_invalid_slot_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.recall_setup(10)

    def test_self_test(self, scope):
        dev, mi = scope
        mi.query.return_value = "0"
        result = dev.self_test()
        mi.query.assert_called_with("*TST?")
        assert result == 0

    def test_set_system_lock_on(self, scope):
        dev, mi = scope
        dev.set_system_lock(True)
        mi.write.assert_called_with(":SYSTem:LOCK ON")

    def test_set_system_lock_off(self, scope):
        dev, mi = scope
        dev.set_system_lock(False)
        mi.write.assert_called_with(":SYSTem:LOCK OFF")

    def test_set_system_message(self, scope):
        dev, mi = scope
        dev.set_system_message("Hello ESET 453")
        mi.write.assert_called_with(':SYSTem:DSP "Hello ESET 453"')

    def test_set_system_message_empty(self, scope):
        dev, mi = scope
        dev.set_system_message("")
        mi.write.assert_called_with(':SYSTem:DSP ""')


# ===========================================================================
# 34. TestDisplayExtras
# ===========================================================================


class TestDisplayExtras:
    def test_set_display_vectors_on(self, scope):
        dev, mi = scope
        dev.set_display_vectors(True)
        mi.write.assert_called_with(":DISPlay:VECtors 1")

    def test_set_display_vectors_off(self, scope):
        dev, mi = scope
        dev.set_display_vectors(False)
        mi.write.assert_called_with(":DISPlay:VECtors 0")

    def test_set_display_annotation(self, scope):
        dev, mi = scope
        dev.set_display_annotation("Test Signal")
        cmds = _writes(mi)
        assert ':DISPlay:ANNotation:TEXT "Test Signal"' in cmds
        assert ":DISPlay:ANNotation ON" in cmds

    def test_clear_display_annotation(self, scope):
        dev, mi = scope
        dev.clear_display_annotation()
        mi.write.assert_called_with(":DISPlay:ANNotation OFF")


# ===========================================================================
# 35. TestChannelUnits
# ===========================================================================


class TestChannelUnits:
    def test_set_channel_units_volt(self, scope):
        dev, mi = scope
        dev.set_channel_units(1, "VOLT")
        mi.write.assert_called_with(":CHANnel1:UNITs VOLT")

    def test_set_channel_units_ampere(self, scope):
        dev, mi = scope
        dev.set_channel_units(2, "AMPERE")
        mi.write.assert_called_with(":CHANnel2:UNITs AMPere")

    def test_set_channel_units_invalid_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_channel_units(1, "OHM")

    def test_get_channel_units(self, scope):
        dev, mi = scope
        mi.query.return_value = "VOLT"
        result = dev.get_channel_units(1)
        mi.query.assert_called_with(":CHANnel1:UNITs?")
        assert result == "VOLT"

    def test_set_channel_units_invalid_channel_raises(self, scope):
        dev, _ = scope
        with pytest.raises(ValueError):
            dev.set_channel_units(5, "VOLT")
