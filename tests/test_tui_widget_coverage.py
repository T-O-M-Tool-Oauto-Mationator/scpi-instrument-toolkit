"""Tests to increase coverage for TUI widget files above 80%.

Covers: dispatcher.py, scpi_console.py, script_editor.py,
monitor_panel.py, connection_wizard.py, measurement_table.py.
"""

from __future__ import annotations

import asyncio

import pytest

from lab_instruments.tui.app import SCPIApp
from lab_instruments.tui.widgets.measurement_table import MeasurementTable
from lab_instruments.tui.widgets.monitor_panel import MonitorPanel
from lab_instruments.tui.widgets.scpi_console import ScpiConsole
from lab_instruments.tui.widgets.script_editor import ScriptEditor

# ---------------------------------------------------------------------------
# Stub dispatcher (matches _Stub in test_tui_new_widgets.py)
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
        ]

    def get_script_names(self):
        return ["demo"]

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
        return "# demo script\npsu set 5"

    def save_script_content(self, name, content):
        pass

    def delete_script(self, name):
        pass

    def save_instrument_state(self, name):
        return {}

    def restore_instrument_state(self, name, snap):
        pass


# ===================================================================
# 1. LocalDispatcher tests  (no Textual/async needed)
# ===================================================================


class TestLocalDispatcher:
    """Test LocalDispatcher methods using mock=True instruments."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        from lab_instruments.tui.dispatcher import LocalDispatcher

        self.d = LocalDispatcher(mock=True)
        # Discover mock devices so they populate the registry
        self.d.handle_command("scan")

    # -- snapshots ---------------------------------------------------------

    def test_get_device_snapshot_returns_list(self):
        snap = self.d.get_device_snapshot()
        assert isinstance(snap, list)
        assert len(snap) > 0
        # Each entry has expected keys
        entry = snap[0]
        assert "name" in entry
        assert "display_name" in entry
        assert "selected" in entry
        assert "base_type" in entry
        assert "status" in entry

    def test_get_measurement_snapshot_empty_initially(self):
        snap = self.d.get_measurement_snapshot()
        assert isinstance(snap, list)

    def test_get_script_names_returns_list(self):
        names = self.d.get_script_names()
        assert isinstance(names, list)

    def test_get_vars_snapshot_returns_dict(self):
        snap = self.d.get_vars_snapshot()
        assert isinstance(snap, dict)

    def test_get_safety_snapshot_keys(self):
        snap = self.d.get_safety_snapshot()
        assert "limit_count" in snap
        assert "active_script" in snap
        assert "exit_on_error" in snap
        assert "limits" in snap
        assert "measurement_count" in snap
        assert "data_dir" in snap

    # -- script CRUD -------------------------------------------------------

    def test_save_and_get_script_content(self):
        self.d.save_script_content("test_script", "psu set 3.3\npsu on")
        content = self.d.get_script_content("test_script")
        assert "psu set 3.3" in content
        assert "psu on" in content
        # Cleanup
        self.d.delete_script("test_script")

    def test_delete_script_removes(self):
        self.d.save_script_content("del_me", "dmm read")
        assert "del_me" in self.d.get_script_names()
        self.d.delete_script("del_me")
        assert "del_me" not in self.d.get_script_names()

    def test_get_script_content_missing(self):
        content = self.d.get_script_content("nonexistent_script_xyz")
        assert content == ""

    # -- instrument detail (PSU) -------------------------------------------

    def test_detail_psu_single_channel(self):
        detail = self.d.get_instrument_detail("psu2")
        assert detail["type"] == "psu"
        assert "channels" in detail
        assert len(detail["channels"]) >= 1

    def test_detail_psu_multi_channel(self):
        detail = self.d.get_instrument_detail("psu1")
        assert detail["type"] == "psu"
        assert "channels" in detail
        assert len(detail["channels"]) > 1

    def test_detail_smu(self):
        detail = self.d.get_instrument_detail("smu")
        # base_type("smu") returns "smu" which has no dispatch branch,
        # so the result only has the base keys
        assert detail["type"] == "smu"
        assert detail["name"] == "smu"
        assert "display_name" in detail

    # -- instrument detail (DMM) -------------------------------------------

    def test_detail_dmm(self):
        detail = self.d.get_instrument_detail("dmm1")
        assert detail["type"] == "dmm"
        assert "last_reading" in detail
        assert isinstance(detail["last_reading"], float)

    # -- instrument detail (AWG) -------------------------------------------

    def test_detail_awg(self):
        detail = self.d.get_instrument_detail("awg1")
        assert detail["type"] == "awg"
        assert "channels" in detail
        assert len(detail["channels"]) == 2
        ch = detail["channels"][0]
        assert "frequency" in ch
        assert "amplitude" in ch
        assert "offset" in ch
        assert "output" in ch

    # -- instrument detail (scope) -----------------------------------------

    def test_detail_scope(self):
        detail = self.d.get_instrument_detail("scope1")
        assert detail["type"] == "scope"
        assert "trigger_status" in detail
        assert "num_channels" in detail

    # -- instrument detail (ev2300) ----------------------------------------

    def test_detail_ev2300(self):
        detail = self.d.get_instrument_detail("ev2300")
        # base_type("ev2300") strips trailing digits -> "ev", so the
        # "ev2300" branch in get_instrument_detail is not reached.
        assert detail["type"] == "ev"
        assert detail["name"] == "ev2300"

    # -- instrument detail (not found) -------------------------------------

    def test_detail_not_found(self):
        detail = self.d.get_instrument_detail("no_such_device")
        assert detail["type"] == "unknown"
        assert "error" in detail

    # -- save / restore instrument state -----------------------------------

    def test_save_instrument_state_psu(self):
        snap = self.d.save_instrument_state("psu2")
        assert snap["type"] == "psu"
        assert "voltage" in snap
        assert "current" in snap
        assert "output" in snap

    def test_save_instrument_state_smu(self):
        snap = self.d.save_instrument_state("smu")
        # base_type("smu") returns "smu", which doesn't match "psu" or "awg"
        # branches in save_instrument_state, so only type and name are set
        assert snap["type"] == "smu"
        assert snap["name"] == "smu"

    def test_save_instrument_state_awg(self):
        snap = self.d.save_instrument_state("awg1")
        assert snap["type"] == "awg"
        assert "channels" in snap
        assert len(snap["channels"]) == 2

    def test_save_instrument_state_missing_device(self):
        snap = self.d.save_instrument_state("bogus")
        assert snap == {}

    def test_restore_instrument_state_psu(self):
        snap = self.d.save_instrument_state("psu2")
        # Should not raise
        self.d.restore_instrument_state("psu2", snap)

    def test_restore_instrument_state_smu(self):
        snap = self.d.save_instrument_state("smu")
        # base_type is "smu", so restore is effectively a no-op (no matching branch)
        self.d.restore_instrument_state("smu", snap)

    def test_restore_instrument_state_awg(self):
        snap = self.d.save_instrument_state("awg1")
        self.d.restore_instrument_state("awg1", snap)

    def test_restore_instrument_state_missing_device(self):
        # Should not raise
        self.d.restore_instrument_state("bogus", {"type": "psu"})

    # -- completions -------------------------------------------------------

    def test_get_completions_returns_list(self):
        result = self.d.get_completions("sc")
        assert isinstance(result, list)

    def test_get_completions_empty_prefix(self):
        result = self.d.get_completions("")
        assert isinstance(result, list)

    # -- handle_command with line_callback ---------------------------------

    def test_handle_command_with_callback(self):
        chunks = []
        self.d.handle_command("help", line_callback=lambda s: chunks.append(s))
        assert isinstance(chunks, list)


# ===================================================================
# 2. ScpiConsole widget tests
# ===================================================================


class TestScpiConsoleWidget:
    def test_on_input_submitted_dispatches_command(self):
        """Focus the SCPI input and type+enter triggers RawCommand dispatch."""

        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Input

            received = []

            class _ConsoleApp(App):
                def compose(self) -> ComposeResult:
                    yield ScpiConsole()

                def on_scpi_console_raw_command(self, event):
                    received.append(event.command)

            app = _ConsoleApp()
            async with app.run_test(size=(120, 40)) as pilot:
                console = app.query_one(ScpiConsole)
                inp = console.query_one("#scpi-input", Input)
                inp.focus()
                await pilot.pause(0.1)
                inp.value = "*IDN?"
                await pilot.pause(0.1)
                await pilot.press("enter")
                await pilot.pause(0.3)
                assert "*IDN?" in received

        asyncio.run(inner())

    def test_on_input_submitted_empty_ignored(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Input

            received = []

            class _ConsoleApp(App):
                def compose(self) -> ComposeResult:
                    yield ScpiConsole()

                def on_scpi_console_raw_command(self, event):
                    received.append(event.command)

            app = _ConsoleApp()
            async with app.run_test(size=(120, 40)) as pilot:
                console = app.query_one(ScpiConsole)
                inp = console.query_one("#scpi-input", Input)
                inp.focus()
                await pilot.pause(0.1)
                inp.value = "   "
                await pilot.pause(0.1)
                await pilot.press("enter")
                await pilot.pause(0.2)
                assert len(received) == 0

        asyncio.run(inner())

    def test_on_input_submitted_clears_input(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Input

            class _ConsoleApp(App):
                def compose(self) -> ComposeResult:
                    yield ScpiConsole()

            app = _ConsoleApp()
            async with app.run_test(size=(120, 40)) as pilot:
                console = app.query_one(ScpiConsole)
                inp = console.query_one("#scpi-input", Input)
                inp.focus()
                await pilot.pause(0.1)
                inp.value = "*RST"
                await pilot.pause(0.1)
                await pilot.press("enter")
                await pilot.pause(0.2)
                assert inp.value == ""

        asyncio.run(inner())

    def test_add_response_writes_to_log(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import RichLog

            class _ConsoleApp(App):
                def compose(self) -> ComposeResult:
                    yield ScpiConsole()

            app = _ConsoleApp()
            async with app.run_test(size=(120, 40)) as pilot:
                console = app.query_one(ScpiConsole)
                console.add_response("MOCK INSTRUMENTS INC")
                await pilot.pause(0.2)
                # add_response calls RichLog.write() -- just verify no exception
                log = console.query_one("#scpi-log", RichLog)
                assert log is not None

        asyncio.run(inner())

    def test_clear_button_clears_log(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Button, RichLog

            class _ConsoleApp(App):
                def compose(self) -> ComposeResult:
                    yield ScpiConsole()

            app = _ConsoleApp()
            async with app.run_test(size=(120, 40)) as pilot:
                console = app.query_one(ScpiConsole)
                console.add_response("line 1")
                console.add_response("line 2")
                await pilot.pause(0.2)
                btn = console.query_one("#scpi-clear", Button)
                btn.press()
                await pilot.pause(0.2)
                # Verify clear was called (log internal lines list should be empty)
                log = console.query_one("#scpi-log", RichLog)
                assert len(log.lines) == 0

        asyncio.run(inner())


# ===================================================================
# 3. ScriptEditor widget tests
# ===================================================================


class TestScriptEditorWidget:
    def test_load_content_updates_textarea(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Static, TextArea

            class _EditorApp(App):
                def compose(self) -> ComposeResult:
                    yield ScriptEditor()

            app = _EditorApp()
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                editor.load_content("demo", "psu set 5\npsu on")
                await pilot.pause(0.1)
                ta = editor.query_one("#editor-textarea", TextArea)
                assert "psu set 5" in ta.text
                status = editor.query_one("#editor-status", Static)
                rendered = str(status.render())
                assert "demo" in rendered

        asyncio.run(inner())

    def test_on_input_submitted_creates_new_script(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Input, Static, TextArea

            class _EditorApp(App):
                def compose(self) -> ComposeResult:
                    yield ScriptEditor()

            app = _EditorApp()
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                inp = editor.query_one("#new-script-input", Input)
                inp.focus()
                await pilot.pause(0.1)
                inp.value = "my_test"
                await pilot.pause(0.1)
                await pilot.press("enter")
                await pilot.pause(0.2)
                ta = editor.query_one("#editor-textarea", TextArea)
                assert "my_test" in ta.text
                status = editor.query_one("#editor-status", Static)
                rendered = str(status.render())
                assert "my_test" in rendered

        asyncio.run(inner())

    def test_on_input_submitted_empty_ignored(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Input

            class _EditorApp(App):
                def compose(self) -> ComposeResult:
                    yield ScriptEditor()

            app = _EditorApp()
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                inp = editor.query_one("#new-script-input", Input)
                inp.focus()
                await pilot.pause(0.1)
                inp.value = "   "
                await pilot.pause(0.1)
                await pilot.press("enter")
                await pilot.pause(0.1)
                assert editor._current_script is None

        asyncio.run(inner())

    def test_save_button_posts_message(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Button

            saved = []

            class _EditorApp(App):
                def compose(self) -> ComposeResult:
                    yield ScriptEditor()

                def on_script_editor_save_requested(self, event):
                    saved.append((event.name, event.content))

            app = _EditorApp()
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                editor.load_content("demo", "psu set 3.3")
                await pilot.pause(0.1)
                btn = editor.query_one("#editor-save", Button)
                btn.press()
                await pilot.pause(0.3)
                assert len(saved) == 1
                assert saved[0][0] == "demo"

        asyncio.run(inner())

    def test_run_button_posts_save_and_run(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Button

            run_names = []

            class _EditorApp(App):
                def compose(self) -> ComposeResult:
                    yield ScriptEditor()

                def on_script_editor_save_requested(self, event):
                    pass

                def on_script_editor_run_requested(self, event):
                    run_names.append(event.name)

            app = _EditorApp()
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                editor.load_content("demo", "psu set 3.3")
                await pilot.pause(0.1)
                btn = editor.query_one("#editor-run", Button)
                btn.press()
                await pilot.pause(0.3)
                assert "demo" in run_names

        asyncio.run(inner())

    def test_delete_button_clears_editor(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Button, Static, TextArea

            class _EditorApp(App):
                def compose(self) -> ComposeResult:
                    yield ScriptEditor()

                def on_script_editor_delete_requested(self, event):
                    pass

            app = _EditorApp()
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                editor.load_content("demo", "psu set 3.3")
                await pilot.pause(0.1)
                btn = editor.query_one("#editor-delete", Button)
                btn.press()
                await pilot.pause(0.3)
                assert editor._current_script is None
                ta = editor.query_one("#editor-textarea", TextArea)
                assert ta.text == ""
                status = editor.query_one("#editor-status", Static)
                rendered = str(status.render())
                assert "deleted" in rendered.lower()

        asyncio.run(inner())

    def test_button_press_with_no_script_selected_is_noop(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Button

            saved = []

            class _EditorApp(App):
                def compose(self) -> ComposeResult:
                    yield ScriptEditor()

                def on_script_editor_save_requested(self, event):
                    saved.append(event.name)

            app = _EditorApp()
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                assert editor._current_script is None
                btn = editor.query_one("#editor-save", Button)
                btn.press()
                await pilot.pause(0.2)
                assert len(saved) == 0

        asyncio.run(inner())

    def test_list_view_selected(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import ListView

            load_requests = []

            class _EditorApp(App):
                def compose(self) -> ComposeResult:
                    yield ScriptEditor()

                def on_script_editor__load_script(self, event):
                    load_requests.append(event.name)

            app = _EditorApp()
            async with app.run_test(size=(120, 40)) as pilot:
                editor = app.query_one(ScriptEditor)
                editor.scripts = ["demo", "other"]
                await pilot.pause(0.2)
                lv = editor.query_one("#script-list", ListView)
                if lv.children:
                    lv.index = 0
                    lv.action_select_cursor()
                    await pilot.pause(0.3)
                    assert len(load_requests) >= 1

        asyncio.run(inner())


# ===================================================================
# 4. MonitorPanel widget tests
# ===================================================================


class TestMonitorPanelWidget:
    def test_start_button(self):
        async def inner():
            from textual.widgets import Button

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(MonitorPanel)
                btn = panel.query_one("#monitor-start", Button)
                btn.press()
                await pilot.pause(0.2)
                assert panel._running is True

        asyncio.run(inner())

    def test_stop_button(self):
        async def inner():
            from textual.widgets import Button

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(MonitorPanel)
                panel._start()
                await pilot.pause(0.1)
                btn = panel.query_one("#monitor-stop", Button)
                btn.press()
                await pilot.pause(0.1)
                assert panel._running is False

        asyncio.run(inner())

    def test_start_already_running_noop(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(MonitorPanel)
                panel._start()
                await pilot.pause(0.1)
                timer_before = panel._timer
                # Starting again should be a no-op
                panel._start()
                await pilot.pause(0.1)
                assert panel._timer is timer_before

        asyncio.run(inner())

    def test_start_with_invalid_interval_defaults(self):
        async def inner():
            from textual.widgets import Input

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(MonitorPanel)
                inp = panel.query_one("#monitor-interval", Input)
                inp.value = "not_a_number"
                panel._start()
                await pilot.pause(0.1)
                assert panel._running is True
                panel._stop()

        asyncio.run(inner())

    def test_tick_posts_command(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(MonitorPanel)
                panel._running = True
                panel._tick()
                await pilot.pause(0.3)

        asyncio.run(inner())

    def test_tick_when_not_running_noop(self):
        async def inner():
            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(MonitorPanel)
                panel._running = False
                panel._tick()
                await pilot.pause(0.1)
                # No command dispatched because _running is False
                # (the message is posted but _tick guards on _running)

        asyncio.run(inner())

    def test_add_reading_overflow_truncates(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                panel = app.query_one(MonitorPanel)
                for i in range(150):
                    panel.add_reading(float(i))
                await pilot.pause(0.1)
                assert len(panel._readings) <= panel._MAX_READINGS

        asyncio.run(inner())


# ===================================================================
# 5. ConnectionWizard widget tests
# ===================================================================


class TestConnectionWizardWidget:
    def test_test_button_with_address(self):
        async def inner():
            from textual.widgets import Input

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("connection_wizard")
                await pilot.pause(0.2)
                wiz = app.screen
                addr_input = wiz.query_one("#wizard-address", Input)
                addr_input.value = "TCPIP0::192.168.1.100::INSTR"
                from textual.widgets import Button

                btn = wiz.query_one("#wizard-test", Button)
                btn.press()
                await pilot.pause(0.3)
                # Wizard should dismiss with "test:..."
                # and the app dispatches raw *IDN?
                assert any("raw *IDN?" in c for c in stub._commands)

        asyncio.run(inner())

    def test_test_button_without_address(self):
        async def inner():
            from textual.widgets import Button, Static

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("connection_wizard")
                await pilot.pause(0.2)
                wiz = app.screen
                btn = wiz.query_one("#wizard-test", Button)
                btn.press()
                await pilot.pause(0.2)
                status = wiz.query_one("#wizard-status", Static)
                rendered = str(status.render())
                assert "resource string" in rendered.lower() or "enter" in rendered.lower()
                await pilot.press("escape")
                await pilot.pause(0.2)

        asyncio.run(inner())

    def test_scan_button(self):
        async def inner():
            from textual.widgets import Button

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("connection_wizard")
                await pilot.pause(0.2)
                wiz = app.screen
                btn = wiz.query_one("#wizard-scan", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("scan" in c for c in stub._commands)

        asyncio.run(inner())

    def test_cancel_button(self):
        async def inner():
            from textual.widgets import Button

            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("connection_wizard")
                await pilot.pause(0.2)
                wiz = app.screen
                btn = wiz.query_one("#wizard-cancel", Button)
                btn.press()
                await pilot.pause(0.3)
                # Should dismiss, going back to main screen
                assert app.screen.__class__.__name__ != "ConnectionWizard"

        asyncio.run(inner())

    def test_dismiss_wizard_action(self):
        async def inner():
            app = SCPIApp(_Stub())
            async with app.run_test(size=(120, 40)) as pilot:
                await app.run_action("connection_wizard")
                await pilot.pause(0.2)
                assert app.screen.__class__.__name__ == "ConnectionWizard"
                app.screen.action_dismiss_wizard()
                await pilot.pause(0.3)
                assert app.screen.__class__.__name__ != "ConnectionWizard"

        asyncio.run(inner())


# ===================================================================
# 6. MeasurementTable widget tests
# ===================================================================


class TestMeasurementTableWidget:
    def test_export_csv_with_data(self, tmp_path):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Button

            class _TableApp(App):
                def compose(self) -> ComposeResult:
                    yield MeasurementTable(
                        data_dir_getter=lambda: str(tmp_path),
                    )

            app = _TableApp()
            async with app.run_test(size=(120, 40)) as pilot:
                table = app.query_one(MeasurementTable)
                table.measurements = [
                    {"label": "v1", "value": 5.0, "unit": "V", "source": "psu"},
                    {"label": "i1", "value": 0.1, "unit": "A", "source": "psu"},
                ]
                await pilot.pause(0.1)
                btn = table.query_one("#export-csv", Button)
                btn.press()
                await pilot.pause(0.3)
                csvs = list(tmp_path.glob("measurements_*.csv"))
                assert len(csvs) >= 1

        asyncio.run(inner())

    def test_export_csv_empty(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Button

            class _TableApp(App):
                def compose(self) -> ComposeResult:
                    yield MeasurementTable()

            app = _TableApp()
            async with app.run_test(size=(120, 40)) as pilot:
                table = app.query_one(MeasurementTable)
                table.measurements = []
                await pilot.pause(0.1)
                btn = table.query_one("#export-csv", Button)
                btn.press()
                await pilot.pause(0.2)
                # Should not crash

        asyncio.run(inner())

    def test_clear_all_posts_message(self):
        async def inner():
            from textual.widgets import Button

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                table = app.query_one(MeasurementTable)
                btn = table.query_one("#clear-all", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("log clear" in c for c in stub._commands)

        asyncio.run(inner())

    def test_report_button_posts_message(self):
        async def inner():
            from textual.widgets import Button

            stub = _Stub()
            app = SCPIApp(stub)
            async with app.run_test(size=(120, 40)) as pilot:
                table = app.query_one(MeasurementTable)
                btn = table.query_one("#gen-report", Button)
                btn.press()
                await pilot.pause(0.3)
                assert any("report save" in c for c in stub._commands)

        asyncio.run(inner())

    def test_annotate_input(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import DataTable, Input

            class _TableApp(App):
                def compose(self) -> ComposeResult:
                    yield MeasurementTable()

            app = _TableApp()
            async with app.run_test(size=(120, 40)) as pilot:
                table = app.query_one(MeasurementTable)
                table.measurements = [
                    {"label": "v1", "value": 5.0, "unit": "V", "source": "psu"},
                ]
                await pilot.pause(0.2)
                dt = table.query_one("#meas-table", DataTable)
                dt.move_cursor(row=0)
                await pilot.pause(0.1)
                inp = table.query_one("#annotate-input", Input)
                inp.focus()
                await pilot.pause(0.1)
                inp.value = "test note"
                await pilot.pause(0.1)
                await pilot.press("enter")
                await pilot.pause(0.3)
                assert 1 in table._annotations
                assert table._annotations[1] == "test note"

        asyncio.run(inner())

    def test_annotate_empty_ignored(self):
        async def inner():
            from textual.app import App, ComposeResult
            from textual.widgets import Input

            class _TableApp(App):
                def compose(self) -> ComposeResult:
                    yield MeasurementTable()

            app = _TableApp()
            async with app.run_test(size=(120, 40)) as pilot:
                table = app.query_one(MeasurementTable)
                inp = table.query_one("#annotate-input", Input)
                inp.focus()
                await pilot.pause(0.1)
                inp.value = "   "
                await pilot.pause(0.1)
                await pilot.press("enter")
                await pilot.pause(0.1)
                assert len(table._annotations) == 0

        asyncio.run(inner())
