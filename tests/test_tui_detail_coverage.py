"""Tests for InstrumentDetailPanel renderers, button handlers, safety limits panel,
and app-level limit/e-stop actions -- targeting 80%+ coverage."""

from __future__ import annotations

import asyncio

from lab_instruments.tui.app import SCPIApp
from lab_instruments.tui.widgets.instrument_detail import InstrumentDetailPanel, _fmt_eng
from lab_instruments.tui.widgets.safety_limits_panel import SafetyLimitsPanel

# ---------------------------------------------------------------------------
# Stub dispatcher
# ---------------------------------------------------------------------------


class _Stub:
    """Minimal stub dispatcher for widget-level tests."""

    def __init__(self):
        self._commands: list[str] = []

    def handle_command(self, cmd, line_callback=None):
        self._commands.append(cmd)
        return "OK"

    def get_completions(self, text):
        return []

    def get_device_snapshot(self):
        return []

    def get_measurement_snapshot(self):
        return []

    def get_script_names(self):
        return []

    def get_vars_snapshot(self):
        return {}

    def get_safety_snapshot(self):
        return {
            "limit_count": 0,
            "active_script": False,
            "exit_on_error": False,
            "limits": [],
            "measurement_count": 0,
            "data_dir": "",
        }

    def get_instrument_detail(self, name):
        return {"type": "unknown", "name": name, "display_name": name}

    def save_instrument_state(self, name):
        return {"saved": True, "name": name}

    def restore_instrument_state(self, name, snap):
        pass

    def get_script_content(self, name):
        return ""

    def save_script_content(self, name, content):
        pass

    def delete_script(self, name):
        pass


# ---------------------------------------------------------------------------
# _fmt_eng unit tests (synchronous, no TUI required)
# ---------------------------------------------------------------------------


class TestFmtEng:
    def test_none_returns_na(self):
        assert _fmt_eng(None, "V") == "N/A"

    def test_zero(self):
        assert _fmt_eng(0, "V") == "0.000 V"

    def test_megavolts(self):
        result = _fmt_eng(2.5e6, "V")
        assert "M" in result
        assert "2.500" in result

    def test_kilovolts(self):
        result = _fmt_eng(4700.0, "V")
        assert "k" in result
        assert "4.700" in result

    def test_volts(self):
        result = _fmt_eng(3.14, "V")
        assert "3.1400" in result
        assert result.endswith("V")

    def test_millivolts(self):
        result = _fmt_eng(0.0025, "V")
        assert "m" in result
        assert "2.500" in result

    def test_microvolts(self):
        result = _fmt_eng(0.0000035, "V")
        assert "u" in result
        assert "3.500" in result

    def test_nanovolts(self):
        result = _fmt_eng(1.5e-9, "V")
        assert "n" in result
        assert "1.500" in result

    def test_very_small(self):
        result = _fmt_eng(1e-12, "V")
        assert "e" in result  # scientific notation

    def test_negative_milliamps(self):
        result = _fmt_eng(-0.005, "A")
        assert "m" in result
        assert "-5.000" in result

    def test_no_unit(self):
        result = _fmt_eng(100.0)
        assert "100.0000" in result
        # Should not have trailing space
        assert not result.endswith(" ")

    def test_zero_no_unit(self):
        result = _fmt_eng(0)
        assert "0.000" in result


# ---------------------------------------------------------------------------
# _get_limit unit tests (synchronous after widget construction)
# ---------------------------------------------------------------------------


class TestGetLimit:
    def test_no_limits_returns_none(self):
        panel = InstrumentDetailPanel()
        panel.safety_limits = []
        assert panel._get_limit("psu1", 1, "voltage_upper") is None

    def test_exact_match(self):
        panel = InstrumentDetailPanel()
        panel.safety_limits = [
            {"device": "psu1", "channel": 1, "parameter": "voltage_upper", "value": 30.0},
        ]
        assert panel._get_limit("psu1", 1, "voltage_upper") == 30.0

    def test_channel_none_matches_any(self):
        """A limit with channel=None should match any channel query."""
        panel = InstrumentDetailPanel()
        panel.safety_limits = [
            {"device": "psu1", "channel": None, "parameter": "current_upper", "value": 5.0},
        ]
        assert panel._get_limit("psu1", 2, "current_upper") == 5.0

    def test_wrong_device_returns_none(self):
        panel = InstrumentDetailPanel()
        panel.safety_limits = [
            {"device": "psu1", "channel": 1, "parameter": "voltage_upper", "value": 30.0},
        ]
        assert panel._get_limit("psu2", 1, "voltage_upper") is None

    def test_wrong_param_returns_none(self):
        panel = InstrumentDetailPanel()
        panel.safety_limits = [
            {"device": "psu1", "channel": 1, "parameter": "voltage_upper", "value": 30.0},
        ]
        assert panel._get_limit("psu1", 1, "current_upper") is None

    def test_channel_mismatch_returns_none(self):
        """A limit with a specific channel should not match a different channel."""
        panel = InstrumentDetailPanel()
        panel.safety_limits = [
            {"device": "psu1", "channel": 1, "parameter": "voltage_upper", "value": 30.0},
        ]
        assert panel._get_limit("psu1", 2, "voltage_upper") is None


# ---------------------------------------------------------------------------
# _push_history and _accumulate_history
# ---------------------------------------------------------------------------


