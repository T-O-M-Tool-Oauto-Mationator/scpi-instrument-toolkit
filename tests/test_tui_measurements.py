"""Tests for MeasurementTable widget and app integration - CP4."""

from __future__ import annotations

import asyncio
import csv

from textual.widgets import ContentSwitcher, DataTable

from lab_instruments.tui.widgets.measurement_table import MeasurementTable

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _entry(label: str, value, unit: str = "V", source: str = "psu1") -> dict:
    return {"label": label, "value": value, "unit": unit, "source": source}


class _StubDispatcher:
    def __init__(self, measurements: list[dict] | None = None, devices: list[dict] | None = None):
        self._commands: list[str] = []
        self._measurements: list[dict] = measurements or []
        self._devices: list[dict] = devices or []
        self._completions: dict[str, list[str]] = {}

    def handle_command(self, cmd: str, line_callback=None) -> str:
        self._commands.append(cmd)
        return f"OK: {cmd}"

    def get_completions(self, text: str) -> list[str]:
        return list(self._completions.get(text, []))

    def get_device_snapshot(self) -> list[dict]:
        return list(self._devices)

    def get_measurement_snapshot(self) -> list[dict]:
        return [dict(e) for e in self._measurements]


# ---------------------------------------------------------------------------
# MeasurementTable widget tests (standalone)
# ---------------------------------------------------------------------------


