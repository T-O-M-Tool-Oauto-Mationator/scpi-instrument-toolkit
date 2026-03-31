"""Instrument detail panel - shows live status for the selected instrument."""

from __future__ import annotations

from collections import deque

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Sparkline, Static


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

    The ``safety_limits`` reactive holds the list of limit dicts from
    the safety snapshot, used to colour readings that exceed limits.
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
    InstrumentDetailPanel .over-limit {
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
    InstrumentDetailPanel .input-row {
        height: auto;
        padding: 0 0 0 2;
        layout: horizontal;
    }
    InstrumentDetailPanel .input-row Input {
        width: 1fr;
        margin: 0 1 0 0;
        dock: none;
    }
    InstrumentDetailPanel .input-row Button {
        min-width: 8;
        dock: none;
    }
    InstrumentDetailPanel .limit-row {
        height: auto;
        padding: 0 0 0 2;
        layout: horizontal;
    }
    InstrumentDetailPanel .limit-row Input {
        width: 1fr;
        margin: 0 1 0 0;
        dock: none;
    }
    InstrumentDetailPanel .limit-row Button {
        min-width: 8;
        dock: none;
    }
    InstrumentDetailPanel .limit-row Label {
        width: auto;
        margin: 0 1 0 0;
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

    class SetLimitRequested(Message):
        """Posted when user sets a safety limit from the detail panel."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    detail: reactive[dict] = reactive(dict)
    safety_limits: reactive[list] = reactive(list)

    _HISTORY_LEN = 30

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._history: dict[str, deque] = {}

    def _get_limit(self, device: str, channel: int | str | None, param: str) -> float | None:
        """Look up a safety limit value for a device/channel/parameter."""
        for entry in self.safety_limits:
            if entry.get("device") == device and entry.get("parameter") == param:
                entry_ch = entry.get("channel")
                if entry_ch is None or entry_ch == channel:
                    return entry.get("value")
        return None

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

    # Channel accent colors matching the GUI
    _CH_COLORS = ["yellow", "cyan", "magenta", "green", "bright_cyan", "bright_magenta"]

    def _render_psu(self, body: Vertical, detail: dict, name: str) -> None:
        channels = detail.get("channels", [])
        multi = len(channels) > 1

        for idx, ch in enumerate(channels):
            label = ch.get("label", f"CH{ch.get('id', '?')}")
            ch_id = ch.get("id", idx + 1)
            output = ch.get("output", False)
            badge = "[green bold]ON[/green bold]" if output else "[dim]OFF[/dim]"
            color = self._CH_COLORS[idx % len(self._CH_COLORS)]

            # Check safety limits for over-limit colouring
            v_set_val = ch.get("voltage_set")
            i_lim_val = ch.get("current_limit")
            v_upper = self._get_limit(name, ch_id, "voltage_upper")
            i_upper = self._get_limit(name, ch_id, "current_upper")
            # Also check type-level limits (e.g. "psu")
            if v_upper is None:
                v_upper = self._get_limit("psu", ch_id, "voltage_upper")
            if i_upper is None:
                i_upper = self._get_limit("psu", ch_id, "current_upper")

            v_over = v_upper is not None and v_set_val is not None and v_set_val > v_upper + 1e-9
            i_over = i_upper is not None and i_lim_val is not None and i_lim_val > i_upper + 1e-9

            v_color = "red bold" if v_over else "green"
            i_color = "red bold" if i_over else "yellow"
            v_set = _fmt_eng(v_set_val, "V")
            i_lim = _fmt_eng(i_lim_val, "A")
            line = (
                f"  [{color} bold]{label}[/{color} bold]  "
                f"Set: [{v_color}]{v_set}[/{v_color}] / [{i_color}]{i_lim}[/{i_color}]  {badge}"
            )

            if "voltage_meas" in ch:
                v_meas_val = ch.get("voltage_meas")
                i_meas_val = ch.get("current_meas")
                vm_over = v_upper is not None and v_meas_val is not None and v_meas_val > v_upper + 1e-9
                im_over = i_upper is not None and i_meas_val is not None and i_meas_val > i_upper + 1e-9
                vm_color = "red bold" if vm_over else "green"
                im_color = "red bold" if im_over else "yellow"
                v_meas = _fmt_eng(v_meas_val, "V")
                i_meas = _fmt_eng(i_meas_val, "A")
                line += f"\n         Meas: [{vm_color}]{v_meas}[/{vm_color}] / [{im_color}]{i_meas}[/{im_color}]"

            if v_over:
                line += f"\n         [red bold]OVER LIMIT: {v_set} > max {v_upper}V[/red bold]"
            if i_over:
                line += f"\n         [red bold]OVER LIMIT: {i_lim} > max {i_upper}A[/red bold]"

            body.mount(Static(line, markup=True, classes="detail-section"))
            self._mount_sparkline(body, f"{name}_{label}_voltage", f"{label} Voltage")
            self._mount_sparkline(body, f"{name}_{label}_current", f"{label} Current")

            # Per-channel voltage/current setpoint inputs
            inp_row = Horizontal(classes="input-row")
            body.mount(inp_row)
            v_default = f"{v_set_val:.3f}" if v_set_val is not None else "0"
            i_default = f"{i_lim_val:.4f}" if i_lim_val is not None else "0"
            inp_row.mount(Input(placeholder="Voltage (V)", value=v_default, id=f"inp-{name}-{ch_id}-v"))
            inp_row.mount(Input(placeholder="Current (A)", value=i_default, id=f"inp-{name}-{ch_id}-i"))
            inp_row.mount(Button("Apply", id=f"apply-{name}-{ch_id}", variant="primary"))

            # Per-channel output toggle (for multi-channel PSUs)
            if multi:
                ch_row = Horizontal(classes="action-row")
                body.mount(ch_row)
                ch_row.mount(Button(f"{label} ON", id=f"qa-{name}-ch{ch_id}on", variant="success"))
                ch_row.mount(Button(f"{label} OFF", id=f"qa-{name}-ch{ch_id}off", variant="error"))

            # Per-channel limit setting
            lim_row = Horizontal(classes="limit-row")
            body.mount(lim_row)
            lim_row.mount(Label("Limits:", id=f"limlbl-{name}-{ch_id}"))
            v_lim_default = f"{v_upper:g}" if v_upper is not None else ""
            i_lim_default = f"{i_upper:g}" if i_upper is not None else ""
            lim_row.mount(Input(placeholder="V max", value=v_lim_default, id=f"lim-{name}-{ch_id}-v"))
            lim_row.mount(Input(placeholder="A max", value=i_lim_default, id=f"lim-{name}-{ch_id}-i"))
            lim_row.mount(Button("Set", id=f"setlim-{name}-{ch_id}", variant="warning"))

        # Batch action buttons
        row = Horizontal(classes="action-row")
        body.mount(row)
        row.mount(Button("All ON", id=f"qa-{name}-allon", variant="success"))
        row.mount(Button("All OFF", id=f"qa-{name}-alloff", variant="error"))
        row.mount(Button("Save", id=f"ss-{name}-save", variant="primary"))
        row.mount(Button("Restore", id=f"ss-{name}-restore", variant="default"))

    def _render_smu(self, body: Vertical, detail: dict, name: str) -> None:
        mode = detail.get("output_mode", "voltage").capitalize()
        output = detail.get("output", False)
        badge = "[green bold]ON[/green bold]" if output else "[dim]OFF[/dim]"
        compliance = detail.get("in_compliance", False)
        comp_text = "[red bold]IN COMPLIANCE[/red bold]" if compliance else "[green]OK[/green]"
        temp = detail.get("temperature")
        temp_text = f"{temp:.1f} C" if temp is not None else "N/A"

        v_set_val = detail.get("voltage_set")
        i_lim_val = detail.get("current_limit")
        v_meas_val = detail.get("voltage_meas")
        i_meas_val = detail.get("current_meas")

        # Check safety limits
        v_upper = self._get_limit(name, None, "voltage_upper") or self._get_limit("smu", None, "voltage_upper")
        i_upper = self._get_limit(name, None, "current_upper") or self._get_limit("smu", None, "current_upper")

        v_over = v_upper is not None and v_set_val is not None and abs(v_set_val) > v_upper + 1e-9
        i_over = i_upper is not None and i_lim_val is not None and abs(i_lim_val) > i_upper + 1e-9
        vm_over = v_upper is not None and v_meas_val is not None and abs(v_meas_val) > v_upper + 1e-9
        im_over = i_upper is not None and i_meas_val is not None and abs(i_meas_val) > i_upper + 1e-9

        v_set = _fmt_eng(v_set_val, "V")
        i_lim = _fmt_eng(i_lim_val, "A")
        vc = "red bold" if v_over else ""
        ic = "red bold" if i_over else ""
        v_set_markup = f"[{vc}]{v_set}[/{vc}]" if vc else v_set
        i_lim_markup = f"[{ic}]{i_lim}[/{ic}]" if ic else i_lim

        v_meas = _fmt_eng(v_meas_val, "V")
        i_meas = _fmt_eng(i_meas_val, "A")
        vmc = "red bold" if vm_over else ""
        imc = "red bold" if im_over else ""
        v_meas_markup = f"[{vmc}]{v_meas}[/{vmc}]" if vmc else v_meas
        i_meas_markup = f"[{imc}]{i_meas}[/{imc}]" if imc else i_meas

        lines = [
            f"  Mode:       {mode} Source",
            f"  Setpoint:   {v_set_markup} / {i_lim_markup}",
            f"  Measured:   {v_meas_markup} / {i_meas_markup}",
            f"  Compliance: {comp_text}",
            f"  Temp:       {temp_text}",
            f"  Output:     {badge}",
        ]
        if v_over:
            lines.append(f"  [red bold]OVER LIMIT: voltage {v_set} > max {v_upper}V[/red bold]")
        if i_over:
            lines.append(f"  [red bold]OVER LIMIT: current {i_lim} > max {i_upper}A[/red bold]")

        body.mount(Static("\n".join(lines), markup=True, classes="detail-section"))
        self._mount_sparkline(body, f"{name}_voltage", "Voltage")
        self._mount_sparkline(body, f"{name}_current", "Current")

        # Mode toggle
        mode_row = Horizontal(classes="action-row")
        body.mount(mode_row)
        mode_row.mount(Button("Voltage Mode", id=f"qa-{name}-modev", variant="primary"))
        mode_row.mount(Button("Current Mode", id=f"qa-{name}-modei", variant="primary"))

        # Setpoint controls
        inp_row = Horizontal(classes="input-row")
        body.mount(inp_row)
        v_default = f"{v_set_val:.3f}" if v_set_val is not None else "0"
        i_default = f"{i_lim_val:.4f}" if i_lim_val is not None else "0"
        inp_row.mount(Input(placeholder="Voltage (V)", value=v_default, id=f"inp-{name}-1-v"))
        inp_row.mount(Input(placeholder="Current (A)", value=i_default, id=f"inp-{name}-1-i"))
        inp_row.mount(Button("Apply", id=f"apply-{name}-1", variant="primary"))

        # Limit setting
        lim_row = Horizontal(classes="limit-row")
        body.mount(lim_row)
        lim_row.mount(Label("Limits:"))
        v_lim_default = f"{v_upper:g}" if v_upper is not None else ""
        i_lim_default = f"{i_upper:g}" if i_upper is not None else ""
        lim_row.mount(Input(placeholder="V max", value=v_lim_default, id=f"lim-{name}-1-v"))
        lim_row.mount(Input(placeholder="A max", value=i_lim_default, id=f"lim-{name}-1-i"))
        lim_row.mount(Button("Set", id=f"setlim-{name}-1", variant="warning"))

        row = Horizontal(classes="action-row")
        body.mount(row)
        row.mount(Button("Output ON", id=f"qa-{name}-on", variant="success"))
        row.mount(Button("Output OFF", id=f"qa-{name}-off", variant="error"))
        row.mount(Button("Save", id=f"ss-{name}-save", variant="primary"))
        row.mount(Button("Restore", id=f"ss-{name}-restore", variant="default"))

    _DMM_MODES = [
        ("dc_voltage", "DC Voltage"),
        ("ac_voltage", "AC Voltage"),
        ("dc_current", "DC Current"),
        ("ac_current", "AC Current"),
        ("resistance", "Resistance (2W)"),
        ("four_wire_resistance", "Resistance (4W)"),
        ("frequency", "Frequency"),
        ("period", "Period"),
        ("continuity", "Continuity"),
        ("diode", "Diode"),
        ("capacitance", "Capacitance"),
        ("temperature", "Temperature"),
    ]

    def _render_dmm(self, body: Vertical, detail: dict, name: str) -> None:
        reading = detail.get("last_reading")
        mode = detail.get("mode", "")
        reading_text = f"{reading:.6f}" if reading is not None else "N/A"

        lines = [
            f"  Reading: {reading_text}",
        ]
        if mode:
            lines.append(f"  Mode:    {mode}")
        body.mount(Static("\n".join(lines), markup=True, classes="detail-section"))
        self._mount_sparkline(body, f"{name}_reading", "Reading")

        # Mode selector buttons (compact 2-row layout)
        mode_row1 = Horizontal(classes="action-row")
        body.mount(mode_row1)
        for mode_id, mode_label in self._DMM_MODES[:6]:
            mode_row1.mount(Button(mode_label, id=f"qa-{name}-mode-{mode_id}", variant="default"))

        mode_row2 = Horizontal(classes="action-row")
        body.mount(mode_row2)
        for mode_id, mode_label in self._DMM_MODES[6:]:
            mode_row2.mount(Button(mode_label, id=f"qa-{name}-mode-{mode_id}", variant="default"))

        row = Horizontal(classes="action-row")
        body.mount(row)
        row.mount(Button("Read", id=f"qa-{name}-read", variant="primary"))

    _AWG_WAVEFORMS = ["SIN", "SQU", "RAMP", "PULS", "NOIS", "DC"]

    def _render_awg(self, body: Vertical, detail: dict, name: str) -> None:
        channels = detail.get("channels", [])
        ch_colors = ["cyan", "magenta"]
        for idx, ch in enumerate(channels):
            ch_id = ch.get("id", idx + 1)
            output = ch.get("output", False)
            badge = "[green bold]ON[/green bold]" if output else "[dim]OFF[/dim]"
            color = ch_colors[idx % len(ch_colors)]

            freq_val = ch.get("frequency")
            amp_val = ch.get("amplitude")
            offset_val = ch.get("offset")

            # Check AWG safety limits
            vpp_upper = self._get_limit(name, ch_id, "vpp_upper") or self._get_limit("awg", ch_id, "vpp_upper")
            freq_upper = self._get_limit(name, ch_id, "freq_upper") or self._get_limit("awg", ch_id, "freq_upper")
            amp_over = vpp_upper is not None and amp_val is not None and amp_val > vpp_upper + 1e-9
            freq_over = freq_upper is not None and freq_val is not None and freq_val > freq_upper + 1e-9

            freq = _fmt_eng(freq_val, "Hz")
            amp = _fmt_eng(amp_val, "Vpp")
            offset = _fmt_eng(offset_val, "V")

            fc = "red bold" if freq_over else ""
            ac = "red bold" if amp_over else ""
            freq_m = f"[{fc}]{freq}[/{fc}]" if fc else freq
            amp_m = f"[{ac}]{amp}[/{ac}]" if ac else amp

            line = f"  [{color} bold]CH{ch_id}[/{color} bold]  {freq_m}  {amp_m}  offset {offset}  {badge}"
            if amp_over:
                line += f"\n       [red bold]OVER LIMIT: {amp} > max {vpp_upper}Vpp[/red bold]"
            if freq_over:
                line += f"\n       [red bold]OVER LIMIT: {freq} > max {_fmt_eng(freq_upper, 'Hz')}[/red bold]"
            body.mount(Static(line, markup=True, classes="detail-section"))

            # Per-channel parameter inputs
            inp_row = Horizontal(classes="input-row")
            body.mount(inp_row)
            f_default = f"{freq_val:g}" if freq_val is not None else "10000"
            a_default = f"{amp_val:g}" if amp_val is not None else "1"
            o_default = f"{offset_val:g}" if offset_val is not None else "0"
            inp_row.mount(Input(placeholder="Freq (Hz)", value=f_default, id=f"inp-{name}-{ch_id}-freq"))
            inp_row.mount(Input(placeholder="Amp (Vpp)", value=a_default, id=f"inp-{name}-{ch_id}-amp"))
            inp_row.mount(Input(placeholder="Offset (V)", value=o_default, id=f"inp-{name}-{ch_id}-off"))
            inp_row.mount(Button("Apply", id=f"awgapply-{name}-{ch_id}", variant="primary"))

            # Waveform selector buttons
            wave_row = Horizontal(classes="action-row")
            body.mount(wave_row)
            for wf in self._AWG_WAVEFORMS:
                wave_row.mount(Button(wf, id=f"qa-{name}-wave{ch_id}-{wf.lower()}", variant="default"))

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
        trig_color = "green" if trigger and trigger.upper() in ("TD", "TRIGGERED") else "yellow"

        lines = [
            f"  Trigger: [{trig_color}]{trigger}[/{trig_color}]",
            f"  Channels: {num_ch}",
        ]
        body.mount(Static("\n".join(lines), markup=True, classes="detail-section"))

        # Per-channel enable/disable
        ch_row = Horizontal(classes="action-row")
        body.mount(ch_row)
        for ch_num in range(1, num_ch + 1):
            ch_row.mount(Button(f"CH{ch_num} ON", id=f"qa-{name}-scopech{ch_num}on", variant="success"))
            ch_row.mount(Button(f"CH{ch_num} OFF", id=f"qa-{name}-scopech{ch_num}off", variant="error"))

        row = Horizontal(classes="action-row")
        body.mount(row)
        row.mount(Button("Run", id=f"qa-{name}-run", variant="success"))
        row.mount(Button("Stop", id=f"qa-{name}-stop", variant="error"))
        row.mount(Button("Single", id=f"qa-{name}-single", variant="warning"))
        row.mount(Button("Autoset", id=f"qa-{name}-autoset", variant="primary"))

    def _render_ev2300(self, body: Vertical, detail: dict) -> None:
        name = detail.get("name", "ev2300")
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

        # I2C read/write controls
        body.mount(Static("  [bold]I2C Interface[/bold]", markup=True, classes="detail-section"))
        addr_row = Horizontal(classes="input-row")
        body.mount(addr_row)
        addr_row.mount(Input(placeholder="Addr (hex, e.g. 0x08)", value="0x08", id=f"ev-{name}-addr"))
        addr_row.mount(Input(placeholder="Reg (hex, e.g. 0x00)", value="0x00", id=f"ev-{name}-reg"))
        addr_row.mount(Input(placeholder="Value (hex)", value="", id=f"ev-{name}-val"))

        read_row = Horizontal(classes="action-row")
        body.mount(read_row)
        read_row.mount(Button("Read Word", id=f"qa-{name}-readword", variant="primary"))
        read_row.mount(Button("Read Byte", id=f"qa-{name}-readbyte", variant="primary"))
        read_row.mount(Button("Read Block", id=f"qa-{name}-readblock", variant="primary"))

        write_row = Horizontal(classes="action-row")
        body.mount(write_row)
        write_row.mount(Button("Write Word", id=f"qa-{name}-writeword", variant="warning"))
        write_row.mount(Button("Write Byte", id=f"qa-{name}-writebyte", variant="warning"))

    # ------------------------------------------------------------------
    # Quick-action button handler
    # ------------------------------------------------------------------

    def _read_input(self, input_id: str) -> str:
        """Read the value from an Input widget by ID, returning '' if missing."""
        try:
            return self.query_one(f"#{input_id}", Input).value.strip()
        except Exception:  # noqa: BLE001
            return ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Translate button presses into QuickAction, SetLimit, or state snapshot messages."""
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

        # PSU/SMU Apply buttons: apply-<device>-<channel>
        if bid.startswith("apply-"):
            event.stop()
            rest = bid[6:]  # <device>-<channel>
            parts = rest.rsplit("-", 1)
            if len(parts) == 2:
                dev_name, ch = parts
                v = self._read_input(f"inp-{dev_name}-{ch}-v")
                i = self._read_input(f"inp-{dev_name}-{ch}-i")
                cmds = [f"use {dev_name}"]
                if v:
                    cmds.append(f"psu chan {ch} set_voltage {v}")
                if i:
                    cmds.append(f"psu chan {ch} set_current_limit {i}")
                self.post_message(self.QuickAction("\n".join(cmds)))
            return

        # AWG Apply buttons: awgapply-<device>-<channel>
        if bid.startswith("awgapply-"):
            event.stop()
            rest = bid[9:]
            parts = rest.rsplit("-", 1)
            if len(parts) == 2:
                dev_name, ch = parts
                freq = self._read_input(f"inp-{dev_name}-{ch}-freq")
                amp = self._read_input(f"inp-{dev_name}-{ch}-amp")
                off = self._read_input(f"inp-{dev_name}-{ch}-off")
                cmds = [f"use {dev_name}"]
                if freq:
                    cmds.append(f"awg chan {ch} set_frequency {freq}")
                if amp:
                    cmds.append(f"awg chan {ch} set_amplitude {amp}")
                if off:
                    cmds.append(f"awg chan {ch} set_offset {off}")
                self.post_message(self.QuickAction("\n".join(cmds)))
            return

        # Safety limit buttons: setlim-<device>-<channel>
        if bid.startswith("setlim-"):
            event.stop()
            rest = bid[7:]
            parts = rest.rsplit("-", 1)
            if len(parts) == 2:
                dev_name, ch = parts
                v_lim = self._read_input(f"lim-{dev_name}-{ch}-v")
                i_lim = self._read_input(f"lim-{dev_name}-{ch}-i")
                cmds = []
                if v_lim:
                    cmds.append(f"upper_limit {dev_name} chan {ch} voltage {v_lim}")
                if i_lim:
                    cmds.append(f"upper_limit {dev_name} chan {ch} current {i_lim}")
                if cmds:
                    self.post_message(self.SetLimitRequested("\n".join(cmds)))
            return

        # Quick action buttons: qa-<device>-<action>
        if not bid.startswith("qa-"):
            return
        event.stop()

        # Parse: qa-<device_name>-<action>
        rest = bid[3:]

        # Static command map for simple actions
        cmd_map = {
            "on": lambda d: f"use {d}\npsu chan on",
            "off": lambda d: f"use {d}\npsu chan off",
            "allon": lambda d: f"use {d}\npsu output on",
            "alloff": lambda d: f"use {d}\npsu output off",
            "read": lambda d: f"use {d}\ndmm read",
            "run": lambda d: f"use {d}\nscope run",
            "stop": lambda d: f"use {d}\nscope stop",
            "single": lambda d: f"use {d}\nscope single",
            "autoset": lambda d: f"use {d}\nscope autoset",
            "modev": lambda d: f"use {d}\nsmu mode voltage",
            "modei": lambda d: f"use {d}\nsmu mode current",
        }

        # Try to match against known action suffixes
        for action_key, cmd_fn in cmd_map.items():
            if rest.endswith(f"-{action_key}"):
                dev_name = rest[: -(len(action_key) + 1)]
                self.post_message(self.QuickAction(cmd_fn(dev_name)))
                return

        # Per-channel AWG ON/OFF: qa-<dev>-ch<N>on / qa-<dev>-ch<N>off
        import re

        m = re.match(r"(.+)-ch(\d+)(on|off)$", rest)
        if m:
            dev_name, ch_num, state = m.group(1), m.group(2), m.group(3)
            self.post_message(self.QuickAction(f"use {dev_name}\nawg chan {ch_num} {state}"))
            return

        # Scope per-channel: qa-<dev>-scopech<N>on / qa-<dev>-scopech<N>off
        m = re.match(r"(.+)-scopech(\d+)(on|off)$", rest)
        if m:
            dev_name, ch_num, state = m.group(1), m.group(2), m.group(3)
            self.post_message(self.QuickAction(f"use {dev_name}\nscope chan {ch_num} {state}"))
            return

        # AWG waveform: qa-<dev>-wave<ch>-<waveform>
        m = re.match(r"(.+)-wave(\d+)-(\w+)$", rest)
        if m:
            dev_name, ch_num, wf = m.group(1), m.group(2), m.group(3)
            self.post_message(self.QuickAction(f"use {dev_name}\nawg chan {ch_num} set_function {wf}"))
            return

        # DMM mode: qa-<dev>-mode-<mode_id>
        m = re.match(r"(.+)-mode-(\w+)$", rest)
        if m:
            dev_name, mode_id = m.group(1), m.group(2)
            self.post_message(self.QuickAction(f"use {dev_name}\ndmm mode {mode_id}"))
            return

        # EV2300 I2C operations
        m = re.match(r"(.+)-(read\w+|write\w+)$", rest)
        if m:
            dev_name, op = m.group(1), m.group(2)
            addr = self._read_input(f"ev-{dev_name}-addr")
            reg = self._read_input(f"ev-{dev_name}-reg")
            val = self._read_input(f"ev-{dev_name}-val")
            if op in ("readword", "readbyte", "readblock"):
                cmd = f"use {dev_name}\nev2300 {op.replace('read', 'read_')} {addr} {reg}"
            else:
                cmd = f"use {dev_name}\nev2300 {op.replace('write', 'write_')} {addr} {reg} {val}"
            self.post_message(self.QuickAction(cmd))
            return
