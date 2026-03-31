"""SCPI Instrument Toolkit - Textual TUI application."""

import contextlib
import sys
import time as _time

from rich.ansi import AnsiDecoder
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Footer, Header, Input, RichLog, TabbedContent, TabPane
from textual.worker import Worker, WorkerState

from .command_provider import SCPICommandProvider
from .completer import ReplSuggester
from .dispatcher import CommandDispatcher, LocalDispatcher
from .history import CommandHistory
from .widgets import (
    DeviceSidebar,
    HelpTooltip,
    InstrumentDetailPanel,
    MeasurementTable,
    MonitorPanel,
    NotificationCenter,
    PlotPanel,
    SafetyBar,
    SafetyLimitsPanel,
    ScpiConsole,
    ScriptBrowser,
    ScriptEditor,
    VarInspector,
    WaveformViewer,
)
from .widgets.help_tooltip import get_hint

# ANSI decoder for color escape sequences from command output
_ANSI_DECODER = AnsiDecoder()


class SCPIApp(App):
    """Textual app for SCPI command entry and output display."""

    TITLE = "SCPI Instrument Toolkit -- TUI (Tom User Interface)"
    SUB_TITLE = "lab_instruments"

    COMMANDS = App.COMMANDS | {SCPICommandProvider}

    BINDINGS = [
        # Shown in footer (essential shortcuts only)
        Binding("ctrl+l", "clear_log", "Clear", show=True),
        Binding("ctrl+r", "retry_last", "Retry", show=True),
        Binding("f1", "show_help", "Help", show=True),
        Binding("f2", "take_screenshot", "Screenshot", show=True),
        Binding("f3", "connection_wizard", "Connect", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
        # Hidden (tabs provide navigation; press F1 for full list)
        Binding("alt+c", "show_console", "SCPI", show=False),
        Binding("alt+d", "toggle_sidebar", "Devices", show=False),
        Binding("alt+e", "show_editor", "Editor", show=False),
        Binding("alt+i", "show_detail", "Detail", show=False),
        Binding("alt+l", "show_limits", "Limits", show=False),
        Binding("alt+m", "toggle_measurements", "Meas", show=False),
        Binding("alt+n", "show_notifications", "Notif", show=False),
        Binding("alt+o", "show_monitor", "Monitor", show=False),
        Binding("alt+p", "show_plot", "Plot", show=False),
        Binding("alt+s", "show_scripts", "Scripts", show=False),
        Binding("alt+v", "show_vars", "Vars", show=False),
        Binding("alt+w", "show_waveform", "Wave", show=False),
    ]

    DEFAULT_CSS = """
    #main-row {
        height: 1fr;
    }
    DeviceSidebar {
        width: 26;
        border-right: solid $primary-darken-2;
    }
    #log-area {
        height: 1fr;
    }
    TabbedContent {
        height: 1fr;
    }
    TabPane {
        height: 1fr;
        padding: 0;
    }
    #log-output {
        height: 1fr;
        border: solid $primary-darken-2;
        padding: 0 1;
    }
    Input {
        dock: bottom;
    }
    Input.busy {
        border: tall $warning;
    }
    SafetyBar {
        dock: bottom;
    }
    """

    def __init__(
        self,
        dispatcher: CommandDispatcher | None = None,
        device_poll_interval: float = 2.0,
        meas_poll_interval: float = 5.0,
        script_poll_interval: float = 2.0,
        safety_poll_interval: float = 1.0,
        detail_poll_interval: float = 2.0,
    ) -> None:
        super().__init__()
        self._dispatcher: CommandDispatcher = dispatcher if dispatcher is not None else LocalDispatcher()
        self._history: CommandHistory = CommandHistory()
        self._device_poll_interval: float = device_poll_interval
        self._meas_poll_interval: float = meas_poll_interval
        self._script_poll_interval: float = script_poll_interval
        self._safety_poll_interval: float = safety_poll_interval
        self._detail_poll_interval: float = detail_poll_interval
        self._selected_device: str | None = None
        self._prev_safety: dict = {}
        self._running_count: int = 0
        self._state_snapshots: dict[str, dict] = {}
        self._notification_log: list[dict] = []

    def compose(self) -> ComposeResult:
        """Build widget tree."""
        yield Header()
        with Horizontal(id="main-row"):
            yield DeviceSidebar(id="device-sidebar")
            with Vertical(id="log-area"):  # noqa: SIM117
                with TabbedContent(id="main-content"):
                    with TabPane("Log", id="log-view"):
                        yield RichLog(id="log-output", wrap=True, auto_scroll=True, markup=True)
                    with TabPane("Meas", id="meas-view"):
                        yield MeasurementTable(data_dir_getter=self._get_data_dir)
                    with TabPane("Scripts", id="script-view"):
                        yield ScriptBrowser()
                    with TabPane("Vars", id="vars-view"):
                        yield VarInspector()
                    with TabPane("Detail", id="detail-view"):
                        yield InstrumentDetailPanel()
                    with TabPane("Limits", id="limits-view"):
                        yield SafetyLimitsPanel()
                    with TabPane("Plot", id="plot-view"):
                        yield PlotPanel()
                    with TabPane("Notif", id="notif-view"):
                        yield NotificationCenter()
                    with TabPane("Monitor", id="monitor-view"):
                        yield MonitorPanel()
                    with TabPane("Wave", id="wave-view"):
                        yield WaveformViewer()
                    with TabPane("SCPI", id="scpi-view"):
                        yield ScpiConsole()
                    with TabPane("Editor", id="editor-view"):
                        yield ScriptEditor()
        yield HelpTooltip(id="help-tooltip")
        yield Input(placeholder="Enter command...", id="cmd_input", suggester=ReplSuggester(self._dispatcher))
        yield SafetyBar(id="safety-bar")
        yield Footer()

    def _get_data_dir(self) -> str:
        """Return data directory for CSV exports."""
        if hasattr(self._dispatcher, "repl"):
            return str(self._dispatcher.repl.ctx.get_data_dir())
        return str(__import__("pathlib").Path.home())

    def on_mount(self) -> None:
        """Focus input and start polling intervals."""
        self.query_one("#cmd_input", Input).focus()
        self.set_interval(self._device_poll_interval, self._refresh_devices)
        self.set_interval(self._meas_poll_interval, self._refresh_measurements)
        self.set_interval(self._script_poll_interval, self._refresh_scripts)
        self.set_interval(self._script_poll_interval, self._refresh_vars)
        self.set_interval(self._safety_poll_interval, self._refresh_safety)
        self.set_interval(self._detail_poll_interval, self._refresh_detail)

    # ------------------------------------------------------------------
    # Notification helper
    # ------------------------------------------------------------------

    def _log_notification(self, message: str, severity: str = "information", timeout: int = 8) -> None:
        """Log a notification to history AND show a toast."""
        self._notification_log.append(
            {
                "message": message,
                "severity": severity,
                "timestamp": _time.strftime("%H:%M:%S"),
            }
        )
        with contextlib.suppress(Exception):
            self.query_one(NotificationCenter).notifications = list(self._notification_log)
        self.notify(message, severity=severity, timeout=timeout)

    # ------------------------------------------------------------------
    # Refresh helpers
    # ------------------------------------------------------------------

    def _refresh_devices(self) -> None:
        if not hasattr(self._dispatcher, "get_device_snapshot"):
            return
        self.query_one(DeviceSidebar).devices = self._dispatcher.get_device_snapshot()

    def _refresh_measurements(self) -> None:
        if not hasattr(self._dispatcher, "get_measurement_snapshot"):
            return
        with contextlib.suppress(Exception):
            snap = self._dispatcher.get_measurement_snapshot()
            self.query_one(MeasurementTable).measurements = snap
            self.query_one(PlotPanel).measurements = snap

    def _refresh_scripts(self) -> None:
        if not hasattr(self._dispatcher, "get_script_names"):
            return
        names = self._dispatcher.get_script_names()
        self.query_one(ScriptBrowser).scripts = names
        with contextlib.suppress(Exception):
            self.query_one(ScriptEditor).scripts = names

    def _refresh_vars(self) -> None:
        if not hasattr(self._dispatcher, "get_vars_snapshot"):
            return
        self.query_one(VarInspector).variables = self._dispatcher.get_vars_snapshot()

    def _refresh_safety(self) -> None:
        if not hasattr(self._dispatcher, "get_safety_snapshot"):
            return
        snap = self._dispatcher.get_safety_snapshot()
        prev_count = self._prev_safety.get("limit_count", 0)
        if snap.get("limit_count", 0) > prev_count:
            self._log_notification("Safety limit triggered", severity="warning")
        self._prev_safety = dict(snap)
        self.query_one(SafetyBar).safety_info = snap
        with contextlib.suppress(Exception):
            self.query_one(SafetyLimitsPanel).limits = snap.get("limits", [])

    def _refresh_detail(self) -> None:
        if self._selected_device is None:
            return
        if not hasattr(self._dispatcher, "get_instrument_detail"):
            return
        # Always refresh (even when not visible) so sparkline history accumulates
        with contextlib.suppress(Exception):
            detail = self._dispatcher.get_instrument_detail(self._selected_device)
            self.query_one(InstrumentDetailPanel).detail = detail

    # ------------------------------------------------------------------
    # Tab helper
    # ------------------------------------------------------------------

    def _switch_tab(self, tab_id: str) -> None:
        """Switch TabbedContent to the given tab, or back to log-view if already there."""
        tabbed = self.query_one("#main-content", TabbedContent)
        tabbed.active = tab_id

    def _toggle_tab(self, tab_id: str) -> None:
        """Toggle between tab_id and log-view."""
        tabbed = self.query_one("#main-content", TabbedContent)
        tabbed.active = tab_id if tabbed.active != tab_id else "log-view"

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def on_key(self, event: Key) -> None:
        """Intercept up/down arrows when the command input is focused."""
        inp = self.query_one("#cmd_input", Input)
        if self.focused is not inp:
            return
        if event.key == "up":
            result = self._history.up()
            if result is not None:
                inp.value = result
                inp.cursor_position = len(result)
            event.stop()
        elif event.key == "down":
            result = self._history.down()
            inp.value = result if result is not None else ""
            inp.cursor_position = len(inp.value)
            event.stop()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user enter on input line."""
        cmd = event.value.strip()
        if not cmd:
            return
        self._history.push(cmd)
        event.input.clear()
        self._switch_tab("log-view")
        self.query_one("#log-output", RichLog).write(f"[bold cyan]> {cmd}[/bold cyan]")
        self._dispatch_command(cmd)

    def on_device_sidebar_device_selected(self, event: DeviceSidebar.DeviceSelected) -> None:
        """Select the instrument and show its detail panel."""
        event.stop()
        self._selected_device = event.device_name
        # Switch to detail view FIRST, then silently select the device
        self._switch_tab("detail-view")
        if hasattr(self._dispatcher, "get_instrument_detail"):
            with contextlib.suppress(Exception):
                detail = self._dispatcher.get_instrument_detail(event.device_name)
                self.query_one(InstrumentDetailPanel).detail = detail
        # Select the device in the REPL (runs in background, no tab switch)
        self._dispatch_command(f"use {event.device_name}")

    def on_instrument_detail_panel_quick_action(self, event: InstrumentDetailPanel.QuickAction) -> None:
        """Dispatch quick-action commands from the detail panel."""
        event.stop()
        self._switch_tab("log-view")
        for line in event.command.split("\n"):
            line = line.strip()
            if line:
                self.query_one("#log-output", RichLog).write(f"[bold cyan]> {line}[/bold cyan]")
                self._dispatch_command(line)

    def on_device_sidebar_bulk_action(self, event: DeviceSidebar.BulkAction) -> None:
        """Dispatch bulk operation from sidebar buttons."""
        event.stop()
        self._switch_tab("log-view")
        self.query_one("#log-output", RichLog).write(f"[bold cyan]> {event.command}[/bold cyan]")
        self._dispatch_command(event.command)

    def on_measurement_table_clear_requested(self, event: MeasurementTable.ClearRequested) -> None:
        """Clear all measurements."""
        event.stop()
        self._switch_tab("log-view")
        self.query_one("#log-output", RichLog).write("[bold cyan]> log clear[/bold cyan]")
        self._dispatch_command("log clear")

    def on_measurement_table_report_requested(self, event: MeasurementTable.ReportRequested) -> None:
        """Generate a test report."""
        event.stop()
        self._switch_tab("log-view")
        self.query_one("#log-output", RichLog).write("[bold cyan]> report save[/bold cyan]")
        self._dispatch_command("report save")

    def on_plot_panel_quick_action(self, event: PlotPanel.QuickAction) -> None:
        """Dispatch plot commands from the plot panel."""
        event.stop()
        self._switch_tab("log-view")
        self.query_one("#log-output", RichLog).write(f"[bold cyan]> {event.command}[/bold cyan]")
        self._dispatch_command(event.command)

    def on_instrument_detail_panel_save_state_requested(self, event: InstrumentDetailPanel.SaveStateRequested) -> None:
        """Save the instrument's current state."""
        event.stop()
        name = event.device_name
        if hasattr(self._dispatcher, "save_instrument_state"):
            snap = self._dispatcher.save_instrument_state(name)
            self._state_snapshots[name] = snap
            self._log_notification(f"State saved for {name}", severity="information")

    def on_instrument_detail_panel_restore_state_requested(
        self, event: InstrumentDetailPanel.RestoreStateRequested
    ) -> None:
        """Restore a previously saved instrument state."""
        event.stop()
        name = event.device_name
        snap = self._state_snapshots.get(name)
        if not snap:
            self._log_notification(f"No saved state for {name}", severity="warning")
            return
        if hasattr(self._dispatcher, "restore_instrument_state"):
            self._dispatcher.restore_instrument_state(name, snap)
            self._log_notification(f"State restored for {name}", severity="information")
            self._refresh_detail()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update contextual help tooltip as user types."""
        if event.input.id != "cmd_input":
            return
        tooltip = self.query_one(HelpTooltip)
        tooltip.text = get_hint(event.value)

    def on_script_browser_script_selected(self, event: ScriptBrowser.ScriptSelected) -> None:
        """Run a script when selected from the browser."""
        event.stop()
        self._switch_tab("log-view")
        cmd = f"run_script {event.script_name}"
        self.query_one("#log-output", RichLog).write(f"[bold cyan]> {cmd}[/bold cyan]")
        self._dispatch_command(cmd)

    def on_script_editor__load_script(self, event: ScriptEditor._LoadScript) -> None:
        """Load script content into the editor."""
        event.stop()
        if hasattr(self._dispatcher, "get_script_content"):
            content = self._dispatcher.get_script_content(event.name)
            self.query_one(ScriptEditor).load_content(event.name, content)

    def on_script_editor_save_requested(self, event: ScriptEditor.SaveRequested) -> None:
        """Save script content to disk."""
        event.stop()
        if hasattr(self._dispatcher, "save_script_content"):
            self._dispatcher.save_script_content(event.name, event.content)
            self._log_notification(f"Script '{event.name}' saved", severity="information")
            self._refresh_scripts()

    def on_script_editor_run_requested(self, event: ScriptEditor.RunRequested) -> None:
        """Run a script from the editor."""
        event.stop()
        self._switch_tab("log-view")
        cmd = f"run {event.name}"
        self.query_one("#log-output", RichLog).write(f"[bold cyan]> {cmd}[/bold cyan]")
        self._dispatch_command(cmd)

    def on_script_editor_delete_requested(self, event: ScriptEditor.DeleteRequested) -> None:
        """Delete a script."""
        event.stop()
        if hasattr(self._dispatcher, "delete_script"):
            self._dispatcher.delete_script(event.name)
            self._log_notification(f"Script '{event.name}' deleted", severity="warning")
            self._refresh_scripts()

    def on_monitor_panel_monitor_command(self, event: MonitorPanel.MonitorCommand) -> None:
        """Handle monitor tick -- dispatch read command and feed result back."""
        event.stop()

        @work(thread=True, exit_on_error=False, name="monitor-read")
        def _read(self_app: SCPIApp, cmd: str) -> None:
            import io

            with io.StringIO() as buf:
                import contextlib as _cl

                with _cl.redirect_stdout(buf):
                    self_app._dispatcher.handle_command(cmd)
                raw = buf.getvalue().strip()
            try:
                value = float(raw.split()[-1]) if raw else 0.0
            except (ValueError, IndexError):
                value = 0.0
            self_app.call_from_thread(self_app.query_one(MonitorPanel).add_reading, value)

        _read(self, event.command)

    def on_waveform_viewer_capture_requested(self, event: WaveformViewer.CaptureRequested) -> None:
        """Generate a waveform for display."""
        event.stop()
        import math

        # Generate a mock sine wave for demonstration
        data = [math.sin(2 * math.pi * i / 50) for i in range(200)]
        self.query_one(WaveformViewer).data = data
        self._log_notification("Waveform captured", severity="information")

    def on_scpi_console_raw_command(self, event: ScpiConsole.RawCommand) -> None:
        """Dispatch raw SCPI command and feed response to console."""
        event.stop()
        console = self.query_one(ScpiConsole)
        cmd = f"raw {event.command}"

        @work(thread=True, exit_on_error=False, name="scpi-raw")
        def _raw(self_app: SCPIApp, full_cmd: str) -> None:
            result = self_app._dispatcher.handle_command(full_cmd)
            self_app.call_from_thread(console.add_response, result.strip() if result else "(no response)")

        _raw(self, cmd)

    def _stream_line(self, raw: str) -> None:
        """Write a chunk of output to the RichLog (thread-safe via call_from_thread).

        If the raw text contains ANSI codes they are decoded by Rich.
        Plain-text lines matching common REPL patterns (errors, warnings,
        success) are wrapped in Rich markup so they stand out.
        """
        log = self.query_one("#log-output", RichLog)
        if "\033[" in raw:
            for line in _ANSI_DECODER.decode(raw):
                log.write(line)
            return

        stripped = raw.strip()
        if not stripped:
            return

        upper = stripped.upper()
        if any(
            upper.startswith(tag)
            for tag in ("ERROR", "[ERROR]", "SAFETY BLOCKED", "SAFETY ENFORCED", "SAFETY LIMIT EXCEEDED")
        ):
            log.write(f"[bold red]{stripped}[/bold red]")
        elif any(upper.startswith(tag) for tag in ("WARNING", "[WARNING]", "RETROACTIVE:")):
            log.write(f"[bold yellow]{stripped}[/bold yellow]")
        elif any(upper.startswith(tag) for tag in ("SUCCESS", "[SUCCESS]", "PASS")):
            log.write(f"[bold green]{stripped}[/bold green]")
        else:
            log.write(stripped)

    @work(thread=True, exit_on_error=False, name="dispatch")
    def _dispatch_command(self, cmd: str) -> str:
        """Execute command in background worker, streaming output live."""

        def _on_output(chunk: str) -> None:
            self.call_from_thread(self._stream_line, chunk)

        return self._dispatcher.handle_command(cmd, line_callback=_on_output)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion -- refresh panels or show errors."""
        if event.worker.name != "dispatch":
            return
        if event.state == WorkerState.RUNNING:
            self._running_count += 1
            self._update_input_state()
        elif event.state == WorkerState.SUCCESS:
            self._running_count = max(0, self._running_count - 1)
            self._update_input_state()
            self._refresh_measurements()
            self._refresh_vars()
        elif event.state in (WorkerState.ERROR, WorkerState.CANCELLED):
            self._running_count = max(0, self._running_count - 1)
            self._update_input_state()
            if event.state == WorkerState.ERROR:
                self._stream_line(f"\033[91m[ERROR] {event.worker.error}\033[0m\n")
                self._log_notification(str(event.worker.error), severity="error")

    def _update_input_state(self) -> None:
        """Update input placeholder and loading indicator based on worker state."""
        inp = self.query_one("#cmd_input", Input)
        if self._running_count > 0:
            inp.placeholder = "Running command..."
            inp.add_class("busy")
        else:
            inp.placeholder = "Enter command..."
            inp.remove_class("busy")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_clear_log(self) -> None:
        """Clear output log."""
        self.query_one("#log-output", RichLog).clear()

    def action_toggle_sidebar(self) -> None:
        """Toggle the device sidebar visibility."""
        sidebar = self.query_one(DeviceSidebar)
        sidebar.display = not sidebar.display

    def action_toggle_measurements(self) -> None:
        """Toggle between log view and measurement table."""
        self._toggle_tab("meas-view")

    def action_show_scripts(self) -> None:
        """Switch to script browser panel."""
        self._switch_tab("script-view")

    def action_show_vars(self) -> None:
        """Switch to variable inspector panel."""
        self._switch_tab("vars-view")

    def action_show_limits(self) -> None:
        """Toggle safety limits panel."""
        self._toggle_tab("limits-view")

    def action_show_plot(self) -> None:
        """Toggle plot panel."""
        self._toggle_tab("plot-view")

    def action_show_notifications(self) -> None:
        """Toggle notification center."""
        self._toggle_tab("notif-view")

    def action_retry_last(self) -> None:
        """Re-run the most recent command."""
        last = self._history.peek_last()
        if last is None:
            self._log_notification("No command to retry", severity="warning")
            return
        self._history.push(last)
        self._switch_tab("log-view")
        self.query_one("#log-output", RichLog).write(f"[bold cyan]> {last}[/bold cyan]")
        self._dispatch_command(last)

    def action_show_editor(self) -> None:
        """Toggle script editor."""
        self._toggle_tab("editor-view")

    def action_show_console(self) -> None:
        """Toggle raw SCPI console."""
        self._toggle_tab("scpi-view")

    def action_show_monitor(self) -> None:
        """Toggle live monitor panel."""
        self._toggle_tab("monitor-view")

    def action_show_waveform(self) -> None:
        """Toggle waveform viewer."""
        self._toggle_tab("wave-view")

    def action_connection_wizard(self) -> None:
        """Open the instrument connection wizard."""
        from .widgets.connection_wizard import ConnectionWizard

        def _on_dismiss(result: str | None) -> None:
            if result is None:
                return
            if result == "scan":
                self._switch_tab("log-view")
                self.query_one("#log-output", RichLog).write("[bold cyan]> scan[/bold cyan]")
                self._dispatch_command("scan")
            elif result.startswith("test:"):
                addr = result[5:]
                self._switch_tab("log-view")
                self.query_one("#log-output", RichLog).write(f"[bold cyan]> raw *IDN? @ {addr}[/bold cyan]")
                self._dispatch_command("raw *IDN?")

        self.push_screen(ConnectionWizard(), callback=_on_dismiss)

    def action_show_detail(self) -> None:
        """Switch to instrument detail panel."""
        self._toggle_tab("detail-view")

    def action_show_help(self) -> None:
        """Open the help overlay."""
        from .widgets.help_screen import HelpScreen

        self.push_screen(HelpScreen())

    def action_take_screenshot(self) -> None:
        """Save a screenshot of the TUI as SVG."""
        from pathlib import Path

        data_dir = self._get_data_dir()
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        stamp = _time.strftime("%Y%m%d_%H%M%S")
        fname = f"tui_screenshot_{stamp}.svg"
        result = self.save_screenshot(path=data_dir, filename=fname)
        self._log_notification(f"Screenshot saved: {result}", severity="information")

    def action_quit(self) -> None:
        """Exit app."""
        self.exit()


def main() -> None:
    """Entry point for the SCPI TUI application."""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        from lab_instruments.repl.shell import _REPL_VERSION

        print(
            f"scpi-instrument-toolkit v{_REPL_VERSION}\n"
            "\n"
            "Usage: scpi-tui [--mock] [--version] [--help]\n"
            "\n"
            "Options:\n"
            "  --mock     Run with simulated instruments (no hardware required)\n"
            "  --version  Print version and exit\n"
            "  --help     Show this help and exit\n"
        )
        sys.exit(0)

    if "--version" in args or "-V" in args:
        from lab_instruments.repl.shell import _REPL_VERSION

        print(f"scpi-instrument-toolkit v{_REPL_VERSION}")
        sys.exit(0)

    mock = "--mock" in args
    SCPIApp(LocalDispatcher(mock=mock)).run()


if __name__ == "__main__":
    main()
