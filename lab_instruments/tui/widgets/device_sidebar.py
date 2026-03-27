"""Device status sidebar widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView


class DeviceSidebar(Widget):
    """Sidebar that lists connected instruments with selection state.

    The `devices` reactive is a list of snapshot dicts produced by
    LocalDispatcher.get_device_snapshot(). The watcher repopulates the
    ListView on every update so the sidebar always reflects current state.
    """

    DEFAULT_CSS = """
    DeviceSidebar {
        width: 22;
        border-right: solid $primary-darken-2;
        padding: 0 1;
    }
    DeviceSidebar .sidebar-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    DeviceSidebar ListView {
        height: 1fr;
        border: none;
    }
    """

    devices: reactive[list[dict]] = reactive(list, layout=True)

    def compose(self) -> ComposeResult:
        yield Label("Instruments", classes="sidebar-title")
        yield ListView(id="device-list")

    def watch_devices(self, devices: list[dict]) -> None:
        """Repopulate the ListView whenever the devices snapshot changes."""
        lv = self.query_one("#device-list", ListView)
        lv.clear()
        for dev in devices:
            name = dev.get("name", "")
            display = dev.get("display_name", name)
            selected = dev.get("selected", False)
            label_text = f"[bold]> {display}[/bold]" if selected else f"  {display}"
            lv.append(ListItem(Label(label_text, markup=True), name=name))
