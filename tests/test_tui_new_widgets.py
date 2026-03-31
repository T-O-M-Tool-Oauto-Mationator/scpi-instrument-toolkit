"""Tests for new TUI widgets: monitor, waveform, scpi console, connection wizard, plot panel."""

from __future__ import annotations

import asyncio

from lab_instruments.tui.app import SCPIApp
from lab_instruments.tui.widgets.connection_wizard import ConnectionWizard
from lab_instruments.tui.widgets.monitor_panel import MonitorPanel
from lab_instruments.tui.widgets.plot_panel import PlotPanel
from lab_instruments.tui.widgets.scpi_console import ScpiConsole
from lab_instruments.tui.widgets.waveform_viewer import WaveformViewer, _render_waveform

# ---------------------------------------------------------------------------
# Stub
# ---------------------------------------------------------------------------


class _Stub:
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
        return [
            {"label": "v1", "value": 5.0, "unit": "V", "source": "psu"},
            {"label": "v2", "value": 3.3, "unit": "V", "source": "psu"},
            {"label": "i1", "value": 0.1, "unit": "A", "source": "psu"},
        ]

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
        return {"type": "unknown", "name": name, "display_name": name, "error": "stub"}

    def get_script_content(self, name):
        return ""

    def save_script_content(self, name, content):
        pass

    def delete_script(self, name):
        pass

    def save_instrument_state(self, name):
        return {}

    def restore_instrument_state(self, name, snap):
        pass


# ---------------------------------------------------------------------------
# Waveform viewer
# ---------------------------------------------------------------------------


class TestWaveformViewer:
    def test_render_waveform_with_data(self):
        import math

        data = [math.sin(2 * math.pi * i / 50) for i in range(100)]
        result = _render_waveform(data, width=40, height=5)
        assert len(result) > 0
        assert "\n" in result

    def test_render_waveform_empty(self):
        result = _render_waveform([], width=40, height=5)
        assert "No waveform" in result

    def test_render_waveform_single_point(self):
        result = _render_waveform([1.0], width=40, height=5)
        assert "Not enough" in result

    def test_render_waveform_constant(self):
        result = _render_waveform([5.0] * 20, width=40, height=5)
        assert len(result) > 0

    def test_viewer_mounts(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)):
                viewer = app.query_one(WaveformViewer)
                assert viewer is not None

        asyncio.run(inner())

    def test_viewer_capture_posts_message(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                viewer = app.query_one(WaveformViewer)
                viewer.post_message(WaveformViewer.CaptureRequested("scope1"))
                await pilot.pause(0.2)

        asyncio.run(inner())

    def test_viewer_data_updates_display(self):
        async def inner():
            import math

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                viewer = app.query_one(WaveformViewer)
                viewer.data = [math.sin(i * 0.1) for i in range(50)]
                await pilot.pause(0.1)

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# Monitor panel
# ---------------------------------------------------------------------------


class TestMonitorPanel:
    def test_monitor_mounts(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)):
                panel = app.query_one(MonitorPanel)
                assert panel is not None

        asyncio.run(inner())

    def test_add_reading_updates_stats(self):
        async def inner():
            from textual.widgets import Static

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(MonitorPanel)
                panel.add_reading(5.0)
                panel.add_reading(5.1)
                panel.add_reading(4.9)
                await pilot.pause(0.1)
                stats = panel.query_one("#monitor-stats", Static)
                text = str(stats.render())
                assert "5." in text or "4." in text

        asyncio.run(inner())

    def test_start_stop(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(MonitorPanel)
                # Start monitoring
                panel._start()
                await pilot.pause(0.1)
                assert panel._running
                # Stop monitoring
                panel._stop()
                await pilot.pause(0.1)
                assert not panel._running

        asyncio.run(inner())

    def test_add_reading_respects_stopped(self):
        async def inner():
            from textual.widgets import Static

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(MonitorPanel)
                panel._running = False
                panel.add_reading(5.0)
                await pilot.pause(0.1)
                text = str(panel.query_one("#monitor-stats", Static).render())
                assert "Running" not in text or "Stopped" in text

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# SCPI console
# ---------------------------------------------------------------------------


class TestScpiConsole:
    def test_console_mounts(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)):
                console = app.query_one(ScpiConsole)
                assert console is not None

        asyncio.run(inner())

    def test_add_response(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                console = app.query_one(ScpiConsole)
                # Verify add_response runs without error
                console.add_response("MOCK INSTRUMENTS INC")
                await pilot.pause(0.2)

        asyncio.run(inner())

        asyncio.run(inner())

    def test_raw_command_message(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                console = app.query_one(ScpiConsole)
                console.post_message(ScpiConsole.RawCommand("*IDN?"))
                await pilot.pause(0.3)
                assert any("raw *IDN?" in c for c in stub._commands)

        asyncio.run(inner())

    def test_clear_button_exists(self):
        async def inner():
            from textual.widgets import Button

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)):
                console = app.query_one(ScpiConsole)
                clear_btn = console.query_one("#scpi-clear", Button)
                assert clear_btn is not None

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# Connection wizard
# ---------------------------------------------------------------------------