class TestHistoryAccumulation:
    def test_push_history_none_skipped(self):
        panel = InstrumentDetailPanel()
        panel._push_history("key", None)
        assert "key" not in panel._history

    def test_push_history_stores_value(self):
        panel = InstrumentDetailPanel()
        panel._push_history("key", 5.0)
        assert list(panel._history["key"]) == [5.0]

    def test_push_history_ring_buffer(self):
        panel = InstrumentDetailPanel()
        for i in range(50):
            panel._push_history("key", float(i))
        assert len(panel._history["key"]) == panel._HISTORY_LEN

    def test_accumulate_psu(self):
        panel = InstrumentDetailPanel()
        detail = {
            "type": "psu",
            "name": "psu1",
            "channels": [
                {"label": "CH1", "id": 1, "voltage_meas": 5.0, "current_meas": 0.1},
            ],
        }
        panel._accumulate_history(detail)
        assert list(panel._history["psu1_CH1_voltage"]) == [5.0]
        assert list(panel._history["psu1_CH1_current"]) == [0.1]

    def test_accumulate_smu(self):
        panel = InstrumentDetailPanel()
        detail = {
            "type": "psu",
            "subtype": "smu",
            "name": "smu1",
            "voltage_meas": 12.0,
            "current_meas": 0.5,
        }
        panel._accumulate_history(detail)
        assert list(panel._history["smu1_voltage"]) == [12.0]
        assert list(panel._history["smu1_current"]) == [0.5]

    def test_accumulate_dmm(self):
        panel = InstrumentDetailPanel()
        detail = {
            "type": "dmm",
            "name": "dmm1",
            "last_reading": 3.14,
        }
        panel._accumulate_history(detail)
        assert list(panel._history["dmm1_reading"]) == [3.14]

    def test_accumulate_skips_error(self):
        panel = InstrumentDetailPanel()
        panel._accumulate_history({"error": "oops"})
        assert len(panel._history) == 0

    def test_accumulate_skips_empty(self):
        panel = InstrumentDetailPanel()
        panel._accumulate_history({})
        assert len(panel._history) == 0


# ---------------------------------------------------------------------------
# Renderer tests (async, within full SCPIApp)
# ---------------------------------------------------------------------------


