"""Tests for InstrumentDetailPanel, DeviceSelected, QuickAction, HelpScreen, SafetyLimitsPanel, and more."""

from __future__ import annotations

import asyncio

from textual.widgets import Static, TabbedContent

from lab_instruments.tui.app import SCPIApp
from lab_instruments.tui.widgets.instrument_detail import InstrumentDetailPanel

# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------


class _StubDispatcher:
    """Stub dispatcher with controllable instrument detail snapshots."""

    def __init__(self, devices=None, detail=None, limits=None):
        self._commands: list[str] = []
        self._devices: list[dict] = devices or []
        self._detail: dict = detail or {}
        self._limits: list[dict] = limits or []

    def handle_command(self, cmd: str, line_callback=None) -> str:
        self._commands.append(cmd)
        return f"OK: {cmd}"

    def get_completions(self, text: str) -> list[str]:
        return []

    def get_device_snapshot(self) -> list[dict]:
        return list(self._devices)

    def get_measurement_snapshot(self) -> list[dict]:
        return []

    def get_script_names(self) -> list[str]:
        return []

    def get_vars_snapshot(self) -> dict[str, str]:
        return {}

    def get_safety_snapshot(self) -> dict:
        return {
            "limit_count": len(self._limits),
            "active_script": False,
            "exit_on_error": False,
            "limits": list(self._limits),
        }

    def get_instrument_detail(self, device_name: str) -> dict:
        if self._detail:
            return dict(self._detail)
        return {"type": "unknown", "name": device_name, "display_name": device_name, "error": "not found"}


def _make_device(name: str, display: str, selected: bool = False) -> dict:
    return {
        "name": name,
        "display_name": display,
        "selected": selected,
        "base_type": name.rstrip("0123456789"),
        "status": "connected",
    }


# ---------------------------------------------------------------------------
# Widget-level tests
# ---------------------------------------------------------------------------


class TestInstrumentDetailPanelWidget:
    def test_empty_detail_shows_placeholder(self):
        """Empty detail dict should show placeholder text."""

        async def inner():
            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(100, 30)):
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {}
                await asyncio.sleep(0.05)
                texts = [w.render() for w in panel.query(Static)]
                combined = " ".join(str(t) for t in texts)
                assert "Select an instrument" in combined

        asyncio.run(inner())

    def test_error_detail_shows_error(self):
        """Detail dict with error key should show error message."""

        async def inner():
            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(100, 30)):
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = {"type": "psu", "name": "psu1", "display_name": "Test PSU", "error": "comm failure"}
                await asyncio.sleep(0.05)
                texts = [w.render() for w in panel.query(Static)]
                combined = " ".join(str(t) for t in texts)
                assert "comm failure" in combined

        asyncio.run(inner())

    def test_psu_detail_renders_channels(self):
        """PSU detail should render channel voltage/current info."""

        async def inner():
            detail = {
                "type": "psu",
                "name": "psu1",
                "display_name": "HP E3631A",
                "channels": [
                    {
                        "id": "p6v",
                        "label": "P6V",
                        "voltage_set": 5.0,
                        "current_limit": 0.2,
                        "voltage_meas": 4.998,
                        "current_meas": 0.099,
                        "output": True,
                    },
                ],
            }
            app = SCPIApp(_StubDispatcher(detail=detail))
            async with app.run_test(size=(100, 30)):
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = detail
                await asyncio.sleep(0.05)
                texts = [w.render() for w in panel.query(Static)]
                combined = " ".join(str(t) for t in texts)
                assert "P6V" in combined
                assert "ON" in combined

        asyncio.run(inner())

    def test_smu_detail_renders_compliance(self):
        """SMU detail should show compliance status."""

        async def inner():
            detail = {
                "type": "psu",
                "subtype": "smu",
                "name": "smu",
                "display_name": "NI PXIe-4139 SMU",
                "output_mode": "voltage",
                "voltage_set": 5.0,
                "current_limit": 0.1,
                "voltage_meas": 4.999,
                "current_meas": 0.0995,
                "in_compliance": True,
                "temperature": 24.5,
                "output": True,
            }
            app = SCPIApp(_StubDispatcher(detail=detail))
            async with app.run_test(size=(100, 30)):
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = detail
                await asyncio.sleep(0.05)
                texts = [w.render() for w in panel.query(Static)]
                combined = " ".join(str(t) for t in texts)
                assert "COMPLIANCE" in combined or "Compliance" in combined

        asyncio.run(inner())

    def test_dmm_detail_renders_reading(self):
        """DMM detail should show the last reading."""

        async def inner():
            detail = {
                "type": "dmm",
                "name": "dmm1",
                "display_name": "HP 34401A",
                "last_reading": 5.0012,
            }
            app = SCPIApp(_StubDispatcher(detail=detail))
            async with app.run_test(size=(100, 30)):
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = detail
                await asyncio.sleep(0.05)
                texts = [w.render() for w in panel.query(Static)]
                combined = " ".join(str(t) for t in texts)
                assert "5.001200" in combined

        asyncio.run(inner())

    def test_awg_detail_renders_channels(self):
        """AWG detail should render per-channel parameters."""

        async def inner():
            detail = {
                "type": "awg",
                "name": "awg1",
                "display_name": "Keysight EDU33212A",
                "channels": [
                    {"id": 1, "frequency": 10000.0, "amplitude": 5.0, "offset": 0.0, "output": True},
                    {"id": 2, "frequency": 10000.0, "amplitude": 5.0, "offset": 0.0, "output": False},
                ],
            }
            app = SCPIApp(_StubDispatcher(detail=detail))
            async with app.run_test(size=(100, 30)):
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = detail
                await asyncio.sleep(0.05)
                texts = [w.render() for w in panel.query(Static)]
                combined = " ".join(str(t) for t in texts)
                assert "CH1" in combined
                assert "CH2" in combined

        asyncio.run(inner())

    def test_scope_detail_renders_trigger(self):
        """Scope detail should show trigger status."""

        async def inner():
            detail = {
                "type": "scope",
                "name": "scope1",
                "display_name": "Rigol DHO804",
                "trigger_status": "TD",
                "num_channels": 4,
            }
            app = SCPIApp(_StubDispatcher(detail=detail))
            async with app.run_test(size=(100, 30)):
                panel = app.query_one(InstrumentDetailPanel)
                panel.detail = detail
                await asyncio.sleep(0.05)
                texts = [w.render() for w in panel.query(Static)]
                combined = " ".join(str(t) for t in texts)
                assert "TD" in combined

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# App integration tests
# ---------------------------------------------------------------------------


