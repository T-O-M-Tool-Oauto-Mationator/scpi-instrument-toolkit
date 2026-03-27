"""SCPI Instrument Toolkit - Textual TUI application."""

from typing import Optional

from rich.ansi import AnsiDecoder
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Input, RichLog
from textual.worker import Worker, WorkerState

from .dispatcher import CommandDispatcher, LocalDispatcher

_ANSI_DECODER = AnsiDecoder()


class SCPIApp(App):
    TITLE = "SCPI Instrument Toolkit"
    SUB_TITLE = "lab_instruments"

    BINDINGS = [
        Binding("ctrl+l", "clear_log", "Clear", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

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
        super().__init__()
        self._dispatcher: CommandDispatcher = dispatcher if dispatcher is not None else LocalDispatcher()

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="output", wrap=True, auto_scroll=True, markup=True)
        yield Input(placeholder="Enter command...", id="cmd_input")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#cmd_input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if not cmd:
            return
        event.input.clear()
        self.query_one("#output", RichLog).write(f"[bold cyan]> {cmd}[/bold cyan]")
        self._dispatch_command(cmd)

    @work(thread=True, exit_on_error=False, name="dispatch")
    def _dispatch_command(self, cmd: str) -> str:
        """Run cmd on a thread pool - never blocks the Textual event loop."""
        return self._dispatcher.handle_command(cmd)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != "dispatch":
            return
        if event.state == WorkerState.SUCCESS:
            self._write_output(event.worker.result or "")
        elif event.state == WorkerState.ERROR:
            self._write_output(f"\033[91m[ERROR] {event.worker.error}\033[0m\n")

    def _write_output(self, raw: str) -> None:
        """Decode ANSI escape codes and write rich.Text lines to RichLog."""
        log = self.query_one("#output", RichLog)
        for line in _ANSI_DECODER.decode(raw):
            log.write(line)

    def action_clear_log(self) -> None:
        self.query_one("#output", RichLog).clear()

    def action_quit(self) -> None:
        self.exit()


def main() -> None:
    """Entry point for the SCPI TUI application."""
    SCPIApp().run()


if __name__ == "__main__":
    main()
