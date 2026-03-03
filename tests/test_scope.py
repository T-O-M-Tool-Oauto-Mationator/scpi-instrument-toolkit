"""tests/test_scope.py — Driver-level unit tests for oscilloscope drivers (no hardware required)."""

import pytest


def _writes(mock_inst):
    """Return all SCPI strings passed to instrument.write() in call order."""
    return [c.args[0] for c in mock_inst.write.call_args_list]


# ===========================================================================
# Rigol_DHO804  (uses self.instrument.write() directly — not DeviceManager.send_command)
# ===========================================================================


class TestRigol_ChannelControl:
    def test_enable_ch1(self, rigol_dho804):
        scope, mi = rigol_dho804
        scope.enable_channel(1)
        mi.write.assert_called_with(":CHANnel1:DISPlay ON")

    def test_disable_ch2(self, rigol_dho804):
        scope, mi = rigol_dho804
        scope.disable_channel(2)
        mi.write.assert_called_with(":CHANnel2:DISPlay OFF")

    def test_invalid_channel_raises(self, rigol_dho804):
        scope, _ = rigol_dho804
        with pytest.raises(ValueError):
            scope.enable_channel(5)


class TestRigol_VerticalScale:
    def test_scale_and_offset(self, rigol_dho804):
        scope, mi = rigol_dho804
        scope.set_vertical_scale(1, 0.5, offset=2.0)
        cmds = _writes(mi)
        assert ":CHANnel1:SCALe 0.5" in cmds
        assert ":CHANnel1:OFFSet 2.0" in cmds


class TestRigol_ChannelPosition:
    def test_set_position(self, rigol_dho804):
        scope, mi = rigol_dho804
        scope.set_channel_position(1, 2.5)
        mi.write.assert_called_with(":CHANnel1:POSition 2.5")

    def test_get_position(self, rigol_dho804):
        scope, mi = rigol_dho804
        mi.query.return_value = "2.5"
        result = scope.get_channel_position(1)
        mi.query.assert_called_with(":CHANnel1:POSition?")
        assert result == pytest.approx(2.5)


class TestRigol_Coupling:
    @pytest.mark.parametrize("coupling", ["DC", "AC", "GND"])
    def test_valid_coupling(self, rigol_dho804, coupling):
        scope, mi = rigol_dho804
        scope.set_coupling(1, coupling)
        mi.write.assert_called_with(f":CHANnel1:COUPling {coupling}")

    def test_invalid_coupling_raises(self, rigol_dho804):
        scope, _ = rigol_dho804
        with pytest.raises(ValueError):
            scope.set_coupling(1, "BOGUS")


class TestRigol_BandwidthLimit:
    def test_20m_limit(self, rigol_dho804):
        scope, mi = rigol_dho804
        scope.set_bandwidth_limit(1, "20M")
        mi.write.assert_called_with(":CHANnel1:BWLimit 20M")

    def test_off(self, rigol_dho804):
        scope, mi = rigol_dho804
        scope.set_bandwidth_limit(1, "OFF")
        mi.write.assert_called_with(":CHANnel1:BWLimit OFF")


class TestRigol_Invert:
    def test_invert_on(self, rigol_dho804):
        scope, mi = rigol_dho804
        scope.invert_channel(1, True)
        mi.write.assert_called_with(":CHANnel1:INVert ON")

    def test_invert_off(self, rigol_dho804):
        scope, mi = rigol_dho804
        scope.invert_channel(1, False)
        mi.write.assert_called_with(":CHANnel1:INVert OFF")


class TestRigol_ProbeRatio:
    def test_10x_probe(self, rigol_dho804):
        scope, mi = rigol_dho804
        scope.set_probe_ratio(1, 10)
        mi.write.assert_called_with(":CHANnel1:PROBe 10")

    def test_invalid_ratio_raises(self, rigol_dho804):
        scope, _ = rigol_dho804
        with pytest.raises(ValueError):
            scope.set_probe_ratio(1, 7)


# ===========================================================================
# Tektronix_MSO2024  (uses DeviceManager.send_command → instrument.write)
# ===========================================================================


