"""Measurement table widget with CSV export."""

from __future__ import annotations

import csv
import time
from collections.abc import Callable
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Label


class MeasurementTable(Widget):
    """Scrollable DataTable showing MeasurementStore entries with CSV export.

    data_dir_getter is a callable that returns the directory path for CSV
    exports. Injecting it makes the widget testable without touching env vars.
    """

    DEFAULT_CSS = """
    MeasurementTable {
        height: 1fr;
        padding: 0 1;
    }
    MeasurementTable #meas-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    MeasurementTable DataTable {
        height: 1fr;
    }
    MeasurementTable .meas-actions {
        dock: bottom;
        height: auto;
        layout: horizontal;
        padding: 1 0 0 0;
    }
    MeasurementTable .meas-actions Button {
        margin: 0 1 0 0;
        min-width: 12;
    }
    MeasurementTable #annotate-input {
        dock: bottom;
        margin: 0 0 0 0;
    }
    """

    class ClearRequested(Message):
        """Posted when the user clicks Clear All."""

    class ReportRequested(Message):
        """Posted when the user clicks Generate Report."""

    measurements: reactive[list[dict]] = reactive(list, layout=True)

    def __init__(
        self,
        data_dir_getter: Callable[[], str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._data_dir_getter = data_dir_getter
        self._annotations: dict[int, str] = {}

    def compose(self) -> ComposeResult:
        yield Label("Measurements", id="meas-title")
        yield DataTable(id="meas-table", zebra_stripes=True, cursor_type="row")
        yield Input(placeholder="Select row, type note, press Enter", id="annotate-input")
        with Horizontal(classes="meas-actions"):
            yield Button("Export CSV", id="export-csv", variant="primary")
            yield Button("Clear All", id="clear-all", variant="error")
            yield Button("Report", id="gen-report", variant="warning")

    def on_mount(self) -> None:
        table = self.query_one("#meas-table", DataTable)
        table.add_columns("#", "Label", "Value", "Unit", "Source", "Notes")

    def watch_measurements(self, measurements: list[dict]) -> None:
        """Repopulate table rows whenever the snapshot changes."""
        table = self.query_one("#meas-table", DataTable)
        table.clear()
        for i, entry in enumerate(measurements, start=1):
            table.add_row(
                str(i),
                str(entry.get("label", "")),
                str(entry.get("value", "")),
                str(entry.get("unit", "")),
                str(entry.get("source", "")),
                self._annotations.get(i, ""),
                key=str(i),
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "annotate-input":
            return
        note = event.value.strip()
        if not note:
            return
        event.input.clear()
        table = self.query_one("#meas-table", DataTable)
        if table.cursor_row is not None and table.row_count > 0:
            row_idx = table.cursor_row + 1  # 1-based to match display
            self._annotations[row_idx] = note
            self.watch_measurements(self.measurements)  # rebuild table
            self.notify(f"Note added to row {row_idx}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "export-csv":
            event.stop()
            self._export_csv()
        elif event.button.id == "clear-all":
            self.post_message(self.ClearRequested())
        elif event.button.id == "gen-report":
            self.post_message(self.ReportRequested())

    def _export_csv(self) -> None:
        """Write current measurements to a timestamped CSV file."""
        if not self.measurements:
            self.notify("No measurements to export.", severity="warning")
            return

        dest_dir = Path(self._data_dir_getter()) if self._data_dir_getter else Path.home()
        dest_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        path = dest_dir / f"measurements_{stamp}.csv"

        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["label", "value", "unit", "source", "notes"])
            writer.writeheader()
            for i, entry in enumerate(self.measurements, start=1):
                row = dict(entry)
                row["notes"] = self._annotations.get(i, "")
                writer.writerow(row)

        self.notify(f"Exported {len(self.measurements)} rows to {path.name}")
