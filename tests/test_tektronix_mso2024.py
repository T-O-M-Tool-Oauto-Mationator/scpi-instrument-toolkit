"""tests/test_tektronix_mso2024.py -- Driver-level unit tests for Tektronix MSO2024."""

import csv

import pytest

# ===========================================================================
# 1. TestSaveWaveformCsvSingleChannel
# ===========================================================================


class TestSaveWaveformCsvSingleChannel:
    def test_save_waveform_csv_single_channel(self, tektronix_mso2024, tmp_path, monkeypatch):
        """Single int channel writes a 2-column CSV with correct header and data."""
        scope, _mi = tektronix_mso2024
        monkeypatch.setattr(
            scope,
            "get_waveform_scaled",
            lambda ch: ([0.0, 0.001, 0.002], [1.0, 2.0, 3.0]),
        )
        out = tmp_path / "ch1.csv"
        scope.save_waveform_csv(1, str(out))

        with open(str(out), newline="") as f:
            rows = list(csv.reader(f))

        assert rows[0] == ["Time (s)", "Channel 1 Voltage (V)"]
        assert rows[1] == ["0.0", "1.0"]
        assert rows[2] == ["0.001", "2.0"]
        assert rows[3] == ["0.002", "3.0"]


# ===========================================================================
# 2. TestSaveWaveformCsvListDelegates  (regression for #78)
# ===========================================================================


class TestSaveWaveformCsvListDelegates:
    def test_save_waveform_csv_list_delegates(self, tektronix_mso2024, tmp_path, monkeypatch):
        """list arg [1,2] must not raise TypeError and must produce multi-channel CSV."""
        scope, _mi = tektronix_mso2024

        def fake_scaled(ch):
            return ([0.0, 0.001], [1.0, 2.0]) if ch == 1 else ([0.0, 0.001], [3.0, 4.0])

        monkeypatch.setattr(scope, "get_waveform_scaled", fake_scaled)
        out = tmp_path / "multi.csv"
        scope.save_waveform_csv([1, 2], str(out))

        with open(str(out), newline="") as f:
            rows = list(csv.reader(f))

        assert rows[0] == ["Time (s)", "CH1 Voltage (V)", "CH2 Voltage (V)"]
        assert rows[1][0] == "0.0"
        assert rows[1][1] == "1.0"
        assert rows[1][2] == "3.0"


# ===========================================================================
# 3. TestSaveWaveformCsvTupleDelegates
# ===========================================================================


class TestSaveWaveformCsvTupleDelegates:
    def test_save_waveform_csv_tuple_delegates(self, tektronix_mso2024, tmp_path, monkeypatch):
        """tuple (1,2) also delegates to save_waveforms_csv without error."""
        scope, _mi = tektronix_mso2024

        def fake_scaled(ch):
            return ([0.0, 0.001], [1.0, 2.0]) if ch == 1 else ([0.0, 0.001], [3.0, 4.0])

        monkeypatch.setattr(scope, "get_waveform_scaled", fake_scaled)
        out = tmp_path / "tuple.csv"
        scope.save_waveform_csv((1, 2), str(out))

        with open(str(out), newline="") as f:
            rows = list(csv.reader(f))

        assert rows[0] == ["Time (s)", "CH1 Voltage (V)", "CH2 Voltage (V)"]


# ===========================================================================
# 4. TestSaveWaveformCsvInvalidChannel
# ===========================================================================


class TestSaveWaveformCsvInvalidChannel:
    def test_save_waveform_csv_invalid_channel(self, tektronix_mso2024, tmp_path):
        """Channel 5 raises ValueError -- validation happens inside get_waveform_scaled."""
        scope, _mi = tektronix_mso2024
        out = tmp_path / "bad.csv"
        with pytest.raises(ValueError):
            scope.save_waveform_csv(5, str(out))


# ===========================================================================
# 5. TestSaveWaveformsCsvMultiple
# ===========================================================================


class TestSaveWaveformsCsvMultiple:
    def test_save_waveforms_csv_multiple(self, tektronix_mso2024, tmp_path, monkeypatch):
        """save_waveforms_csv([1,2], ...) writes correct multi-column CSV."""
        scope, _mi = tektronix_mso2024

        def fake_scaled(ch):
            return ([0.0, 0.001], [1.0, 2.0]) if ch == 1 else ([0.0, 0.001], [3.0, 4.0])

        monkeypatch.setattr(scope, "get_waveform_scaled", fake_scaled)
        out = tmp_path / "waveforms.csv"
        scope.save_waveforms_csv([1, 2], str(out))

        with open(str(out), newline="") as f:
            rows = list(csv.reader(f))

        assert rows[0] == ["Time (s)", "CH1 Voltage (V)", "CH2 Voltage (V)"]
        assert rows[1] == ["0.0", "1.0", "3.0"]
        assert rows[2] == ["0.001", "2.0", "4.0"]


# ===========================================================================
# 6. TestContextManagerExitFiresOnException
# ===========================================================================


class TestContextManagerExitFiresOnException:
    def test_context_manager_exit_fires_on_exception(self, tektronix_mso2024):
        """__exit__ must fire (disabling all channels) even when the body raises."""
        scope, mi = tektronix_mso2024

        try:
            with scope:
                mi.reset_mock()
                raise RuntimeError("test body error")
        except RuntimeError:
            pass

        sent = [c.args[0] for c in mi.write.call_args_list]
        for ch_name in ("CH1", "CH2", "CH3", "CH4"):
            assert f"SELect:{ch_name} OFF" in sent
        assert "SELect:MATH OFF" in sent


# ===========================================================================
# 7. TestCacheUpdates
# ===========================================================================