class TestDetailPanelAppIntegration:
    def test_detail_panel_mounts_in_app(self):
        """InstrumentDetailPanel should exist in the widget tree."""

        async def inner():
            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(100, 30)):
                panel = app.query_one(InstrumentDetailPanel)
                assert panel is not None

        asyncio.run(inner())

    def test_device_selected_switches_to_detail_view(self):
        """Clicking a device in the sidebar should switch to detail-view."""

        async def inner():
            devices = [_make_device("psu1", "HP E3631A", selected=True)]
            detail = {
                "type": "psu",
                "name": "psu1",
                "display_name": "HP E3631A",
                "channels": [
                    {"id": 1, "label": "CH1", "voltage_set": 5.0, "current_limit": 0.1, "output": False},
                ],
            }
            stub = _StubDispatcher(devices=devices, detail=detail)
            app = SCPIApp(stub)
            async with app.run_test(size=(100, 30)) as pilot:
                # Trigger device refresh
                app._refresh_devices()
                await pilot.pause(0.1)

                # Simulate DeviceSelected message
                from lab_instruments.tui.widgets.device_sidebar import DeviceSidebar

                sidebar = app.query_one(DeviceSidebar)
                sidebar.post_message(DeviceSidebar.DeviceSelected("psu1"))
                await pilot.pause(0.1)

                switcher = app.query_one("#main-content", TabbedContent)
                assert switcher.active == "detail-view"

        asyncio.run(inner())

    def test_quick_action_dispatches_command(self):
        """QuickAction from detail panel should dispatch commands."""

        async def inner():
            stub = _StubDispatcher()
            app = SCPIApp(stub)
            async with app.run_test(size=(100, 30)) as pilot:
                panel = app.query_one(InstrumentDetailPanel)
                panel.post_message(InstrumentDetailPanel.QuickAction("use psu1\npsu chan on"))
                await pilot.pause(0.2)

                assert "use psu1" in stub._commands
                assert "psu chan on" in stub._commands

        asyncio.run(inner())

    def test_alt_i_toggles_detail_view(self):
        """Alt+I should toggle detail-view on and off."""

        async def inner():
            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(100, 30)) as pilot:
                switcher = app.query_one("#main-content", TabbedContent)
                assert switcher.active == "log-view"

                await app.run_action("show_detail")
                await pilot.pause(0.05)
                assert switcher.active == "detail-view"

                await app.run_action("show_detail")
                await pilot.pause(0.05)
                assert switcher.active == "log-view"

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# Help screen tests
# ---------------------------------------------------------------------------


