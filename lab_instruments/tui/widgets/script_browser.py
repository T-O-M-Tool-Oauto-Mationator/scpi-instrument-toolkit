"""Script browser widget - lists and runs .scpi scripts."""

from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView


class ScriptBrowser(Widget):
    """Sidebar-style panel listing available .scpi scripts.

    Posting ScriptSelected when the user picks one lets the App dispatch
    the run_script command without the widget knowing about the dispatcher.
    """

    DEFAULT_CSS = """
    ScriptBrowser {
        height: 1fr;
        padding: 0 1;
    }
    ScriptBrowser .sidebar-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    ScriptBrowser ListView {
        height: 1fr;
        border: none;
    }
    """

    class ScriptSelected(Message):
        """Posted when the user selects a script to run."""

        def __init__(self, script_name: str) -> None:
            super().__init__()
            self.script_name = script_name

    scripts: reactive[list[str]] = reactive(list, layout=True)

    def compose(self) -> ComposeResult:
        yield Label("Scripts", classes="sidebar-title")
        yield ListView(id="script-list")

    def watch_scripts(self, scripts: list[str]) -> None:
        """Repopulate the ListView whenever the script list changes."""
        lv = self.query_one("#script-list", ListView)
        lv.clear()
        for name in scripts:
            lv.append(ListItem(Label(name), name=name))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Post ScriptSelected when the user picks a script."""
        event.stop()
        name = event.item.name or ""
        if name:
            self.post_message(self.ScriptSelected(name))