class TestCacheUpdates:
    def test_set_coupling_updates_cache(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        scope.set_coupling(1, "DC")
        assert scope._cache["ch1_coupling"] == "DC"

    def test_set_horizontal_scale_updates_cache(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        scope.set_horizontal_scale(0.001)
        assert scope._cache["horizontal_scale"] == 0.001

    def test_set_vertical_scale_updates_cache(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        scope.set_vertical_scale(1, 2.0, 1.5)
        assert scope._cache["ch1_scale"] == 2.0
        assert scope._cache["ch1_position"] == 1.5

    def test_configure_trigger_updates_cache(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        scope.configure_trigger(1, 1.5, slope="RISE", mode="AUTO")
        assert scope._cache["trigger_source"] == 1
        assert scope._cache["trigger_level"] == 1.5
        assert scope._cache["trigger_slope"] == "RISE"
        assert scope._cache["trigger_mode"] == "AUTO"


# ===========================================================================
# 8. TestAllowlistValidation
# ===========================================================================


class TestAllowlistValidation:
    def test_set_coupling_invalid_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="Coupling"):
            scope.set_coupling(1, "INVALID")

    def test_set_acquisition_mode_invalid_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="Mode"):
            scope.set_acquisition_mode("INVALID")

    def test_set_acquisition_stop_after_invalid_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="Mode"):
            scope.set_acquisition_stop_after("INVALID")

    def test_configure_trigger_invalid_slope_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="Slope"):
            scope.configure_trigger(1, 1.0, slope="INVALID")

    def test_configure_trigger_invalid_mode_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="Mode"):
            scope.configure_trigger(1, 1.0, mode="INVALID")

    def test_measure_delay_invalid_edge_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="edge1"):
            scope.measure_delay(1, 2, edge1="INVALID")

    def test_measure_delay_invalid_direction_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="direction"):
            scope.measure_delay(1, 2, direction="INVALID")


# ===========================================================================
# 9. TestNumericValidation
# ===========================================================================


class TestNumericValidation:
    def test_set_horizontal_scale_zero_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="positive"):
            scope.set_horizontal_scale(0)

    def test_set_horizontal_scale_negative_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="positive"):
            scope.set_horizontal_scale(-1.0)

    def test_set_horizontal_position_below_zero_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="between 0 and 100"):
            scope.set_horizontal_position(-1.0)

    def test_set_horizontal_position_above_100_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="between 0 and 100"):
            scope.set_horizontal_position(101.0)

    def test_set_vertical_scale_zero_raises(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError, match="positive"):
            scope.set_vertical_scale(1, 0)


# ===========================================================================
# 10. TestGetErrorUsesEventQueue  (regression: SYSTem:ERRor? hangs the bus)
# ===========================================================================


class TestGetErrorUsesEventQueue:
    """Tek 2-Series does not implement SYSTem:ERRor? — the driver must use
    *ESR? + ALLEv? per the Programmer Manual. Querying SYSTem:ERRor? hangs
    the bus until the VISA timeout fires; this regression catches that.
    """

    def test_get_error_no_pending_event_returns_no_error(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        mi.query.return_value = "0"  # *ESR? returns 0 = no events
        result = scope.get_error()
        assert result == '0,"No error"'
        # Must not have queried SYSTem:ERRor?
        queries = [c.args[0] for c in mi.query.call_args_list]
        assert "*ESR?" in queries
        assert not any("SYST" in q for q in queries)

    def test_get_error_with_pending_event_drains_via_allev(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        # Bit 5 (CME, command error) is set
        mi.query.side_effect = ["32", '420,"Query UNTERMINATED"']
        result = scope.get_error()
        assert "Query UNTERMINATED" in result
        queries = [c.args[0] for c in mi.query.call_args_list]
        assert queries == ["*ESR?", "ALLEv?"]

    def test_get_error_handles_garbage_esr_response(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        mi.query.return_value = "not-a-number"
        result = scope.get_error()
        assert result == '0,"No error"'


# ===========================================================================
# 11. TestScreenshot  (new method using Tek-specific SAVe:IMAGe)
# ===========================================================================


class TestScreenshot:
    def test_screenshot_emits_save_image(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.screenshot("C:/captures/test.png")
        writes = [c.args[0] for c in mi.write.call_args_list]
        assert 'SAVe:IMAGe "C:/captures/test.png"' in writes

    def test_screenshot_rejects_empty_path(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError):
            scope.screenshot("")

    def test_screenshot_rejects_non_string(self, tektronix_mso2024):
        scope, _mi = tektronix_mso2024
        with pytest.raises(ValueError):
            scope.screenshot(123)

    def test_screenshot_rejects_embedded_double_quote(self, tektronix_mso2024):
        """Regression: SAVe:IMAGe wraps the path in `"..."`. A `"` inside the
        path would terminate the SCPI string and let further tokens be
        injected. Reject up front."""
        scope, mi = tektronix_mso2024
        with pytest.raises(ValueError, match="double-quote"):
            scope.screenshot('C:/foo".bin"; *RST')
        # Nothing should have been sent to the bus on rejection.
        assert not any("SAVe:IMAGe" in c.args[0] for c in mi.write.call_args_list)


# ===========================================================================
# 12. TestMeasClear  (new method using Tek-specific MEASUrement:DELETEALL)
# ===========================================================================


class TestMeasClear:
    def test_meas_clear_emits_delete_all(self, tektronix_mso2024):
        scope, mi = tektronix_mso2024
        scope.meas_clear()
        writes = [c.args[0] for c in mi.write.call_args_list]
        assert "MEASUrement:DELETEALL" in writes
        # Must NOT use the Rigol-style MEASure:CLEar
        assert not any("MEASure:CLEar" in w for w in writes)