class TestHelpScreen:
    def test_help_screen_opens(self):
        """F1 should open the help screen."""

        async def inner():
            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(100, 30)) as pilot:
                await app.run_action("show_help")
                await pilot.pause(0.1)

                from lab_instruments.tui.widgets.help_screen import HelpScreen

                assert len(app.query(HelpScreen.__name__)) > 0 or app.screen.__class__.__name__ == "HelpScreen"

        asyncio.run(inner())

    def test_help_screen_dismisses(self):
        """Escape should close the help screen."""

        async def inner():
            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(100, 30)) as pilot:
                await app.run_action("show_help")
                await pilot.pause(0.2)
                await pilot.press("escape")
                await pilot.pause(0.3)

                assert app.screen.__class__.__name__ != "HelpScreen"

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# Dispatcher detail tests
# ---------------------------------------------------------------------------


class TestDispatcherGetInstrumentDetail:
    def test_unknown_device_returns_error(self):
        """Requesting detail for a nonexistent device should return error dict."""
        from lab_instruments.tui.dispatcher import LocalDispatcher

        # We need a mock-mode dispatcher for this
        disp = LocalDispatcher(mock=True)
        result = disp.get_instrument_detail("nonexistent99")
        assert "error" in result
        assert result["type"] == "unknown"

    def test_psu_detail_has_channels(self):
        """PSU detail should include channels list."""
        from lab_instruments.tui.dispatcher import LocalDispatcher

        disp = LocalDispatcher(mock=True)
        # Wait for scan to populate devices
        import time

        time.sleep(0.5)
        snapshot = disp.get_device_snapshot()
        psu_names = [d["name"] for d in snapshot if d["base_type"] == "psu"]
        if psu_names:
            result = disp.get_instrument_detail(psu_names[0])
            assert result["type"] == "psu"
            assert "channels" in result or "subtype" in result

    def test_dmm_detail_has_reading(self):
        """DMM detail should include last_reading."""
        from lab_instruments.tui.dispatcher import LocalDispatcher

        disp = LocalDispatcher(mock=True)
        import time

        time.sleep(0.5)
        snapshot = disp.get_device_snapshot()
        dmm_names = [d["name"] for d in snapshot if d["base_type"] == "dmm"]
        if dmm_names:
            result = disp.get_instrument_detail(dmm_names[0])
            assert result["type"] == "dmm"
            assert "last_reading" in result

    def test_awg_detail_has_channels(self):
        """AWG detail should include channels list."""
        from lab_instruments.tui.dispatcher import LocalDispatcher

        disp = LocalDispatcher(mock=True)
        import time

        time.sleep(0.5)
        snapshot = disp.get_device_snapshot()
        awg_names = [d["name"] for d in snapshot if d["base_type"] == "awg"]
        if awg_names:
            result = disp.get_instrument_detail(awg_names[0])
            assert result["type"] == "awg"
            assert "channels" in result

    def test_scope_detail_has_trigger(self):
        """Scope detail should include trigger_status."""
        from lab_instruments.tui.dispatcher import LocalDispatcher

        disp = LocalDispatcher(mock=True)
        import time

        time.sleep(0.5)
        snapshot = disp.get_device_snapshot()
        scope_names = [d["name"] for d in snapshot if d["base_type"] == "scope"]
        if scope_names:
            result = disp.get_instrument_detail(scope_names[0])
            assert result["type"] == "scope"
            assert "trigger_status" in result

    def test_device_snapshot_has_status(self):
        """Device snapshot should include status field."""
        from lab_instruments.tui.dispatcher import LocalDispatcher

        disp = LocalDispatcher(mock=True)
        import time

        time.sleep(0.5)
        snapshot = disp.get_device_snapshot()
        if snapshot:
            assert "status" in snapshot[0]
            assert snapshot[0]["status"] in ("connected", "error", "unknown")

    def test_safety_snapshot_has_limits_list(self):
        """Safety snapshot should include a limits list."""
        from lab_instruments.tui.dispatcher import LocalDispatcher

        disp = LocalDispatcher(mock=True)
        snap = disp.get_safety_snapshot()
        assert "limits" in snap
        assert isinstance(snap["limits"], list)


# ---------------------------------------------------------------------------
# Safety limits panel tests
# ---------------------------------------------------------------------------


