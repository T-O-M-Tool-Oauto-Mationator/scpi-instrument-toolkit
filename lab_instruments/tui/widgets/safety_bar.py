"""Safety status bar widget - always-visible summary of safety limits."""

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

_EMPTY: dict = {}


class SafetyBar(Widget):
    """Single-line bar docked at the bottom of the screen.

    Displays limit count, active-script flag, and exit-on-error flag.
    Text is assembled entirely from the safety_info dict values - no
    hardcoded fallback strings.
    """

    DEFAULT_CSS = """
    SafetyBar {
        height: 1;
        dock: bottom;
        background: $panel;
        padding: 0 1;
    }
    SafetyBar Label {
        width: 1fr;
        color: $text-muted;
    }
    SafetyBar.active Label {
        color: $warning;
    }
    """

    safety_info: reactive[dict] = reactive(lambda: dict(_EMPTY))

    def compose(self) -> ComposeResult:
        yield Label("", id="safety-label")

    device_count: reactive[int] = reactive(0)

    def watch_safety_info(self, info: dict) -> None:
        """Rebuild the label text from the info dict."""
        limit_count = info.get("limit_count", 0)
        meas_count = info.get("measurement_count", 0)
        in_script = info.get("active_script", False)
        exit_on_error = info.get("exit_on_error", False)

        parts = [
            f"Devices: {self.device_count}",
            f"Limits: {limit_count}",
            f"Meas: {meas_count}",
            f"Script: {'ON' if in_script else 'OFF'}",
            f"exit_on_error: {'ON' if exit_on_error else 'OFF'}",
        ]
        self.query_one("#safety-label", Label).update("  |  ".join(parts))

    def watch_device_count(self, _count: int) -> None:
        """Re-render the label when device count changes."""
        # Re-run the info watcher to pick up the new count
        info = dict(self.safety_info) if self.safety_info else {}
        limit_count = info.get("limit_count", 0)
        meas_count = info.get("measurement_count", 0)
        in_script = info.get("active_script", False)
        exit_on_error = info.get("exit_on_error", False)

        parts = [
            f"Devices: {self.device_count}",
            f"Limits: {limit_count}",
            f"Meas: {meas_count}",
            f"Script: {'ON' if in_script else 'OFF'}",
            f"exit_on_error: {'ON' if exit_on_error else 'OFF'}",
        ]
        try:
            self.query_one("#safety-label", Label).update("  |  ".join(parts))
        except Exception:  # noqa: BLE001
            pass

        # Highlight bar when a script is actively running
        self.set_class(bool(in_script), "active")
