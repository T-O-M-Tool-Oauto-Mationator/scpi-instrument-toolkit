"""Safety limits panel - displays all configured safety limits in a table."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Label

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
    """Displays all configured safety limits in a DataTable.

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
    """

    limits: reactive[list[dict]] = reactive(list, layout=True)

    def compose(self) -> ComposeResult:
        yield Label("Safety Limits", classes="panel-title")
        yield DataTable(id="limits-table", zebra_stripes=True)

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