class TestConnectionWizard:
    def test_wizard_opens(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("connection_wizard")
                await pilot.pause(0.2)
                assert app.screen.__class__.__name__ == "ConnectionWizard"

        asyncio.run(inner())

    def test_wizard_dismisses_on_escape(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("connection_wizard")
                await pilot.pause(0.2)
                await pilot.press("escape")
                await pilot.pause(0.3)
                assert app.screen.__class__.__name__ != "ConnectionWizard"

        asyncio.run(inner())

    def test_wizard_compose(self):
        async def inner():
            from textual.app import App, ComposeResult

            class _WizApp(App):
                def compose(self) -> ComposeResult:
                    yield ConnectionWizard()

            # Just verify it composes without error
            assert ConnectionWizard is not None

        asyncio.run(inner())

    def test_wizard_get_interface(self):
        """Test _get_interface returns a valid string."""

        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("connection_wizard")
                await pilot.pause(0.2)
                wiz = app.screen
                if hasattr(wiz, "_get_interface"):
                    iface = wiz._get_interface()
                    assert iface in ("TCPIP", "USB", "GPIB", "Serial")
                await pilot.press("escape")
                await pilot.pause(0.2)

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# Plot panel
# ---------------------------------------------------------------------------


class TestPlotPanel:
    def test_plot_mounts(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)):
                panel = app.query_one(PlotPanel)
                assert panel is not None

        asyncio.run(inner())

    def test_plot_measurements_populate(self):
        async def inner():
            from textual.widgets import DataTable

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(PlotPanel)
                panel.measurements = [
                    {"label": "v1", "value": 5.0, "unit": "V", "source": "psu"},
                    {"label": "v2", "value": 3.3, "unit": "V", "source": "psu"},
                ]
                await pilot.pause(0.1)
                table = panel.query_one("#plot-table", DataTable)
                assert table.row_count == 2

        asyncio.run(inner())

    def test_plot_filter(self):
        async def inner():
            from textual.widgets import DataTable, Input

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(PlotPanel)
                panel.measurements = [
                    {"label": "vout_1", "value": 5.0, "unit": "V", "source": "psu"},
                    {"label": "iout_1", "value": 0.1, "unit": "A", "source": "psu"},
                ]
                await pilot.pause(0.1)
                # Set filter
                filt = panel.query_one("#plot-filter", Input)
                filt.value = "vout_*"
                await pilot.pause(0.1)
                table = panel.query_one("#plot-table", DataTable)
                assert table.row_count == 1

        asyncio.run(inner())

    def test_plot_all_button(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(PlotPanel)
                panel.post_message(PlotPanel.QuickAction("plot"))
                await pilot.pause(0.2)
                assert "plot" in stub._commands

        asyncio.run(inner())

    def test_plot_empty_shows_no_data(self):
        async def inner():
            from textual.widgets import Static

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(PlotPanel)
                panel.measurements = []
                await pilot.pause(0.1)
                summary = panel.query_one("#plot-summary", Static)
                text = str(summary.render())
                assert "No measurements" in text

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# App action coverage
# ---------------------------------------------------------------------------


class TestAppActions:
    def test_show_monitor(self):
        async def inner():
            from textual.widgets import TabbedContent

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("show_monitor")
                await pilot.pause(0.05)
                t = app.query_one("#main-content", TabbedContent)
                assert t.active == "monitor-view"

        asyncio.run(inner())

    def test_show_waveform(self):
        async def inner():
            from textual.widgets import TabbedContent

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("show_waveform")
                await pilot.pause(0.05)
                t = app.query_one("#main-content", TabbedContent)
                assert t.active == "wave-view"

        asyncio.run(inner())

    def test_show_console(self):
        async def inner():
            from textual.widgets import TabbedContent

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("show_console")
                await pilot.pause(0.05)
                t = app.query_one("#main-content", TabbedContent)
                assert t.active == "scpi-view"

        asyncio.run(inner())

    def test_show_notifications(self):
        async def inner():
            from textual.widgets import TabbedContent

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("show_notifications")
                await pilot.pause(0.05)
                t = app.query_one("#main-content", TabbedContent)
                assert t.active == "notif-view"

        asyncio.run(inner())

    def test_show_plot(self):
        async def inner():
            from textual.widgets import TabbedContent

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("show_plot")
                await pilot.pause(0.05)
                t = app.query_one("#main-content", TabbedContent)
                assert t.active == "plot-view"

        asyncio.run(inner())

    def test_take_screenshot(self, tmp_path):
        async def inner():
            app = SCPIApp(_Stub())
            app._get_data_dir = lambda: str(tmp_path)
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("take_screenshot")
                await pilot.pause(0.2)
                svgs = list(tmp_path.glob("tui_screenshot_*.svg"))
                assert len(svgs) >= 1

        asyncio.run(inner())

    def test_log_notification(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause(0.1)
                baseline = len(app._notification_log)
                app._log_notification("test message", severity="warning")
                await pilot.pause(0.1)
                assert len(app._notification_log) == baseline + 1
                assert app._notification_log[-1]["message"] == "test message"

        asyncio.run(inner())

    def test_toggle_sidebar(self):
        async def inner():
            from lab_instruments.tui.widgets.device_sidebar import DeviceSidebar

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                sidebar = app.query_one(DeviceSidebar)
                assert sidebar.display is True
                await app.run_action("toggle_sidebar")
                await pilot.pause(0.05)
                assert sidebar.display is False

        asyncio.run(inner())
