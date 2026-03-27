"""Tests for DeviceSidebar widget and app integration - CP3."""

import asyncio

from textual.widgets import Label, ListItem, ListView

from lab_instruments.tui.widgets.device_sidebar import DeviceSidebar

# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------


class _StubDispatcher:
    """State-tracking stub with controllable device snapshot."""

    def __init__(self, devices: list[dict] | None = None):
        self._commands: list[str] = []
        self._devices: list[dict] = devices or []
        self._completions: dict[str, list[str]] = {}

    def handle_command(self, cmd: str) -> str:
        self._commands.append(cmd)
        return f"OK: {cmd}"

    def get_completions(self, text: str) -> list[str]:
        return list(self._completions.get(text, []))

    def get_device_snapshot(self) -> list[dict]:
        return list(self._devices)


def _make_device(name: str, display: str, selected: bool = False) -> dict:
    return {
        "name": name,
        "display_name": display,
        "selected": selected,
        "base_type": name.rstrip("0123456789"),
    }


# ---------------------------------------------------------------------------
# DeviceSidebar widget tests (standalone)
# ---------------------------------------------------------------------------


class TestDeviceSidebarWidget:
    def test_empty_device_list_yields_empty_listview(self):
        """Sidebar with no devices should show an empty ListView."""

        async def inner():
            app = DeviceSidebar()

            class _Wrap(app.__class__.__mro__[3]):  # type: ignore[misc]
                pass

            # Mount standalone via a minimal app harness
            from textual.app import App, ComposeResult

            class WrapApp(App):
                def compose(self) -> ComposeResult:
                    yield DeviceSidebar(id="sb")

            wa = WrapApp()
            async with wa.run_test(size=(40, 24)) as pilot:
                sb = wa.query_one("#sb", DeviceSidebar)
                sb.devices = []
                await pilot.pause(0.05)
                lv = sb.query_one("#device-list", ListView)
                assert len(lv) == 0

        asyncio.run(inner())

    def test_single_device_populates_list(self):
        """One device should appear as one ListView item."""
        from textual.app import App, ComposeResult

        async def inner():
            class WrapApp(App):
                def compose(self) -> ComposeResult:
                    yield DeviceSidebar(id="sb")

            wa = WrapApp()
            async with wa.run_test(size=(40, 24)) as pilot:
                sb = wa.query_one("#sb", DeviceSidebar)
                sb.devices = [_make_device("psu1", "HP E3631A")]
                await pilot.pause(0.1)
                lv = sb.query_one("#device-list", ListView)
                assert len(lv) == 1

        asyncio.run(inner())

    def test_selected_device_label_contains_arrow(self):
        """The selected device's label text should contain '>'."""
        from textual.app import App, ComposeResult

        async def inner():
            class WrapApp(App):
                def compose(self) -> ComposeResult:
                    yield DeviceSidebar(id="sb")

            wa = WrapApp()
            async with wa.run_test(size=(40, 24)) as pilot:
                sb = wa.query_one("#sb", DeviceSidebar)
                sb.devices = [
                    _make_device("psu1", "HP E3631A", selected=True),
                    _make_device("dmm1", "HP 34401A", selected=False),
                ]
                await pilot.pause(0.1)
                lv = sb.query_one("#device-list", ListView)
                # First item (psu1) is selected - its name attr should match
                first: ListItem = lv._nodes[0]  # type: ignore[assignment]
                lbl = first.query_one(Label)
                assert ">" in str(lbl.render())

        asyncio.run(inner())

    def test_watch_devices_clears_old_entries(self):
        """Setting devices twice should show only the second set."""
        from textual.app import App, ComposeResult

        async def inner():
            class WrapApp(App):
                def compose(self) -> ComposeResult:
                    yield DeviceSidebar(id="sb")

            wa = WrapApp()
            async with wa.run_test(size=(40, 24)) as pilot:
                sb = wa.query_one("#sb", DeviceSidebar)
                sb.devices = [_make_device("psu1", "HP E3631A")]
                await pilot.pause(0.1)
                sb.devices = [_make_device("awg1", "Keysight EDU"), _make_device("dmm1", "HP 34401A")]
                await pilot.pause(0.1)
                lv = sb.query_one("#device-list", ListView)
                assert len(lv) == 2

        asyncio.run(inner())


# ---------------------------------------------------------------------------
# App-level integration tests
# ---------------------------------------------------------------------------


class TestDeviceSidebarInApp:
    def _make_app(self, devices: list[dict] | None = None, poll_interval: float = 60.0):
        from lab_instruments.tui.app import SCPIApp

        stub = _StubDispatcher(devices)
        app = SCPIApp(stub, device_poll_interval=poll_interval)
        return app, stub

    def test_sidebar_mounts(self):
        """DeviceSidebar should be present in the widget tree."""

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)):
                assert app.query_one(DeviceSidebar) is not None

        asyncio.run(inner())

    def test_sidebar_visible_by_default(self):
        """Sidebar should be visible on startup."""

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)):
                sb = app.query_one(DeviceSidebar)
                assert sb.display is True

        asyncio.run(inner())

    def test_toggle_sidebar_hides_it(self):
        """action_toggle_sidebar should hide the sidebar."""

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                await app.run_action("toggle_sidebar")
                await pilot.pause(0.05)
                sb = app.query_one(DeviceSidebar)
                assert sb.display is False

        asyncio.run(inner())

    def test_toggle_sidebar_twice_restores_visibility(self):
        """Two toggle_sidebar actions should restore the sidebar."""

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                await app.run_action("toggle_sidebar")
                await pilot.pause(0.05)
                await app.run_action("toggle_sidebar")
                await pilot.pause(0.05)
                sb = app.query_one(DeviceSidebar)
                assert sb.display is True

        asyncio.run(inner())

    def test_refresh_devices_updates_sidebar(self):
        """Calling _refresh_devices manually should push snapshot to sidebar."""

        async def inner():
            devices = [_make_device("psu1", "HP E3631A")]
            app, stub = self._make_app(devices)
            async with app.run_test(size=(80, 24)) as pilot:
                app._refresh_devices()
                await pilot.pause(0.1)
                sb = app.query_one(DeviceSidebar)
                assert len(sb.devices) == 1
                assert sb.devices[0]["name"] == "psu1"

        asyncio.run(inner())

    def test_poll_interval_constructor_param(self):
        """Custom poll interval should be stored without error."""

        async def inner():
            app, _ = self._make_app(poll_interval=0.05)
            async with app.run_test(size=(80, 24)):
                assert app._device_poll_interval == 0.05

        asyncio.run(inner())

    def test_stub_without_get_device_snapshot_does_not_crash(self):
        """Dispatcher without get_device_snapshot should not crash on refresh."""
        from lab_instruments.tui.app import SCPIApp

        class _MinimalStub:
            def handle_command(self, cmd: str) -> str:
                return ""

            def get_completions(self, text: str) -> list[str]:
                return []

        async def inner():
            app = SCPIApp(_MinimalStub())
            async with app.run_test(size=(80, 24)) as pilot:
                # Should not raise even though get_device_snapshot is absent
                app._refresh_devices()
                await pilot.pause(0.05)

        asyncio.run(inner())