class TestMeasurementTableWidget:
    def _wrap_app(self, getter=None):
        from textual.app import App, ComposeResult

        class WrapApp(App):
            def compose(self) -> ComposeResult:
                yield MeasurementTable(id="mt", data_dir_getter=getter)

        return WrapApp()

    def test_columns_present_after_mount(self):
        """DataTable should have the expected columns after mount."""

        async def inner():
            wa = self._wrap_app()
            async with wa.run_test(size=(80, 24)):
                table = wa.query_one("#meas-table", DataTable)
                col_labels = [str(c.label) for c in table.columns.values()]
                for expected in ("#", "Label", "Value", "Unit", "Source"):
                    assert expected in col_labels

        asyncio.run(inner())

    def test_rows_populated_from_measurements(self):
        """Setting measurements should add matching rows to DataTable."""

        async def inner():
            wa = self._wrap_app()
            async with wa.run_test(size=(80, 24)) as pilot:
                mt = wa.query_one("#mt", MeasurementTable)
                mt.measurements = [
                    _entry("Vout", 5.01),
                    _entry("Iout", 0.1, unit="A"),
                    _entry("Temp", 25.3, unit="degrees C"),
                ]
                await pilot.pause(0.1)
                table = wa.query_one("#meas-table", DataTable)
                assert table.row_count == 3

        asyncio.run(inner())

    def test_watch_clears_and_repopulates(self):
        """Setting measurements twice should show only the second set."""

        async def inner():
            wa = self._wrap_app()
            async with wa.run_test(size=(80, 24)) as pilot:
                mt = wa.query_one("#mt", MeasurementTable)
                mt.measurements = [_entry("Vout", 5.0)]
                await pilot.pause(0.1)
                mt.measurements = [_entry("A", 1.0), _entry("B", 2.0)]
                await pilot.pause(0.1)
                table = wa.query_one("#meas-table", DataTable)
                assert table.row_count == 2

        asyncio.run(inner())

    def test_export_csv_writes_file(self, tmp_path):
        """Export button should write a CSV file to the data_dir_getter path."""

        async def inner():
            wa = self._wrap_app(getter=lambda: str(tmp_path))
            async with wa.run_test(size=(80, 24)) as pilot:
                mt = wa.query_one("#mt", MeasurementTable)
                entries = [_entry("Vout", 5.01), _entry("Iout", 0.1, unit="A")]
                mt.measurements = entries
                await pilot.pause(0.1)
                await pilot.click("#export-csv")
                await pilot.pause(0.2)

            csv_files = list(tmp_path.glob("measurements_*.csv"))
            assert len(csv_files) == 1

        asyncio.run(inner())

    def test_export_csv_headers_and_rows(self, tmp_path):
        """Exported CSV must have correct headers and data rows."""

        async def inner():
            wa = self._wrap_app(getter=lambda: str(tmp_path))
            async with wa.run_test(size=(80, 24)) as pilot:
                mt = wa.query_one("#mt", MeasurementTable)
                mt.measurements = [_entry("Vout", 5.01), _entry("Iout", 0.1, unit="A")]
                await pilot.pause(0.1)
                await pilot.click("#export-csv")
                await pilot.pause(0.2)

            csv_files = list(tmp_path.glob("measurements_*.csv"))
            with csv_files[0].open(newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            assert len(rows) == 2
            assert set(rows[0].keys()) == {"label", "value", "unit", "source"}
            assert rows[0]["label"] == "Vout"
            assert rows[1]["unit"] == "A"

        asyncio.run(inner())

    def test_export_csv_empty_shows_warning(self):
        """Exporting with no measurements should not write a file."""

        async def inner():
            notifications: list[str] = []

            from textual.app import App, ComposeResult

            class WrapApp(App):
                def compose(self) -> ComposeResult:
                    yield MeasurementTable(id="mt")

                def notify(self, message, **kwargs):
                    notifications.append(message)
                    return super().notify(message, **kwargs)

            wa = WrapApp()
            async with wa.run_test(size=(80, 24)) as pilot:
                mt = wa.query_one("#mt", MeasurementTable)
                mt.measurements = []
                await pilot.pause(0.05)
                await pilot.click("#export-csv")
                await pilot.pause(0.1)

            assert any("No measurements" in n for n in notifications)

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# App-level integration tests
# ---------------------------------------------------------------------------


class TestMeasurementTableInApp:
    def _make_app(self, measurements=None, poll_interval=60.0):
        from lab_instruments.tui.app import SCPIApp

        stub = _StubDispatcher(measurements=measurements)
        app = SCPIApp(stub, meas_poll_interval=poll_interval)
        return app, stub

    def test_switcher_starts_on_log_view(self):
        """ContentSwitcher should default to log-view."""

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)):
                sw = app.query_one("#main-content", ContentSwitcher)
                assert sw.current == "log-view"

        asyncio.run(inner())

    def test_toggle_measurements_switches_to_meas_view(self):
        """action_toggle_measurements should switch to meas-view."""

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                await app.run_action("toggle_measurements")
                await pilot.pause(0.05)
                sw = app.query_one("#main-content", ContentSwitcher)
                assert sw.current == "meas-view"

        asyncio.run(inner())

    def test_toggle_measurements_twice_returns_to_log_view(self):
        """Two toggles should return to log-view."""

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                await app.run_action("toggle_measurements")
                await pilot.pause(0.05)
                await app.run_action("toggle_measurements")
                await pilot.pause(0.05)
                sw = app.query_one("#main-content", ContentSwitcher)
                assert sw.current == "log-view"

        asyncio.run(inner())

    def test_refresh_measurements_updates_table(self):
        """_refresh_measurements should push snapshot to MeasurementTable."""

        async def inner():
            entries = [_entry("Vout", 5.0), _entry("Iout", 0.1, unit="A")]
            app, _ = self._make_app(measurements=entries)
            async with app.run_test(size=(80, 24)) as pilot:
                app._refresh_measurements()
                await pilot.pause(0.1)
                mt = app.query_one(MeasurementTable)
                assert len(mt.measurements) == 2

        asyncio.run(inner())

    def test_submitting_command_switches_to_log_view(self):
        """Entering a command while on meas-view should switch back to log-view."""

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                await app.run_action("toggle_measurements")
                await pilot.pause(0.05)
                await pilot.click("#cmd_input")
                for ch in "scan":
                    await pilot.press(ch)
                await pilot.press("enter")
                await pilot.pause(0.1)
                sw = app.query_one("#main-content", ContentSwitcher)
                assert sw.current == "log-view"

        asyncio.run(inner())

    def test_meas_poll_interval_constructor_param(self):
        """Custom meas_poll_interval should be stored."""

        async def inner():
            app, _ = self._make_app(poll_interval=0.05)
            async with app.run_test(size=(80, 24)):
                assert app._meas_poll_interval == 0.05

        asyncio.run(inner())

    def test_measurements_refresh_after_command_dispatch(self):
        """Measurements table must update immediately after a command completes.

        Regression: with poll-only refresh, running 'Vout = dmm meas' would not
        appear in the table until the next poll tick (up to 5 seconds later).
        Now _refresh_measurements() is called in on_worker_state_changed SUCCESS.
        """

        async def inner():
            # Stub starts with 0 measurements; after the command runs it returns 1.
            stub = _StubDispatcher(measurements=[])
            from lab_instruments.tui.app import SCPIApp

            app = SCPIApp(stub, meas_poll_interval=9999.0)  # disable auto-poll
            async with app.run_test(size=(80, 24)) as pilot:
                mt = app.query_one(MeasurementTable)
                assert len(mt.measurements) == 0

                # Simulate dispatcher recording a measurement mid-command
                stub._measurements.append(_entry("Vout", 5.01))

                await pilot.click("#cmd_input")
                for ch in "Vout = dmm meas":
                    await pilot.press(ch)
                await pilot.press("enter")
                await pilot.pause(0.3)  # wait for worker + refresh

                assert len(mt.measurements) == 1
                assert mt.measurements[0]["label"] == "Vout"

        asyncio.run(inner())
