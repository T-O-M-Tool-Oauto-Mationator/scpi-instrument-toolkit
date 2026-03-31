"""Device status sidebar widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, ListItem, ListView


class DeviceSidebar(Widget):
    """Sidebar that lists connected instruments with selection state.

    The `devices` reactive is a list of snapshot dicts produced by
    LocalDispatcher.get_device_snapshot(). The watcher repopulates the
    ListView on every update so the sidebar always reflects current state.
    """

    DEFAULT_CSS = """
    DeviceSidebar {
        width: 26;
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
    DeviceSidebar .bulk-actions {
        height: auto;
        layout: horizontal;
        padding: 1 0 0 0;
    }
    DeviceSidebar .bulk-actions Button {
        margin: 0 1 0 0;
        min-width: 5;
    }
    """

    class DeviceSelected(Message):
        """Posted when the user clicks a device in the sidebar."""

        def __init__(self, device_name: str) -> None:
            super().__init__()
            self.device_name = device_name

    class BulkAction(Message):
        """Posted when the user clicks a bulk operation button."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    devices: reactive[list[dict]] = reactive(list, layout=True)

    def compose(self) -> ComposeResult:
        yield Label("Instruments", classes="sidebar-title")
        yield ListView(id="device-list")
        with Horizontal(classes="bulk-actions"):
            yield Button("OFF", id="bulk-off", variant="error")
            yield Button("Safe", id="bulk-safe", variant="warning")
            yield Button("Reset", id="bulk-reset", variant="default")

    def watch_devices(self, devices: list[dict]) -> None:
        """Repopulate the ListView whenever the devices snapshot changes."""
        lv = self.query_one("#device-list", ListView)
        lv.clear()
        for dev in devices:
            name = dev.get("name", "")
            display = dev.get("display_name", name)
            selected = dev.get("selected", False)
            status = dev.get("status", "unknown")
            dot = {"connected": "[green]●[/green]", "error": "[red]●[/red]"}.get(status, "[yellow]●[/yellow]")
            label_text = f"[bold]> {dot} {display}[/bold]" if selected else f"  {dot} {display}"
            lv.append(ListItem(Label(label_text, markup=True), name=name))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Post DeviceSelected when the user clicks an instrument."""
        event.stop()
        name = event.item.name or ""
        if name:
            self.post_message(self.DeviceSelected(name))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle bulk operation button presses."""
        cmd_map = {"bulk-off": "state off", "bulk-safe": "state safe", "bulk-reset": "state reset"}
        cmd = cmd_map.get(event.button.id or "")
        if cmd:
            event.stop()
            self.post_message(self.BulkAction(cmd))
