"""Connection wizard - modal screen for connecting to instruments."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RadioButton, RadioSet, Static


class ConnectionWizard(ModalScreen[str | None]):
    """Modal dialog that walks through connecting to an instrument.

    Dismisses with:
    - ``"scan"`` to trigger a full instrument scan
    - ``"test:<resource_string>"`` to test a specific connection
    - ``None`` on cancel
    """

    BINDINGS = [("escape", "dismiss_wizard", "Cancel")]

    DEFAULT_CSS = """
    ConnectionWizard {
        align: center middle;
    }
    #wizard-dialog {
        width: 60;
        height: auto;
        max-height: 80%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #wizard-dialog Label {
        margin: 0 0 1 0;
    }
    #wizard-dialog RadioSet {
        height: auto;
        margin: 0 0 1 0;
    }
    #wizard-dialog Input {
        margin: 0 0 1 0;
    }
    #wizard-dialog Button {
        margin: 0 1 0 0;
    }
    .wizard-buttons {
        height: auto;
        layout: horizontal;
        padding: 1 0 0 0;
    }
    #wizard-status {
        height: auto;
        padding: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="wizard-dialog"):
            yield Label("[bold]Connect to Instrument[/bold]")
            yield Label("Interface:")
            with RadioSet(id="wizard-interface"):
                yield RadioButton("TCPIP", value=True)
                yield RadioButton("USB")
                yield RadioButton("GPIB")
                yield RadioButton("Serial")
            yield Label("Resource string:")
            yield Input(
                placeholder="TCPIP0::192.168.1.100::INSTR",
                id="wizard-address",
            )
            yield Static("", id="wizard-status")
            with Vertical(classes="wizard-buttons"):
                yield Button("Test Connection", id="wizard-test", variant="primary")
                yield Button("Scan All", id="wizard-scan", variant="success")
                yield Button("Cancel", id="wizard-cancel", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wizard-test":
            event.stop()
            addr = self.query_one("#wizard-address", Input).value.strip()
            if addr:
                self.query_one("#wizard-status", Static).update("[yellow]Testing...[/yellow]")
                self.dismiss(f"test:{addr}")
            else:
                self.query_one("#wizard-status", Static).update("[red]Enter a resource string[/red]")
        elif event.button.id == "wizard-scan":
            event.stop()
            self.dismiss("scan")
        elif event.button.id == "wizard-cancel":
            event.stop()
            self.dismiss(None)

    def action_dismiss_wizard(self) -> None:
        self.dismiss(None)
