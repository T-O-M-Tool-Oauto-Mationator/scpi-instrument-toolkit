"""Measurement table widget with CSV export."""

from __future__ import annotations

import csv
import time
from collections.abc import Callable
from pathlib import Path

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, DataTable, Label


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
    MeasurementTable #export-csv {
        dock: bottom;
        margin: 1 0 0 0;
        width: auto;
    }
    """

    measurements: reactive[list[dict]] = reactive(list, layout=True)

    def __init__(
        self,
        data_dir_getter: Callable[[], str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._data_dir_getter = data_dir_getter

    def compose(self) -> ComposeResult:
        yield Label("Measurements", id="meas-title")
        yield DataTable(id="meas-table", zebra_stripes=True)
        yield Button("Export CSV", id="export-csv", variant="primary")

    def on_mount(self) -> None:
        table = self.query_one("#meas-table", DataTable)
        table.add_columns("#", "Label", "Value", "Unit", "Source")

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
                key=str(i),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "export-csv":
            self._export_csv()

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
            writer = csv.DictWriter(fh, fieldnames=["label", "value", "unit", "source"])
            writer.writeheader()
            writer.writerows(self.measurements)

        self.notify(f"Exported {len(self.measurements)} rows to {path.name}")
