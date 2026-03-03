"""tests/test_mock_instruments.py — Verify mock instrument interfaces and return ranges."""

import pytest

from lab_instruments.mock_instruments import (
    MockAWG,
    MockBase,
    MockDHO804,
    MockDMM,
    MockEDU33212A,
    MockHP_E3631A,
    MockJDS6600,
    MockMPS6010H,
    MockMSO2024,
    MockPSU,
    MockScope,
    get_mock_devices,
)


class TestMockBase:
    def test_idn_response(self):
        base = MockBase()
        result = base.query("*IDN?")
        assert "MOCK INSTRUMENTS INC." in result

    def test_idn_includes_class_name(self):
        class MyInstrument(MockBase):
            pass

        inst = MyInstrument()
        assert "MyInstrument" in inst.query("*IDN?")

    def test_disconnect_does_not_raise(self):
        MockBase().disconnect()

    def test_reset_does_not_raise(self):
        MockBase().reset()

    def test_send_command_does_not_raise(self):
        MockBase().send_command("*RST")


class TestMockPSU:
    def test_measure_voltage_range(self):
        psu = MockPSU()
        for _ in range(20):
            v = psu.measure_voltage()
            assert 4.985 <= v <= 5.015

    def test_measure_current_range(self):
        psu = MockPSU()
        for _ in range(20):
            i = psu.measure_current()
            assert 0.099 <= i <= 0.101

    def test_initial_voltage_setpoint(self):
        psu = MockPSU()
        assert psu.get_voltage_setpoint() == 5.0

    def test_initial_current_limit(self):
        psu = MockPSU()
        assert psu.get_current_limit() == 0.1

    def test_initial_output_state_false(self):
        psu = MockPSU()
        assert psu.get_output_state() is False

    def test_enable_output(self):
        psu = MockPSU()
        psu.enable_output(True)
        assert psu.get_output_state() is True

    def test_set_voltage(self):
        psu = MockPSU()
        psu.set_voltage(12.0)
        assert psu.get_voltage_setpoint() == 12.0

    def test_save_state_does_not_raise(self):
        MockPSU().save_state(1)

    def test_recall_state_does_not_raise(self):
        MockPSU().recall_state(1)

    def test_set_tracking_does_not_raise(self):
        MockPSU().set_tracking(True)


class TestMockAWG:
    def test_enable_output_ch1(self):
        awg = MockAWG()
        awg.enable_output(1, True)
        assert awg.get_output_state(1) is True

    def test_set_frequency(self):
        awg = MockAWG()
        awg.set_frequency(1, 500)
        assert awg.get_frequency(1) == 500.0

    def test_set_amplitude(self):
        awg = MockAWG()
        awg.set_amplitude(2, 3.3)
        assert awg.get_amplitude(2) == pytest.approx(3.3)

    def test_set_offset(self):
        awg = MockAWG()
        awg.set_offset(1, 1.65)
        assert awg.get_offset(1) == pytest.approx(1.65)

    def test_set_waveform_does_not_raise(self):
        awg = MockAWG()
        awg.set_waveform(1, "sine", frequency=1000)

    def test_disable_all_channels(self):
        awg = MockAWG()
        awg.enable_output(1, True)
        awg.enable_output(2, True)
        awg.disable_all_channels()
        assert awg.get_output_state(1) is False
        assert awg.get_output_state(2) is False


class TestMockDMM:
    def test_read_range(self):
        dmm = MockDMM()
        for _ in range(20):
            v = dmm.read()
            assert 4.998 <= v <= 5.002

    def test_fetch_range(self):
        dmm = MockDMM()
        for _ in range(20):
            v = dmm.fetch()
            assert 4.998 <= v <= 5.002

    def test_measure_resistance_2wire(self):
        dmm = MockDMM()
        for _ in range(10):
            r = dmm.measure_resistance_2wire()
            assert 99.5 <= r <= 100.5

    def test_measure_dc_current(self):
        dmm = MockDMM()
        for _ in range(10):
            i = dmm.measure_dc_current()
            assert 0.0998 <= i <= 0.1002

    def test_configure_dc_voltage_does_not_raise(self):
        MockDMM().configure_dc_voltage()

    def test_set_mode_does_not_raise(self):
        MockDMM().set_mode("vdc")


class TestMockScope:
    def test_get_trigger_status(self):
        assert MockScope().get_trigger_status() == "TD"

    def test_wait_for_stop(self):
        assert MockScope().wait_for_stop() is True

    def test_measure_bnf_frequency(self):
        scope = MockScope()
        for _ in range(10):
            f = scope.measure_bnf(1, "FREQUENCY")
            assert 999.5 <= f <= 1000.5

    def test_measure_bnf_pk2pk(self):
        scope = MockScope()
        for _ in range(10):
            v = scope.measure_bnf(1, "PK2PK")
            assert 1.98 <= v <= 2.02

    def test_measure_bnf_unknown_returns_float(self):
        scope = MockScope()
        result = scope.measure_bnf(1, "UNKNOWN")
        assert isinstance(result, float)


class TestMockDHO804:
    def test_get_screenshot_is_png(self):
        dho = MockDHO804()
        data = dho.get_screenshot()
        assert isinstance(data, bytes)
        assert data[:4] == b"\x89PNG"

    def test_get_memory_depth(self):
        assert MockDHO804().get_memory_depth() == "AUTO"

    def test_get_sample_rate(self):
        assert MockDHO804().get_sample_rate() == 1e9

    def test_get_mask_statistics_keys(self):
        stats = MockDHO804().get_mask_statistics()
        assert "passed" in stats
        assert "failed" in stats
        assert "total" in stats

    def test_get_mask_statistics_total(self):
        assert MockDHO804().get_mask_statistics()["total"] == 100


class TestGetMockDevices:
    def test_returns_8_keys(self):
        devices = get_mock_devices(verbose=False)
        assert len(devices) == 8

    def test_expected_keys(self):
        devices = get_mock_devices(verbose=False)
        for key in ("psu1", "psu2", "awg1", "awg2", "dmm1", "dmm2", "scope1", "scope2"):
            assert key in devices

    def test_psu1_type(self):
        assert isinstance(get_mock_devices(verbose=False)["psu1"], MockHP_E3631A)

    def test_psu2_type(self):
        assert isinstance(get_mock_devices(verbose=False)["psu2"], MockMPS6010H)

    def test_awg1_type(self):
        assert isinstance(get_mock_devices(verbose=False)["awg1"], MockEDU33212A)

    def test_awg2_type(self):
        assert isinstance(get_mock_devices(verbose=False)["awg2"], MockJDS6600)

    def test_scope1_type(self):
        assert isinstance(get_mock_devices(verbose=False)["scope1"], MockDHO804)

    def test_scope2_type(self):
        assert isinstance(get_mock_devices(verbose=False)["scope2"], MockMSO2024)
