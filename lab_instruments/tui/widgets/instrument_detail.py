"""Instrument detail panel - shows live status for the selected instrument."""

from __future__ import annotations

from collections import deque

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, Sparkline, Static


def _fmt_eng(value: float | None, unit: str = "") -> str:
    """Format a number with engineering-style suffixes."""
    if value is None:
        return "N/A"
    abs_val = abs(value)
    if abs_val == 0:
        return f"0.000 {unit}".strip()
    if abs_val >= 1e6:
        return f"{value / 1e6:.3f} M{unit}".strip()
    if abs_val >= 1e3:
        return f"{value / 1e3:.3f} k{unit}".strip()
    if abs_val >= 1:
        return f"{value:.4f} {unit}".strip()
    if abs_val >= 1e-3:
        return f"{value * 1e3:.3f} m{unit}".strip()
    if abs_val >= 1e-6:
        return f"{value * 1e6:.3f} u{unit}".strip()
    if abs_val >= 1e-9:
        return f"{value * 1e9:.3f} n{unit}".strip()
    return f"{value:.6e} {unit}".strip()


class InstrumentDetailPanel(Widget):
    """Displays live status for a single selected instrument.

    The ``detail`` reactive holds the snapshot dict from the dispatcher.
    When it changes the widget rebuilds its content to match the
    instrument type (PSU, DMM, AWG, Scope, SMU, EV2300).
    """

    DEFAULT_CSS = """
    InstrumentDetailPanel {
        height: 1fr;
        padding: 1 2;
        overflow-y: auto;
    }
    InstrumentDetailPanel .detail-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    InstrumentDetailPanel .detail-body {
        height: auto;
    }
    InstrumentDetailPanel .detail-section {
        padding: 0 0 0 0;
    }
    InstrumentDetailPanel .on-badge {
        color: $success;
        text-style: bold;
    }
    InstrumentDetailPanel .off-badge {
        color: $text-muted;
    }
    InstrumentDetailPanel .compliance-warn {
        color: $error;
        text-style: bold;
    }
    InstrumentDetailPanel Sparkline {
        height: 3;
        margin: 0 0 1 0;
    }
    InstrumentDetailPanel .action-row {
        height: auto;
        padding: 1 0 0 0;
        layout: horizontal;
    }
    InstrumentDetailPanel .action-row Button {
        margin: 0 1 0 0;
        min-width: 12;
    }
    """

    class QuickAction(Message):
        """Posted when the user clicks a quick-action button."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    class SaveStateRequested(Message):
        """Posted when the user clicks Save State."""

        def __init__(self, device_name: str) -> None:
            super().__init__()
            self.device_name = device_name

    class RestoreStateRequested(Message):
        """Posted when the user clicks Restore State."""

        def __init__(self, device_name: str) -> None:
            super().__init__()
            self.device_name = device_name

    detail: reactive[dict] = reactive(dict)

    _HISTORY_LEN = 30

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._history: dict[str, deque] = {}

    def _push_history(self, key: str, value: float | None) -> None:
        if value is None:
            return
        if key not in self._history:
            self._history[key] = deque(maxlen=self._HISTORY_LEN)
        self._history[key].append(value)

    def _accumulate_history(self, detail: dict) -> None:
        """Extract numeric readings and append to ring buffers."""
        if not detail or "error" in detail:
            return
        name = detail.get("name", "")
        dtype = detail.get("type", "")
        if dtype == "psu" and detail.get("subtype") == "smu":
            self._push_history(f"{name}_voltage", detail.get("voltage_meas"))
            self._push_history(f"{name}_current", detail.get("current_meas"))
        elif dtype == "psu":
            for ch in detail.get("channels", []):
                ch_id = ch.get("label", ch.get("id", ""))
                self._push_history(f"{name}_{ch_id}_voltage", ch.get("voltage_meas"))
                self._push_history(f"{name}_{ch_id}_current", ch.get("current_meas"))
        elif dtype == "dmm":
            self._push_history(f"{name}_reading", detail.get("last_reading"))

    def _mount_sparkline(self, body: Vertical, key: str, label: str) -> None:
        """Mount a labeled Sparkline if history data exists for the key."""
        data = self._history.get(key)
        if data and len(data) >= 2:
            body.mount(Static(f"  [dim]{label}[/dim]", markup=True))
            body.mount(Sparkline(list(data), id=f"spark-{key}"))

    def compose(self) -> ComposeResult:
        yield Label("Instrument Detail", classes="detail-title")
        yield Vertical(id="detail-body", classes="detail-body")

    def watch_detail(self, detail: dict) -> None:
        """Rebuild content whenever the detail snapshot changes."""
        # Accumulate history BEFORE rebuilding the DOM
        self._accumulate_history(detail)

        body = self.query_one("#detail-body", Vertical)
        body.remove_children()

        if not detail:
            body.mount(Static("[dim]Select an instrument from the sidebar[/dim]"))
            return

        if "error" in detail:
            body.mount(Static(f"[red]{detail['error']}[/red]"))
            return

        dtype = detail.get("type", "")
        name = detail.get("name", "")
        display = detail.get("display_name", name)

        body.mount(Static(f"[bold]{display}[/bold]  [dim]({name})[/dim]", classes="detail-section"))

        if dtype == "psu" and detail.get("subtype") == "smu":
            self._render_smu(body, detail, name)
        elif dtype == "psu":
            self._render_psu(body, detail, name)
        elif dtype == "dmm":
            self._render_dmm(body, detail, name)
        elif dtype == "awg":
            self._render_awg(body, detail, name)
        elif dtype == "scope":
            self._render_scope(body, detail, name)
        elif dtype == "ev2300":
            self._render_ev2300(body, detail)

    # ------------------------------------------------------------------
    # Renderers
    # ------------------------------------------------------------------

    def _render_psu(self, body: Vertical, detail: dict, name: str) -> None:
        channels = detail.get("channels", [])
        for ch in channels:
            label = ch.get("label", f"CH{ch.get('id', '?')}")
            output = ch.get("output", False)
            badge = "[green]ON[/green]" if output else "[dim]OFF[/dim]"

            v_set = _fmt_eng(ch.get("voltage_set"), "V")
            i_lim = _fmt_eng(ch.get("current_limit"), "A")
            line = f"  {label}  Set: {v_set} / {i_lim}  {badge}"

            if "voltage_meas" in ch:
                v_meas = _fmt_eng(ch.get("voltage_meas"), "V")
                i_meas = _fmt_eng(ch.get("current_meas"), "A")
                line += f"\n         Meas: {v_meas} / {i_meas}"

            body.mount(Static(line, markup=True, classes="detail-section"))
            self._mount_sparkline(body, f"{name}_{label}_voltage", f"{label} Voltage")
            self._mount_sparkline(body, f"{name}_{label}_current", f"{label} Current")

        # Quick action buttons
        row = Horizontal(classes="action-row")
        body.mount(row)
        row.mount(Button("Output ON", id=f"qa-{name}-on", variant="success"))
        row.mount(Button("Output OFF", id=f"qa-{name}-off", variant="error"))
        row.mount(Button("Save", id=f"ss-{name}-save", variant="primary"))
        row.mount(Button("Restore", id=f"ss-{name}-restore", variant="default"))

    def _render_smu(self, body: Vertical, detail: dict, name: str) -> None:
        mode = detail.get("output_mode", "voltage").capitalize()
        output = detail.get("output", False)
        badge = "[green]ON[/green]" if output else "[dim]OFF[/dim]"
        compliance = detail.get("in_compliance", False)
        comp_text = "[red bold]IN COMPLIANCE[/red bold]" if compliance else "[green]OK[/green]"
        temp = detail.get("temperature")
        temp_text = f"{temp:.1f} C" if temp is not None else "N/A"

        v_set = _fmt_eng(detail.get("voltage_set"), "V")
        i_lim = _fmt_eng(detail.get("current_limit"), "A")
        v_meas = _fmt_eng(detail.get("voltage_meas"), "V")
        i_meas = _fmt_eng(detail.get("current_meas"), "A")

        lines = [
            f"  Mode:       {mode} Source",
            f"  Setpoint:   {v_set} / {i_lim}",
            f"  Measured:   {v_meas} / {i_meas}",
            f"  Compliance: {comp_text}",
            f"  Temp:       {temp_text}",
            f"  Output:     {badge}",
        ]
        body.mount(Static("\n".join(lines), markup=True, classes="detail-section"))
        self._mount_sparkline(body, f"{name}_voltage", "Voltage")
        self._mount_sparkline(body, f"{name}_current", "Current")

        row = Horizontal(classes="action-row")
        body.mount(row)
        row.mount(Button("Output ON", id=f"qa-{name}-on", variant="success"))
        row.mount(Button("Output OFF", id=f"qa-{name}-off", variant="error"))
        row.mount(Button("Save", id=f"ss-{name}-save", variant="primary"))
        row.mount(Button("Restore", id=f"ss-{name}-restore", variant="default"))

    def _render_dmm(self, body: Vertical, detail: dict, name: str) -> None:
        reading = detail.get("last_reading")
        reading_text = f"{reading:.6f}" if reading is not None else "N/A"

        lines = [
            f"  Reading: {reading_text}",
        ]
        body.mount(Static("\n".join(lines), markup=True, classes="detail-section"))
        self._mount_sparkline(body, f"{name}_reading", "Reading")

        row = Horizontal(classes="action-row")
        body.mount(row)
        row.mount(Button("Read", id=f"qa-{name}-read", variant="primary"))

    def _render_awg(self, body: Vertical, detail: dict, name: str) -> None:
        channels = detail.get("channels", [])
        for ch in channels:
            ch_id = ch.get("id", "?")
            output = ch.get("output", False)
            badge = "[green]ON[/green]" if output else "[dim]OFF[/dim]"

            freq = _fmt_eng(ch.get("frequency"), "Hz")
            amp = _fmt_eng(ch.get("amplitude"), "Vpp")
            offset = _fmt_eng(ch.get("offset"), "V")

            line = f"  CH{ch_id}  {freq}  {amp}  offset {offset}  {badge}"
            body.mount(Static(line, markup=True, classes="detail-section"))

        row = Horizontal(classes="action-row")
        body.mount(row)
        row.mount(Button("CH1 ON", id=f"qa-{name}-ch1on", variant="success"))
        row.mount(Button("CH1 OFF", id=f"qa-{name}-ch1off", variant="error"))
        row.mount(Button("CH2 ON", id=f"qa-{name}-ch2on", variant="success"))
        row.mount(Button("CH2 OFF", id=f"qa-{name}-ch2off", variant="error"))
        row2 = Horizontal(classes="action-row")
        body.mount(row2)
        row2.mount(Button("Save", id=f"ss-{name}-save", variant="primary"))
        row2.mount(Button("Restore", id=f"ss-{name}-restore", variant="default"))

    def _render_scope(self, body: Vertical, detail: dict, name: str) -> None:
        trigger = detail.get("trigger_status", "unknown")
        num_ch = detail.get("num_channels", 4)

        lines = [
            f"  Trigger: {trigger}",
            f"  Channels: {num_ch}",
        ]
        body.mount(Static("\n".join(lines), markup=True, classes="detail-section"))

        row = Horizontal(classes="action-row")
        body.mount(row)
        row.mount(Button("Run", id=f"qa-{name}-run", variant="success"))
        row.mount(Button("Stop", id=f"qa-{name}-stop", variant="error"))
        row.mount(Button("Single", id=f"qa-{name}-single", variant="warning"))
        row.mount(Button("Autoset", id=f"qa-{name}-autoset", variant="primary"))

    def _render_ev2300(self, body: Vertical, detail: dict) -> None:
        connected = detail.get("connected", False)
        conn_text = "[green]Connected[/green]" if connected else "[red]Disconnected[/red]"
        serial = detail.get("serial", "N/A")
        product = detail.get("product", "N/A")

        lines = [
            f"  Status:  {conn_text}",
            f"  Product: {product}",
            f"  Serial:  {serial}",
        ]
        body.mount(Static("\n".join(lines), markup=True, classes="detail-section"))

    # ------------------------------------------------------------------
    # Quick-action button handler
    # ------------------------------------------------------------------

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Translate button presses into QuickAction or state snapshot messages."""
        bid = event.button.id or ""

        # State snapshot buttons: ss-<device>-save / ss-<device>-restore
        if bid.startswith("ss-"):
            event.stop()
            parts = bid[3:].rsplit("-", 1)
            if len(parts) == 2:
                dev_name, action = parts
                if action == "save":
                    self.post_message(self.SaveStateRequested(dev_name))
                elif action == "restore":
                    self.post_message(self.RestoreStateRequested(dev_name))
            return

        # Quick action buttons: qa-<device>-<action>
        if not bid.startswith("qa-"):
            return
        event.stop()

        parts = bid[3:].rsplit("-", 1)
        if len(parts) != 2:
            return
        dev_name, action = parts

        cmd_map = {
            "on": f"use {dev_name}\npsu chan on",
            "off": f"use {dev_name}\npsu chan off",
            "read": f"use {dev_name}\ndmm read",
            "run": f"use {dev_name}\nscope run",
            "stop": f"use {dev_name}\nscope stop",
            "single": f"use {dev_name}\nscope single",
            "autoset": f"use {dev_name}\nscope autoset",
            "ch1on": f"use {dev_name}\nawg chan 1 on",
            "ch1off": f"use {dev_name}\nawg chan 1 off",
            "ch2on": f"use {dev_name}\nawg chan 2 on",
            "ch2off": f"use {dev_name}\nawg chan 2 off",
        }

        cmd = cmd_map.get(action)
        if cmd:
            self.post_message(self.QuickAction(cmd))
