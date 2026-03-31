"""Plot panel - preview and launch matplotlib plots of measurements."""

from __future__ import annotations

import fnmatch

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Label, Static


class PlotPanel(Widget):
    """Displays measurement preview and provides buttons to plot or save.

    The ``measurements`` reactive receives the full snapshot from the
    dispatcher. A filter input lets users narrow by glob pattern.
    Buttons post ``QuickAction`` messages that the app dispatches as
    REPL plot commands.
    """

    DEFAULT_CSS = """
    PlotPanel {
        height: 1fr;
        padding: 0 1;
    }
    PlotPanel .panel-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    PlotPanel #plot-filter {
        height: 3;
        margin: 0 0 1 0;
    }
    PlotPanel #plot-summary {
        height: auto;
        padding: 0 0 1 0;
        color: $text-muted;
    }
    PlotPanel DataTable {
        height: 1fr;
    }
    PlotPanel .plot-actions {
        height: auto;
        padding: 1 0 0 0;
        layout: horizontal;
    }
    PlotPanel .plot-actions Button {
        margin: 0 1 0 0;
        min-width: 14;
    }
    """

    class QuickAction(Message):
        """Posted when the user clicks a plot action button."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    measurements: reactive[list[dict]] = reactive(list, layout=True)

    def compose(self) -> ComposeResult:
        yield Label("Plot", classes="panel-title")
        yield Input(placeholder="Filter pattern (e.g. linereg_*)", id="plot-filter")
        yield Static("", id="plot-summary")
        yield DataTable(id="plot-table", zebra_stripes=True)
        with Horizontal(classes="plot-actions"):
            yield Button("Plot All", id="plot-all", variant="primary")
            yield Button("Plot Filtered", id="plot-filtered", variant="success")
            yield Button("Save PNG", id="plot-save", variant="warning")

    def on_mount(self) -> None:
        table = self.query_one("#plot-table", DataTable)
        table.add_columns("#", "Label", "Value", "Unit")

    def watch_measurements(self, measurements: list[dict]) -> None:
        """Rebuild the preview table when measurements change."""
        self._update_preview()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "plot-filter":
            self._update_preview()

    def _get_filter(self) -> str:
        return self.query_one("#plot-filter", Input).value.strip()

    def _filtered(self) -> list[dict]:
        pattern = self._get_filter()
        if not pattern:
            return list(self.measurements)
        return [e for e in self.measurements if fnmatch.fnmatch(e.get("label", ""), pattern)]

    def _update_preview(self) -> None:
        matched = self._filtered()
        table = self.query_one("#plot-table", DataTable)
        table.clear()
        for i, entry in enumerate(matched, start=1):
            table.add_row(
                str(i),
                str(entry.get("label", "")),
                str(entry.get("value", "")),
                str(entry.get("unit", "")),
            )

        # Summary line
        units: dict[str, int] = {}
        for e in matched:
            u = e.get("unit", "") or ""
            units[u] = units.get(u, 0) + 1
        if matched:
            parts = [f"{u or 'no unit'}: {c}" for u, c in sorted(units.items())]
            summary = f"Matched: {len(matched)} measurements  ({', '.join(parts)})"
        else:
            summary = "No measurements to plot"
        self.query_one("#plot-summary", Static).update(summary)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "plot-all":
            self.post_message(self.QuickAction("plot"))
        elif bid == "plot-filtered":
            pattern = self._get_filter()
            cmd = f"plot {pattern}" if pattern else "plot"
            self.post_message(self.QuickAction(cmd))
        elif bid == "plot-save":
            import time

            stamp = time.strftime("%Y%m%d_%H%M%S")
            fname = f"measurements_{stamp}.png"
            pattern = self._get_filter()
            cmd = f"plot {pattern} --save {fname}" if pattern else f"plot --save {fname}"
            self.post_message(self.QuickAction(cmd))
