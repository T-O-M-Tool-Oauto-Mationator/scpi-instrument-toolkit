"""Notification center - scrollable history of all toast notifications."""

from __future__ import annotations

from rich.markup import escape
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, RichLog


class NotificationCenter(Widget):
    """Scrollable history of all toast notifications.

    The ``notifications`` reactive receives a list of dicts, each with
    keys: message, severity, timestamp.  The RichLog display is
    color-coded by severity (red for error, yellow for warning,
    green for information).
    """

    DEFAULT_CSS = """
    NotificationCenter {
        height: 1fr;
        padding: 0 1;
    }
    NotificationCenter .panel-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    NotificationCenter RichLog {
        height: 1fr;
    }
    NotificationCenter #notif-clear {
        dock: bottom;
        width: auto;
        margin: 1 0 0 0;
    }
    """

    notifications: reactive[list[dict]] = reactive(list, layout=True)

    def compose(self) -> ComposeResult:
        yield Label("Notifications (0)", id="notif-title", classes="panel-title")
        yield RichLog(id="notif-log", wrap=True, auto_scroll=True, markup=True)
        yield Button("Clear", id="notif-clear", variant="error")

    def watch_notifications(self, notifications: list[dict]) -> None:
        self.query_one("#notif-title", Label).update(f"Notifications ({len(notifications)})")
        log = self.query_one("#notif-log", RichLog)
        log.clear()
        for n in notifications:
            severity = n.get("severity", "information")
            ts = n.get("timestamp", "")
            msg = n.get("message", "")
            color = {"error": "red", "warning": "yellow"}.get(severity, "green")
            log.write(f"[{color}][{escape(ts)}] {escape(msg)}[/{color}]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "notif-clear":
            event.stop()
            self.notifications = []
