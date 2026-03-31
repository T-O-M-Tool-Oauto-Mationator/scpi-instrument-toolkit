"""Script editor - in-TUI editor for .scpi scripts using Textual's TextArea."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Label, ListItem, ListView, Static, TextArea


class ScriptEditor(Widget):
    """In-TUI script editor with file list, TextArea editor, and action buttons.

    The left side shows a list of available scripts. Clicking one loads
    it into the TextArea for editing.  Buttons allow creating, saving,
    running, and deleting scripts.
    """

    DEFAULT_CSS = """
    ScriptEditor {
        height: 1fr;
        layout: horizontal;
    }
    ScriptEditor #editor-sidebar {
        width: 22;
        border-right: solid $primary-darken-2;
        padding: 0 1;
    }
    ScriptEditor .sidebar-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    ScriptEditor #script-list {
        height: 1fr;
    }
    ScriptEditor #new-script-input {
        margin: 1 0 0 0;
    }
    ScriptEditor #editor-main {
        height: 1fr;
        width: 1fr;
    }
    ScriptEditor #editor-status {
        height: 1;
        padding: 0 1;
        color: $text-muted;
    }
    ScriptEditor TextArea {
        height: 1fr;
    }
    ScriptEditor .editor-actions {
        height: auto;
        layout: horizontal;
        padding: 1 0 0 0;
    }
    ScriptEditor .editor-actions Button {
        margin: 0 1 0 0;
        min-width: 10;
    }
    """

    class SaveRequested(Message):
        """Posted when the user clicks Save."""

        def __init__(self, name: str, content: str) -> None:
            super().__init__()
            self.name = name
            self.content = content

    class RunRequested(Message):
        """Posted when the user clicks Run."""

        def __init__(self, name: str) -> None:
            super().__init__()
            self.name = name

    class DeleteRequested(Message):
        """Posted when the user clicks Delete."""

        def __init__(self, name: str) -> None:
            super().__init__()
            self.name = name

    scripts: reactive[list[str]] = reactive(list, layout=True)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._current_script: str | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="editor-sidebar"):
            yield Label("Scripts", classes="sidebar-title")
            yield ListView(id="script-list")
            yield Input(placeholder="New script name", id="new-script-input")
        with Vertical(id="editor-main"):
            yield Static("[dim]Select or create a script[/dim]", id="editor-status")
            yield TextArea.code_editor("", id="editor-textarea", theme="monokai")
            with Horizontal(classes="editor-actions"):
                yield Button("Save", id="editor-save", variant="success")
                yield Button("Run", id="editor-run", variant="primary")
                yield Button("Delete", id="editor-delete", variant="error")

    def watch_scripts(self, scripts: list[str]) -> None:
        """Repopulate the script list."""
        lv = self.query_one("#script-list", ListView)
        lv.clear()
        for name in scripts:
            prefix = "> " if name == self._current_script else "  "
            lv.append(ListItem(Label(f"{prefix}{name}"), name=name))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Load the selected script into the editor."""
        event.stop()
        name = event.item.name or ""
        if name:
            self._current_script = name
            self.post_message(self._LoadScript(name))

    def load_content(self, name: str, content: str) -> None:
        """Load script content into the TextArea (called by the app)."""
        self._current_script = name
        ta = self.query_one("#editor-textarea", TextArea)
        ta.load_text(content)
        self.query_one("#editor-status", Static).update(f"Editing: [bold]{name}.scpi[/bold]")
        # Refresh list to show current indicator
        self.watch_scripts(self.scripts)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Create a new script when name is entered."""
        if event.input.id != "new-script-input":
            return
        name = event.value.strip()
        if not name:
            return
        event.input.clear()
        self._current_script = name
        ta = self.query_one("#editor-textarea", TextArea)
        ta.load_text(f"# {name}.scpi\n# Enter commands below, one per line\n\n")
        self.query_one("#editor-status", Static).update(f"New script: [bold]{name}.scpi[/bold]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if not self._current_script:
            return
        if event.button.id == "editor-save":
            event.stop()
            content = self.query_one("#editor-textarea", TextArea).text
            self.post_message(self.SaveRequested(self._current_script, content))
        elif event.button.id == "editor-run":
            event.stop()
            # Save first, then run
            content = self.query_one("#editor-textarea", TextArea).text
            self.post_message(self.SaveRequested(self._current_script, content))
            self.post_message(self.RunRequested(self._current_script))
        elif event.button.id == "editor-delete":
            event.stop()
            self.post_message(self.DeleteRequested(self._current_script))
            self._current_script = None
            self.query_one("#editor-textarea", TextArea).load_text("")
            self.query_one("#editor-status", Static).update("[dim]Script deleted[/dim]")

    class _LoadScript(Message):
        """Internal message requesting script content from the app."""

        def __init__(self, name: str) -> None:
            super().__init__()
            self.name = name
