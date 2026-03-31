"""Safety limits panel - displays all configured safety limits in a table with inline editing."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Label

# Human-readable names for limit parameter keys
_PARAM_LABELS = {
    "voltage_upper": "Voltage max",
    "voltage_lower": "Voltage min",
    "current_upper": "Current max",
    "current_lower": "Current min",
    "vpp_upper": "Vpp max",
    "vpp_lower": "Vpp min",
    "vpeak_upper": "Peak max",
    "vpeak_lower": "Peak min",
    "vtrough_upper": "Trough max",
    "vtrough_lower": "Trough min",
    "freq_upper": "Freq max",
    "freq_lower": "Freq min",
}

_PARAM_UNITS = {
    "voltage_upper": "V",
    "voltage_lower": "V",
    "current_upper": "A",
    "current_lower": "A",
    "vpp_upper": "V",
    "vpp_lower": "V",
    "vpeak_upper": "V",
    "vpeak_lower": "V",
    "vtrough_upper": "V",
    "vtrough_lower": "V",
    "freq_upper": "Hz",
    "freq_lower": "Hz",
}


class SafetyLimitsPanel(Widget):
    """Displays all configured safety limits in a DataTable with an
    inline form to add new limits.

    The ``limits`` reactive receives a list of dicts from the dispatcher,
    each with keys: device, channel, parameter, value.
    """

    DEFAULT_CSS = """
    SafetyLimitsPanel {
        height: 1fr;
        padding: 0 1;
    }
    SafetyLimitsPanel .panel-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    SafetyLimitsPanel DataTable {
        height: 1fr;
    }
    SafetyLimitsPanel .no-limits {
        color: $text-muted;
        padding: 1 0;
    }
    SafetyLimitsPanel .add-limit-row {
        height: auto;
        padding: 1 0 0 0;
        layout: horizontal;
    }
    SafetyLimitsPanel .add-limit-row Input {
        width: 1fr;
        margin: 0 1 0 0;
        dock: none;
    }
    SafetyLimitsPanel .add-limit-row Button {
        min-width: 10;
        dock: none;
    }
    SafetyLimitsPanel .add-limit-row Label {
        width: auto;
        margin: 0 1 0 0;
    }
    """

    class SetLimitRequested(Message):
        """Posted when the user submits a new limit via the form."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    limits: reactive[list[dict]] = reactive(list, layout=True)

    def compose(self) -> ComposeResult:
        yield Label("Safety Limits", classes="panel-title")
        yield DataTable(id="limits-table", zebra_stripes=True)
        yield Label("Add Limit:", classes="panel-title")
        with Horizontal(classes="add-limit-row"):
            yield Input(placeholder="Device (e.g. psu1)", id="new-lim-device")
            yield Input(placeholder="Channel (or blank)", id="new-lim-chan")
            yield Input(placeholder="Param (voltage, current, vpp, freq)", id="new-lim-param")
            yield Input(placeholder="Value", id="new-lim-value")
        with Horizontal(classes="add-limit-row"):
            yield Button("Set Upper", id="add-upper-limit", variant="warning")
            yield Button("Set Lower", id="add-lower-limit", variant="primary")

    def on_mount(self) -> None:
        table = self.query_one("#limits-table", DataTable)
        table.add_columns("Device", "Channel", "Parameter", "Value")

    def watch_limits(self, limits: list[dict]) -> None:
        """Rebuild the DataTable whenever the limits list changes."""
        table = self.query_one("#limits-table", DataTable)
        table.clear()

        if not limits:
            table.add_row("--", "--", "No limits configured", "--")
            return

        for entry in sorted(limits, key=lambda e: (e.get("device", ""), e.get("parameter", ""))):
            device = entry.get("device", "?")
            channel = entry.get("channel")
            ch_str = f"CH{channel}" if channel is not None else "All"
            param_key = entry.get("parameter", "?")
            param_label = _PARAM_LABELS.get(param_key, param_key)
            value = entry.get("value", 0.0)
            unit = _PARAM_UNITS.get(param_key, "")
            table.add_row(device, ch_str, param_label, f"{value:g} {unit}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Set Upper / Set Lower button presses."""
        bid = event.button.id or ""
        if bid not in ("add-upper-limit", "add-lower-limit"):
            return
        event.stop()

        device = self.query_one("#new-lim-device", Input).value.strip()
        chan = self.query_one("#new-lim-chan", Input).value.strip()
        param = self.query_one("#new-lim-param", Input).value.strip()
        value = self.query_one("#new-lim-value", Input).value.strip()

        if not device or not param or not value:
            return

        direction = "upper_limit" if bid == "add-upper-limit" else "lower_limit"
        chan_part = f" chan {chan}" if chan else ""
        cmd = f"{direction} {device}{chan_part} {param} {value}"
        self.post_message(self.SetLimitRequested(cmd))
