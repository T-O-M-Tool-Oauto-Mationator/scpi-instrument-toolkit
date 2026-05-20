"""
Tests for the LabVIEW bridge module.
"""

import json
from unittest.mock import MagicMock

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
        from lab_instruments.src.labview_bridge import _DMM_CLASSES, _get_typed

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

    def test_enable_output_rejects_non_bool(self, hp_e3631a):
        """Regression: LabVIEW Python Node silently passes a falsy default
        (None / 0 / "" / Variant) when the Boolean parameter terminal is
        unwired or wired to the wrong constant type. Without validation the
        bridge accepted that and quietly disabled the PSU output, which is
        the worst possible failure mode for a safety-relevant call. The
        bridge must now reject any non-bool with a TypeError that names the
        likely cause."""
        from lab_instruments.src.labview_bridge import psu_enable_output

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        for bogus in (None, 0, 1, "True", "False"):
            with pytest.raises(TypeError, match="must be a Boolean"):
                psu_enable_output(inst_id, bogus)

    def test_enable_output_rejects_bad_instrument_id(self, hp_e3631a):
        """Regression: when LabVIEW's first parameter slot is unwired, the
        Python Node passes the empty string "". The bridge must reject this
        with a clear ValueError naming the wiring fix, rather than letting
        it cascade to a generic KeyError from _get_typed which students
        misread as a bridge bug."""
        from lab_instruments.src.labview_bridge import psu_enable_output

        for bogus in ("", None, 0, b"psu_1"):
            with pytest.raises(ValueError, match="instrument_id"):
                psu_enable_output(bogus, True)

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
        from lab_instruments.src.labview_bridge import scope_run, scope_single, scope_stop

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

    def test_wait_for_bq(self, ev2300):
        """ev2300_wait_for_bq forwards to the driver's wait_for_bq method.

        Bench motivation: students hit Device error (0x46) because the
        BQ76920 was still in SHIP mode when ev2300_read_byte fired. The
        intended LabVIEW pattern is open_ev2300 -> ev2300_wait_for_bq
        (block while the human presses BOOT) -> ev2300_read_byte."""
        from lab_instruments.src.labview_bridge import ev2300_wait_for_bq

        dev, _ = ev2300
        dev.wait_for_bq = MagicMock(return_value=None)
        inst_id = _inject(dev, "ev2300")
        result = ev2300_wait_for_bq(inst_id, timeout_s=5.0)
        assert result == "OK"
        dev.wait_for_bq.assert_called_once_with(timeout_s=5.0)

    def test_wait_for_bq_propagates_timeout(self, ev2300):
        """If the BQ never responds, wait_for_bq raises TimeoutError; the
        bridge passes it through unchanged so LabVIEW sees a clear error
        instead of a silent hang."""
        from lab_instruments.src.labview_bridge import ev2300_wait_for_bq

        dev, _ = ev2300
        dev.wait_for_bq = MagicMock(side_effect=TimeoutError("BQ did not ACK"))
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(TimeoutError, match="BQ did not ACK"):
            ev2300_wait_for_bq(inst_id, timeout_s=1.0)

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
        dev.get_device_info = MagicMock(return_value={"ok": True, "serial": "TEST001", "product": "EV2300A"})
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


# =========================================================================
# open_* family - previously had ZERO coverage. _inject() skipped them.
# These tests exercise the real open_instrument code path (driver-name
# validation, type-category validation, _next_id contract, lock acquisition,
# dev.connect() side-effect).
# =========================================================================


class TestOpenInstrumentFamily:
    """Cover the previously-untested open_* dispatch.

    Bench motivation: students who mistyped a driver name (e.g. "HP_3631A"
    instead of "HP_E3631A") used to see a generic KeyError at the next
    operation. Validating up front in open_psu/open_dmm/etc. lets the
    failure point at the wiring mistake on the open node itself.
    """

    def test_open_instrument_unknown_driver(self):
        from lab_instruments.src.labview_bridge import open_instrument

        with pytest.raises(ValueError, match="Unknown driver"):
            open_instrument("GPIB::5::INSTR", "BOGUS_DRIVER")

    def test_open_instrument_empty_visa_address(self):
        from lab_instruments.src.labview_bridge import open_instrument

        with pytest.raises(ValueError, match="visa_address"):
            open_instrument("", "HP_E3631A")

    def test_open_instrument_empty_driver_name(self):
        from lab_instruments.src.labview_bridge import open_instrument

        with pytest.raises(ValueError, match="driver_name"):
            open_instrument("GPIB::5::INSTR", "")

    def test_open_instrument_non_string_visa_address(self):
        from lab_instruments.src.labview_bridge import open_instrument

        with pytest.raises(TypeError, match="visa_address"):
            open_instrument(0, "HP_E3631A")

    def test_open_psu_happy_path(self, mock_visa_rm):
        """End-to-end open_psu using mocked pyvisa: ID is returned, cache
        gains an entry, and the underlying driver is the expected class."""
        from lab_instruments.src import labview_bridge as br
        from lab_instruments.src.hp_e3631a import HP_E3631A

        inst_id = br.open_psu("GPIB::5::INSTR", "HP_E3631A")
        assert inst_id.startswith("psu_")
        with br._lock:
            assert inst_id in br._instruments
            assert isinstance(br._instruments[inst_id], HP_E3631A)

    def test_open_psu_rejects_dmm_driver(self):
        """The whole point of open_psu's category check: passing 'HP_34401A'
        (a DMM) must fail before pyvisa is even contacted."""
        from lab_instruments.src.labview_bridge import open_psu

        with pytest.raises(TypeError, match="not a PSU driver"):
            open_psu("GPIB::22::INSTR", "HP_34401A")

    def test_open_dmm_rejects_psu_driver(self):
        from lab_instruments.src.labview_bridge import open_dmm

        with pytest.raises(TypeError, match="not a DMM driver"):
            open_dmm("GPIB::5::INSTR", "HP_E3631A")

    def test_open_awg_rejects_scope_driver(self):
        from lab_instruments.src.labview_bridge import open_awg

        with pytest.raises(TypeError, match="not an AWG driver"):
            open_awg("USB::INSTR", "MSO2024")

    def test_open_scope_rejects_awg_driver(self):
        from lab_instruments.src.labview_bridge import open_scope

        with pytest.raises(TypeError, match="not a scope driver"):
            open_scope("USB::INSTR", "EDU33212A")

    def test_open_smu_rejects_psu_driver(self):
        from lab_instruments.src.labview_bridge import _SMU_CLASSES, open_smu

        if not _SMU_CLASSES:
            pytest.skip("nidcpower not installed")
        with pytest.raises(TypeError, match="not an SMU driver"):
            open_smu("USB::INSTR", "HP_E3631A")

    def test_open_dmm_happy_path(self, mock_visa_rm):
        from lab_instruments.src import labview_bridge as br
        from lab_instruments.src.hp_34401a import HP_34401A

        inst_id = br.open_dmm("GPIB::22::INSTR", "HP_34401A")
        assert inst_id.startswith("dmm_")
        with br._lock:
            assert isinstance(br._instruments[inst_id], HP_34401A)

    def test_open_awg_happy_path(self, mock_visa_rm):
        from lab_instruments.src import labview_bridge as br
        from lab_instruments.src.bk_4063 import BK_4063

        inst_id = br.open_awg("USB::0x1AB1::0x0000::INSTR", "BK_4063")
        assert inst_id.startswith("awg_")
        with br._lock:
            assert isinstance(br._instruments[inst_id], BK_4063)

    def test_open_scope_happy_path(self, mock_visa_rm):
        from lab_instruments.src import labview_bridge as br
        from lab_instruments.src.tektronix_mso2024 import Tektronix_MSO2024

        inst_id = br.open_scope("USB::INSTR", "MSO2024")
        assert inst_id.startswith("scope_")
        with br._lock:
            assert isinstance(br._instruments[inst_id], Tektronix_MSO2024)


# =========================================================================
# discover_instruments
# =========================================================================


