"""Tests for HP E3631A PSU driver — targeting missed lines."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.src.hp_e3631a import HP_E3631A

CHANNELS = list(HP_E3631A.Channel)


@pytest.fixture
def psu(hp_e3631a):
    device, mock_inst = hp_e3631a
    mock_inst.query.return_value = "5.000000E+00"
    return device, mock_inst


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestContextManager:
    def test_enter_exit(self, psu):
        device, mock_inst = psu
        with device:
            pass
        # disable_all_channels called on exit
        mock_inst.write.assert_called()

    def test_connect_calls_disable(self, mock_visa_rm):
        mock_rm, mock_inst = mock_visa_rm

        dev = HP_E3631A("GPIB::5::INSTR")
        dev.instrument = mock_inst
        # connect() calls clear_status and disable_all_channels
        dev.connect()
        mock_inst.write.assert_called()


# ---------------------------------------------------------------------------
# enable_output / disable_all_channels
# ---------------------------------------------------------------------------


class TestOutputControl:
    def test_enable_output_on(self, psu):
        device, mock_inst = psu
        device.enable_output(True)
        mock_inst.write.assert_called()

    def test_enable_output_off(self, psu):
        device, mock_inst = psu
        device.enable_output(False)
        mock_inst.write.assert_called()

    def test_disable_all_channels(self, psu):
        device, mock_inst = psu
        device.disable_all_channels()
        # Should write multiple commands
        assert mock_inst.write.call_count >= 1


# ---------------------------------------------------------------------------
# select_channel
# ---------------------------------------------------------------------------


class TestSelectChannel:
    def test_select_valid_channel(self, psu):
        device, mock_inst = psu
        for ch in CHANNELS:
            mock_inst.reset_mock()
            device.select_channel(ch)
            mock_inst.write.assert_called_once()

    def test_select_invalid_channel_type(self, psu):
        device, mock_inst = psu
        with pytest.raises(TypeError):
            device.select_channel("positive_6_volts_channel")

    def test_select_invalid_channel_int(self, psu):
        device, mock_inst = psu
        with pytest.raises(TypeError):
            device.select_channel(1)


# ---------------------------------------------------------------------------
# set_output_channel
# ---------------------------------------------------------------------------


class TestSetOutputChannel:
    def test_set_output_valid(self, psu):
        device, mock_inst = psu
        device.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, 5.0, 0.5)
        mock_inst.write.assert_called()

    def test_set_output_default_current(self, psu):
        device, mock_inst = psu
        device.set_output_channel(HP_E3631A.Channel.POSITIVE_6V, 5.0)
        mock_inst.write.assert_called()

    def test_set_output_all_channels(self, psu):
        device, mock_inst = psu
        for ch in CHANNELS:
            mock_inst.reset_mock()
            device.set_output_channel(ch, 1.0)
            mock_inst.write.assert_called()

    def test_set_output_invalid_channel_type(self, psu):
        device, mock_inst = psu
        with pytest.raises(TypeError):
            device.set_output_channel("bad_channel", 5.0)


# ---------------------------------------------------------------------------
# measure_voltage / measure_current
# ---------------------------------------------------------------------------


class TestMeasure:
    def test_measure_voltage(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "5.0"
        val = device.measure_voltage(HP_E3631A.Channel.POSITIVE_6V)
        assert isinstance(val, float)

    def test_measure_voltage_invalid_response(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "NOT_A_FLOAT"
        with pytest.raises(ValueError):
            device.measure_voltage(HP_E3631A.Channel.POSITIVE_6V)

    def test_measure_voltage_bad_channel_type(self, psu):
        device, mock_inst = psu
        with pytest.raises(TypeError):
            device.measure_voltage("bad_channel")

    def test_measure_current(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "0.1"
        val = device.measure_current(HP_E3631A.Channel.POSITIVE_6V)
        assert isinstance(val, float)

    def test_measure_current_invalid_response(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "INVALID"
        with pytest.raises(ValueError):
            device.measure_current(HP_E3631A.Channel.POSITIVE_6V)

    def test_measure_current_bad_channel_type(self, psu):
        device, mock_inst = psu
        with pytest.raises(TypeError):
            device.measure_current("bad_channel")


# ---------------------------------------------------------------------------
# set_voltage / set_current_limit
# ---------------------------------------------------------------------------


class TestSetVoltageCurrent:
    def test_set_voltage(self, psu):
        device, mock_inst = psu
        device.set_voltage(HP_E3631A.Channel.POSITIVE_6V, 3.3)
        mock_inst.write.assert_called()

    def test_set_current_limit(self, psu):
        device, mock_inst = psu
        device.set_current_limit(HP_E3631A.Channel.POSITIVE_6V, 0.5)
        mock_inst.write.assert_called()

    def test_set_voltage_bad_channel_type(self, psu):
        device, mock_inst = psu
        with pytest.raises(TypeError):
            device.set_voltage("positive_6_volts_channel", 3.3)

    def test_set_current_limit_bad_channel_type(self, psu):
        device, mock_inst = psu
        with pytest.raises(TypeError):
            device.set_current_limit("positive_6_volts_channel", 0.5)


# ---------------------------------------------------------------------------
# get setpoints
# ---------------------------------------------------------------------------


class TestGetSetpoints:
    def test_get_voltage_setpoint_no_channel(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "5.0"
        val = device.get_voltage_setpoint()
        assert isinstance(val, float)

    def test_get_voltage_setpoint_with_channel(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "5.0"
        val = device.get_voltage_setpoint(HP_E3631A.Channel.POSITIVE_6V)
        assert isinstance(val, float)

    def test_get_voltage_setpoint_bad_channel_type(self, psu):
        device, mock_inst = psu
        with pytest.raises(TypeError):
            device.get_voltage_setpoint("positive_6_volts_channel")

    def test_get_current_limit_no_channel(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "0.5"
        val = device.get_current_limit()
        assert isinstance(val, float)

    def test_get_current_limit_with_channel(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "0.5"
        val = device.get_current_limit(HP_E3631A.Channel.POSITIVE_6V)
        assert isinstance(val, float)

    def test_get_current_limit_bad_channel_type(self, psu):
        device, mock_inst = psu
        with pytest.raises(TypeError):
            device.get_current_limit("positive_6_volts_channel")

    def test_get_output_state_on(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "1"
        assert device.get_output_state() is True

    def test_get_output_state_off(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "0"
        assert device.get_output_state() is False

    def test_get_output_state_on_string(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = "ON"
        assert device.get_output_state() is True


# ---------------------------------------------------------------------------
# Channel enum
# ---------------------------------------------------------------------------


class TestChannelEnum:
    def test_channel_from_number_covers_all(self):
        assert set(HP_E3631A.CHANNEL_FROM_NUMBER.values()) == set(HP_E3631A.Channel)

    def test_channel_from_number_keys(self):
        assert list(HP_E3631A.CHANNEL_FROM_NUMBER.keys()) == [1, 2, 3]

    def test_channel_values_are_scpi_names(self):
        assert HP_E3631A.Channel.POSITIVE_6V.value == "P6V"
        assert HP_E3631A.Channel.POSITIVE_25V.value == "P25V"
        assert HP_E3631A.Channel.NEGATIVE_25V.value == "N25V"

    def test_default_current_limits_keyed_by_enum(self):
        for ch in HP_E3631A.Channel:
            assert ch in HP_E3631A.DEFAULT_CURRENT_LIMIT

    def test_channel_limits_keyed_by_enum(self):
        for ch in HP_E3631A.Channel:
            assert ch in HP_E3631A.CHANNEL_LIMITS


# ---------------------------------------------------------------------------
# get_error
# ---------------------------------------------------------------------------


class TestGetError:
    def test_get_error(self, psu):
        device, mock_inst = psu
        mock_inst.query.return_value = '+0,"No error"'
        err = device.get_error()
        assert err != ""


# ---------------------------------------------------------------------------
# set_tracking / save_state / recall_state
# ---------------------------------------------------------------------------


class TestOtherMethods:
    def test_set_tracking_on(self, psu):
        device, mock_inst = psu
        device.set_tracking(True)
        mock_inst.write.assert_called()

    def test_set_tracking_off(self, psu):
        device, mock_inst = psu
        device.set_tracking(False)
        mock_inst.write.assert_called()

    def test_save_state(self, psu):
        device, mock_inst = psu
        for n in [1, 2, 3]:
            mock_inst.reset_mock()
            device.save_state(n)
            mock_inst.write.assert_called_once()

    def test_save_state_invalid(self, psu):
        device, mock_inst = psu
        with pytest.raises(ValueError):
            device.save_state(0)

    def test_recall_state(self, psu):
        device, mock_inst = psu
        for n in [1, 2, 3]:
            mock_inst.reset_mock()
            device.recall_state(n)
            mock_inst.write.assert_called_once()

    def test_recall_state_invalid(self, psu):
        device, mock_inst = psu
        with pytest.raises(ValueError):
            device.recall_state(4)