class TestTektronix_ChannelControl:
    def test_enable_ch1(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.change_channel_status(1, True)
        mi.write.assert_called_with("SELect:CH1 ON")

    def test_disable_ch3(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.change_channel_status(3, False)
        mi.write.assert_called_with("SELect:CH3 OFF")

    def test_enable_channel_2(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.enable_channel(2)
        mi.write.assert_called_with("SELect:CH2 ON")

    def test_disable_all_channels(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.disable_all_channels()
        cmds = _writes(mi)
        assert "SELect:CH1 OFF" in cmds
        assert "SELect:CH2 OFF" in cmds
        assert "SELect:CH3 OFF" in cmds
        assert "SELect:CH4 OFF" in cmds
        assert "SELect:MATH OFF" in cmds


class TestTektronix_HorizontalScale:
    def test_set_horizontal_scale(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.set_horizontal_scale(1e-3)
        mi.write.assert_called_with("HORizontal:SCAle 0.001")

    def test_set_horizontal_offset(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.set_horizontal_offset(0.001)
        cmds = _writes(mi)
        assert "HORizontal:DELay:MODe ON" in cmds
        assert "HORizontal:DELay:TIMe 0.001" in cmds

    def test_get_horizontal_position(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        mi.query.return_value = "50.0"
        scope.get_horizontal_position()
        mi.query.assert_called_with("HORizontal:POSition?")


class TestTektronix_MoveHorizontal:
    def test_clamp_to_100(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        mi.query.return_value = "98.0"
        scope.move_horizontal(5.0)
        mi.write.assert_called_with("HORizontal:POSition 100.0")


class TestTektronix_AcquisitionMode:
    def test_sample_mode(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.set_acquisition_mode("SAMPLE")
        mi.write.assert_called_with("ACQuire:MODe SAMPLE")

    def test_average_mode_with_count(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.set_acquisition_mode("AVERAGE", num_averages=64)
        cmds = _writes(mi)
        assert "ACQuire:MODe AVERAGE" in cmds
        assert "ACQuire:NUMAVg 64" in cmds

    def test_invalid_mode_raises(self, tektronix_mso2024):
        scope, _ = tektronix_mso2024
        with pytest.raises(ValueError):
            scope.set_acquisition_mode("INVALID")


class TestTektronix_RunStopSingle:
    def test_run(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.run()
        mi.write.assert_called_with("ACQuire:STATE RUN")

    def test_stop(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.stop()
        mi.write.assert_called_with("ACQuire:STATE STOP")

    def test_single(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.single()
        cmds = _writes(mi)
        assert "ACQuire:STOPAfter SEQuence" in cmds
        assert "ACQuire:STATE RUN" in cmds

    def test_is_running_true(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        mi.query.return_value = "1"
        assert scope.is_running() is True

    def test_is_running_false(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        mi.query.return_value = "0"
        assert scope.is_running() is False


class TestTektronix_VerticalScale:
    def test_scale_and_position(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.set_vertical_scale(1, 0.5, position=2.0)
        cmds = _writes(mi)
        assert "CH1:SCAle 0.5" in cmds
        assert "CH1:POSition 2.0" in cmds

    def test_move_vertical(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        mi.query.return_value = "2.0"
        scope.move_vertical(1, -1.0)
        mi.write.assert_called_with("CH1:POSition 1.0")


class TestTektronix_Trigger:
    def test_configure_trigger(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.configure_trigger(1, level=1.5, slope="RISE", mode="AUTO")
        cmds = _writes(mi)
        assert "TRIGger:A:TYPe EDGE" in cmds
        assert "TRIGger:A:EDGE:SOUrce CH1" in cmds
        assert "TRIGger:A:EDGE:SLOpe RISE" in cmds
        assert "TRIGger:A:LEVel:CH1 1.5" in cmds
        assert "TRIGger:A:MODe AUTO" in cmds


class TestTektronix_ProbeAttenuation:
    def test_10x_attenuation(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.set_probe_attenuation(1, 10)
        # gain = 1/10 = 0.1
        mi.write.assert_called_with("CH1:PRObe:GAIN 0.1")


class TestTektronix_ChannelLabel:
    def test_set_label(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.set_channel_label(1, "VCC")
        mi.write.assert_called_with('CH1:LABel:NAMe "VCC"')