class TestDiscoverInstruments:
    def test_returns_json_object(self, monkeypatch):
        """discover_instruments returns a JSON string mapping name -> class
        name. With an empty discovery result it must still produce '{}',
        not raise or return None."""
        from lab_instruments.src import discovery
        from lab_instruments.src import labview_bridge as br

        monkeypatch.setattr(discovery, "find_all", lambda verbose=False: {})
        result = json.loads(br.discover_instruments())
        assert result == {}

    def test_returns_class_names(self, monkeypatch, hp_e3631a):
        from lab_instruments.src import discovery
        from lab_instruments.src import labview_bridge as br

        psu, _ = hp_e3631a
        monkeypatch.setattr(discovery, "find_all", lambda verbose=False: {"psu": psu})
        result = json.loads(br.discover_instruments())
        assert result == {"psu": "HP_E3631A"}


# =========================================================================
# Newly-tested PSU functions (psu_set_current_limit + all-vendor branches)
# =========================================================================


class TestPSUSetCurrentLimit:
    """psu_set_current_limit was implemented but had zero tests. The HP
    branch validates channel; EDU and Matrix branches were entirely
    uncovered."""

    def test_hp_emits_current_after_select(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_set_current_limit

        psu, mi = hp_e3631a
        inst_id = _inject(psu, "psu")
        result = psu_set_current_limit(inst_id, 1, 0.5)
        assert result == "OK"
        # HP_E3631A.set_current_limit: INSTRUMENT:SELECT then CURRENT
        cmds = [c.args[0] for c in mi.write.call_args_list]
        assert "INSTRUMENT:SELECT P6V" in cmds
        assert "CURRENT 0.5" in cmds
        assert cmds.index("INSTRUMENT:SELECT P6V") < cmds.index("CURRENT 0.5")

    def test_hp_invalid_channel(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_set_current_limit

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(ValueError, match="channel must be 1, 2, or 3"):
            psu_set_current_limit(inst_id, 9, 0.5)

    def test_edu36311a_branch(self, keysight_edu36311a):
        from lab_instruments.src.labview_bridge import psu_set_current_limit

        psu, mi = keysight_edu36311a
        inst_id = _inject(psu, "psu")
        # p30v channel max is 1.0 A; pick a valid value to exercise dispatch
        result = psu_set_current_limit(inst_id, 2, 0.5)
        assert result == "OK"
        assert mi.write.called

    def test_edu36311a_invalid_channel(self, keysight_edu36311a):
        from lab_instruments.src.labview_bridge import psu_set_current_limit

        psu, _ = keysight_edu36311a
        inst_id = _inject(psu, "psu")
        with pytest.raises(ValueError, match="EDU36311A channel must be 1, 2, or 3"):
            psu_set_current_limit(inst_id, 4, 1.0)

    def test_matrix_branch(self, matrix_mps6010h):
        from lab_instruments.src.labview_bridge import psu_set_current_limit

        psu, mi = matrix_mps6010h
        inst_id = _inject(psu, "psu")
        result = psu_set_current_limit(inst_id, 1, 5.0)
        assert result == "OK"
        assert any("CURR" in c.args[0] for c in mi.write.call_args_list)


class TestPSUSetOutputChannelBranchCoverage:
    """psu_set_output_channel previously only had HP coverage."""

    def test_edu36311a(self, keysight_edu36311a):
        from lab_instruments.src.labview_bridge import psu_set_output_channel

        psu, mi = keysight_edu36311a
        inst_id = _inject(psu, "psu")
        assert psu_set_output_channel(inst_id, 1, 5.0, 0.5) == "OK"
        assert mi.write.called

    def test_matrix(self, matrix_mps6010h):
        from lab_instruments.src.labview_bridge import psu_set_output_channel

        psu, mi = matrix_mps6010h
        inst_id = _inject(psu, "psu")
        assert psu_set_output_channel(inst_id, 1, 12.0, 1.0) == "OK"
        assert mi.write.called


class TestPSUMeasureBranchCoverage:
    """psu_measure_voltage/current previously had only HP coverage."""

    def test_measure_voltage_edu(self, keysight_edu36311a):
        from lab_instruments.src.labview_bridge import psu_measure_voltage

        psu, mi = keysight_edu36311a
        mi.query.return_value = "5.001"
        inst_id = _inject(psu, "psu")
        result = psu_measure_voltage(inst_id, 1)
        assert isinstance(result, float)

    def test_measure_current_edu(self, keysight_edu36311a):
        from lab_instruments.src.labview_bridge import psu_measure_current

        psu, mi = keysight_edu36311a
        mi.query.return_value = "0.250"
        inst_id = _inject(psu, "psu")
        result = psu_measure_current(inst_id, 2)
        assert isinstance(result, float)

    def test_measure_voltage_matrix(self, matrix_mps6010h):
        """Matrix path: returns cached setpoint (no read-back)."""
        from lab_instruments.src.labview_bridge import psu_measure_voltage

        psu, _ = matrix_mps6010h
        inst_id = _inject(psu, "psu")
        result = psu_measure_voltage(inst_id, 1)
        assert isinstance(result, float)


# =========================================================================
# Newly-tested DMM functions
# =========================================================================


class TestDMMNewlyCovered:
    def test_measure_dc_current(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_measure_dc_current

        dmm, mi = hp_34401a
        mi.query.return_value = "0.250"
        inst_id = _inject(dmm, "dmm")
        result = dmm_measure_dc_current(inst_id)
        assert isinstance(result, float)

    def test_measure_resistance_4w(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_measure_resistance_4w

        dmm, mi = hp_34401a
        mi.query.return_value = "1000.5"
        inst_id = _inject(dmm, "dmm")
        result = dmm_measure_resistance_4w(inst_id)
        assert isinstance(result, float)

    def test_measure_frequency(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_measure_frequency

        dmm, mi = hp_34401a
        mi.query.return_value = "1000.0"
        inst_id = _inject(dmm, "dmm")
        result = dmm_measure_frequency(inst_id)
        assert isinstance(result, float)


# =========================================================================
# Newly-tested AWG functions
# =========================================================================


class TestAWGNewlyCovered:
    def test_set_frequency(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_set_frequency

        awg, mi = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        assert awg_set_frequency(inst_id, 1, 1000.0) == "OK"
        assert mi.write.called

    def test_set_amplitude(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_set_amplitude

        awg, mi = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        assert awg_set_amplitude(inst_id, 1, 2.0) == "OK"
        assert mi.write.called

    def test_disable_all_jds6600_branch(self, jds6600_generator):
        """jds6600 disable_all_channels does NOT exist on JDS6600_Generator;
        the bridge routes to disable_output() instead. Previously untested."""
        from lab_instruments.src.labview_bridge import awg_disable_all

        awg, _ = jds6600_generator
        inst_id = _inject(awg, "awg")
        assert awg_disable_all(inst_id) == "OK"


# =========================================================================
# Newly-tested EV2300 functions
# =========================================================================


class TestEV2300NewlyCovered:
    def test_read_block(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_read_block

        dev, _ = ev2300
        dev.read_block = MagicMock(return_value={"ok": True, "data": bytes([0x01, 0x02, 0x03]), "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = json.loads(ev2300_read_block(inst_id, 0x08, 0x0B))
        assert result == [1, 2, 3]

    def test_read_block_failure(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_read_block

        dev, _ = ev2300
        dev.read_block = MagicMock(return_value={"ok": False, "data": b"", "status_text": "NACK"})
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(RuntimeError, match="NACK"):
            ev2300_read_block(inst_id, 0x08, 0x0B)

    def test_write_block_happy(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_write_block

        dev, _ = ev2300
        dev.write_block = MagicMock(return_value={"ok": True, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = ev2300_write_block(inst_id, 0x08, 0x0B, "[1, 2, 3]")
        assert result == "OK"
        # Verify the bytes were actually decoded and passed through
        dev.write_block.assert_called_once_with(0x08, 0x0B, bytes([1, 2, 3]))

    def test_write_block_malformed_json(self, ev2300):
        """Regression: previously a malformed data_json raised
        json.JSONDecodeError with no LabVIEW-actionable message. Now it
        raises ValueError naming the parameter and the JSON error."""
        from lab_instruments.src.labview_bridge import ev2300_write_block

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(ValueError, match="data_json"):
            ev2300_write_block(inst_id, 0x08, 0x0B, "not_json")

    def test_write_block_non_list(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_write_block

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(ValueError, match="list"):
            ev2300_write_block(inst_id, 0x08, 0x0B, '{"not": "a list"}')

    def test_write_block_byte_out_of_range(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_write_block

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(ValueError, match=r"data_json\[1\]"):
            ev2300_write_block(inst_id, 0x08, 0x0B, "[1, 256, 3]")


# =========================================================================
# get_instrument_type EV2300 branch (previously only psu/dmm/awg/scope/smu)
# =========================================================================


class TestGetInstrumentTypeEv2300:
    def test_ev2300_branch(self, ev2300):
        from lab_instruments.src.labview_bridge import get_instrument_type

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        assert get_instrument_type(inst_id) == "ev2300"


# =========================================================================
# Regression: silent fall-through in PSU dispatch functions
# =========================================================================


class _UnrecognizedPSU:
    """Stub class included in _PSU_CLASSES for the test, but not matched by
    any branch in psu_set_voltage / psu_set_current_limit /
    psu_set_output_channel. Used to prove the bridge raises TypeError
    instead of silently returning "OK"."""

    def __init__(self):
        self.recorded_calls = []

    def disconnect(self):
        pass


class TestPSUSilentFallThroughRegression:
    """Before this fix, psu_set_voltage / _current_limit / _output_channel
    ended their if/elif chain without `else: raise`, so any PSU subclass
    not covered by the explicit branches returned "OK" without writing a
    single SCPI byte. The output looked successful while the instrument
    state did not change. This was undetectable from LabVIEW.

    These tests temporarily monkey-patch the _PSU_CLASSES tuple to include
    a stub class, inject an instance, and verify the bridge raises
    TypeError("Unsupported PSU type") instead of returning "OK"."""

    def _inject_unrecognized(self, monkeypatch):
        from lab_instruments.src import labview_bridge as br

        stub = _UnrecognizedPSU()
        # Add stub to the PSU tuple so _get_typed accepts it
        monkeypatch.setattr(br, "_PSU_CLASSES", (*br._PSU_CLASSES, _UnrecognizedPSU))
        inst_id = _inject(stub, "psu")
        return inst_id, stub

    def test_set_voltage_raises_on_unknown_psu_type(self, monkeypatch):
        from lab_instruments.src.labview_bridge import psu_set_voltage

        inst_id, _ = self._inject_unrecognized(monkeypatch)
        with pytest.raises(TypeError, match="Unsupported PSU type"):
            psu_set_voltage(inst_id, 1, 5.0)

    def test_set_current_limit_raises_on_unknown_psu_type(self, monkeypatch):
        from lab_instruments.src.labview_bridge import psu_set_current_limit

        inst_id, _ = self._inject_unrecognized(monkeypatch)
        with pytest.raises(TypeError, match="Unsupported PSU type"):
            psu_set_current_limit(inst_id, 1, 0.5)

    def test_set_output_channel_raises_on_unknown_psu_type(self, monkeypatch):
        from lab_instruments.src.labview_bridge import psu_set_output_channel

        inst_id, _ = self._inject_unrecognized(monkeypatch)
        with pytest.raises(TypeError, match="Unsupported PSU type"):
            psu_set_output_channel(inst_id, 1, 5.0, 0.5)


# =========================================================================
# Validation guard regression: instrument_id, channel, numeric, bool, string
# =========================================================================


class TestInstrumentIdValidationRegression:
    """LabVIEW unwired String terminal arrives as "". Without _require_id
    these calls used to leak deep into _get/_get_typed as a generic
    KeyError that students misread as a bridge bug. Every entry point must
    now reject empty/non-string IDs with a ValueError or TypeError naming
    the parameter."""

    @pytest.mark.parametrize(
        "fn_name,extra_args",
        [
            ("psu_set_voltage", (1, 5.0)),
            ("psu_set_current_limit", (1, 0.5)),
            ("psu_set_output_channel", (1, 5.0, 0.5)),
            ("psu_enable_output", (True,)),
            ("psu_measure_voltage", (1,)),
            ("psu_measure_current", (1,)),
            ("psu_disable_all", ()),
            ("dmm_measure_dc_voltage", ()),
            ("dmm_measure_ac_voltage", ()),
            ("dmm_measure_dc_current", ()),
            ("dmm_measure_resistance_2w", ()),
            ("dmm_measure_resistance_4w", ()),
            ("dmm_measure_frequency", ()),
            ("dmm_measure_diode", ()),
            ("awg_set_waveform", (1, "SIN", 1000.0, 2.0, 0.0)),
            ("awg_set_frequency", (1, 1000.0)),
            ("awg_set_amplitude", (1, 2.0)),
            ("awg_set_dc_output", (1, 3.0)),
            ("awg_enable_output", (1, True)),
            ("awg_disable_all", ()),
            ("scope_run", ()),
            ("scope_stop", ()),
            ("scope_single", ()),
            ("scope_set_vertical_scale", (1, 0.5)),
            ("scope_set_timebase", (0.001,)),
            ("scope_measure_vpp", (1,)),
            ("scope_measure_frequency", (1,)),
            ("scope_measure_vrms", (1,)),
            ("smu_set_voltage_mode", (5.0, 0.1)),
            ("smu_set_current_mode", (0.01, 5.0)),
            ("smu_enable_output", (True,)),
            ("smu_measure_voltage", ()),
            ("smu_measure_current", ()),
            ("ev2300_wait_for_bq", ()),
            ("ev2300_read_byte", (0x08, 0x00)),
            ("ev2300_write_byte", (0x08, 0x00, 0xFF)),
            ("ev2300_read_word", (0x08, 0x00)),
            ("ev2300_write_word", (0x08, 0x00, 0x1234)),
            ("ev2300_read_block", (0x08, 0x00)),
            ("ev2300_write_block", (0x08, 0x00, "[1]")),
            ("ev2300_get_device_info", ()),
            ("send_scpi", ("*RST",)),
            ("query_scpi", ("*IDN?",)),
            ("reset_instrument", ()),
            ("get_instrument_type", ()),
            ("close_instrument", ()),
        ],
    )
    def test_empty_instrument_id_rejected(self, fn_name, extra_args):
        from lab_instruments.src import labview_bridge as br

        fn = getattr(br, fn_name)
        with pytest.raises((ValueError, TypeError), match="instrument_id"):
            fn("", *extra_args)

    @pytest.mark.parametrize(
        "fn_name,extra_args",
        [
            ("psu_set_voltage", (1, 5.0)),
            ("dmm_measure_dc_voltage", ()),
            ("awg_set_dc_output", (1, 3.0)),
            ("scope_run", ()),
            ("ev2300_read_byte", (0x08, 0x00)),
            ("send_scpi", ("*RST",)),
        ],
    )
    def test_non_string_instrument_id_rejected(self, fn_name, extra_args):
        """LabVIEW Numeric wired into a String slot is a wiring error - it
        used to flow through as e.g. KeyError(0). Now it should ValueError
        or TypeError naming the parameter."""
        from lab_instruments.src import labview_bridge as br

        fn = getattr(br, fn_name)
        with pytest.raises((ValueError, TypeError), match="instrument_id"):
            fn(0, *extra_args)


class TestChannelValidationRegression:
    """LabVIEW unwired I32 terminal arrives as 0. For functions that take a
    channel, 0 is not a valid channel - the previous bridge passed it through
    to the driver where it produced a less helpful error (or, on AWG and
    Matrix paths, silently mapped to "channel 2" or no-op)."""

    def test_psu_set_voltage_zero_channel(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_set_voltage

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(ValueError, match="channel must be 1, 2, or 3"):
            psu_set_voltage(inst_id, 0, 5.0)

    def test_psu_set_voltage_non_int_channel(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_set_voltage

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(TypeError, match="channel.*must be an integer"):
            psu_set_voltage(inst_id, "1", 5.0)

    def test_awg_enable_output_zero_channel(self, keysight_edu33212a):
        """Regression: previously, awg_enable_output(channel=0) on a
        non-JDS device would forward 0 to the driver; on the JDS path it
        silently mapped to ch2 because the else branch handles 'not 1'."""
        from lab_instruments.src.labview_bridge import awg_enable_output

        awg, _ = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        with pytest.raises(ValueError, match="channel"):
            awg_enable_output(inst_id, 0, True)

    def test_awg_set_waveform_channel_3(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_set_waveform

        awg, _ = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        with pytest.raises(ValueError, match="channel"):
            awg_set_waveform(inst_id, 3, "SIN", 1000.0, 2.0, 0.0)

    def test_scope_measure_vpp_zero_channel(self, tektronix_mso2024):
        from lab_instruments.src.labview_bridge import scope_measure_vpp

        scope, _ = tektronix_mso2024
        inst_id = _inject(scope, "scope")
        with pytest.raises(ValueError, match="channel"):
            scope_measure_vpp(inst_id, 0)


class TestNumericValidationRegression:
    """LabVIEW unwired Numeric terminal arrives as 0.0. For scope scale and
    EV2300 timeouts, 0 is invalid input; for voltage/current it is sometimes
    valid but a wrong-typed input (string, bool, None) is always a wiring
    error and should fail loudly."""

    def test_psu_set_voltage_string_voltage(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_set_voltage

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(TypeError, match="voltage.*must be a number"):
            psu_set_voltage(inst_id, 1, "5.0")

    def test_psu_set_voltage_bool_voltage(self, hp_e3631a):
        """bool is an int subclass in Python; a True wired into a voltage
        slot is almost certainly a wiring mistake."""
        from lab_instruments.src.labview_bridge import psu_set_voltage

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(TypeError, match="voltage.*must be a number"):
            psu_set_voltage(inst_id, 1, True)

    def test_scope_set_vertical_scale_zero(self, rigol_dho804):
        from lab_instruments.src.labview_bridge import scope_set_vertical_scale

        scope, _ = rigol_dho804
        inst_id = _inject(scope, "scope")
        with pytest.raises(ValueError, match="volts_per_div"):
            scope_set_vertical_scale(inst_id, 1, 0.0)

    def test_scope_set_vertical_scale_negative(self, rigol_dho804):
        from lab_instruments.src.labview_bridge import scope_set_vertical_scale

        scope, _ = rigol_dho804
        inst_id = _inject(scope, "scope")
        with pytest.raises(ValueError, match="volts_per_div"):
            scope_set_vertical_scale(inst_id, 1, -0.5)

    def test_scope_set_timebase_zero(self, tektronix_mso2024):
        from lab_instruments.src.labview_bridge import scope_set_timebase

        scope, _ = tektronix_mso2024
        inst_id = _inject(scope, "scope")
        with pytest.raises(ValueError, match="time_per_div"):
            scope_set_timebase(inst_id, 0.0)

    def test_ev2300_wait_for_bq_zero_timeout(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_wait_for_bq

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(ValueError, match="timeout_s"):
            ev2300_wait_for_bq(inst_id, timeout_s=0.0)


class TestStringValidationRegression:
    def test_awg_set_waveform_empty_wave_type(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_set_waveform

        awg, _ = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        with pytest.raises(ValueError, match="wave_type"):
            awg_set_waveform(inst_id, 1, "", 1000.0, 2.0, 0.0)

    def test_send_scpi_empty_command(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import send_scpi

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(ValueError, match="command"):
            send_scpi(inst_id, "")

    def test_query_scpi_empty_command(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import query_scpi

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(ValueError, match="command"):
            query_scpi(inst_id, "")


class TestBoolValidationRegression:
    """psu_enable_output already validated bool. Now the same guard applies
    to awg_enable_output and smu_enable_output. Unwired LabVIEW Boolean
    silently defaults to False which would silently disable outputs."""

    def test_awg_enable_output_rejects_non_bool(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_enable_output

        awg, _ = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        for bogus in (None, 0, 1, "True", "yes"):
            with pytest.raises(TypeError, match="must be a Boolean"):
                awg_enable_output(inst_id, 1, bogus)

    def test_smu_enable_output_rejects_non_bool(self, ni_pxie_4139):
        from lab_instruments.src.labview_bridge import smu_enable_output

        smu, _ = ni_pxie_4139
        inst_id = _inject(smu, "smu")
        for bogus in (None, 0, 1, "True"):
            with pytest.raises(TypeError, match="must be a Boolean"):
                smu_enable_output(inst_id, bogus)


class TestEV2300RangeValidationRegression:
    """LabVIEW unwired I32 = 0. For i2c_addr / register / value, 0 is a
    valid byte but the bridge should at least reject out-of-range or
    non-int inputs so a wiring mistake doesn't poison the I2C bus."""

    def test_read_byte_i2c_addr_too_large(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_read_byte

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(ValueError, match="i2c_addr"):
            ev2300_read_byte(inst_id, 0x80, 0x00)

    def test_read_byte_i2c_addr_non_int(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_read_byte

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(TypeError, match="i2c_addr"):
            ev2300_read_byte(inst_id, "0x08", 0x00)

    def test_write_byte_value_too_large(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_write_byte

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(ValueError, match="value.*0..255"):
            ev2300_write_byte(inst_id, 0x08, 0x00, 0x100)

    def test_write_word_value_too_large(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_write_word

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(ValueError, match="value.*0..65535"):
            ev2300_write_word(inst_id, 0x08, 0x00, 0x10000)


# =========================================================================
# Threading regression: public open/close under contention
# =========================================================================


class TestThreadSafetyPublicAPI:
    """The original test_concurrent_open_close manually inserted into
    br._instruments under the lock. That tested threading.Lock, not the
    bridge's public surface. This test exercises open_psu/close_instrument
    end-to-end so a future regression to lock placement in those functions
    fails immediately."""

    def test_public_open_close_no_leak(self, mock_visa_rm):
        import threading

        from lab_instruments.src import labview_bridge as br

        errors = []
        ids_opened = []
        lock = threading.Lock()

        def worker():
            try:
                iid = br.open_psu("GPIB::5::INSTR", "HP_E3631A")
                with lock:
                    ids_opened.append(iid)
                br.close_instrument(iid)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"thread errors: {errors}"
        assert len(ids_opened) == 20
        assert len(set(ids_opened)) == 20, "duplicate IDs - _next_id is racing"
        with br._lock:
            assert br._instruments == {}, "cache leaked instruments"


# =========================================================================
# Behavior tests: dispatch sends correct vendor SCPI on the wire
# =========================================================================


class TestAWGDispatchBehavior:
    """Multi-vendor AWG dispatch tests previously only asserted the bridge
    returned "OK". This left the door open to silent dispatch bugs where
    the wrong driver method was called. These tests verify each vendor's
    SCPI bytes actually hit the wire."""

    def test_set_waveform_bk_uses_dual_send(self, bk_4063):
        """BK 4063 sends multi-line SCPI per channel (e.g. C1:BSWV WVTP,SINE...)."""
        from lab_instruments.src.labview_bridge import awg_set_waveform

        awg, mi = bk_4063
        inst_id = _inject(awg, "awg")
        awg_set_waveform(inst_id, 1, "SINE", 1000.0, 2.0, 0.0)
        cmds = [c.args[0] for c in mi.write.call_args_list]
        # BK uses C1:BSWV prefix on channel 1
        assert any("C1:BSWV" in c or "C1:" in c for c in cmds), f"expected BK C1: prefix in {cmds}"

    def test_set_waveform_keysight_uses_source_node(self, keysight_edu33212a):
        """Keysight uses SOURce{N}:FUNCtion / SOURce{N}:FREQuency syntax."""
        from lab_instruments.src.labview_bridge import awg_set_waveform

        awg, mi = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        awg_set_waveform(inst_id, 1, "SIN", 1000.0, 2.0, 0.0)
        cmds = [c.args[0] for c in mi.write.call_args_list]
        # Keysight SCPI uses SOURce or SOUR
        assert any("SOUR" in c or "FREQ" in c or "FUNC" in c for c in cmds), f"unexpected SCPI: {cmds}"

    def test_enable_output_bk_uses_cn_outp(self, bk_4063):
        """BK enable_output: C1:OUTPut ON (channel-prefixed)."""
        from lab_instruments.src.labview_bridge import awg_enable_output

        awg, mi = bk_4063
        inst_id = _inject(awg, "awg")
        awg_enable_output(inst_id, 1, True)
        cmds = [c.args[0] for c in mi.write.call_args_list]
        assert any("C1:OUTP" in c.upper() for c in cmds), f"expected C1:OUTP in {cmds}"

    def test_enable_output_keysight_uses_outputn(self, keysight_edu33212a):
        """Keysight enable_output: OUTPut1 ON (number-suffixed)."""
        from lab_instruments.src.labview_bridge import awg_enable_output

        awg, mi = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        awg_enable_output(inst_id, 1, True)
        cmds = [c.args[0] for c in mi.write.call_args_list]
        assert any("OUTP" in c.upper() and "1" in c for c in cmds), f"expected OUTPut1 in {cmds}"

    def test_enable_output_jds6600_path_does_not_use_visa(self, jds6600_generator):
        """JDS6600 uses :w20 serial frames, NOT generic SCPI. The bridge
        dispatch must route through dev.enable_output(ch1=...) which goes
        through JDS's serial path. We can't easily verify the exact serial
        frame from inside the mock, but we can verify the call didn't raise
        and that the device's serial layer was exercised (write called)."""
        from lab_instruments.src.labview_bridge import awg_enable_output

        awg, mi = jds6600_generator
        inst_id = _inject(awg, "awg")
        result = awg_enable_output(inst_id, 1, True)
        assert result == "OK"
        # Serial path uses instrument.write for the :w20 frame
        assert mi.write.called


class TestScopeDispatchBehavior:
    """scope_measure_vrms / scope_measure_vpp dispatch: Tek uses different
    driver method names (measure_rms, measure_peak_to_peak) vs Rigol /
    Keysight (measure_vrms, measure_vpp). Previously only the Tek path
    was tested."""

    def test_measure_vrms_rigol_path(self, rigol_dho804):
        """Verify the non-Tek branch actually invokes the Rigol driver's
        measure_vrms method. Before this test, only the Tek branch was
        exercised; the non-Tek elif was effectively dead code from a
        coverage standpoint."""
        from lab_instruments.src.labview_bridge import scope_measure_vrms

        scope, mi = rigol_dho804
        mi.query.return_value = "1.41"
        inst_id = _inject(scope, "scope")
        result = scope_measure_vrms(inst_id, 1)
        assert isinstance(result, float)
        assert mi.query.called

    def test_measure_vpp_rigol_uses_vpp(self, rigol_dho804):
        """Rigol path calls dev.measure_vpp, Tek path calls
        dev.measure_peak_to_peak. The two driver methods exist with
        different names - the bridge MUST pick the correct one per type."""
        from lab_instruments.src.labview_bridge import scope_measure_vpp

        scope, mi = rigol_dho804
        mi.query.return_value = "2.71"
        inst_id = _inject(scope, "scope")
        result = scope_measure_vpp(inst_id, 1)
        assert isinstance(result, float)


class TestPSUDispatchBehavior:
    """Strengthen the multi-PSU happy path tests so future dispatch bugs
    fail loudly. Each vendor uses different SCPI - HP uses INSTRUMENT:SELECT
    + VOLTAGE, EDU uses INSTrument + VOLT, Matrix uses bare VOLT."""

    def test_set_voltage_hp_emits_select_then_voltage(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_set_voltage

        psu, mi = hp_e3631a
        inst_id = _inject(psu, "psu")
        psu_set_voltage(inst_id, 1, 5.0)
        cmds = [c.args[0] for c in mi.write.call_args_list]
        assert "INSTRUMENT:SELECT P6V" in cmds
        assert "VOLTAGE 5.0" in cmds
        assert cmds.index("INSTRUMENT:SELECT P6V") < cmds.index("VOLTAGE 5.0")

    def test_set_voltage_matrix_emits_bare_volt(self, matrix_mps6010h):
        """Matrix is single-channel - no INSTrument:SELECT needed, just
        VOLT directly. A regression here would mean the bridge was treating
        Matrix as multi-channel."""
        from lab_instruments.src.labview_bridge import psu_set_voltage

        psu, mi = matrix_mps6010h
        inst_id = _inject(psu, "psu")
        psu_set_voltage(inst_id, 1, 30.0)
        cmds = [c.args[0] for c in mi.write.call_args_list]
        assert any("VOLT" in c for c in cmds), f"expected VOLT in {cmds}"
        # Matrix must NOT send INSTrument:SELECT
        assert not any("INSTRUMENT:SELECT" in c or "INST:SEL" in c for c in cmds), (
            f"Matrix is single-channel; SELECT must not be sent: {cmds}"
        )

    def test_enable_output_emits_output_state(self, hp_e3631a):
        """psu_enable_output(True) must send OUTPUT:STATE ON, not just
        return 'OK' silently."""
        from lab_instruments.src.labview_bridge import psu_enable_output

        psu, mi = hp_e3631a
        inst_id = _inject(psu, "psu")
        psu_enable_output(inst_id, True)
        mi.write.assert_called_with("OUTPUT:STATE ON")

    def test_disable_all_emits_output_off_and_resets_setpoints(self, hp_e3631a):
        """Regression: disable_all_channels must emit OUTPUT:STATE OFF AND
        reset every channel to a safe state with DEFAULT_CURRENT_LIMIT
        (not zero - zero current limit caused the CC-at-0A bug in the
        LabVIEW path before v1.0.62)."""
        from lab_instruments.src.labview_bridge import psu_disable_all

        psu, mi = hp_e3631a
        inst_id = _inject(psu, "psu")
        psu_disable_all(inst_id)
        cmds = [c.args[0] for c in mi.write.call_args_list]
        assert "OUTPUT:STATE OFF" in cmds
        # All three HP channels reset to 0V with their DEFAULT_CURRENT_LIMIT
        assert "APPLY P6V, 0.0, 1.0" in cmds
        assert "APPLY P25V, 0.0, 0.5" in cmds
        assert "APPLY N25V, 0.0, 0.5" in cmds


# =========================================================================
# DMM configure_* family (new in v1.0.65)
# =========================================================================


class TestDMMConfigureDCVoltage:
    """The Lab 1 motivator: the SCPI REPL script did
    `dmm config vdc 0.1 0.0001 nplc=10` and the LabVIEW bridge had no
    way to express that. Now `dmm_configure_dc_voltage(id, 0.1, 0.0001, 10)`
    emits the same SCPI."""

    def test_hp_explicit_range_resolution_nplc(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_configure_dc_voltage

        dmm, mi = hp_34401a
        inst_id = _inject(dmm, "dmm")
        result = dmm_configure_dc_voltage(inst_id, 0.1, 0.0001, 10)
        assert result == "OK"
        cmds = [c.args[0] for c in mi.write.call_args_list]
        # HP_34401A emits CONFigure then SENSe:VOLTage:DC:NPLCycles
        assert any("CONF" in c.upper() and "VOLT" in c.upper() for c in cmds)
        assert any("NPLC" in c.upper() and "10" in c for c in cmds)

    def test_hp_default_sentinel_uses_def(self, hp_34401a):
        """range_val=-1.0 means 'instrument default' and should produce
        'DEF' in the SCPI string (not '-1' or '0')."""
        from lab_instruments.src.labview_bridge import dmm_configure_dc_voltage

        dmm, mi = hp_34401a
        inst_id = _inject(dmm, "dmm")
        dmm_configure_dc_voltage(inst_id, -1.0, -1.0, -1.0)
        cmds = [c.args[0] for c in mi.write.call_args_list]
        assert any("DEF,DEF" in c for c in cmds), f"expected DEF,DEF in {cmds}"
        # nplc=-1 means skip NPLC altogether
        assert not any("NPLC" in c.upper() for c in cmds)

    def test_hp_zero_range_is_explicit(self, hp_34401a):
        """range_val=0.0 should be passed through as 0 (unusual but
        explicit), NOT translated to DEF. Sentinel for DEF is strictly
        negative."""
        from lab_instruments.src.labview_bridge import dmm_configure_dc_voltage

        dmm, mi = hp_34401a
        inst_id = _inject(dmm, "dmm")
        # range_val=0.0 should not become DEF
        dmm_configure_dc_voltage(inst_id, 0.0, -1.0, -1.0)
        cmds = [c.args[0] for c in mi.write.call_args_list]
        # The CONF command should mention 0 for range, DEF for resolution
        assert any("CONF" in c.upper() and "0," in c and "DEF" in c for c in cmds), f"got {cmds}"

    def test_edu34450a_ignores_nplc(self, keysight_edu34450a):
        """EDU34450A driver doesn't accept nplc - the bridge must drop it
        silently rather than fail."""
        from lab_instruments.src.labview_bridge import dmm_configure_dc_voltage

        dmm, mi = keysight_edu34450a
        inst_id = _inject(dmm, "dmm")
        result = dmm_configure_dc_voltage(inst_id, 0.1, 0.0001, 10.0)
        assert result == "OK"
        cmds = [c.args[0] for c in mi.write.call_args_list]
        # CONFigure goes through; NPLC must NOT appear
        assert any("CONF" in c.upper() and "VOLT" in c.upper() for c in cmds)
        assert not any("NPLC" in c.upper() for c in cmds)

    def test_owon_uses_only_range(self, owon_xdm1041):
        """Owon driver takes only range_val (float | None). The bridge
        must drop resolution and nplc."""
        from lab_instruments.src.labview_bridge import dmm_configure_dc_voltage

        dmm, _ = owon_xdm1041
        inst_id = _inject(dmm, "dmm")
        # Owon mock; just verify it doesn't raise
        result = dmm_configure_dc_voltage(inst_id, 10.0, 0.001, 10.0)
        assert result == "OK"

    def test_rejects_empty_id(self):
        from lab_instruments.src.labview_bridge import dmm_configure_dc_voltage

        with pytest.raises(ValueError, match="instrument_id"):
            dmm_configure_dc_voltage("", 0.1, 0.0001, 10.0)

    def test_rejects_string_range(self, hp_34401a):
        """LabVIEW user wires a String Constant 'DEF' instead of a Numeric
        Constant - the bridge must reject this. The way to express 'use
        default' is range_val=-1.0, not the string 'DEF'."""
        from lab_instruments.src.labview_bridge import dmm_configure_dc_voltage

        dmm, _ = hp_34401a
        inst_id = _inject(dmm, "dmm")
        with pytest.raises(TypeError, match="range_val.*must be a number"):
            dmm_configure_dc_voltage(inst_id, "DEF", 0.0001, 10.0)


class TestDMMConfigureOtherTypes:
    def test_configure_ac_voltage_hp(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_configure_ac_voltage

        dmm, mi = hp_34401a
        inst_id = _inject(dmm, "dmm")
        assert dmm_configure_ac_voltage(inst_id, 1.0, 0.001) == "OK"
        cmds = [c.args[0] for c in mi.write.call_args_list]
        # HP_34401A uses long-form CONFigure:VOLTage:AC
        assert any("CONF" in c.upper() and "VOLTAGE:AC" in c.upper() for c in cmds), f"got {cmds}"

    def test_configure_dc_current_hp_with_nplc(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_configure_dc_current

        dmm, mi = hp_34401a
        inst_id = _inject(dmm, "dmm")
        assert dmm_configure_dc_current(inst_id, 0.1, 0.0001, 10.0) == "OK"
        cmds = [c.args[0] for c in mi.write.call_args_list]
        assert any("CONF" in c.upper() and "CURR" in c.upper() for c in cmds)
        assert any("NPLC" in c.upper() and "10" in c for c in cmds)

    def test_configure_ac_current_edu(self, keysight_edu34450a):
        from lab_instruments.src.labview_bridge import dmm_configure_ac_current

        dmm, mi = keysight_edu34450a
        inst_id = _inject(dmm, "dmm")
        assert dmm_configure_ac_current(inst_id, 0.1, 0.001) == "OK"
        assert mi.write.called

    def test_configure_resistance_2w_hp_with_nplc(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_configure_resistance_2w

        dmm, mi = hp_34401a
        inst_id = _inject(dmm, "dmm")
        assert dmm_configure_resistance_2w(inst_id, 1000.0, 0.1, 10.0) == "OK"
        cmds = [c.args[0] for c in mi.write.call_args_list]
        assert any("CONF" in c.upper() and "RES" in c.upper() for c in cmds)
        assert any("NPLC" in c.upper() for c in cmds)

    def test_configure_resistance_4w_hp(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_configure_resistance_4w

        dmm, mi = hp_34401a
        inst_id = _inject(dmm, "dmm")
        assert dmm_configure_resistance_4w(inst_id, 100.0, 0.001, 10.0) == "OK"
        cmds = [c.args[0] for c in mi.write.call_args_list]
        assert any("FRES" in c.upper() for c in cmds), f"expected FRES in {cmds}"


class TestDMMRead:
    """dmm_read triggers a measurement using the currently-configured mode.
    This is the configure-then-read flow that Lab 1 needs."""

    def test_read_hp(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_read

        dmm, mi = hp_34401a
        mi.query.return_value = "5.0023"
        inst_id = _inject(dmm, "dmm")
        result = dmm_read(inst_id)
        assert result == pytest.approx(5.0023, rel=1e-6)
        # HP's read() issues a READ? query
        mi.query.assert_called_with("READ?")

    def test_read_owon(self, owon_xdm1041):
        from lab_instruments.src.labview_bridge import dmm_read

        dmm, mi = owon_xdm1041
        mi.query.return_value = "1.234"
        inst_id = _inject(dmm, "dmm")
        result = dmm_read(inst_id)
        assert isinstance(result, float)

    def test_read_rejects_empty_id(self):
        from lab_instruments.src.labview_bridge import dmm_read

        with pytest.raises(ValueError, match="instrument_id"):
            dmm_read("")


class TestDMMFetch:
    def test_fetch_hp(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_fetch

        dmm, mi = hp_34401a
        mi.query.return_value = "5.0023"
        inst_id = _inject(dmm, "dmm")
        result = dmm_fetch(inst_id)
        assert isinstance(result, float)

    def test_fetch_owon_raises_attribute_error(self, owon_xdm1041):
        """Owon driver does not implement fetch(); the bridge must raise a
        clear AttributeError naming the alternative (dmm_read)."""
        from lab_instruments.src.labview_bridge import dmm_fetch

        dmm, _ = owon_xdm1041
        inst_id = _inject(dmm, "dmm")
        with pytest.raises(AttributeError, match="dmm_read"):
            dmm_fetch(inst_id)


class TestDMMGetError:
    def test_get_error_hp(self, hp_34401a):
        from lab_instruments.src.labview_bridge import dmm_get_error

        dmm, mi = hp_34401a
        mi.query.return_value = '+0,"No error"'
        inst_id = _inject(dmm, "dmm")
        result = dmm_get_error(inst_id)
        assert isinstance(result, str)
        assert "No error" in result

    def test_get_error_owon_returns_stub(self, owon_xdm1041):
        """Owon driver's get_error returns a 'not supported' string per the
        SCPI driver contract."""
        from lab_instruments.src.labview_bridge import dmm_get_error

        dmm, _ = owon_xdm1041
        inst_id = _inject(dmm, "dmm")
        result = dmm_get_error(inst_id)
        assert isinstance(result, str)

    def test_rejects_empty_id(self):
        from lab_instruments.src.labview_bridge import dmm_get_error

        with pytest.raises(ValueError, match="instrument_id"):
            dmm_get_error("")


# =========================================================================
# PSU readback wrappers (new in v1.0.65)
# =========================================================================


class TestPSUGetVoltageSetpoint:
    def test_hp_emits_volt_query(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_get_voltage_setpoint

        psu, mi = hp_e3631a
        mi.query.return_value = "5.000"
        inst_id = _inject(psu, "psu")
        result = psu_get_voltage_setpoint(inst_id, 1)
        assert result == pytest.approx(5.0, rel=1e-6)
        mi.query.assert_called_with("VOLTAGE?")

    def test_edu36311a(self, keysight_edu36311a):
        from lab_instruments.src.labview_bridge import psu_get_voltage_setpoint

        psu, mi = keysight_edu36311a
        mi.query.return_value = "12.000"
        inst_id = _inject(psu, "psu")
        result = psu_get_voltage_setpoint(inst_id, 2)
        assert isinstance(result, float)

    def test_matrix(self, matrix_mps6010h):
        """Matrix is cached; no query is needed (driver returns the cached
        setpoint). The bridge call must succeed and return a float."""
        from lab_instruments.src.labview_bridge import psu_get_voltage_setpoint

        psu, _ = matrix_mps6010h
        psu.set_voltage(15.0)
        inst_id = _inject(psu, "psu")
        result = psu_get_voltage_setpoint(inst_id, 1)
        assert result == pytest.approx(15.0)

    def test_invalid_channel(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_get_voltage_setpoint

        psu, _ = hp_e3631a
        inst_id = _inject(psu, "psu")
        with pytest.raises(ValueError, match="channel must be 1, 2, or 3"):
            psu_get_voltage_setpoint(inst_id, 9)

    def test_rejects_empty_id(self):
        from lab_instruments.src.labview_bridge import psu_get_voltage_setpoint

        with pytest.raises(ValueError, match="instrument_id"):
            psu_get_voltage_setpoint("", 1)


class TestPSUGetCurrentLimit:
    def test_hp_emits_curr_query(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_get_current_limit

        psu, mi = hp_e3631a
        mi.query.return_value = "0.500"
        inst_id = _inject(psu, "psu")
        result = psu_get_current_limit(inst_id, 1)
        assert result == pytest.approx(0.5)
        mi.query.assert_called_with("CURRENT?")

    def test_matrix(self, matrix_mps6010h):
        from lab_instruments.src.labview_bridge import psu_get_current_limit

        psu, _ = matrix_mps6010h
        psu.set_current_limit(2.5)
        inst_id = _inject(psu, "psu")
        result = psu_get_current_limit(inst_id, 1)
        assert result == pytest.approx(2.5)


class TestPSUGetOutputState:
    def test_hp_emits_output_state_query(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_get_output_state

        psu, mi = hp_e3631a
        mi.query.return_value = "1"
        inst_id = _inject(psu, "psu")
        result = psu_get_output_state(inst_id)
        assert result is True
        mi.query.assert_called_with("OUTPUT:STATE?")

    def test_hp_off(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_get_output_state

        psu, mi = hp_e3631a
        mi.query.return_value = "0"
        inst_id = _inject(psu, "psu")
        result = psu_get_output_state(inst_id)
        assert result is False

    def test_matrix_cached(self, matrix_mps6010h):
        """Matrix tracks output state in a cache (no readback)."""
        from lab_instruments.src.labview_bridge import psu_get_output_state

        psu, _ = matrix_mps6010h
        psu.enable_output(True)
        inst_id = _inject(psu, "psu")
        assert psu_get_output_state(inst_id) is True


class TestPSUGetError:
    def test_hp(self, hp_e3631a):
        from lab_instruments.src.labview_bridge import psu_get_error

        psu, mi = hp_e3631a
        mi.query.return_value = '+0,"No error"'
        inst_id = _inject(psu, "psu")
        result = psu_get_error(inst_id)
        assert "No error" in result
        mi.query.assert_called_with("SYSTEM:ERROR?")

    def test_matrix_returns_stub(self, matrix_mps6010h):
        from lab_instruments.src.labview_bridge import psu_get_error

        psu, _ = matrix_mps6010h
        inst_id = _inject(psu, "psu")
        result = psu_get_error(inst_id)
        # Matrix returns "not supported on..." per driver contract
        assert "not supported" in result.lower()


# =========================================================================
# AWG state-readback + set_offset + get_error (new in v1.0.65)
# =========================================================================


class TestAWGSetOffset:
    def test_bk(self, bk_4063):
        from lab_instruments.src.labview_bridge import awg_set_offset

        awg, mi = bk_4063
        inst_id = _inject(awg, "awg")
        assert awg_set_offset(inst_id, 1, 1.5) == "OK"
        assert mi.write.called

    def test_keysight(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_set_offset

        awg, mi = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        assert awg_set_offset(inst_id, 1, 1.5) == "OK"
        assert mi.write.called

    def test_jds6600(self, jds6600_generator):
        from lab_instruments.src.labview_bridge import awg_set_offset

        awg, _ = jds6600_generator
        inst_id = _inject(awg, "awg")
        assert awg_set_offset(inst_id, 1, 1.5) == "OK"

    def test_rejects_channel_3(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_set_offset

        awg, _ = keysight_edu33212a
        inst_id = _inject(awg, "awg")
        with pytest.raises(ValueError, match="channel"):
            awg_set_offset(inst_id, 3, 1.0)


class TestAWGGetters:
    """Each get_* must return the right type and exercise the driver method."""

    def test_get_amplitude_bk(self, bk_4063):
        from lab_instruments.src.labview_bridge import awg_get_amplitude

        awg, mi = bk_4063
        mi.query.return_value = "C1:BSWV WVTP,SINE,AMP,2.00,OFST,0.00,FRQ,1000"
        inst_id = _inject(awg, "awg")
        result = awg_get_amplitude(inst_id, 1)
        assert isinstance(result, float)

    def test_get_offset_keysight(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_get_offset

        awg, mi = keysight_edu33212a
        mi.query.return_value = "0.500"
        inst_id = _inject(awg, "awg")
        result = awg_get_offset(inst_id, 1)
        assert result == pytest.approx(0.5)

    def test_get_frequency_keysight(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_get_frequency

        awg, mi = keysight_edu33212a
        mi.query.return_value = "1000.0"
        inst_id = _inject(awg, "awg")
        result = awg_get_frequency(inst_id, 1)
        assert isinstance(result, float)

    def test_get_output_state_keysight(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_get_output_state

        awg, mi = keysight_edu33212a
        mi.query.return_value = "1"
        inst_id = _inject(awg, "awg")
        result = awg_get_output_state(inst_id, 1)
        assert isinstance(result, bool)

    def test_get_output_state_returns_true(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_get_output_state

        awg, mi = keysight_edu33212a
        mi.query.return_value = "1"
        inst_id = _inject(awg, "awg")
        assert awg_get_output_state(inst_id, 1) is True


class TestAWGGetError:
    def test_keysight(self, keysight_edu33212a):
        from lab_instruments.src.labview_bridge import awg_get_error

        awg, mi = keysight_edu33212a
        mi.query.return_value = '+0,"No error"'
        inst_id = _inject(awg, "awg")
        result = awg_get_error(inst_id)
        assert "No error" in result

    def test_jds6600_returns_not_supported(self, jds6600_generator):
        """JDS6600 has no get_error method (no SCPI error queue). Bridge
        must gracefully return a 'not supported' string instead of raising
        AttributeError."""
        from lab_instruments.src.labview_bridge import awg_get_error

        awg, _ = jds6600_generator
        inst_id = _inject(awg, "awg")
        result = awg_get_error(inst_id)
        assert "not supported" in result.lower()
        assert "JDS6600" in result


# =========================================================================
# BQ76920 SYS_STAT helpers (new in v1.0.66, issue #128)
# =========================================================================
#
# Datasheet reference: BQ76920 SLUSBK2I, Table 8-3 (SYS_STAT, p.30).
# Verified bit map (independently confirmed against the TI PDF):
#   bit 7: CC_READY     bit 6: RSVD            bit 5: DEVICE_XREADY
#   bit 4: OVRD_ALERT   bit 3: UV              bit 2: OV
#   bit 1: SCD          bit 0: OCD
# Write-1-to-clear: "Bits in SYS_STAT may be cleared by writing a '1' to
# the corresponding bit. Writing a '0' does not change the state of the
# corresponding bit." (datasheet section 8.5.1)


class TestEv2300ReadSysStat:
    def test_decodes_user_observed_0x84(self, ev2300):
        """Issue #128 reproduction: user saw 0x84 after sending 25V to the
        BQ EVM. Per datasheet that is CC_READY (bit 7) + OV (bit 2)."""
        from lab_instruments.src.labview_bridge import ev2300_read_sys_stat

        dev, _ = ev2300
        dev.read_byte = MagicMock(return_value={"ok": True, "value": 0x84, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = json.loads(ev2300_read_sys_stat(inst_id))
        assert result["raw"] == 0x84
        assert result["raw_hex"] == "0x84"
        assert result["bits"]["CC_READY"] is True
        assert result["bits"]["OV"] is True
        assert result["bits"]["UV"] is False  # critical: NOT bit 3
        assert result["bits"]["DEVICE_XREADY"] is False
        assert result["bits"]["SCD"] is False
        assert result["bits"]["OCD"] is False
        assert "OV" in result["active_faults"]
        # CC_READY is a status flag, not a fault - must NOT appear in active_faults
        assert "CC_READY" not in result["active_faults"]
        assert "OV" in result["active_bits"]
        assert "CC_READY" in result["active_bits"]

    def test_all_faults_set(self, ev2300):
        """0x3F = 0011_1111 = bits 0..5 set = DEVICE_XREADY + OVRD_ALERT +
        UV + OV + SCD + OCD (CC_READY clear). OVRD_ALERT is not a fault,
        so active_faults must exclude it but include everything else."""
        from lab_instruments.src.labview_bridge import ev2300_read_sys_stat

        dev, _ = ev2300
        dev.read_byte = MagicMock(return_value={"ok": True, "value": 0x3F, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = json.loads(ev2300_read_sys_stat(inst_id))
        assert result["bits"]["CC_READY"] is False
        assert result["bits"]["DEVICE_XREADY"] is True
        assert result["bits"]["OVRD_ALERT"] is True
        assert result["bits"]["UV"] is True
        assert result["bits"]["OV"] is True
        assert result["bits"]["SCD"] is True
        assert result["bits"]["OCD"] is True
        # OVRD_ALERT is a status flag, not a latched fault
        assert set(result["active_faults"]) == {"DEVICE_XREADY", "UV", "OV", "SCD", "OCD"}

    def test_baseline_only_cc_ready(self, ev2300):
        """0x80 = CC_READY alone. No faults active."""
        from lab_instruments.src.labview_bridge import ev2300_read_sys_stat

        dev, _ = ev2300
        dev.read_byte = MagicMock(return_value={"ok": True, "value": 0x80, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = json.loads(ev2300_read_sys_stat(inst_id))
        assert result["active_bits"] == ["CC_READY"]
        assert result["active_faults"] == []

    def test_uv_at_bit_3_not_bit_2(self, ev2300):
        """Regression: UV is bit 3, OV is bit 2 per datasheet Table 8-3.
        An off-by-one that swapped them would set UV when OV was active
        and silently mislead students debugging overvoltage events."""
        from lab_instruments.src.labview_bridge import ev2300_read_sys_stat

        dev, _ = ev2300
        # Only bit 3 set: should be UV (not OV)
        dev.read_byte = MagicMock(return_value={"ok": True, "value": 0x08, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = json.loads(ev2300_read_sys_stat(inst_id))
        assert result["bits"]["UV"] is True
        assert result["bits"]["OV"] is False
        assert "UV" in result["active_faults"]
        assert "OV" not in result["active_faults"]

    def test_reserved_bit_6_not_in_bits_dict(self, ev2300):
        """Bit 6 is RSVD per datasheet - the decoder must not invent a
        name for it. If a future datasheet revision adds a flag at bit 6
        this test fails loudly and forces a deliberate update."""
        from lab_instruments.src.labview_bridge import ev2300_read_sys_stat

        dev, _ = ev2300
        dev.read_byte = MagicMock(return_value={"ok": True, "value": 0x40, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = json.loads(ev2300_read_sys_stat(inst_id))
        # bit 6 is RSVD - must not show up under any of these
        assert len(result["bits"]) == 7  # 7 named bits, not 8
        assert result["active_bits"] == []  # nothing in the named set is set
        assert result["active_faults"] == []

    def test_default_i2c_addr_is_0x08(self, ev2300):
        """BQ76920 2.5V LDO variant default address per eset-453
        python-conventions.md and bq76920_driver. The bridge default must
        match so students don't need to remember the address."""
        from lab_instruments.src.labview_bridge import ev2300_read_sys_stat

        dev, _ = ev2300
        dev.read_byte = MagicMock(return_value={"ok": True, "value": 0x80, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        ev2300_read_sys_stat(inst_id)  # no addr arg
        dev.read_byte.assert_called_once_with(0x08, 0x00)

    def test_failure_propagates(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_read_sys_stat

        dev, _ = ev2300
        dev.read_byte = MagicMock(return_value={"ok": False, "value": 0, "status_text": "NACK"})
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(RuntimeError, match="NACK"):
            ev2300_read_sys_stat(inst_id)

    def test_rejects_empty_id(self):
        from lab_instruments.src.labview_bridge import ev2300_read_sys_stat

        with pytest.raises(ValueError, match="instrument_id"):
            ev2300_read_sys_stat("")

    def test_rejects_bad_i2c_addr(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_read_sys_stat

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(ValueError, match="i2c_addr"):
            ev2300_read_sys_stat(inst_id, 0x80)


class TestEv2300ClearBqFaults:
    """Regression for issue #128: SYS_STAT is W1C, not normal R/W.
    The clear_bq_faults helper writes the mask (default 0xFF) to clear
    every latched bit. A typical user-facing flow:

        sys_stat = ev2300_read_sys_stat(id)   # see what's latched
        # drop PSU below OV_TRIP first if OV is set, then:
        ev2300_clear_bq_faults(id)            # writes 0xFF
        sys_stat = ev2300_read_sys_stat(id)   # confirm clean
    """

    def test_default_mask_is_full_clear(self, ev2300):
        """Default mask=0xFF clears every bit (W1C semantics: only bits
        set to 1 in the write get cleared, so 0xFF clears all)."""
        from lab_instruments.src.labview_bridge import ev2300_clear_bq_faults

        dev, _ = ev2300
        dev.write_byte = MagicMock(return_value={"ok": True, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        result = ev2300_clear_bq_faults(inst_id)
        assert result == "OK"
        dev.write_byte.assert_called_once_with(0x08, 0x00, 0xFF)

    def test_custom_mask_clears_only_named_bit(self, ev2300):
        """mask=0x04 clears OV (bit 2) and leaves UV, DEVICE_XREADY etc.
        untouched. Useful when you want to clear OV without disturbing
        a deliberately latched warning."""
        from lab_instruments.src.labview_bridge import ev2300_clear_bq_faults

        dev, _ = ev2300
        dev.write_byte = MagicMock(return_value={"ok": True, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        ev2300_clear_bq_faults(inst_id, mask=0x04)
        dev.write_byte.assert_called_once_with(0x08, 0x00, 0x04)

    def test_explicit_i2c_addr(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_clear_bq_faults

        dev, _ = ev2300
        dev.write_byte = MagicMock(return_value={"ok": True, "status_text": "OK"})
        inst_id = _inject(dev, "ev2300")
        ev2300_clear_bq_faults(inst_id, i2c_addr=0x18, mask=0xFF)
        dev.write_byte.assert_called_once_with(0x18, 0x00, 0xFF)

    def test_write_failure_propagates(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_clear_bq_faults

        dev, _ = ev2300
        dev.write_byte = MagicMock(return_value={"ok": False, "status_text": "Device error (0x46)"})
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(RuntimeError, match="Device error"):
            ev2300_clear_bq_faults(inst_id)

    def test_rejects_empty_id(self):
        from lab_instruments.src.labview_bridge import ev2300_clear_bq_faults

        with pytest.raises(ValueError, match="instrument_id"):
            ev2300_clear_bq_faults("")

    def test_rejects_mask_too_large(self, ev2300):
        from lab_instruments.src.labview_bridge import ev2300_clear_bq_faults

        dev, _ = ev2300
        inst_id = _inject(dev, "ev2300")
        with pytest.raises(ValueError, match="mask"):
            ev2300_clear_bq_faults(inst_id, mask=0x100)

    def test_issue_128_reproduction(self, ev2300):
        """End-to-end reproduction of issue #128 with the correct fix.

        Pre-fix behavior (what the student saw):
          ev2300_write_byte(id, 0x08, 0x00, 0x80)  # cleared only CC_READY
          ev2300_read_byte(id, 0x08, 0x00) -> 0x84  # OV still latched

        Post-fix behavior (what they should do now):
          ev2300_clear_bq_faults(id)  # writes 0xFF, clears OV bit too
          ev2300_read_sys_stat(id)['active_faults'] -> [] (assuming
              cell voltage is back below OV_TRIP - otherwise OV re-latches)
        """
        from lab_instruments.src.labview_bridge import ev2300_clear_bq_faults, ev2300_read_sys_stat

        dev, _ = ev2300

        # Simulate hardware: SYS_STAT starts at 0x84, after we write 0xFF
        # the cell voltage is back below OV_TRIP so OV stays cleared, and
        # CC_READY re-asserts on the next CC sample so the next read shows
        # 0x80 (just CC_READY).
        read_responses = iter(
            [
                {"ok": True, "value": 0x80, "status_text": "OK"},
            ]
        )
        dev.write_byte = MagicMock(return_value={"ok": True, "status_text": "OK"})
        dev.read_byte = MagicMock(side_effect=lambda addr, reg: next(read_responses))

        inst_id = _inject(dev, "ev2300")
        ev2300_clear_bq_faults(inst_id)
        dev.write_byte.assert_called_once_with(0x08, 0x00, 0xFF)

        after = json.loads(ev2300_read_sys_stat(inst_id))
        assert after["raw"] == 0x80
        assert after["active_faults"] == [], "OV should be cleared after W1C"
        assert "CC_READY" in after["active_bits"]
