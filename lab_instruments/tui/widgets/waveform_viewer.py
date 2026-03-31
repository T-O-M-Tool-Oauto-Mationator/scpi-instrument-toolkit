"""Waveform capture viewer - text-based ASCII waveform display."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, Static

_BLOCKS = " \u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"  # 9 levels


def _render_waveform(data: list[float], width: int = 60, height: int = 10) -> str:
    """Render data as a block-character waveform."""
    if not data:
        return "[dim]No waveform data[/dim]"
    if len(data) < 2:
        return "[dim]Not enough data points[/dim]"

    # Resample to fit width
    step = max(1, len(data) // width)
    samples = [data[i * step] for i in range(min(width, len(data) // step or 1))]
    if not samples:
        return "[dim]No samples[/dim]"

    mn, mx = min(samples), max(samples)
    rng = mx - mn if mx != mn else 1.0

    lines: list[str] = []
    for row in range(height - 1, -1, -1):
        line = ""
        for val in samples:
            normalized = (val - mn) / rng
            level = normalized * height
            cell_level = level - row
            if cell_level >= 1.0:
                line += _BLOCKS[8]
            elif cell_level > 0:
                idx = int(cell_level * 8)
                line += _BLOCKS[max(0, min(8, idx))]
            else:
                line += " "
        lines.append(line)

    return "\n".join(lines)


class WaveformViewer(Widget):
    """Displays a text-based waveform using Unicode block characters."""

    DEFAULT_CSS = """
    WaveformViewer {
        height: 1fr;
        padding: 0 1;
    }
    WaveformViewer .panel-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    WaveformViewer #waveform-display {
        height: 1fr;
    }
    WaveformViewer #waveform-capture {
        dock: bottom;
        width: auto;
        margin: 1 0 0 0;
    }
    """

    class CaptureRequested(Message):
        """Posted when the user clicks the Capture button."""

        def __init__(self, device_name: str) -> None:
            super().__init__()
            self.device_name = device_name

    data: reactive[list[float]] = reactive(list)
    device_name: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Label("Waveform", classes="panel-title")
        yield Static("[dim]No waveform data -- click Capture[/dim]", id="waveform-display")
        yield Button("Capture", id="waveform-capture", variant="primary")

    def watch_data(self, data: list[float]) -> None:
        display = self.query_one("#waveform-display", Static)
        waveform = _render_waveform(data)
        display.update(waveform)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "waveform-capture":
            event.stop()
            self.post_message(self.CaptureRequested(self.device_name))