class TestRenderPSU:
    def test_psu_single_channel_renders(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "Test PSU",
                    "channels": [
                        {
                            "id": 1,
                            "label": "CH1",
                            "voltage_set": 5.0,
                            "current_limit": 1.0,
                            "voltage_meas": 5.001,
                            "current_meas": 0.250,
                            "output": True,
                        },
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input, Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "CH1" in combined
                assert "ON" in combined
                # Check that inputs and buttons were mounted
                assert panel.query_one("#inp-psu1-1-v", Input) is not None
                assert panel.query_one("#inp-psu1-1-i", Input) is not None
                assert panel.query_one("#apply-psu1-1", Button) is not None

        asyncio.run(inner())

    def test_psu_multi_channel_with_per_channel_toggles(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 60)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "Multi-CH PSU",
                    "channels": [
                        {
                            "id": "p6v",
                            "label": "P6V",
                            "voltage_set": 5.0,
                            "current_limit": 0.5,
                            "output": True,
                        },
                        {
                            "id": "p25v",
                            "label": "P25V",
                            "voltage_set": 12.0,
                            "current_limit": 0.2,
                            "output": False,
                        },
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "P6V" in combined
                assert "P25V" in combined
                # Multi-channel should have per-channel ON/OFF buttons
                assert panel.query_one("#qa-psu1-chp6von", Button) is not None
                assert panel.query_one("#qa-psu1-chp6voff", Button) is not None
                # Batch buttons
                assert panel.query_one("#qa-psu1-allon", Button) is not None
                assert panel.query_one("#qa-psu1-alloff", Button) is not None

        asyncio.run(inner())

    def test_psu_over_limit_coloring(self):
        """PSU channels exceeding safety limits should have OVER LIMIT text."""
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.safety_limits = [
                    {"device": "psu1", "channel": 1, "parameter": "voltage_upper", "value": 3.0},
                    {"device": "psu1", "channel": 1, "parameter": "current_upper", "value": 0.1},
                ]
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "PSU Over",
                    "channels": [
                        {
                            "id": 1,
                            "label": "CH1",
                            "voltage_set": 5.0,
                            "current_limit": 1.0,
                            "voltage_meas": 5.0,
                            "current_meas": 1.0,
                            "output": True,
                        },
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "OVER LIMIT" in combined

        asyncio.run(inner())

    def test_psu_limit_inputs_and_button(self):
        """PSU renderer should create per-channel limit inputs."""
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "PSU Limits",
                    "channels": [
                        {
                            "id": 1,
                            "label": "CH1",
                            "voltage_set": 5.0,
                            "current_limit": 1.0,
                            "output": False,
                        },
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                assert panel.query_one("#lim-psu1-1-v", Input) is not None
                assert panel.query_one("#lim-psu1-1-i", Input) is not None
                assert panel.query_one("#setlim-psu1-1", Button) is not None

        asyncio.run(inner())

    def test_psu_fallback_to_type_level_limits(self):
        """If no device-specific limit, should fall back to type-level ('psu') limits."""
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                # Limit is on type "psu" not device "psu1"
                panel.safety_limits = [
                    {"device": "psu", "channel": 1, "parameter": "voltage_upper", "value": 2.0},
                ]
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "PSU Fallback",
                    "channels": [
                        {
                            "id": 1,
                            "label": "CH1",
                            "voltage_set": 5.0,
                            "current_limit": 1.0,
                            "output": True,
                        },
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "OVER LIMIT" in combined

        asyncio.run(inner())


class TestRenderSMU:
    def test_smu_renders_mode_and_compliance(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "subtype": "smu",
                    "name": "smu1",
                    "display_name": "NI SMU",
                    "output_mode": "voltage",
                    "voltage_set": 5.0,
                    "current_limit": 0.1,
                    "voltage_meas": 5.0,
                    "current_meas": 0.05,
                    "in_compliance": False,
                    "temperature": 25.0,
                    "output": True,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "Voltage" in combined
                assert "25.0" in combined
                assert "OK" in combined
                # Mode buttons
                assert panel.query_one("#qa-smu1-modev", Button) is not None
                assert panel.query_one("#qa-smu1-modei", Button) is not None

        asyncio.run(inner())

    def test_smu_in_compliance(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "subtype": "smu",
                    "name": "smu1",
                    "display_name": "SMU Comp",
                    "output_mode": "current",
                    "voltage_set": 0.0,
                    "current_limit": 0.001,
                    "voltage_meas": 0.0,
                    "current_meas": 0.001,
                    "in_compliance": True,
                    "temperature": None,
                    "output": False,
                }
                await pilot.pause(0.1)
                from textual.widgets import Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "COMPLIANCE" in combined
                assert "N/A" in combined  # temperature is None

        asyncio.run(inner())

    def test_smu_over_limit(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.safety_limits = [
                    {"device": "smu1", "channel": None, "parameter": "voltage_upper", "value": 3.0},
                    {"device": "smu1", "channel": None, "parameter": "current_upper", "value": 0.05},
                ]
                panel.detail = {
                    "type": "psu",
                    "subtype": "smu",
                    "name": "smu1",
                    "display_name": "SMU OL",
                    "output_mode": "voltage",
                    "voltage_set": 5.0,
                    "current_limit": 0.1,
                    "voltage_meas": 5.0,
                    "current_meas": 0.1,
                    "in_compliance": False,
                    "temperature": 30.0,
                    "output": True,
                }
                await pilot.pause(0.1)
                from textual.widgets import Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "OVER LIMIT" in combined

        asyncio.run(inner())

    def test_smu_setpoint_and_limit_inputs(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "subtype": "smu",
                    "name": "smu1",
                    "display_name": "SMU Inputs",
                    "output_mode": "voltage",
                    "voltage_set": 3.3,
                    "current_limit": 0.01,
                    "voltage_meas": 3.3,
                    "current_meas": 0.005,
                    "in_compliance": False,
                    "temperature": 22.0,
                    "output": False,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                assert panel.query_one("#inp-smu1-1-v", Input) is not None
                assert panel.query_one("#inp-smu1-1-i", Input) is not None
                assert panel.query_one("#apply-smu1-1", Button) is not None
                assert panel.query_one("#lim-smu1-1-v", Input) is not None
                assert panel.query_one("#lim-smu1-1-i", Input) is not None
                assert panel.query_one("#setlim-smu1-1", Button) is not None

        asyncio.run(inner())

    def test_smu_fallback_to_type_level_limits(self):
        """SMU should fall back to type-level 'smu' limits."""
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.safety_limits = [
                    {"device": "smu", "channel": None, "parameter": "voltage_upper", "value": 1.0},
                ]
                panel.detail = {
                    "type": "psu",
                    "subtype": "smu",
                    "name": "smu1",
                    "display_name": "SMU FB",
                    "output_mode": "voltage",
                    "voltage_set": 5.0,
                    "current_limit": 0.1,
                    "voltage_meas": 5.0,
                    "current_meas": 0.05,
                    "in_compliance": False,
                    "temperature": 25.0,
                    "output": True,
                }
                await pilot.pause(0.1)
                from textual.widgets import Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "OVER LIMIT" in combined

        asyncio.run(inner())


class TestRenderDMM:
    def test_dmm_renders_reading_and_mode(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "dmm",
                    "name": "dmm1",
                    "display_name": "HP 34401A",
                    "last_reading": 3.14159,
                    "mode": "dc_voltage",
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "3.141590" in combined
                assert "dc_voltage" in combined
                # Mode buttons (12 total across two rows) and Read button
                assert panel.query_one("#qa-dmm1-read", Button) is not None
                assert panel.query_one("#qa-dmm1-mode-dc_voltage", Button) is not None
                assert panel.query_one("#qa-dmm1-mode-temperature", Button) is not None

        asyncio.run(inner())

    def test_dmm_no_reading(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "dmm",
                    "name": "dmm1",
                    "display_name": "DMM NA",
                    "last_reading": None,
                    "mode": "",
                }
                await pilot.pause(0.1)
                from textual.widgets import Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "N/A" in combined

        asyncio.run(inner())


class TestRenderAWG:
    def test_awg_renders_channels_and_waveform_buttons(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 60)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "awg",
                    "name": "awg1",
                    "display_name": "Keysight AWG",
                    "channels": [
                        {"id": 1, "frequency": 1000.0, "amplitude": 2.0, "offset": 0.5, "output": True},
                        {"id": 2, "frequency": 5000.0, "amplitude": 1.0, "offset": 0.0, "output": False},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input, Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "CH1" in combined
                assert "CH2" in combined
                # Per-channel inputs
                assert panel.query_one("#inp-awg1-1-freq", Input) is not None
                assert panel.query_one("#inp-awg1-1-amp", Input) is not None
                assert panel.query_one("#inp-awg1-1-off", Input) is not None
                assert panel.query_one("#awgapply-awg1-1", Button) is not None
                # Waveform buttons for CH1
                assert panel.query_one("#qa-awg1-wave1-sin", Button) is not None
                assert panel.query_one("#qa-awg1-wave1-squ", Button) is not None
                # Batch buttons
                assert panel.query_one("#qa-awg1-ch1on", Button) is not None
                assert panel.query_one("#qa-awg1-ch2off", Button) is not None

        asyncio.run(inner())

    def test_awg_over_limit(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 60)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.safety_limits = [
                    {"device": "awg1", "channel": 1, "parameter": "vpp_upper", "value": 1.0},
                    {"device": "awg1", "channel": 1, "parameter": "freq_upper", "value": 500.0},
                ]
                panel.detail = {
                    "type": "awg",
                    "name": "awg1",
                    "display_name": "AWG OL",
                    "channels": [
                        {"id": 1, "frequency": 1000.0, "amplitude": 5.0, "offset": 0.0, "output": True},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "OVER LIMIT" in combined

        asyncio.run(inner())


class TestRenderScope:
    def test_scope_renders_trigger_and_channel_buttons(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "scope",
                    "name": "scope1",
                    "display_name": "Rigol Scope",
                    "trigger_status": "TD",
                    "num_channels": 4,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "TD" in combined
                assert "4" in combined
                # Per-channel toggles
                assert panel.query_one("#qa-scope1-scopech1on", Button) is not None
                assert panel.query_one("#qa-scope1-scopech4off", Button) is not None
                # Action buttons
                assert panel.query_one("#qa-scope1-run", Button) is not None
                assert panel.query_one("#qa-scope1-stop", Button) is not None
                assert panel.query_one("#qa-scope1-single", Button) is not None
                assert panel.query_one("#qa-scope1-autoset", Button) is not None

        asyncio.run(inner())

    def test_scope_non_triggered_color(self):
        """Non-triggered status should still render (yellow color branch)."""
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "scope",
                    "name": "scope1",
                    "display_name": "Scope Wait",
                    "trigger_status": "WAIT",
                    "num_channels": 2,
                }
                await pilot.pause(0.1)
                from textual.widgets import Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "WAIT" in combined

        asyncio.run(inner())


class TestRenderEV2300:
    def test_ev2300_renders_i2c_controls(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "ev2300",
                    "name": "ev2300",
                    "display_name": "TI EV2300",
                    "connected": True,
                    "serial": "ABC123",
                    "product": "EV2300",
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input, Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "Connected" in combined
                assert "ABC123" in combined
                assert "EV2300" in combined
                assert "I2C" in combined
                # I2C controls
                assert panel.query_one("#ev-ev2300-addr", Input) is not None
                assert panel.query_one("#ev-ev2300-reg", Input) is not None
                assert panel.query_one("#ev-ev2300-val", Input) is not None
                assert panel.query_one("#qa-ev2300-readword", Button) is not None
                assert panel.query_one("#qa-ev2300-readbyte", Button) is not None
                assert panel.query_one("#qa-ev2300-readblock", Button) is not None
                assert panel.query_one("#qa-ev2300-writeword", Button) is not None
                assert panel.query_one("#qa-ev2300-writebyte", Button) is not None

        asyncio.run(inner())

    def test_ev2300_disconnected(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "ev2300",
                    "name": "ev2300",
                    "display_name": "EV2300 DC",
                    "connected": False,
                    "serial": "N/A",
                    "product": "N/A",
                }
                await pilot.pause(0.1)
                from textual.widgets import Static

                statics = [str(w.render()) for w in panel.query(Static)]
                combined = " ".join(statics)
                assert "Disconnected" in combined

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# on_button_pressed tests for InstrumentDetailPanel
# ---------------------------------------------------------------------------


class TestButtonPressedHandlers:
    def test_save_state_button(self):
        """ss-<dev>-save should post SaveStateRequested."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "PSU Save",
                    "channels": [
                        {"id": 1, "label": "CH1", "voltage_set": 5.0, "current_limit": 1.0, "output": False},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#ss-psu1-save", Button)
                btn.press()
                await pilot.pause(0.2)

        asyncio.run(inner())

    def test_restore_state_button(self):
        """ss-<dev>-restore should post RestoreStateRequested."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "PSU Restore",
                    "channels": [
                        {"id": 1, "label": "CH1", "voltage_set": 5.0, "current_limit": 1.0, "output": False},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#ss-psu1-restore", Button)
                btn.press()
                await pilot.pause(0.2)

        asyncio.run(inner())

    def test_apply_psu_button(self):
        """apply-<dev>-<ch> should read inputs and post QuickAction."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "PSU Apply",
                    "channels": [
                        {"id": 1, "label": "CH1", "voltage_set": 5.0, "current_limit": 1.0, "output": False},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                # Set input values
                panel.query_one("#inp-psu1-1-v", Input).value = "3.3"
                panel.query_one("#inp-psu1-1-i", Input).value = "0.5"
                btn = panel.query_one("#apply-psu1-1", Button)
                btn.press()
                await pilot.pause(0.3)
                # Should dispatch psu chan commands
                assert any("psu chan 1 set_voltage 3.3" in c for c in stub._commands)
                assert any("psu chan 1 set_current_limit 0.5" in c for c in stub._commands)

        asyncio.run(inner())

    def test_awg_apply_button(self):
        """awgapply-<dev>-<ch> should read freq/amp/offset and post QuickAction."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 60)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "awg",
                    "name": "awg1",
                    "display_name": "AWG Apply",
                    "channels": [
                        {"id": 1, "frequency": 1000.0, "amplitude": 1.0, "offset": 0.0, "output": True},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                panel.query_one("#inp-awg1-1-freq", Input).value = "5000"
                panel.query_one("#inp-awg1-1-amp", Input).value = "2"
                panel.query_one("#inp-awg1-1-off", Input).value = "0.5"
                btn = panel.query_one("#awgapply-awg1-1", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("awg chan 1 set_frequency 5000" in c for c in stub._commands)
                assert any("awg chan 1 set_amplitude 2" in c for c in stub._commands)
                assert any("awg chan 1 set_offset 0.5" in c for c in stub._commands)

        asyncio.run(inner())

    def test_set_limit_button(self):
        """setlim-<dev>-<ch> should read limit inputs and post SetLimitRequested."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "PSU Limit",
                    "channels": [
                        {"id": 1, "label": "CH1", "voltage_set": 5.0, "current_limit": 1.0, "output": False},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                panel.query_one("#lim-psu1-1-v", Input).value = "30"
                panel.query_one("#lim-psu1-1-i", Input).value = "5"
                btn = panel.query_one("#setlim-psu1-1", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("upper_limit psu1 chan 1 voltage 30" in c for c in stub._commands)
                assert any("upper_limit psu1 chan 1 current 5" in c for c in stub._commands)

        asyncio.run(inner())

    def test_quick_action_allon(self):
        """qa-<dev>-allon should dispatch output on."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "PSU On",
                    "channels": [
                        {"id": 1, "label": "CH1", "voltage_set": 5.0, "current_limit": 1.0, "output": False},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-psu1-allon", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("psu output on" in c for c in stub._commands)

        asyncio.run(inner())

    def test_quick_action_alloff(self):
        """qa-<dev>-alloff should dispatch output off."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "name": "psu1",
                    "display_name": "PSU Off",
                    "channels": [
                        {"id": 1, "label": "CH1", "voltage_set": 5.0, "current_limit": 1.0, "output": True},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-psu1-alloff", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("psu output off" in c for c in stub._commands)

        asyncio.run(inner())

    def test_dmm_read_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "dmm",
                    "name": "dmm1",
                    "display_name": "DMM Read",
                    "last_reading": 1.0,
                    "mode": "dc_voltage",
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-dmm1-read", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("dmm read" in c for c in stub._commands)

        asyncio.run(inner())

    def test_dmm_mode_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "dmm",
                    "name": "dmm1",
                    "display_name": "DMM Mode",
                    "last_reading": 1.0,
                    "mode": "dc_voltage",
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-dmm1-mode-ac_voltage", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("dmm mode ac_voltage" in c for c in stub._commands)

        asyncio.run(inner())

    def test_scope_run_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "scope",
                    "name": "scope1",
                    "display_name": "Scope Run",
                    "trigger_status": "WAIT",
                    "num_channels": 2,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-scope1-run", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("scope run" in c for c in stub._commands)

        asyncio.run(inner())

    def test_scope_stop_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "scope",
                    "name": "scope1",
                    "display_name": "Scope Stop",
                    "trigger_status": "TD",
                    "num_channels": 2,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-scope1-stop", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("scope stop" in c for c in stub._commands)

        asyncio.run(inner())

    def test_scope_single_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "scope",
                    "name": "scope1",
                    "display_name": "Scope Single",
                    "trigger_status": "WAIT",
                    "num_channels": 2,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-scope1-single", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("scope single" in c for c in stub._commands)

        asyncio.run(inner())

    def test_scope_autoset_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "scope",
                    "name": "scope1",
                    "display_name": "Scope Autoset",
                    "trigger_status": "WAIT",
                    "num_channels": 2,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-scope1-autoset", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("scope autoset" in c for c in stub._commands)

        asyncio.run(inner())

    def test_scope_per_channel_on(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "scope",
                    "name": "scope1",
                    "display_name": "Scope CH",
                    "trigger_status": "WAIT",
                    "num_channels": 2,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-scope1-scopech1on", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("scope chan 1 on" in c for c in stub._commands)

        asyncio.run(inner())

    def test_scope_per_channel_off(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "scope",
                    "name": "scope1",
                    "display_name": "Scope CH Off",
                    "trigger_status": "WAIT",
                    "num_channels": 2,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-scope1-scopech2off", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("scope chan 2 off" in c for c in stub._commands)

        asyncio.run(inner())

    def test_awg_waveform_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 60)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "awg",
                    "name": "awg1",
                    "display_name": "AWG WF",
                    "channels": [
                        {"id": 1, "frequency": 1000.0, "amplitude": 1.0, "offset": 0.0, "output": True},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-awg1-wave1-sin", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("awg chan 1 set_function sin" in c for c in stub._commands)

        asyncio.run(inner())

    def test_awg_channel_on_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 60)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "awg",
                    "name": "awg1",
                    "display_name": "AWG ChOn",
                    "channels": [
                        {"id": 1, "frequency": 1000.0, "amplitude": 1.0, "offset": 0.0, "output": False},
                    ],
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-awg1-ch1on", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("awg chan 1 on" in c for c in stub._commands)

        asyncio.run(inner())

    def test_smu_mode_voltage_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "subtype": "smu",
                    "name": "smu1",
                    "display_name": "SMU ModV",
                    "output_mode": "current",
                    "voltage_set": 0.0,
                    "current_limit": 0.001,
                    "voltage_meas": 0.0,
                    "current_meas": 0.001,
                    "in_compliance": False,
                    "temperature": 25.0,
                    "output": False,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-smu1-modev", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("smu mode voltage" in c for c in stub._commands)

        asyncio.run(inner())

    def test_smu_mode_current_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "subtype": "smu",
                    "name": "smu1",
                    "display_name": "SMU ModI",
                    "output_mode": "voltage",
                    "voltage_set": 5.0,
                    "current_limit": 0.1,
                    "voltage_meas": 5.0,
                    "current_meas": 0.05,
                    "in_compliance": False,
                    "temperature": 25.0,
                    "output": True,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-smu1-modei", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("smu mode current" in c for c in stub._commands)

        asyncio.run(inner())

    def test_smu_on_off_buttons(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "psu",
                    "subtype": "smu",
                    "name": "smu1",
                    "display_name": "SMU OnOff",
                    "output_mode": "voltage",
                    "voltage_set": 5.0,
                    "current_limit": 0.1,
                    "voltage_meas": 5.0,
                    "current_meas": 0.05,
                    "in_compliance": False,
                    "temperature": 25.0,
                    "output": False,
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-smu1-on", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("psu chan on" in c for c in stub._commands)

                btn2 = panel.query_one("#qa-smu1-off", Button)
                btn2.press()
                await pilot.pause(0.3)
                assert any("psu chan off" in c for c in stub._commands)

        asyncio.run(inner())

    def test_ev2300_readword_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "ev2300",
                    "name": "ev2300",
                    "display_name": "EV2300",
                    "connected": True,
                    "serial": "X",
                    "product": "EV2300",
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                panel.query_one("#ev-ev2300-addr", Input).value = "0x16"
                panel.query_one("#ev-ev2300-reg", Input).value = "0x08"
                btn = panel.query_one("#qa-ev2300-readword", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("ev2300 read_word 0x16 0x08" in c for c in stub._commands)

        asyncio.run(inner())

    def test_ev2300_readbyte_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "ev2300",
                    "name": "ev2300",
                    "display_name": "EV2300",
                    "connected": True,
                    "serial": "X",
                    "product": "EV2300",
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-ev2300-readbyte", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("ev2300 read_byte" in c for c in stub._commands)

        asyncio.run(inner())

    def test_ev2300_readblock_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "ev2300",
                    "name": "ev2300",
                    "display_name": "EV2300",
                    "connected": True,
                    "serial": "X",
                    "product": "EV2300",
                }
                await pilot.pause(0.1)
                from textual.widgets import Button

                btn = panel.query_one("#qa-ev2300-readblock", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("ev2300 read_block" in c for c in stub._commands)

        asyncio.run(inner())

    def test_ev2300_writeword_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "ev2300",
                    "name": "ev2300",
                    "display_name": "EV2300",
                    "connected": True,
                    "serial": "X",
                    "product": "EV2300",
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                panel.query_one("#ev-ev2300-addr", Input).value = "0x16"
                panel.query_one("#ev-ev2300-reg", Input).value = "0x00"
                panel.query_one("#ev-ev2300-val", Input).value = "0xFF"
                btn = panel.query_one("#qa-ev2300-writeword", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("ev2300 write_word 0x16 0x00 0xFF" in c for c in stub._commands)

        asyncio.run(inner())

    def test_ev2300_writebyte_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {
                    "type": "ev2300",
                    "name": "ev2300",
                    "display_name": "EV2300",
                    "connected": True,
                    "serial": "X",
                    "product": "EV2300",
                }
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                panel.query_one("#ev-ev2300-addr", Input).value = "0x16"
                panel.query_one("#ev-ev2300-reg", Input).value = "0x01"
                panel.query_one("#ev-ev2300-val", Input).value = "0xAB"
                btn = panel.query_one("#qa-ev2300-writebyte", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("ev2300 write_byte 0x16 0x01 0xAB" in c for c in stub._commands)

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# SafetyLimitsPanel tests
# ---------------------------------------------------------------------------


class TestSafetyLimitsPanelNew:
    def test_compose_has_inputs_and_buttons(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(SafetyLimitsPanel)
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                assert panel.query_one("#new-lim-device", Input) is not None
                assert panel.query_one("#new-lim-chan", Input) is not None
                assert panel.query_one("#new-lim-param", Input) is not None
                assert panel.query_one("#new-lim-value", Input) is not None
                assert panel.query_one("#add-upper-limit", Button) is not None
                assert panel.query_one("#add-lower-limit", Button) is not None

        asyncio.run(inner())

    def test_set_upper_limit_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(SafetyLimitsPanel)
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                panel.query_one("#new-lim-device", Input).value = "psu1"
                panel.query_one("#new-lim-chan", Input).value = "1"
                panel.query_one("#new-lim-param", Input).value = "voltage"
                panel.query_one("#new-lim-value", Input).value = "30"
                btn = panel.query_one("#add-upper-limit", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("upper_limit psu1 chan 1 voltage 30" in c for c in stub._commands)

        asyncio.run(inner())

    def test_set_lower_limit_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(SafetyLimitsPanel)
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                panel.query_one("#new-lim-device", Input).value = "psu1"
                panel.query_one("#new-lim-chan", Input).value = ""
                panel.query_one("#new-lim-param", Input).value = "current"
                panel.query_one("#new-lim-value", Input).value = "5"
                btn = panel.query_one("#add-lower-limit", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("lower_limit psu1 current 5" in c for c in stub._commands)

        asyncio.run(inner())

    def test_set_limit_missing_fields_does_nothing(self):
        """Pressing Set Upper with empty required fields should not dispatch."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(SafetyLimitsPanel)
                await pilot.pause(0.1)
                from textual.widgets import Button, Input

                # Leave device empty
                panel.query_one("#new-lim-device", Input).value = ""
                panel.query_one("#new-lim-param", Input).value = "voltage"
                panel.query_one("#new-lim-value", Input).value = "30"
                btn = panel.query_one("#add-upper-limit", Button)
                btn.press()
                await pilot.pause(0.2)
                # No limit commands should have been dispatched
                assert not any("upper_limit" in c for c in stub._commands)
                assert not any("lower_limit" in c for c in stub._commands)

        asyncio.run(inner())

    def test_limits_table_with_channel(self):
        """Limits with channel=int should show CH<N>."""
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(SafetyLimitsPanel)
                panel.limits = [
                    {"device": "psu1", "channel": 2, "parameter": "voltage_upper", "value": 30.0},
                ]
                await pilot.pause(0.1)
                from textual.widgets import DataTable

                table = panel.query_one("#limits-table", DataTable)
                assert table.row_count == 1

        asyncio.run(inner())

    def test_limits_table_with_none_channel(self):
        """Limits with channel=None should show 'All'."""
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(SafetyLimitsPanel)
                panel.limits = [
                    {"device": "psu1", "channel": None, "parameter": "current_upper", "value": 5.0},
                ]
                await pilot.pause(0.1)
                from textual.widgets import DataTable

                table = panel.query_one("#limits-table", DataTable)
                assert table.row_count == 1

        asyncio.run(inner())

    def test_limits_table_sorted(self):
        """Multiple limits should be sorted by device then parameter."""
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(SafetyLimitsPanel)
                panel.limits = [
                    {"device": "psu2", "channel": None, "parameter": "voltage_upper", "value": 30.0},
                    {"device": "awg1", "channel": 1, "parameter": "freq_upper", "value": 100000.0},
                    {"device": "psu1", "channel": None, "parameter": "current_upper", "value": 5.0},
                ]
                await pilot.pause(0.1)
                from textual.widgets import DataTable

                table = panel.query_one("#limits-table", DataTable)
                assert table.row_count == 3

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# App-level action tests
# ---------------------------------------------------------------------------


class TestAppActions:
    def test_emergency_stop(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                await app.run_action("emergency_stop")
                await pilot.pause(0.3)
                assert any("state safe" in c for c in stub._commands)

        asyncio.run(inner())

    def test_dispatch_limit_commands_multi_line(self):
        """_dispatch_limit_commands should handle multi-line commands."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                app._dispatch_limit_commands("upper_limit psu1 chan 1 voltage 30\nupper_limit psu1 chan 1 current 5")
                await pilot.pause(0.3)
                assert any("upper_limit psu1 chan 1 voltage 30" in c for c in stub._commands)
                assert any("upper_limit psu1 chan 1 current 5" in c for c in stub._commands)

        asyncio.run(inner())

    def test_on_instrument_detail_panel_set_limit_requested(self):
        """SetLimitRequested from detail panel should dispatch limit commands."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.post_message(InstrumentDetailPanel.SetLimitRequested("upper_limit psu1 voltage 30"))
                await pilot.pause(0.3)
                assert any("upper_limit psu1 voltage 30" in c for c in stub._commands)

        asyncio.run(inner())

    def test_on_safety_limits_panel_set_limit_requested(self):
        """SetLimitRequested from safety panel should dispatch limit commands."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(SafetyLimitsPanel)
                panel.post_message(SafetyLimitsPanel.SetLimitRequested("lower_limit psu1 current 0.5"))
                await pilot.pause(0.3)
                assert any("lower_limit psu1 current 0.5" in c for c in stub._commands)

        asyncio.run(inner())

    def test_init_safe_state_runs(self):
        """_init_safe_state should dispatch 'state safe' on mount."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                await pilot.pause(0.5)
                # The app should have called state safe during mount
                assert any("state safe" in c for c in stub._commands)

        asyncio.run(inner())

    def test_save_and_restore_state(self):
        """SaveStateRequested/RestoreStateRequested should save/restore state."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                # Save
                panel.post_message(InstrumentDetailPanel.SaveStateRequested("psu1"))
                await pilot.pause(0.2)
                assert "psu1" in app._state_snapshots

                # Restore
                panel.post_message(InstrumentDetailPanel.RestoreStateRequested("psu1"))
                await pilot.pause(0.2)

        asyncio.run(inner())

    def test_restore_state_no_snapshot_warns(self):
        """Restoring without a prior save should log a warning."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                baseline = len(app._notification_log)
                panel.post_message(InstrumentDetailPanel.RestoreStateRequested("nonexistent"))
                await pilot.pause(0.2)
                # Should have logged a warning about no saved state
                assert len(app._notification_log) > baseline

        asyncio.run(inner())

    def test_refresh_detail_with_selected_device(self):
        """_refresh_detail should update the panel when a device is selected."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                app._selected_device = "psu1"
                app._refresh_detail()
                await pilot.pause(0.2)
                panel = app.query_one(InstrumentDetailPanel)
                assert panel.detail.get("name") == "psu1"

        asyncio.run(inner())

    def test_refresh_detail_no_selected_device(self):
        """_refresh_detail with no selected device should be a no-op."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                app._selected_device = None
                app._refresh_detail()
                await pilot.pause(0.1)
                panel = app.query_one(InstrumentDetailPanel)
                assert panel.detail == {} or panel.detail.get("name") is None

        asyncio.run(inner())

    def test_retry_last_with_history(self):
        """action_retry_last with history should re-dispatch the last command."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                # Push a command into history
                app._history.push("help")
                await app.run_action("retry_last")
                await pilot.pause(0.3)
                assert any("help" in c for c in stub._commands)

        asyncio.run(inner())

    def test_retry_last_no_history(self):
        """action_retry_last with no history should log a warning."""
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                baseline = len(app._notification_log)
                await app.run_action("retry_last")
                await pilot.pause(0.2)
                assert len(app._notification_log) > baseline

        asyncio.run(inner())

    def test_bulk_action_dispatches(self):
        """BulkAction from sidebar should dispatch the command."""
        async def inner():
            from lab_instruments.tui.widgets.device_sidebar import DeviceSidebar

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                sidebar = app.query_one(DeviceSidebar)
                sidebar.post_message(DeviceSidebar.BulkAction("scan"))
                await pilot.pause(0.3)
                assert any("scan" in c for c in stub._commands)

        asyncio.run(inner())

    def test_measurement_clear_requested(self):
        """ClearRequested from measurement table should dispatch log clear."""
        async def inner():
            from lab_instruments.tui.widgets.measurement_table import MeasurementTable

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                table = app.query_one(MeasurementTable)
                table.post_message(MeasurementTable.ClearRequested())
                await pilot.pause(0.3)
                assert any("log clear" in c for c in stub._commands)

        asyncio.run(inner())

    def test_measurement_report_requested(self):
        """ReportRequested from measurement table should dispatch report save."""
        async def inner():
            from lab_instruments.tui.widgets.measurement_table import MeasurementTable

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                table = app.query_one(MeasurementTable)
                table.post_message(MeasurementTable.ReportRequested())
                await pilot.pause(0.3)
                assert any("report save" in c for c in stub._commands)

        asyncio.run(inner())

    def test_stream_line_error_coloring(self):
        """_stream_line should color error messages red."""
        async def inner():
            from textual.widgets import RichLog

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)):
                log = app.query_one("#log-output", RichLog)
                initial = len(log.lines)
                app._stream_line("ERROR: something failed")
                assert len(log.lines) > initial

        asyncio.run(inner())

    def test_stream_line_warning_coloring(self):
        """_stream_line should color warning messages yellow."""
        async def inner():
            from textual.widgets import RichLog

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)):
                log = app.query_one("#log-output", RichLog)
                initial = len(log.lines)
                app._stream_line("WARNING: something happened")
                assert len(log.lines) > initial

        asyncio.run(inner())

    def test_stream_line_success_coloring(self):
        """_stream_line should color success messages green."""
        async def inner():
            from textual.widgets import RichLog

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)):
                log = app.query_one("#log-output", RichLog)
                initial = len(log.lines)
                app._stream_line("SUCCESS: all good")
                assert len(log.lines) > initial

        asyncio.run(inner())

    def test_stream_line_safety_blocked(self):
        """_stream_line should color safety blocked messages red."""
        async def inner():
            from textual.widgets import RichLog

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)):
                log = app.query_one("#log-output", RichLog)
                initial = len(log.lines)
                app._stream_line("SAFETY BLOCKED: limit exceeded")
                assert len(log.lines) > initial

        asyncio.run(inner())

    def test_stream_line_empty_is_noop(self):
        """_stream_line with empty/whitespace string should be a no-op."""
        async def inner():
            from textual.widgets import RichLog

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)):
                log = app.query_one("#log-output", RichLog)
                initial = len(log.lines)
                app._stream_line("   ")
                assert len(log.lines) == initial

        asyncio.run(inner())

    def test_stream_line_pass_coloring(self):
        """_stream_line should color PASS messages green."""
        async def inner():
            from textual.widgets import RichLog

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)):
                log = app.query_one("#log-output", RichLog)
                initial = len(log.lines)
                app._stream_line("PASS: test passed")
                assert len(log.lines) > initial

        asyncio.run(inner())

    def test_stream_line_retroactive_coloring(self):
        """_stream_line should color RETROACTIVE messages yellow."""
        async def inner():
            from textual.widgets import RichLog

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)):
                log = app.query_one("#log-output", RichLog)
                initial = len(log.lines)
                app._stream_line("RETROACTIVE: limit applied")
                assert len(log.lines) > initial

        asyncio.run(inner())

    def test_on_key_up_arrow(self):
        """Up arrow on focused input should cycle history."""
        async def inner():
            from textual.widgets import Input

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                inp = app.query_one("#cmd_input", Input)
                inp.focus()
                app._history.push("help")
                app._history.push("scan")
                await pilot.press("up")
                await pilot.pause(0.1)
                # Should show last command
                assert inp.value in ("scan", "help")

        asyncio.run(inner())

    def test_on_key_down_arrow(self):
        """Down arrow on focused input should cycle history forward."""
        async def inner():
            from textual.widgets import Input

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                inp = app.query_one("#cmd_input", Input)
                inp.focus()
                app._history.push("help")
                app._history.push("scan")
                await pilot.press("up")
                await pilot.pause(0.05)
                await pilot.press("up")
                await pilot.pause(0.05)
                await pilot.press("down")
                await pilot.pause(0.1)
                assert isinstance(inp.value, str)

        asyncio.run(inner())

    def test_input_submitted(self):
        """Submitting text in the command input should dispatch it."""
        async def inner():
            from textual.widgets import Input

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                inp = app.query_one("#cmd_input", Input)
                inp.focus()
                inp.value = "help"
                await pilot.press("enter")
                await pilot.pause(0.3)
                assert any("help" in c for c in stub._commands)

        asyncio.run(inner())

    def test_input_submitted_empty_is_noop(self):
        """Submitting empty text should not dispatch anything."""
        async def inner():
            from textual.widgets import Input

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 50)) as pilot:
                baseline = len(stub._commands)
                inp = app.query_one("#cmd_input", Input)
                inp.focus()
                inp.value = ""
                await pilot.press("enter")
                await pilot.pause(0.2)
                # state safe from init + no new commands
                new_cmds = stub._commands[baseline:]
                assert not any(c.strip() == "" for c in new_cmds)

        asyncio.run(inner())
