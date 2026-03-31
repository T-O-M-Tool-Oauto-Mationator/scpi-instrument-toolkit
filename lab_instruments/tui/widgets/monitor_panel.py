"""Live monitoring panel - auto-reads instrument at configurable interval."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Sparkline, Static


class MonitorPanel(Widget):
    """Auto-reads the active instrument at a configurable interval.

    Posts ``MonitorCommand`` on each tick. The app dispatches the
    command and feeds the numeric result back via ``add_reading``.
    """

    DEFAULT_CSS = """
    MonitorPanel {
        height: 1fr;
        padding: 0 1;
    }
    MonitorPanel .panel-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    MonitorPanel #monitor-stats {
        height: auto;
        padding: 0 0 1 0;
    }
    MonitorPanel Sparkline {
        height: 5;
        margin: 0 0 1 0;
    }
    MonitorPanel #monitor-interval {
        width: 20;
    }
    MonitorPanel .monitor-controls {
        height: auto;
        layout: horizontal;
        padding: 1 0 0 0;
    }
    MonitorPanel .monitor-controls Button {
        margin: 0 1 0 0;
        min-width: 10;
    }
    """

    class MonitorCommand(Message):
        """Posted on each tick requesting an instrument reading."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    _MAX_READINGS = 100

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._readings: list[float] = []
        self._running: bool = False
        self._timer: Timer | None = None
        self.monitor_command: str = "dmm read"

    def compose(self) -> ComposeResult:
        yield Label("Monitor", classes="panel-title")
        yield Static("[dim]Stopped -- press Start to begin[/dim]", id="monitor-stats")
        yield Sparkline([], id="monitor-spark")
        yield Label("Interval (ms):")
        yield Input(value="500", id="monitor-interval")
        with Horizontal(classes="monitor-controls"):
            yield Button("Start", id="monitor-start", variant="success")
            yield Button("Stop", id="monitor-stop", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "monitor-start":
            event.stop()
            self._start()
        elif event.button.id == "monitor-stop":
            event.stop()
            self._stop()

    def _start(self) -> None:
        if self._running:
            return
        try:
            ms = int(self.query_one("#monitor-interval", Input).value)
        except ValueError:
            ms = 500
        self._running = True
        self._timer = self.set_interval(max(ms, 100) / 1000.0, self._tick)
        self.query_one("#monitor-stats", Static).update("[green]Running...[/green]")

    def _stop(self) -> None:
        self._running = False
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
        self.query_one("#monitor-stats", Static).update("[dim]Stopped[/dim]")

    def _tick(self) -> None:
        if self._running:
            self.post_message(self.MonitorCommand(self.monitor_command))

    def add_reading(self, value: float) -> None:
        """Called by the app when a reading is received."""
        self._readings.append(value)
        if len(self._readings) > self._MAX_READINGS:
            self._readings = self._readings[-self._MAX_READINGS :]
        self.query_one("#monitor-spark", Sparkline).data = self._readings
        vals = self._readings
        current = vals[-1]
        mn, mx, avg = min(vals), max(vals), sum(vals) / len(vals)
        self.query_one("#monitor-stats", Static).update(
            f"[green]Running[/green]  "
            f"Current: {current:.6f}  Min: {mn:.6f}  Max: {mx:.6f}  Mean: {avg:.6f}  "
            f"({len(vals)} samples)"
        )