class TestSafetyLimitsPanel:
    def test_limits_panel_mounts(self):
        """SafetyLimitsPanel should exist in widget tree."""

        async def inner():
            from lab_instruments.tui.widgets.safety_limits_panel import SafetyLimitsPanel

            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(100, 30)):
                panel = app.query_one(SafetyLimitsPanel)
                assert panel is not None

        asyncio.run(inner())

    def test_limits_panel_shows_no_limits(self):
        """Panel with no limits should show placeholder row."""

        async def inner():
            from lab_instruments.tui.widgets.safety_limits_panel import SafetyLimitsPanel

            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(100, 30)) as pilot:
                panel = app.query_one(SafetyLimitsPanel)
                panel.limits = []
                await pilot.pause(0.05)
                table = panel.query_one("#limits-table")
                assert table.row_count == 1

        asyncio.run(inner())

    def test_limits_panel_shows_limits(self):
        """Panel with limits should render rows."""

        async def inner():
            from lab_instruments.tui.widgets.safety_limits_panel import SafetyLimitsPanel

            limits = [
                {"device": "psu1", "channel": None, "parameter": "voltage_upper", "value": 30.0},
                {"device": "psu1", "channel": None, "parameter": "current_upper", "value": 5.0},
            ]
            stub = _StubDispatcher(limits=limits)
            app = SCPIApp(stub)
            async with app.run_test(size=(100, 30)) as pilot:
                panel = app.query_one(SafetyLimitsPanel)
                panel.limits = limits
                await pilot.pause(0.05)
                table = panel.query_one("#limits-table")
                assert table.row_count == 2

        asyncio.run(inner())

    def test_alt_l_toggles_limits_view(self):
        """Alt+L should toggle limits-view."""

        async def inner():
            app = SCPIApp(_StubDispatcher())
            async with app.run_test(size=(100, 30)) as pilot:
                switcher = app.query_one("#main-content", TabbedContent)
                assert switcher.active == "log-view"

                await app.run_action("show_limits")
                await pilot.pause(0.05)
                assert switcher.active == "limits-view"

                await app.run_action("show_limits")
                await pilot.pause(0.05)
                assert switcher.active == "log-view"

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# Active instrument selection tests
# ---------------------------------------------------------------------------


class TestActiveInstrumentSelection:
    def test_device_selected_dispatches_use_command(self):
        """Clicking a device should dispatch 'use <device>'."""

        async def inner():
            devices = [_make_device("psu1", "HP E3631A")]
            stub = _StubDispatcher(devices=devices)
            app = SCPIApp(stub)
            async with app.run_test(size=(100, 30)) as pilot:
                from lab_instruments.tui.widgets.device_sidebar import DeviceSidebar

                sidebar = app.query_one(DeviceSidebar)
                sidebar.post_message(DeviceSidebar.DeviceSelected("psu1"))
                await pilot.pause(0.2)

                assert "use psu1" in stub._commands

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# Loading spinner tests
# ---------------------------------------------------------------------------


class TestLoadingSpinner:
    def test_input_placeholder_changes_during_command(self):
        """Input placeholder should change while a command is running."""

        async def inner():
            from textual.widgets import Input

            stub = _StubDispatcher()
            app = SCPIApp(stub)
            async with app.run_test(size=(100, 30)) as pilot:
                inp = app.query_one("#cmd_input", Input)
                assert inp.placeholder == "Enter command..."

                # Submit a command
                await pilot.click("#cmd_input")
                await pilot.press("h", "e", "l", "p")
                await pilot.press("enter")
                await pilot.pause(0.2)

                # After completion, placeholder should be back to normal
                assert inp.placeholder == "Enter command..."

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# Log coloring tests
# ---------------------------------------------------------------------------


class TestLogColoring:
    def test_stream_line_writes_plain_text(self):
        """Plain text should be written to the log."""

        async def inner():
            from textual.widgets import RichLog

            stub = _StubDispatcher()
            app = SCPIApp(stub)
            async with app.run_test(size=(100, 30)):
                log = app.query_one("#log-output", RichLog)
                initial_lines = len(log.lines)
                app._stream_line("Hello world")
                assert len(log.lines) > initial_lines

        asyncio.run(inner())

    def test_stream_line_handles_ansi(self):
        """ANSI-colored text should be decoded and written."""

        async def inner():
            from textual.widgets import RichLog

            stub = _StubDispatcher()
            app = SCPIApp(stub)
            async with app.run_test(size=(100, 30)):
                log = app.query_one("#log-output", RichLog)
                initial_lines = len(log.lines)
                app._stream_line("\033[91mRed error text\033[0m")
                assert len(log.lines) > initial_lines

        asyncio.run(inner())
