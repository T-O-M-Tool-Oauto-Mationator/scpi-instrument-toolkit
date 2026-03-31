"""Raw SCPI console - dedicated input/output for raw SCPI commands."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Label, RichLog


class ScpiConsole(Widget):
    """Dedicated panel for sending raw SCPI commands with a response log.

    Posts ``RawCommand`` when the user submits a command.  The app
    dispatches it and feeds the response back via ``add_response``.
    """

    DEFAULT_CSS = """
    ScpiConsole {
        height: 1fr;
        padding: 0 1;
    }
    ScpiConsole .panel-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    ScpiConsole RichLog {
        height: 1fr;
    }
    ScpiConsole #scpi-clear {
        dock: bottom;
        width: auto;
        margin: 1 0 0 0;
    }
    ScpiConsole #scpi-input {
        dock: bottom;
    }
    """

    class RawCommand(Message):
        """Posted when the user submits a raw SCPI command."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    def compose(self) -> ComposeResult:
        yield Label("Raw SCPI Console", classes="panel-title")
        yield RichLog(id="scpi-log", wrap=True, auto_scroll=True, markup=True)
        yield Button("Clear", id="scpi-clear", variant="error")
        yield Input(placeholder="Enter SCPI command (e.g. *IDN?)", id="scpi-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "scpi-input":
            return
        cmd = event.value.strip()
        if not cmd:
            return
        event.input.clear()
        self.query_one("#scpi-log", RichLog).write(f"[bold cyan]> {cmd}[/bold cyan]")
        self.post_message(self.RawCommand(cmd))

    def add_response(self, response: str) -> None:
        """Write a response line to the SCPI log."""
        self.query_one("#scpi-log", RichLog).write(response)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "scpi-clear":
            event.stop()
            self.query_one("#scpi-log", RichLog).clear()
