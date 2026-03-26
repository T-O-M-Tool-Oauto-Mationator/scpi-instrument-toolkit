"""tests/test_ni_pxie_4139.py — Driver-level unit tests for the NI PXIe-4139 SMU."""

import pytest

# ===========================================================================
# Connection
# ===========================================================================


class TestNIPXIe4139_Connect:
    def test_session_opened(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        assert smu._session is ms

    def test_resource_name(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        assert smu.resource_name == "PXI1Slot2"


# ===========================================================================
# Enable / Disable Output
# ===========================================================================


class TestNIPXIe4139_EnableOutput:
    def test_enable_on(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        smu.enable_output(True)
        assert ms.output_enabled is True
        ms.commit.assert_called()
        ms.initiate.assert_called_once()

    def test_enable_off(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        smu.enable_output(False)
        assert ms.voltage_level == 0.0
        assert ms.output_enabled is False
        ms.abort.assert_called_once()


# ===========================================================================
# Set Voltage
# ===========================================================================


class TestNIPXIe4139_SetVoltage:
    def test_set_voltage(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        smu.set_voltage(5.0)
        assert ms.voltage_level == 5.0
        ms.commit.assert_called_once()

    def test_set_negative_voltage(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        smu.set_voltage(-12.0)
        assert ms.voltage_level == -12.0

    def test_voltage_too_high_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        with pytest.raises(ValueError):
            smu.set_voltage(100.0)

    def test_voltage_too_low_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        with pytest.raises(ValueError):
            smu.set_voltage(-100.0)


# ===========================================================================
# Set Current Limit
# ===========================================================================


class TestNIPXIe4139_SetCurrentLimit:
    def test_set_current_limit(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        smu.set_current_limit(0.5)
        assert ms.current_limit == 0.5
        ms.commit.assert_called_once()

    def test_current_limit_too_high_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        with pytest.raises(ValueError):
            smu.set_current_limit(5.0)

    def test_current_limit_negative_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        with pytest.raises(ValueError):
            smu.set_current_limit(-0.1)


# ===========================================================================
# Measurements
# ===========================================================================


class TestNIPXIe4139_Measure:
    def test_measure_voltage(self, ni_pxie_4139):
        from unittest.mock import MagicMock

        smu, ms = ni_pxie_4139
        ms.measure_multiple.return_value = [MagicMock(voltage=3.14, current=0.001)]
        result = smu.measure_voltage()
        assert result == 3.14
        ms.measure_multiple.assert_called_once()

    def test_measure_current(self, ni_pxie_4139):
        from unittest.mock import MagicMock

        smu, ms = ni_pxie_4139
        ms.measure_multiple.return_value = [MagicMock(voltage=5.0, current=0.042)]
        result = smu.measure_current()
        assert result == 0.042
        ms.measure_multiple.assert_called_once()


# ===========================================================================
# Getters
# ===========================================================================


class TestNIPXIe4139_GetSetpoints:
    def test_get_voltage_setpoint(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.voltage_level = 12.0
        assert smu.get_voltage_setpoint() == 12.0

    def test_get_current_limit(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.current_limit = 0.25
        assert smu.get_current_limit() == 0.25

    def test_get_output_state_off(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.output_enabled = False
        assert smu.get_output_state() is False

    def test_get_output_state_on(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.output_enabled = True
        assert smu.get_output_state() is True


# ===========================================================================
# Disable All Channels (Safe State)
# ===========================================================================


class TestNIPXIe4139_DisableAllChannels:
    def test_safe_state(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.voltage_level = 10.0
        ms.output_enabled = True
        smu.disable_all_channels()
        assert ms.voltage_level == 0.0
        assert ms.current_limit == 0.01
        assert ms.output_enabled is False


# ===========================================================================
# Context Manager
# ===========================================================================


class TestNIPXIe4139_ContextManager:
    def test_exit_disables(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.voltage_level = 5.0
        ms.output_enabled = True
        smu.__exit__(None, None, None)
        assert ms.voltage_level == 0.0
        assert ms.output_enabled is False


# ===========================================================================
# Disconnect
# ===========================================================================


class TestNIPXIe4139_Disconnect:
    def test_disconnect(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        smu.disconnect()
        ms.close.assert_called_once()
        assert smu._session is None

    def test_disconnect_when_not_connected(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        smu._session = None
        smu.disconnect()  # Should not raise


# ===========================================================================
# SCPI Compatibility Stubs
# ===========================================================================


class TestNIPXIe4139_Stubs:
    def test_query_returns_idn(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        result = smu.query("*IDN?")
        assert "PXIe-4139" in result
        assert "PXI1Slot2" in result

    def test_send_command_noop(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        smu.send_command("*RST")  # Should not raise

    def test_get_error_returns_stub(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        result = smu.get_error()
        assert "not supported" in result
        assert "NI_PXIe_4139" in result


# ===========================================================================
# Error when not connected
# ===========================================================================


class TestNIPXIe4139_NotConnected:
    def test_set_voltage_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        smu._session = None
        with pytest.raises(ConnectionError):
            smu.set_voltage(1.0)

    def test_measure_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        smu._session = None
        with pytest.raises(ConnectionError):
            smu.measure_voltage()


# ===========================================================================
# Atomic V+I measurement
# ===========================================================================


class TestNIPXIe4139_MeasureVI:
    def test_returns_dict(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.measure_multiple.return_value = [type("M", (), {"voltage": 3.3, "current": 0.05, "in_compliance": False})()]
        result = smu.measure_vi()
        assert result["voltage"] == pytest.approx(3.3)
        assert result["current"] == pytest.approx(0.05)
        assert result["in_compliance"] is False
        ms.measure_multiple.assert_called_once()

    def test_compliance_true(self, ni_pxie_4139):
        # in_compliance comes from query_in_compliance(), not measure_multiple
        smu, ms = ni_pxie_4139
        ms.query_in_compliance.return_value = True
        result = smu.measure_vi()
        assert result["in_compliance"] is True

    def test_measure_voltage_uses_single_call(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.measure_multiple.return_value = [type("M", (), {"voltage": 1.5, "current": 0.0, "in_compliance": False})()]
        assert smu.measure_voltage() == pytest.approx(1.5)
        assert ms.measure_multiple.call_count == 1

    def test_measure_current_uses_single_call(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.measure_multiple.return_value = [type("M", (), {"voltage": 0.0, "current": 0.042, "in_compliance": False})()]
        assert smu.measure_current() == pytest.approx(0.042)
        assert ms.measure_multiple.call_count == 1


# ===========================================================================
# Compliance query
# ===========================================================================


class TestNIPXIe4139_QueryCompliance:
    def test_not_in_compliance(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.query_in_compliance.return_value = False
        assert smu.query_in_compliance() is False

    def test_in_compliance(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.query_in_compliance.return_value = True
        assert smu.query_in_compliance() is True

    def test_not_connected_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        smu._session = None
        with pytest.raises(ConnectionError):
            smu.query_in_compliance()


# ===========================================================================
# Source delay
# ===========================================================================


class TestNIPXIe4139_SourceDelay:
    def test_set_source_delay(self, ni_pxie_4139):
        import datetime

        smu, ms = ni_pxie_4139
        smu.set_source_delay(0.5)
        assert ms.source_delay == datetime.timedelta(seconds=0.5)
        ms.commit.assert_called()

    def test_set_source_delay_zero(self, ni_pxie_4139):
        import datetime

        smu, ms = ni_pxie_4139
        smu.set_source_delay(0.0)
        assert ms.source_delay == datetime.timedelta(seconds=0.0)

    def test_set_source_delay_negative_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        with pytest.raises(ValueError):
            smu.set_source_delay(-0.1)

    def test_set_source_delay_too_high_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        with pytest.raises(ValueError):
            smu.set_source_delay(smu.MAX_SOURCE_DELAY + 1)

    def test_get_source_delay(self, ni_pxie_4139):
        import datetime

        smu, ms = ni_pxie_4139
        ms.source_delay = datetime.timedelta(seconds=0.25)
        assert smu.get_source_delay() == pytest.approx(0.25)


# ===========================================================================
# Output mode (voltage / current)
# ===========================================================================


class TestNIPXIe4139_CurrentMode:
    def test_set_current_mode(self, ni_pxie_4139):
        import nidcpower

        smu, ms = ni_pxie_4139
        smu.set_current_mode(0.05, 5.0)
        assert ms.current_level == pytest.approx(0.05)
        assert ms.voltage_limit == pytest.approx(5.0)
        assert ms.output_function == nidcpower.OutputFunction.DC_CURRENT
        ms.commit.assert_called()
        assert smu._output_mode == "current"

    def test_set_current_mode_default_voltage_limit(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        smu.set_current_mode(0.01)
        assert ms.voltage_limit == pytest.approx(smu.DEFAULT_VOLTAGE_LIMIT)

    def test_set_current_mode_too_high_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        with pytest.raises(ValueError):
            smu.set_current_mode(5.0)

    def test_set_current_mode_voltage_limit_too_high_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        with pytest.raises(ValueError):
            smu.set_current_mode(0.01, 100.0)

    def test_set_voltage_mode_switches_back(self, ni_pxie_4139):
        import nidcpower

        smu, ms = ni_pxie_4139
        smu.set_current_mode(0.05, 5.0)
        smu.set_voltage_mode(3.3, 0.1)
        assert ms.output_function == nidcpower.OutputFunction.DC_VOLTAGE
        assert ms.voltage_level == pytest.approx(3.3)
        assert ms.current_limit == pytest.approx(0.1)
        assert smu._output_mode == "voltage"

    def test_get_output_mode_default(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        assert smu.get_output_mode() == "voltage"

    def test_get_output_mode_after_current(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        smu.set_current_mode(0.01)
        assert smu.get_output_mode() == "current"


# ===========================================================================
# Samples to average
# ===========================================================================


class TestNIPXIe4139_SamplesToAverage:
    def test_set_samples_to_average(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        smu.set_samples_to_average(10)
        assert ms.samples_to_average == 10
        ms.commit.assert_called()

    def test_set_samples_to_average_one(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        smu.set_samples_to_average(1)
        assert ms.samples_to_average == 1

    def test_set_samples_to_average_zero_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        with pytest.raises(ValueError):
            smu.set_samples_to_average(0)

    def test_get_samples_to_average(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.samples_to_average = 5
        assert smu.get_samples_to_average() == 5


# ===========================================================================
# Temperature
# ===========================================================================


class TestNIPXIe4139_Temperature:
    def test_returns_float(self, ni_pxie_4139):
        smu, ms = ni_pxie_4139
        ms.read_current_temperature.return_value = 27.3
        temp = smu.read_temperature()
        assert isinstance(temp, float)
        assert temp == pytest.approx(27.3)
        ms.read_current_temperature.assert_called_once()

    def test_not_connected_raises(self, ni_pxie_4139):
        smu, _ms = ni_pxie_4139
        smu._session = None
        with pytest.raises(ConnectionError):
            smu.read_temperature()
