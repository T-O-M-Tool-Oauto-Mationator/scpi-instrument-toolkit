"""
Tests for the LabVIEW bridge module.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers — inject a driver instance directly into the bridge cache
# ---------------------------------------------------------------------------


def _inject(dev, prefix="inst"):
    """Inject a driver instance into the bridge cache, return its ID."""
    from lab_instruments.src import labview_bridge as br

    with br._lock:
        br._id_counter += 1
        inst_id = f"{prefix}_{br._id_counter}"
        br._instruments[inst_id] = dev
    return inst_id


@pytest.fixture(autouse=True)
def _clean_bridge():
    """Reset bridge state between tests."""
    from lab_instruments.src import labview_bridge as br

    yield
    with br._lock:
        br._instruments.clear()
        br._id_counter = 0


# =========================================================================
# Cache management
# =========================================================================


class TestCacheManagement:
    def test_list_open_instruments_empty(self):
        from lab_instruments.src.labview_bridge import list_open_instruments

        result = json.loads(list_open_instruments())
        assert result == {}

    def test_list_open_instruments_after_inject(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import list_open_instruments

        psu, _ = hp_e3631a
        _inject(psu, "psu")
        result = json.loads(list_open_instruments())
        assert len(result) == 1
        assert "HP_E3631A" in list(result.values())[0]

    def test_close_instrument(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import close_instrument

        psu, mock_inst = hp_e3631a
        inst_id = _inject(psu, "psu")
        result = close_instrument(inst_id)
        assert result == "OK"
        # Cache should be empty now
        from lab_instruments.src.labview_bridge import list_open_instruments

        assert json.loads(list_open_instruments()) == {}

    def test_close_instrument_unknown_id(self):
        from lab_instruments.src.labview_bridge import close_instrument

        with pytest.raises(KeyError):
            close_instrument("nonexistent_99")

    def test_close_all(self, hp_e3631a, hp_34401a):
        from lab_instruments.src.labview_bridge import close_all, list_open_instruments

        psu, _ = hp_e3631a
        dmm, _ = hp_34401a
        _inject(psu, "psu")
        _inject(dmm, "dmm")
        result = close_all()
        assert result == "OK"
        assert json.loads(list_open_instruments()) == {}

    def test_get_unknown_id(self):
        from lab_instruments.src.labview_bridge import _get

        with pytest.raises(KeyError, match="No instrument"):
            _get("ghost_1")

    def test_get_typed_wrong_type(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import _get_typed, _DMM_CLASSES

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(TypeError, match="HP_E3631A"):
            _get_typed(inst_id, _DMM_CLASSES)


# =========================================================================
# Discovery
# =========================================================================


class TestDiscovery:
    def test_list_available_drivers(self):
        from lab_instruments.src.labview_bridge import list_available_drivers

        drivers = json.loads(list_available_drivers())
        assert "HP_E3631A" in drivers
        assert "HP_34401A" in drivers
        assert "EDU33212A" in drivers
        assert isinstance(drivers, list)

    def test_list_visa_resources(self, mock_visa_rm):
        mock_rm, _ = mock_visa_rm
        mock_rm.list_resources.return_value = ("USB::1::INSTR", "GPIB::5::INSTR")
        from lab_instruments.src.labview_bridge import list_visa_resources

        resources = json.loads(list_visa_resources())
        assert len(resources) == 2

    def test_get_version(self):
        from lab_instruments.src.labview_bridge import get_version

        version = get_version()
        assert isinstance(version, str)
        assert "." in version


# =========================================================================
# PSU operations
# =========================================================================


class TestPSU:
    def test_set_voltage_hp(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_set_voltage

        psu, mock_inst = hp_e3631a
        inst_id = _inject(psu, "psu")
        result = psu_set_voltage(inst_id, 1, 5.0)
        assert result == "OK"
        # Should have selected channel and set voltage
        assert mock_inst.write.called

    def test_set_voltage_hp_invalid_channel(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_set_voltage

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(ValueError, match="channel must be 1, 2, or 3"):
            psu_set_voltage(inst_id, 5, 5.0)

    def test_set_voltage_edu36311a(self, keysight_edu36311a):
        from lab_instruments.src.labview_bridge import psu_set_voltage

        psu, mock_inst = keysight_edu36311a
        inst_id = _inject(psu, "psu")
        result = psu_set_voltage(inst_id, 2, 12.0)
        assert result == "OK"
        assert mock_inst.write.called

    def test_set_voltage_matrix(self, matrix_mps6010h):
        from lab_instruments.src.labview_bridge import psu_set_voltage

        psu, mock_inst = matrix_mps6010h
        inst_id = _inject(psu, "psu")
        result = psu_set_voltage(inst_id, 1, 30.0)
        assert result == "OK"

    def test_set_output_channel(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_set_output_channel

        psu, mock_inst = hp_e3631a
        inst_id = _inject(psu, "psu")
        result = psu_set_output_channel(inst_id, 2, 15.0, 0.5)
        assert result == "OK"

    def test_enable_output(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_enable_output

        psu, mock_inst = hp_e3631a
        inst_id = _inject(psu, "psu")
        result = psu_enable_output(inst_id, True)
        assert result == "OK"

    def test_measure_voltage_hp(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_measure_voltage

        psu, mock_inst = hp_e3631a
        mock_inst.query.return_value = "5.001"
        inst_id = _inject(psu, "psu")
        result = psu_measure_voltage(inst_id, 1)
        assert isinstance(result, float)

    def test_measure_current_hp(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_measure_current

        psu, mock_inst = hp_e3631a
        mock_inst.query.return_value = "0.123"
        inst_id = _inject(psu, "psu")
        result = psu_measure_current(inst_id, 2)
        assert isinstance(result, float)

    def test_disable_all(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_disable_all

        psu, mock_inst = hp_e3631a
        inst_id = _inject(psu, "psu")
        result = psu_disable_all(inst_id)
        assert result == "OK"

    def test_psu_wrong_type(self, hp_34401a):
        from lab_instruments.src.labview_bridge import psu_set_voltage

        dmm, _ = hp_34401a
        inst_id = _inject(dmm, "dmm")
        with pytest.raises(TypeError):
            psu_set_voltage(inst_id, 1, 5.0)


# =========================================================================
# DMM operations
# =========================================================================


class TestDMM:
    def test_measure_dc_voltage(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_measure_dc_voltage

        dmm, mock_inst = hp_34401a
        mock_inst.query.return_value = "3.300"
        inst_id = _inject(dmm, "dmm")
        result = dmm_measure_dc_voltage(inst_id)
        assert isinstance(result, float)

    def test_measure_ac_voltage(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_measure_ac_voltage

        dmm, mock_inst = hp_34401a
        mock_inst.query.return_value = "1.200"
        inst_id = _inject(dmm, "dmm")
        result = dmm_measure_ac_voltage(inst_id)
        assert isinstance(result, float)

    def test_measure_resistance_2w(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_measure_resistance_2w

        dmm, mock_inst = hp_34401a
        mock_inst.query.return_value = "100.5"
        inst_id = _inject(dmm, "dmm")
        result = dmm_measure_resistance_2w(inst_id)
        assert isinstance(result, float)

    def test_measure_diode(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_measure_diode

        dmm, mock_inst = hp_34401a
        mock_inst.query.return_value = "0.650"
        inst_id = _inject(dmm, "dmm")
        result = dmm_measure_diode(inst_id)
        assert isinstance(result, float)

    def test_dmm_wrong_type(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import dmm_measure_dc_voltage

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(TypeError):
            dmm_measure_dc_voltage(inst_id)


# =========================================================================
# AWG operations
# =========================================================================


class TestAWG:
    def test_set_waveform_keysight(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_set_waveform

        awg, mock_inst = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        result = awg_set_waveform(inst_id, 1, "SIN", 1000.0, 2.0, 0.0)
        assert result == "OK"

    def test_set_waveform_bk(self, bk_4063):
        from lab_instruments.src.labview_bridge import awg_set_waveform

        awg, mock_inst = bk_4063
        inst_id = _inject(awg, "awg")
        result = awg_set_waveform(inst_id, 1, "SINE", 500.0, 1.0, 0.0)
        assert result == "OK"

    def test_set_waveform_jds6600(self, jds6600_generator):
        from lab_instruments.src.labview_bridge import awg_set_waveform

        awg, mock_inst = jds6600_generator
        inst_id = _inject(awg, "awg")
        result = awg_set_waveform(inst_id, 1, "sine", 1000.0, 2.0, 0.0)
        assert result == "OK"

    def test_set_dc_output_keysight(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_set_dc_output

        awg, mock_inst = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        result = awg_set_dc_output(inst_id, 1, 3.0)
        assert result == "OK"

    def test_set_dc_output_jds6600(self, jds6600_generator):
        from lab_instruments.src.labview_bridge import awg_set_dc_output

        awg, mock_inst = jds6600_generator
        inst_id = _inject(awg, "awg")
        result = awg_set_dc_output(inst_id, 1, 3.0)
        assert result == "OK"

    def test_enable_output_keysight(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_enable_output

        awg, mock_inst = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        result = awg_enable_output(inst_id, 1, True)
        assert result == "OK"

    def test_enable_output_jds6600(self, jds6600_generator):
        from lab_instruments.src.labview_bridge import awg_enable_output

        awg, mock_inst = jds6600_generator
        inst_id = _inject(awg, "awg")
        result = awg_enable_output(inst_id, 2, True)
        assert result == "OK"

    def test_disable_all(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_disable_all

        awg, mock_inst = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        result = awg_disable_all(inst_id)
        assert result == "OK"


# =========================================================================
# Scope operations
# =========================================================================


class TestScope:
    def test_run_stop_single(self, tektronix_mso2024):
        from lab_instruments.src.labview_bridge import scope_run, scope_stop, scope_single

        scope, mock_inst = tektronix_mso2024
        inst_id = _inject(scope, "scope")
        assert scope_run(inst_id) == "OK"
        assert scope_stop(inst_id) == "OK"
        assert scope_single(inst_id) == "OK"

    def test_set_vertical_scale(self, rigol_dho804):
        from lab_instruments.src.labview_bridge import scope_set_vertical_scale

        scope, mock_inst = rigol_dho804
        inst_id = _inject(scope, "scope")
        result = scope_set_vertical_scale(inst_id, 1, 0.5)
        assert result == "OK"

    def test_set_timebase(self, tektronix_mso2024):
        from lab_instruments.src.labview_bridge import scope_set_timebase

        scope, mock_inst = tektronix_mso2024
        inst_id = _inject(scope, "scope")
        result = scope_set_timebase(inst_id, 0.001)
        assert result == "OK"

    def test_measure_vpp_tek(self, tektronix_mso2024):
        from lab_instruments.src.labview_bridge import scope_measure_vpp

        scope, mock_inst = tektronix_mso2024
        mock_inst.query.return_value = "3.14"
        inst_id = _inject(scope, "scope")
        result = scope_measure_vpp(inst_id, 1)
        assert isinstance(result, float)

    def test_measure_vpp_rigol(self, rigol_dho804):
        from lab_instruments.src.labview_bridge import scope_measure_vpp

        scope, mock_inst = rigol_dho804
        mock_inst.query.return_value = "2.71"
        inst_id = _inject(scope, "scope")
        result = scope_measure_vpp(inst_id, 1)
        assert isinstance(result, float)

    def test_measure_frequency(self, tektronix_mso2024):
        from lab_instruments.src.labview_bridge import scope_measure_frequency

        scope, mock_inst = tektronix_mso2024
        mock_inst.query.return_value = "1000.0"
        inst_id = _inject(scope, "scope")
        result = scope_measure_frequency(inst_id, 1)
        assert isinstance(result, float)

    def test_measure_vrms_tek(self, tektronix_mso2024):
        from lab_instruments.src.labview_bridge import scope_measure_vrms

        scope, mock_inst = tektronix_mso2024
        mock_inst.query.return_value = "1.41"
        inst_id = _inject(scope, "scope")
        result = scope_measure_vrms(inst_id, 1)
        assert isinstance(result, float)


# =========================================================================
# SMU operations
# =========================================================================


class TestSMU:
    def test_set_voltage_mode(self, ni_pxie_4139):
        from lab_instruments.src.labview_bridge import smu_set_voltage_mode

        smu, _ = ni_pxie_4139
        inst_id = _inject(smu, "smu")
        result = smu_set_voltage_mode(inst_id, 5.0, 0.1)
        assert result == "OK"

    def test_set_current_mode(self, ni_pxie_4139):
        from lab_instruments.src.labview_bridge import smu_set_current_mode

        smu, _ = ni_pxie_4139
        inst_id = _inject(smu, "smu")
        result = smu_set_current_mode(inst_id, 0.01, 5.0)
        assert result == "OK"

    def test_enable_output(self, ni_pxie_4139):
        from lab_instruments.src.labview_bridge import smu_enable_output

        smu, _ = ni_pxie_4139
        inst_id = _inject(smu, "smu")
        result = smu_enable_output(inst_id, True)
        assert result == "OK"

    def test_measure_voltage(self, ni_pxie_4139):
        from lab_instruments.src.labview_bridge import smu_measure_voltage

        smu, mock_session = ni_pxie_4139
        mock_session.measure_multiple.return_value = [MagicMock(voltage=3.3, current=0.01)]
        mock_session.query_in_compliance.return_value = False
        inst_id = _inject(smu, "smu")
        result = smu_measure_voltage(inst_id)
        assert isinstance(result, float)

    def test_measure_current(self, ni_pxie_4139):
        from lab_instruments.src.labview_bridge import smu_measure_current

        smu, mock_session = ni_pxie_4139
        mock_session.measure_multiple.return_value = [MagicMock(voltage=5.0, current=0.05)]
        mock_session.query_in_compliance.return_value = False
        inst_id = _inject(smu, "smu")
        result = smu_measure_current(inst_id)
        assert isinstance(result, float)


# =========================================================================
# EV2300 operations
# =========================================================================


class TestEV2300:
    def test_read_byte(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_read_byte

        dev, mock_backend = ev2300
        # Mock read_byte to return success
        dev.read_byte = MagicMock(return_value={"ok": True, "value": 0xAB, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = ev2300_read_byte(inst_id, 0x08, 0x00)
        assert result == 0xAB

    def test_write_byte(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_write_byte

        dev, _ = ev2300
        dev.write_byte = MagicMock(return_value={"ok": True, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = ev2300_write_byte(inst_id, 0x08, 0x00, 0xFF)
        assert result == "OK"

    def test_read_byte_failure(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_read_byte

        dev, _ = ev2300
        dev.read_byte = MagicMock(return_value={"ok": False, "value": 0, "status_text": "NACK"})
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(RuntimeError, match="NACK"):
            ev2300_read_byte(inst_id, 0x08, 0x00)

    def test_read_word(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_read_word

        dev, _ = ev2300
        dev.read_word = MagicMock(return_value={"ok": True, "value": 0x1234, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = ev2300_read_word(inst_id, 0x08, 0x50)
        assert result == 0x1234

    def test_write_word(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_write_word

        dev, _ = ev2300
        dev.write_word = MagicMock(return_value={"ok": True, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = ev2300_write_word(inst_id, 0x08, 0x09, 0xBE)
        assert result == "OK"

    def test_get_device_info(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_get_device_info

        dev, _ = ev2300
        dev.get_device_info = MagicMock(
            return_value={"ok": True, "serial": "TEST001", "product": "EV2300A"}
        )
        inst_id = _inject(dev, "ev2300")
        result = json.loads(ev2300_get_device_info(inst_id))
        assert result["serial"] == "TEST001"


# =========================================================================
# Generic / raw SCPI
# =========================================================================


class TestGeneric:
    def test_send_scpi(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import send_scpi

        psu, mock_inst = hp_e3631a
        inst_id = _inject(psu, "psu")
        result = send_scpi(inst_id, "*RST")
        assert result == "OK"

    def test_query_scpi(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import query_scpi

        psu, mock_inst = hp_e3631a
        mock_inst.query.return_value = "HP,E3631A,SN123,v1.0"
        inst_id = _inject(psu, "psu")
        result = query_scpi(inst_id, "*IDN?")
        assert "E3631A" in result

    def test_reset_instrument(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import reset_instrument

        psu, mock_inst = hp_e3631a
        inst_id = _inject(psu, "psu")
        result = reset_instrument(inst_id)
        assert result == "OK"

    def test_get_instrument_type_psu(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import get_instrument_type

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        assert get_instrument_type(inst_id) == "psu"

    def test_get_instrument_type_dmm(self, hp_34401a):
        from lab_instruments.src.labview_bridge import get_instrument_type

        dmm, _ = hp_34401a
        inst_id = _inject(dmm, "dmm")
        assert get_instrument_type(inst_id) == "dmm"

    def test_get_instrument_type_awg(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import get_instrument_type

        awg, _ = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        assert get_instrument_type(inst_id) == "awg"

    def test_get_instrument_type_scope(self, tektronix_mso2024):
        from lab_instruments.src.labview_bridge import get_instrument_type

        scope, _ = tektronix_mso2024
        inst_id = _inject(scope, "scope")
        assert get_instrument_type(inst_id) == "scope"

    def test_get_instrument_type_smu(self, ni_pxie_4139):
        from lab_instruments.src.labview_bridge import get_instrument_type

        smu, _ = ni_pxie_4139
        inst_id = _inject(smu, "smu")
        assert get_instrument_type(inst_id) == "smu"


# =========================================================================
# Thread safety
# =========================================================================


class TestThreadSafety:
    def test_concurrent_open_close(self, mock_visa_rm):
        """Verify concurrent cache operations don't corrupt state."""
        import threading

        from lab_instruments.src import labview_bridge as br
        from lab_instruments.src.hp_e3631a import HP_E3631A

        _, mock_inst = mock_visa_rm
        errors = []

        def open_and_close():
            try:
                dev = HP_E3631A("GPIB::5::INSTR")
                dev.instrument = mock_inst
                with br._lock:
                    br._id_counter += 1
                    iid = f"psu_{br._id_counter}"
                    br._instruments[iid] = dev
                # Small operation then remove
                with br._lock:
                    br._instruments.pop(iid, None)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=open_and_close) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        # Cache should be empty after all threads completed
        assert len(br._instruments) == 0
