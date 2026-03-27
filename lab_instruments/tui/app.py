"""SCPI Instrument Toolkit - Textual TUI application."""

import sys
from typing import Optional

from rich.ansi import AnsiDecoder
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.events import Key
from textual.widgets import Footer, Header, Input, RichLog
from textual.worker import Worker, WorkerState

from .completer import ReplSuggester
from .dispatcher import CommandDispatcher, LocalDispatcher
from .history import CommandHistory

# ANSI decoder for color escape sequences from command output
_ANSI_DECODER = AnsiDecoder()


class SCPIApp(App):
    """Textual app for SCPI command entry and output display."""

    TITLE = "SCPI Instrument Toolkit"
    SUB_TITLE = "lab_instruments"

    # keyboard shortcuts shown in footer
    BINDINGS = [
        Binding("ctrl+l", "clear_log", "Clear", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    # layout CSS for Textual widgets
    DEFAULT_CSS = """
    RichLog {
        height: 1fr;
        border: solid $primary-darken-2;
        padding: 0 1;
    }
    Input {
        dock: bottom;
    }
    """

    def __init__(self, dispatcher: Optional[CommandDispatcher] = None) -> None:
        """Initialize the app and dispatcher."""
        super().__init__()
        self._dispatcher: CommandDispatcher = dispatcher if dispatcher is not None else LocalDispatcher()
        self._history: CommandHistory = CommandHistory()

    def compose(self) -> ComposeResult:
        """Build widget tree."""
        yield Header()
        yield RichLog(id="output", wrap=True, auto_scroll=True, markup=True)
        yield Input(placeholder="Enter command...", id="cmd_input", suggester=ReplSuggester(self._dispatcher))
        yield Footer()

    def on_mount(self) -> None:
        """Focus input on startup."""
        self.query_one("#cmd_input", Input).focus()

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
        self.query_one("#output", RichLog).write(f"[bold cyan]> {cmd}[/bold cyan]")
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
        elif event.state == WorkerState.ERROR:
            self._write_output(f"\033[91m[ERROR] {event.worker.error}\033[0m\n")

    def _write_output(self, raw: str) -> None:
        """Decode ANSI output and append to log."""
        log = self.query_one("#output", RichLog)
        for line in _ANSI_DECODER.decode(raw):
            log.write(line)

    def action_clear_log(self) -> None:
        """Clear output log."""
        self.query_one("#output", RichLog).clear()

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
