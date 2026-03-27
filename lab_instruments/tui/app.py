"""SCPI Instrument Toolkit - Textual TUI application."""

import sys
from typing import Optional

from rich.ansi import AnsiDecoder
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import ContentSwitcher, Footer, Header, Input, RichLog
from textual.worker import Worker, WorkerState

from .command_provider import SCPICommandProvider
from .completer import ReplSuggester
from .dispatcher import CommandDispatcher, LocalDispatcher
from .history import CommandHistory
from .widgets import DeviceSidebar, MeasurementTable, SafetyBar, ScriptBrowser, VarInspector

# ANSI decoder for color escape sequences from command output
_ANSI_DECODER = AnsiDecoder()


class SCPIApp(App):
    """Textual app for SCPI command entry and output display."""

    TITLE = "SCPI Instrument Toolkit"
    SUB_TITLE = "lab_instruments"

    COMMANDS = App.COMMANDS | {SCPICommandProvider}

    BINDINGS = [
        Binding("ctrl+l", "clear_log", "Clear", show=True),
        Binding("ctrl+d", "toggle_sidebar", "Devices", show=True),
        Binding("ctrl+m", "toggle_measurements", "Meas", show=True),
        Binding("ctrl+r", "show_scripts", "Scripts", show=True),
        Binding("ctrl+v", "show_vars", "Vars", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    DEFAULT_CSS = """
    #main-row {
        height: 1fr;
    }
    DeviceSidebar {
        width: 22;
        border-right: solid $primary-darken-2;
    }
    #log-area {
        height: 1fr;
    }
    ContentSwitcher {
        height: 1fr;
    }
    RichLog {
        height: 1fr;
        border: solid $primary-darken-2;
        padding: 0 1;
    }
    MeasurementTable {
        height: 1fr;
        border: solid $primary-darken-2;
    }
    ScriptBrowser {
        height: 1fr;
        border: solid $primary-darken-2;
    }
    VarInspector {
        height: 1fr;
        border: solid $primary-darken-2;
    }
    Input {
        dock: bottom;
    }
    SafetyBar {
        dock: bottom;
    }
    """

    def __init__(
        self,
        dispatcher: Optional[CommandDispatcher] = None,
        device_poll_interval: float = 2.0,
        meas_poll_interval: float = 5.0,
        script_poll_interval: float = 2.0,
        safety_poll_interval: float = 1.0,
    ) -> None:
        super().__init__()
        self._dispatcher: CommandDispatcher = dispatcher if dispatcher is not None else LocalDispatcher()
        self._history: CommandHistory = CommandHistory()
        self._device_poll_interval: float = device_poll_interval
        self._meas_poll_interval: float = meas_poll_interval
        self._script_poll_interval: float = script_poll_interval
        self._safety_poll_interval: float = safety_poll_interval

    def compose(self) -> ComposeResult:
        """Build widget tree."""
        yield Header()
        with Horizontal(id="main-row"):
            yield DeviceSidebar(id="device-sidebar")
            with Vertical(id="log-area"):  # noqa: SIM117
                with ContentSwitcher(initial="log-view", id="main-content"):
                    yield RichLog(id="log-view", wrap=True, auto_scroll=True, markup=True)
                    yield MeasurementTable(
                        id="meas-view",
                        data_dir_getter=self._get_data_dir,
                    )
                    yield ScriptBrowser(id="script-view")
                    yield VarInspector(id="vars-view")
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
        self.query_one(MeasurementTable).measurements = self._dispatcher.get_measurement_snapshot()

    def _refresh_scripts(self) -> None:
        if not hasattr(self._dispatcher, "get_script_names"):
            return
        self.query_one(ScriptBrowser).scripts = self._dispatcher.get_script_names()

    def _refresh_vars(self) -> None:
        if not hasattr(self._dispatcher, "get_vars_snapshot"):
            return
        self.query_one(VarInspector).variables = self._dispatcher.get_vars_snapshot()

    def _refresh_safety(self) -> None:
        if not hasattr(self._dispatcher, "get_safety_snapshot"):
            return
        self.query_one(SafetyBar).safety_info = self._dispatcher.get_safety_snapshot()

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
        # Always switch to log-view when a command is submitted
        self.query_one("#main-content", ContentSwitcher).current = "log-view"
        self.query_one("#log-view", RichLog).write(f"[bold cyan]> {cmd}[/bold cyan]")
        self._dispatch_command(cmd)

    def on_script_browser_script_selected(self, event: ScriptBrowser.ScriptSelected) -> None:
        """Run a script when selected from the browser."""
        event.stop()
        self.query_one("#main-content", ContentSwitcher).current = "log-view"
        cmd = f"run_script {event.script_name}"
        self.query_one("#log-view", RichLog).write(f"[bold cyan]> {cmd}[/bold cyan]")
        self._dispatch_command(cmd)

    @work(thread=True, exit_on_error=False, name="dispatch")
    def _dispatch_command(self, cmd: str) -> str:
        """Execute command in background worker."""
        return self._dispatcher.handle_command(cmd)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Get called when worker finishes or errors."""
        if event.worker.name != "dispatch":
            return
        if event.state == WorkerState.SUCCESS:
            self._write_output(event.worker.result or "")
            self._refresh_measurements()
            self._refresh_vars()
        elif event.state == WorkerState.ERROR:
            self._write_output(f"\033[91m[ERROR] {event.worker.error}\033[0m\n")

    def _write_output(self, raw: str) -> None:
        """Decode ANSI output and append to log."""
        log = self.query_one("#log-view", RichLog)
        for line in _ANSI_DECODER.decode(raw):
            log.write(line)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_clear_log(self) -> None:
        """Clear output log."""
        self.query_one("#log-view", RichLog).clear()

    def action_toggle_sidebar(self) -> None:
        """Toggle the device sidebar visibility."""
        sidebar = self.query_one(DeviceSidebar)
        sidebar.display = not sidebar.display

    def action_toggle_measurements(self) -> None:
        """Toggle between log view and measurement table."""
        switcher = self.query_one("#main-content", ContentSwitcher)
        switcher.current = "meas-view" if switcher.current != "meas-view" else "log-view"

    def action_show_scripts(self) -> None:
        """Switch to script browser panel."""
        self.query_one("#main-content", ContentSwitcher).current = "script-view"

    def action_show_vars(self) -> None:
        """Switch to variable inspector panel."""
        self.query_one("#main-content", ContentSwitcher).current = "vars-view"

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
