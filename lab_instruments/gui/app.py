"""SCPI Instrument Toolkit - Desktop GUI."""

from __future__ import annotations

import argparse
import atexit
import contextlib
import io
import re
import signal
import sys
from enum import Enum, auto
from typing import Any

from PySide6.QtCore import QPoint, QRect, QSettings, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QAction, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDockWidget,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# -- ANSI helpers ------------------------------------------------------------

_ANSI_RE = re.compile(r"\033\[([0-9;]*)m")
_ANSI_COLORS = {"91": "#f38ba8", "92": "#1e7a1e", "93": "#b8860b", "94": "#1a6bbf", "96": "#0e7a70"}


def _ansi_to_html(text: str) -> str:
    if "\033" not in text:
        return _esc(text).replace("\n", "<br>")
    parts: list[str] = []
    opens = 0
    end = 0
    for m in _ANSI_RE.finditer(text):
        parts.append(_esc(text[end : m.start()]))
        end = m.end()
        for c in (m.group(1) or "0").split(";"):
            c = c.lstrip("0") or "0"
            if c == "0":
                parts.append("</span>" * opens)
                opens = 0
            elif c == "1":
                parts.append("<span style='font-weight:bold'>")
                opens += 1
            elif c in _ANSI_COLORS:
                parts.append(f"<span style='color:{_ANSI_COLORS[c]}'>")
                opens += 1
    parts.append(_esc(text[end:]))
    parts.append("</span>" * opens)
    return "".join(parts).replace("\n", "<br>")


def _esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# -- Dispatcher --------------------------------------------------------------


class _Dispatcher:
    def __init__(self, mock: bool = False) -> None:
        from lab_instruments.repl.shell import InstrumentRepl

        saved_int = signal.getsignal(signal.SIGINT)
        saved_term = signal.getsignal(signal.SIGTERM) if hasattr(signal, "SIGTERM") else None

        if mock:
            from lab_instruments import mock_instruments
            from lab_instruments.src import discovery as _disc

            _disc.InstrumentDiscovery.__init__ = lambda self: None
            _disc.InstrumentDiscovery.scan = lambda self, verbose=True: mock_instruments.get_mock_devices(verbose)

        self._repl = InstrumentRepl()

        signal.signal(signal.SIGINT, saved_int)
        if saved_term is not None:
            signal.signal(signal.SIGTERM, saved_term)

        atexit.unregister(self._repl._cleanup_on_exit)
        self._repl._cleanup_done = True
        self._repl._term_fd = None
        self._repl._term_settings = None

        if hasattr(self._repl, "_scan_done"):
            self._repl._scan_done.wait(timeout=15)

        if mock:
            self.run("scan")

    def run(self, command: str) -> str:
        buf = io.StringIO()
        old_repl_stdout = self._repl.stdout
        self._repl.stdout = buf
        with contextlib.redirect_stdout(buf):
            self._repl.onecmd(command)
        self._repl.stdout = old_repl_stdout
        return buf.getvalue()

    @property
    def registry(self):
        return self._repl.ctx.registry

    def device(self, name: str) -> Any | None:
        return self.registry.devices.get(name)

    def devices_of_type(self, base: str) -> list[tuple[str, str]]:
        result = []
        for name in sorted(self.registry.devices):
            if re.sub(r"\d+$", "", name) == base:
                result.append((name, self.registry.display_name(name)))
        return result

    def has_cap(self, name: str, cap_name: str) -> bool:
        from lab_instruments.repl.capabilities import Capability

        cap_map = {
            "multi_channel": Capability.PSU_MULTI_CHANNEL,
            "readback": Capability.PSU_READBACK,
            "tracking": Capability.PSU_TRACKING,
            "save_recall": Capability.PSU_SAVE_RECALL,
        }
        cap = cap_map.get(cap_name)
        return bool(cap and self.registry.has_cap(name, cap))


# -- Helpers -----------------------------------------------------------------


def _mono(size: int = 11) -> QFont:
    f = QFont("Monospace", size)
    f.setStyleHint(QFont.StyleHint.Monospace)
    f.setFamilies(["JetBrains Mono", "Cascadia Code", "Consolas", "Courier New", "monospace"])
    return f


# -- Console -----------------------------------------------------------------


class _Console(QWidget):
    command_ran = Signal()  # emitted after every non-clear command

    def __init__(self, d: _Dispatcher, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._history: list[str] = []
        self._hist_idx = -1

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(_mono())
        self._output.document().setMaximumBlockCount(5000)
        lay.addWidget(self._output, 1)

        row = QHBoxLayout()
        lbl = QLabel("eset>")
        lbl.setFont(_mono())
        lbl.setStyleSheet("color: #1a6bbf;")
        row.addWidget(lbl)
        self._input = QLineEdit()
        self._input.setFont(_mono())
        self._input.setPlaceholderText("Type a command...")
        self._input.returnPressed.connect(self._on_submit)
        row.addWidget(self._input, 1)
        lay.addLayout(row)

    def keyPressEvent(self, ev):  # noqa: N802
        if self._input.hasFocus():
            if ev.key() == Qt.Key.Key_Up:
                self._nav(1)
                return
            if ev.key() == Qt.Key.Key_Down:
                self._nav(-1)
                return
        super().keyPressEvent(ev)

    def _nav(self, d: int) -> None:
        if not self._history:
            return
        self._hist_idx = max(-1, min(len(self._history) - 1, self._hist_idx + d))
        self._input.setText("" if self._hist_idx == -1 else self._history[-(self._hist_idx + 1)])

    def _on_submit(self) -> None:
        cmd = self._input.text().strip()
        if not cmd:
            return
        self._history.append(cmd)
        if len(self._history) > 500:
            self._history = self._history[-500:]
        self._hist_idx = -1
        self._input.clear()
        if cmd == "clear":
            self._output.clear()
            return
        self.log(f"<b style='color:#1a6bbf'>eset&gt;</b> {_esc(cmd)}")
        result = self._d.run(cmd)
        if result.strip():
            self.log(_ansi_to_html(result.rstrip("\n")))
        self.command_ran.emit()

    def log(self, html: str) -> None:
        sb = self._output.verticalScrollBar()
        at_bottom = sb.value() >= sb.maximum() - 4
        self._output.append(html)
        if at_bottom:
            sb.setValue(sb.maximum())

    def log_action(self, cmd: str, result: str = "") -> None:
        self.log(f"<span style='color:#555'>[gui]</span> <b style='color:#1a6bbf'>eset&gt;</b> {_esc(cmd)}")
        if result.strip():
            self.log(_ansi_to_html(result.rstrip("\n")))


# -- Spinbox: cursor stays on the number, not the suffix ---------------------


class _NumSpin(QDoubleSpinBox):
    def _select_number(self) -> None:
        le = self.lineEdit()
        end = len(le.text()) - len(self.suffix())
        le.setSelection(0, max(end, 0))

    def focusInEvent(self, event):  # noqa: N802
        super().focusInEvent(event)
        QTimer.singleShot(0, self._select_number)

    def mousePressEvent(self, event):  # noqa: N802
        super().mousePressEvent(event)
        QTimer.singleShot(0, self._select_number)


# -- Channel accent colors ---------------------------------------------------

_CH_ACCENTS = [
    "#b8860b",  # ch1 – yellow  (e.g. P6V)
    "#1a6bbf",  # ch2 – blue    (e.g. P25V / P30V)
    "#7c3aed",  # ch3 – mauve   (e.g. N25V / N30V)
    "#1e7a1e",  # ch4 – green
    "#0e7a70",  # ch5 – teal
    "#c45c00",  # ch6 – peach
]


# -- PSU channel widget ------------------------------------------------------


class _PSUChannel(QGroupBox):
    def __init__(
        self,
        channel: int,
        label: str,
        max_v: float | None = None,
        max_i: float | None = None,
        accent: str = "#1a6bbf",
        parent: QWidget | None = None,
    ) -> None:
        title = f"{label}   {max_v:g} V / {max_i:g} A" if max_v is not None and max_i is not None else label
        super().__init__(title, parent)
        self.channel = channel
        self._accent = accent
        self._max_v = max_v if max_v is not None else 60.0
        self._max_i = max_i if max_i is not None else 10.0
        self.setStyleSheet(
            f"QGroupBox {{ border: 2px solid #aaa; border-radius: 7px; "
            f"margin-top: 12px; padding-top: 14px; }}"
            f"QGroupBox::title {{ color: {accent}; subcontrol-origin: margin; "
            f"left: 10px; padding: 0 6px; font-weight: bold; }}"
        )
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(8, 8, 8, 8)

        meas = QHBoxLayout()
        meas.setSpacing(5)

        for attr, unit, color in [("v_display", "V", "#1e7a1e"), ("i_display", "A", "#c45c00")]:
            disp = QLabel("0.000")
            disp.setFont(_mono(18))
            disp.setStyleSheet(
                f"color: {color}; border-radius: 5px; "
                f"padding: 4px 8px"
            )
            disp.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            disp.setMinimumHeight(42)
            setattr(self, attr, disp)
            meas.addWidget(disp, 1)

        layout.addLayout(meas)

        sp_row = QHBoxLayout()
        sp_row.setSpacing(4)

        self.v_spin = _NumSpin()
        self.v_spin.setRange(0, self._max_v)
        self.v_spin.setDecimals(3)
        self.v_spin.setSingleStep(0.1)
        self.v_spin.setSuffix(" V")
        self.v_spin.setMinimumWidth(88)
        sp_row.addWidget(self.v_spin, 1)

        self.i_spin = _NumSpin()
        self.i_spin.setRange(0, self._max_i)
        self.i_spin.setDecimals(4)
        self.i_spin.setSingleStep(0.01)
        self.i_spin.setValue(0.1)
        self.i_spin.setSuffix(" A")
        self.i_spin.setMinimumWidth(88)
        sp_row.addWidget(self.i_spin, 1)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {self._accent}; font-weight: bold; "
            f"border: 1px solid {self._accent}88; border-radius: 4px; padding: 4px 10px; }} "
            f"QPushButton:hover {{ background: {self._accent}; color: #1e1e2e; }}"
        )
        sp_row.addWidget(self.apply_btn)
        layout.addLayout(sp_row)

        self.toggle_btn = QPushButton("○  OUTPUT OFF")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setMinimumHeight(32)
        self._set_toggle_style(False)
        layout.addWidget(self.toggle_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        
        layout.addWidget(sep)

        lim_row = QHBoxLayout()
        lim_row.setSpacing(4)

        lim_lbl = QLabel("Limits")
        lim_lbl.setStyleSheet("font-size: 10px;")
        lim_row.addWidget(lim_lbl)

        self.v_lim_spin = _NumSpin()
        self.v_lim_spin.setRange(0, self._max_v)
        self.v_lim_spin.setDecimals(3)
        self.v_lim_spin.setSingleStep(0.1)
        self.v_lim_spin.setSuffix(" V")
        self.v_lim_spin.setValue(self._max_v)
        self.v_lim_spin.setMinimumWidth(84)
        self.v_lim_spin.setStyleSheet(
            "QDoubleSpinBox { font-size: 11px; }"
        )
        lim_row.addWidget(self.v_lim_spin, 1)

        self.i_lim_spin = _NumSpin()
        self.i_lim_spin.setRange(0, self._max_i)
        self.i_lim_spin.setDecimals(4)
        self.i_lim_spin.setSingleStep(0.01)
        self.i_lim_spin.setSuffix(" A")
        self.i_lim_spin.setValue(self._max_i)
        self.i_lim_spin.setMinimumWidth(84)
        self.i_lim_spin.setStyleSheet(
            "QDoubleSpinBox { font-size: 11px; }"
        )
        lim_row.addWidget(self.i_lim_spin, 1)

        self.set_lim_btn = QPushButton("✓")
        self.set_lim_btn.setFixedWidth(28)
        self._lim_state = "idle"
        self._set_lim_state("idle")
        lim_row.addWidget(self.set_lim_btn)
        layout.addLayout(lim_row)

        self.v_lim_spin.valueChanged.connect(self._on_lim_spin_changed)
        self.i_lim_spin.valueChanged.connect(self._on_lim_spin_changed)

    def _on_lim_spin_changed(self) -> None:
        if self._lim_state != "pending":
            self._set_lim_state("pending")

    def _set_lim_state(self, state: str) -> None:
        self._lim_state = state
        if state == "active":
            # Green: limit is confirmed and active
            self.set_lim_btn.setText("✓")
            self.set_lim_btn.setStyleSheet(
                "QPushButton { border: 2px solid #28a745; color: #a6e3a1; border-radius: 4px; "
                "padding: 3px; background: #d4edda; font-weight: bold; }"
                "QPushButton:hover { background: #28a745; color: white; }"
            )
        elif state == "pending":
            # Amber: value changed but not yet applied
            self.set_lim_btn.setText("!")
            self.set_lim_btn.setStyleSheet(
                "QPushButton { border: 2px solid orange; color: darkorange; border-radius: 4px; "
                "padding: 3px; font-weight: bold; }"
                "QPushButton:hover { background: orange; color: white; }"
            )
        else:
            # Idle: no active limit constraint
            self.set_lim_btn.setText("✓")
            self.set_lim_btn.setStyleSheet(
                "QPushButton { border: 1px solid #aaa; border-radius: 4px; padding: 3px; }"
                "QPushButton:hover { background: #ddd; }"
            )

    def _set_toggle_style(self, on: bool) -> None:
        if on:
            self.toggle_btn.setText("●  OUTPUT ON")
            self.toggle_btn.setStyleSheet(
                "QPushButton { background: #d4edda; color: #155724; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #28a745; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #28a745; color: white; }"
            )
        else:
            self.toggle_btn.setText("○  OUTPUT OFF")
            self.toggle_btn.setStyleSheet(
                "QPushButton { background: transparent; color: #c0392b; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #c0392b88; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #c0392b; color: white; }"
            )

    def _read_v_i(self, dev: Any, ch_key: str | None) -> tuple[float, float]:
        try:
            v = dev.get_voltage_setpoint(ch_key) if ch_key else dev.get_voltage_setpoint()
        except TypeError:
            v = dev.get_voltage_setpoint()
        try:
            i = dev.get_current_limit(ch_key) if ch_key else dev.get_current_limit()
        except TypeError:
            i = dev.get_current_limit()
        return v, i

    def init_from_device(self, dev: Any, ch_key: str | None = None) -> None:
        v, i = self._read_v_i(dev, ch_key)
        self.v_spin.blockSignals(True)
        self.v_spin.setValue(v)
        self.v_spin.blockSignals(False)
        self.i_spin.blockSignals(True)
        self.i_spin.setValue(i)
        self.i_spin.blockSignals(False)

    def sync_from_device(self, dev: Any, output_state: bool | None = None, ch_key: str | None = None) -> None:
        v, i = self._read_v_i(dev, ch_key)
        on = output_state if output_state is not None else dev.get_output_state()

        v_w = len(str(int(self._max_v))) + 4
        i_w = len(str(int(self._max_i))) + 5

        v_lim = self.v_lim_spin.value()
        i_lim = self.i_lim_spin.value()
        v_over = v > v_lim + 1e-9
        i_over = i > i_lim + 1e-9

        v_color = "#f38ba8" if v_over else "#1e7a1e"
        i_color = "#c0392b" if i_over else "#c45c00"
        self.v_display.setStyleSheet(
            f"color: {v_color}; border-radius: 5px; "
            f"padding: 4px 8px"
        )
        self.i_display.setStyleSheet(
            f"color: {i_color}; border-radius: 5px; "
            f"padding: 4px 8px"
        )
        self.v_display.setText(f"{v:{v_w}.3f} V")
        self.i_display.setText(f"{i:{i_w}.4f} A")

        self.toggle_btn.blockSignals(True)
        self.toggle_btn.setChecked(on)
        self.toggle_btn.blockSignals(False)
        self._set_toggle_style(on)


# -- PSU device card (one per PSU, all shown side by side) -------------------


class _PSUBlock(QFrame):
    """Self-contained card for one PSU device."""

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._psu = name
        self._chs: dict[int, _PSUChannel] = {}
        self._ch_output: dict[int, bool] = {}
        self._ch_keys: dict[int, str | None] = {}
        self.setObjectName("psublock")
        self.setStyleSheet(
            "#psublock { border: 1px solid #ccc; border-radius: 10px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._build()
        self._rebuild()
        self._init_channels()
        self._poll()

    def _con(self) -> _Console | None:
        w = self.parent()
        while w is not None:
            if hasattr(w, "_console"):
                return w._console  # type: ignore[attr-defined]
            w = w.parent()
        return None

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        hdr = QFrame()
        hdr.setStyleSheet(
            "QFrame { border-bottom: 1px solid #ccc; border-radius: 0; }"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 9, 14, 9)
        hdr_lay.setSpacing(8)

        name_lbl = QLabel(f"<b>{self._psu}</b>")
        name_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        hdr_lay.addWidget(name_lbl)

        dev = self._d.device(self._psu)
        if dev:
            disp_name = self._d.registry.display_name(self._psu)
            type_lbl = QLabel(disp_name)
            type_lbl.setStyleSheet("font-size: 11px;")
            hdr_lay.addWidget(type_lbl, 1)
        else:
            hdr_lay.addStretch(1)

        outer.addWidget(hdr)

        body = QWidget()
        
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(10, 10, 10, 6)
        body_lay.setSpacing(8)

        self._ch_row_w = QWidget()
        
        self._ch_row_lay = QHBoxLayout(self._ch_row_w)
        self._ch_row_lay.setContentsMargins(0, 0, 0, 0)
        self._ch_row_lay.setSpacing(8)
        body_lay.addWidget(self._ch_row_w)

        foot = QHBoxLayout()
        foot.setSpacing(6)

        for text, color, slot in [
            ("All ON", "#1e7a1e", self._all_on),
            ("All OFF", "#c0392b", self._all_off),
        ]:
            b = QPushButton(text)
            b.setStyleSheet(
                f"QPushButton {{ border: 1px solid {color}66; color: {color}; border-radius: 4px; "
                f"padding: 4px 12px; font-weight: bold; font-size: 11px; }} "
                f"QPushButton:hover {{ background: {color}; }}"
            )
            b.clicked.connect(slot)
            foot.addWidget(b)

        foot.addStretch()

        self._track_btn = QPushButton("Track: OFF")
        self._track_btn.setCheckable(True)
        self._track_btn.setVisible(False)
        self._track_btn.toggled.connect(self._on_track)
        foot.addWidget(self._track_btn)

        for text, action in [("Save", "save"), ("Recall", "recall")]:
            b = QPushButton(text)
            b.setVisible(False)
            b.clicked.connect(lambda _, a=action: self._save_recall(a))
            foot.addWidget(b)
            setattr(self, f"_{action}_btn", b)

        body_lay.addLayout(foot)

        self._status = QLabel("")
        self._status.setStyleSheet("font-size: 10px;")
        body_lay.addWidget(self._status)
        body_lay.addStretch(1)

        outer.addWidget(body, 1)

    def _rebuild(self) -> None:
        for w in list(self._chs.values()):
            self._ch_row_lay.removeWidget(w)
            w.deleteLater()
        self._chs.clear()

        dev = self._d.device(self._psu)
        if not dev:
            return

        multi = self._d.has_cap(self._psu, "multi_channel")
        ch_map = getattr(dev, "CHANNEL_MAP", None)
        ch_limits = getattr(dev, "CHANNEL_LIMITS", {})
        dev_max_v: float | None = getattr(dev, "MAX_VOLTAGE", None)
        dev_max_i: float | None = getattr(dev, "MAX_CURRENT", None)

        if multi and ch_map:
            keys = list(ch_map.keys())
            defs = [(i + 1, ch_map[k], k) for i, k in enumerate(keys)]
        elif multi:
            defs = [(1, "CH1 (P6V)", None), (2, "CH2 (P25V)", None), (3, "CH3 (N25V)", None)]
        else:
            defs = [(1, "Output", None)]

        self._ch_keys.clear()
        for num, label, ch_key in defs:
            if ch_key and ch_key in ch_limits:
                max_v, max_i = ch_limits[ch_key]
            elif dev_max_v is not None:
                max_v, max_i = dev_max_v, dev_max_i
            else:
                max_v, max_i = None, None

            accent = _CH_ACCENTS[(num - 1) % len(_CH_ACCENTS)]
            ch = _PSUChannel(num, label, max_v, max_i, accent)
            ch.apply_btn.clicked.connect(lambda _, n=num: self._apply(n))
            ch.toggle_btn.clicked.connect(lambda checked, n=num: self._output(n, checked))
            ch.set_lim_btn.clicked.connect(lambda _, n=num: self._set_limit(n))
            self._chs[num] = ch
            self._ch_keys[num] = ch_key
            self._ch_row_lay.addWidget(ch)

        self._track_btn.setVisible(multi and self._d.has_cap(self._psu, "tracking"))
        self._save_btn.setVisible(self._d.has_cap(self._psu, "save_recall"))
        self._recall_btn.setVisible(self._d.has_cap(self._psu, "save_recall"))

    def _init_channels(self) -> None:
        dev = self._d.device(self._psu)
        if not dev:
            return
        multi = self._d.has_cap(self._psu, "multi_channel")
        if multi:
            self._ch_output = {num: False for num in self._chs}
        else:
            state = dev.get_output_state()
            self._ch_output = {num: state for num in self._chs}

        ctx_limits = self._d._repl.ctx.safety_limits
        for num, w in self._chs.items():
            ch_key = self._ch_keys.get(num)
            w.init_from_device(dev, ch_key)
            saved = ctx_limits.get((self._psu, num), {})
            if "voltage_upper" in saved:
                w.v_lim_spin.blockSignals(True)
                w.v_lim_spin.setValue(saved["voltage_upper"])
                w.v_lim_spin.blockSignals(False)
            if "current_upper" in saved:
                w.i_lim_spin.blockSignals(True)
                w.i_lim_spin.setValue(saved["current_upper"])
                w.i_lim_spin.blockSignals(False)

    @Slot()
    def _poll(self) -> None:
        dev = self._d.device(self._psu)
        if not dev:
            return
        multi = self._d.has_cap(self._psu, "multi_channel")
        for ch_num, w in self._chs.items():
            ch_key = self._ch_keys.get(ch_num)
            state: bool | None = None
            if multi:
                try:
                    # Direct per-channel query — avoids stateful select_channel side effects
                    state = dev.get_output_state(ch_key)
                except TypeError:
                    # Device doesn't support ch arg — fall back to cached value
                    state = self._ch_output.get(ch_num, False)
                if state is not None:
                    self._ch_output[ch_num] = state
            w.sync_from_device(dev, state, ch_key)

    def _apply(self, ch_num: int) -> None:
        dev = self._d.device(self._psu)
        w = self._chs.get(ch_num)
        if not dev or not w:
            return
        v, i = w.v_spin.value(), w.i_spin.value()
        v_lim, i_lim = w.v_lim_spin.value(), w.i_lim_spin.value()

        if v > v_lim + 1e-9:
            self._status.setText(f"BLOCKED: {v}V > limit {v_lim}V")
            self._status.setStyleSheet("color: #c0392b; font-size: 10px; font-weight: bold;")
            con = self._con()
            if con:
                con.log_action(f"{self._psu} ch{ch_num}", f"[BLOCKED] {v}V > limit {v_lim}V")
            return
        if i > i_lim + 1e-9:
            self._status.setText(f"BLOCKED: {i}A > limit {i_lim}A")
            self._status.setStyleSheet("color: #c0392b; font-size: 10px; font-weight: bold;")
            con = self._con()
            if con:
                con.log_action(f"{self._psu} ch{ch_num}", f"[BLOCKED] {i}A > limit {i_lim}A")
            return

        multi = self._d.has_cap(self._psu, "multi_channel")
        if multi:
            key = self._ch_keys.get(ch_num) or str(ch_num)
            dev.set_output_channel(key, v, i)
            cmd = f"{self._psu} set {ch_num} {v} {i}"
        else:
            dev.set_voltage(v)
            dev.set_current_limit(i)
            cmd = f"{self._psu} set {v} {i}"

        con = self._con()
        if con:
            con.log_action(cmd, f"Set: {v}V @ {i}A")
        self._status.setText(f"Applied: {v}V @ {i}A")
        self._status.setStyleSheet("color: #155724; font-size: 10px;")
        self._poll()

    def _set_limit(self, ch_num: int) -> None:
        w = self._chs.get(ch_num)
        if not w:
            return
        v_lim, i_lim = w.v_lim_spin.value(), w.i_lim_spin.value()
        w.v_spin.setMaximum(v_lim)
        w.i_spin.setMaximum(i_lim)
        self._d._repl.ctx.safety_limits[(self._psu, ch_num)] = {
            "voltage_upper": v_lim,
            "current_upper": i_lim,
        }
        w._set_lim_state("active")
        self._status.setText(f"CH{ch_num} limits: ≤{v_lim}V / ≤{i_lim}A")
        self._status.setStyleSheet("color: darkorange; font-size: 10px;")
        con = self._con()
        if con:
            con.log_action(f"limit {self._psu} ch{ch_num} {v_lim}V {i_lim}A", "Safety limits set")

    def _output(self, ch_num: int, on: bool) -> None:
        dev = self._d.device(self._psu)
        if not dev:
            return
        multi = self._d.has_cap(self._psu, "multi_channel")
        if multi and hasattr(dev, "select_channel"):
            key = self._ch_keys.get(ch_num)
            if key:
                dev.select_channel(key)
        dev.enable_output(on)
        self._ch_output[ch_num] = on
        cmd = f"{self._psu} chan {ch_num} {'on' if on else 'off'}"
        con = self._con()
        if con:
            con.log_action(cmd, f"Output {'enabled' if on else 'disabled'}")
        self._poll()

    @Slot()
    def _all_on(self) -> None:
        dev = self._d.device(self._psu)
        if dev:
            dev.enable_output(True)
            for num in self._chs:
                self._ch_output[num] = True
            con = self._con()
            if con:
                con.log_action(f"{self._psu} on", "All outputs ON")
            self._poll()

    @Slot()
    def _all_off(self) -> None:
        dev = self._d.device(self._psu)
        if dev:
            dev.enable_output(False)
            for num in self._chs:
                self._ch_output[num] = False
            con = self._con()
            if con:
                con.log_action(f"{self._psu} off", "All outputs OFF")
            self._poll()

    @Slot(bool)
    def _on_track(self, on: bool) -> None:
        dev = self._d.device(self._psu)
        if dev and hasattr(dev, "set_tracking"):
            dev.set_tracking(on)
            self._track_btn.setText(f"Track: {'ON' if on else 'OFF'}")

    def _save_recall(self, action: str) -> None:
        dev = self._d.device(self._psu)
        if dev:
            (dev.save_state if action == "save" else dev.recall_state)(1)
            con = self._con()
            if con:
                con.log_action(f"{self._psu} {action} 1")

    def stop(self) -> None:
        pass  # no-op: no timer to stop


# -- AWG device card ---------------------------------------------------------

_AWG_WAVEFORMS = ["SIN", "SQU", "RAMP", "PULS", "NOIS", "DC"]
_AWG_CH_ACCENTS = ["#1a6bbf", "#7c3aed"]  # CH1: blue, CH2: purple


def _get_awg_waveforms(dev) -> list[str]:
    """Return the waveform list for this AWG device, falling back to the default."""
    if hasattr(dev, "VALID_WAVEFORMS"):
        wf = dev.VALID_WAVEFORMS
        return list(wf) if isinstance(wf, list) else sorted(wf)
    if hasattr(dev, "WAVEFORMS") and isinstance(getattr(dev, "WAVEFORMS", None), dict):
        return [k.upper() for k in dev.WAVEFORMS]
    return list(_AWG_WAVEFORMS)


class _AWGChannel(QGroupBox):
    def __init__(self, channel: int, accent: str, waveforms: list[str] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(f"CH{channel}", parent)
        self.channel = channel
        self._accent = accent
        self._waveforms = waveforms if waveforms is not None else _AWG_WAVEFORMS
        self.setStyleSheet(
            f"QGroupBox {{ border: 2px solid #aaa; border-radius: 7px; "
            f"margin-top: 12px; padding-top: 14px; }}"
            f"QGroupBox::title {{ color: {accent}; subcontrol-origin: margin; "
            f"left: 10px; padding: 0 6px; font-weight: bold; }}"
        )
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(8, 8, 8, 8)

        # Display row: frequency + amplitude
        meas = QHBoxLayout()
        meas.setSpacing(5)
        self.freq_display = QLabel("10000.000 Hz")
        self.freq_display.setFont(_mono(18))
        self.freq_display.setStyleSheet(
            "color: #1e7a1e; border-radius: 5px; "
            "padding: 4px 8px"
        )
        self.freq_display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.freq_display.setMinimumHeight(42)
        meas.addWidget(self.freq_display, 2)
        self.amp_display = QLabel("5.0000 Vpp")
        self.amp_display.setFont(_mono(18))
        self.amp_display.setStyleSheet(
            "color: #c45c00; border-radius: 5px; "
            "padding: 4px 8px"
        )
        self.amp_display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.amp_display.setMinimumHeight(42)
        meas.addWidget(self.amp_display, 1)
        layout.addLayout(meas)

        # Control row: waveform + freq + amp + Apply
        ctrl = QHBoxLayout()
        ctrl.setSpacing(4)
        self.wave_combo = QComboBox()
        self.wave_combo.addItems(self._waveforms)
        self.wave_combo.setMinimumWidth(65)
        ctrl.addWidget(self.wave_combo)
        self.freq_spin = _NumSpin()
        self.freq_spin.setRange(0.001, 60e6)
        self.freq_spin.setDecimals(3)
        self.freq_spin.setValue(10000.0)
        self.freq_spin.setSuffix(" Hz")
        self.freq_spin.setMinimumWidth(100)
        ctrl.addWidget(self.freq_spin, 1)
        self.amp_spin = _NumSpin()
        self.amp_spin.setRange(0.001, 20.0)
        self.amp_spin.setDecimals(4)
        self.amp_spin.setValue(5.0)
        self.amp_spin.setSuffix(" Vpp")
        self.amp_spin.setMinimumWidth(88)
        ctrl.addWidget(self.amp_spin, 1)
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {self._accent}; font-weight: bold; "
            f"border: 1px solid {self._accent}88; border-radius: 4px; padding: 4px 10px; }} "
            f"QPushButton:hover {{ background: {self._accent}; color: #1e1e2e; }}"
        )
        ctrl.addWidget(self.apply_btn)
        layout.addLayout(ctrl)

        # Toggle
        self.toggle_btn = QPushButton(f"○  CH{self.channel} OFF")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setMinimumHeight(32)
        self._set_toggle_style(False)
        layout.addWidget(self.toggle_btn)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # Offset row (secondary param, styled like PSU limits row)
        off_row = QHBoxLayout()
        off_row.setSpacing(4)
        off_lbl = QLabel("Offset")
        off_lbl.setStyleSheet("font-size: 10px;")
        off_row.addWidget(off_lbl)
        self.offset_spin = _NumSpin()
        self.offset_spin.setRange(-10.0, 10.0)
        self.offset_spin.setDecimals(4)
        self.offset_spin.setSuffix(" V")
        self.offset_spin.setMinimumWidth(88)
        self.offset_spin.setStyleSheet(
            "QDoubleSpinBox { font-size: 11px; }"
        )
        off_row.addWidget(self.offset_spin)
        off_row.addStretch()
        layout.addLayout(off_row)

    def _set_toggle_style(self, on: bool) -> None:
        if on:
            self.toggle_btn.setText(f"●  CH{self.channel} ON")
            self.toggle_btn.setStyleSheet(
                "QPushButton { background: #d4edda; color: #155724; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #28a745; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #28a745; color: white; }"
            )
        else:
            self.toggle_btn.setText(f"○  CH{self.channel} OFF")
            self.toggle_btn.setStyleSheet(
                "QPushButton { background: transparent; color: #c0392b; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #c0392b88; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #c0392b; color: white; }"
            )

    def sync_from_device(self, dev: Any, on: bool) -> None:
        with contextlib.suppress(Exception):
            freq = dev.get_frequency(self.channel)
            if freq is not None:
                if freq >= 1e6:
                    self.freq_display.setText(f"{freq / 1e6:.3f} MHz")
                elif freq >= 1e3:
                    self.freq_display.setText(f"{freq / 1e3:.3f} kHz")
                else:
                    self.freq_display.setText(f"{freq:.3f} Hz")
                self.freq_spin.blockSignals(True)
                self.freq_spin.setValue(freq)
                self.freq_spin.blockSignals(False)
        with contextlib.suppress(Exception):
            amp = dev.get_amplitude(self.channel)
            if amp is not None:
                self.amp_display.setText(f"{amp:.4f} Vpp")
                self.amp_spin.blockSignals(True)
                self.amp_spin.setValue(amp)
                self.amp_spin.blockSignals(False)
        with contextlib.suppress(Exception):
            offset = dev.get_offset(self.channel)
            if offset is not None:
                self.offset_spin.blockSignals(True)
                self.offset_spin.setValue(offset)
                self.offset_spin.blockSignals(False)
        self.toggle_btn.blockSignals(True)
        self.toggle_btn.setChecked(on)
        self.toggle_btn.blockSignals(False)
        self._set_toggle_style(on)


class _AWGBlock(QFrame):
    """Self-contained card for one AWG device."""

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._awg = name
        self._chs: dict[int, _AWGChannel] = {}
        self.setObjectName("awgblock")
        self.setStyleSheet(
            "#awgblock { border: 1px solid #ccc; border-radius: 10px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._build()
        self._poll()

    def _con(self) -> _Console | None:
        w = self.parent()
        while w is not None:
            if hasattr(w, "_console"):
                return w._console  # type: ignore[attr-defined]
            w = w.parent()
        return None

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setStyleSheet(
            "QFrame { border-bottom: 1px solid #ccc; border-radius: 0; }"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 9, 14, 9)
        hdr_lay.setSpacing(8)
        name_lbl = QLabel(f"<b>{self._awg}</b>")
        name_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        hdr_lay.addWidget(name_lbl)
        dev = self._d.device(self._awg)
        if dev:
            disp = self._d.registry.display_name(self._awg)
            type_lbl = QLabel(disp or "")
            type_lbl.setStyleSheet("font-size: 11px;")
            hdr_lay.addWidget(type_lbl, 1)
        else:
            hdr_lay.addStretch(1)
        outer.addWidget(hdr)

        # Body
        body = QWidget()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(10, 10, 10, 6)
        body_lay.setSpacing(8)

        ch_row = QHBoxLayout()
        ch_row.setSpacing(8)
        _dev = self._d.device(self._awg)
        _waveforms = _get_awg_waveforms(_dev) if _dev else None
        for i, accent in enumerate(_AWG_CH_ACCENTS, 1):
            ch = _AWGChannel(i, accent, _waveforms)
            ch.apply_btn.clicked.connect(lambda _, n=i: self._apply(n))
            ch.toggle_btn.clicked.connect(lambda checked, n=i: self._output(n, checked))
            self._chs[i] = ch
            ch_row.addWidget(ch)
        body_lay.addLayout(ch_row)

        foot = QHBoxLayout()
        foot.setSpacing(6)
        for text, color, slot in [
            ("All ON", "#1e7a1e", self._all_on),
            ("All OFF", "#c0392b", self._all_off),
        ]:
            b = QPushButton(text)
            b.setStyleSheet(
                f"QPushButton {{ border: 1px solid {color}66; color: {color}; border-radius: 4px; "
                f"padding: 4px 12px; font-weight: bold; font-size: 11px; }} "
                f"QPushButton:hover {{ background: {color}; }}"
            )
            b.clicked.connect(slot)
            foot.addWidget(b)
        foot.addStretch()
        body_lay.addLayout(foot)

        self._status = QLabel("")
        self._status.setStyleSheet("font-size: 10px;")
        body_lay.addWidget(self._status)
        body_lay.addStretch(1)

        outer.addWidget(body, 1)

    def _apply(self, ch: int) -> None:
        dev = self._d.device(self._awg)
        w = self._chs.get(ch)
        if not dev or not w:
            return
        wave = w.wave_combo.currentText()
        freq = w.freq_spin.value()
        amp = w.amp_spin.value()
        offset = w.offset_spin.value()
        try:
            dev.set_waveform(ch, wave)
            dev.set_frequency(ch, freq)
            dev.set_amplitude(ch, amp)
            dev.set_offset(ch, offset)
            msg = f"CH{ch}: {wave} {freq:.1f}Hz {amp:.4f}Vpp offset={offset:.4f}V"
            self._status.setText(msg)
            self._status.setStyleSheet("color: #155724; font-size: 10px;")
            con = self._con()
            if con:
                con.log_action(
                    f"{self._awg} wave {ch} {wave.lower()} freq={freq} amp={amp} offset={offset}", msg
                )
            self._poll()
        except Exception as exc:
            self._status.setText(str(exc))
            self._status.setStyleSheet("color: #c0392b; font-size: 10px;")

    def _output(self, ch: int, on: bool) -> None:
        dev = self._d.device(self._awg)
        if not dev:
            return
        try:
            dev.enable_output(ch, on)
            msg = f"CH{ch}: {'ON' if on else 'OFF'}"
            self._status.setText(msg)
            self._status.setStyleSheet("color: #155724; font-size: 10px;")
            con = self._con()
            if con:
                con.log_action(f"{self._awg} chan {ch} {'on' if on else 'off'}", msg)
            self._poll()
        except Exception as exc:
            self._status.setText(str(exc))
            self._status.setStyleSheet("color: #c0392b; font-size: 10px;")

    def _all_on(self) -> None:
        dev = self._d.device(self._awg)
        if not dev:
            return
        for ch in self._chs:
            with contextlib.suppress(Exception):
                dev.enable_output(ch, True)
        con = self._con()
        if con:
            con.log_action(f"{self._awg} on", "All channels ON")
        self._poll()

    def _all_off(self) -> None:
        dev = self._d.device(self._awg)
        if not dev:
            return
        for ch in self._chs:
            with contextlib.suppress(Exception):
                dev.enable_output(ch, False)
        con = self._con()
        if con:
            con.log_action(f"{self._awg} off", "All channels OFF")
        self._poll()

    @Slot()
    def _poll(self) -> None:
        dev = self._d.device(self._awg)
        if not dev:
            return
        for ch_num, w in self._chs.items():
            with contextlib.suppress(Exception):
                on = dev.get_output_state(ch_num)
                w.sync_from_device(dev, on)

    def stop(self) -> None:
        pass


# -- SMU device card ---------------------------------------------------------


class _SMUBlock(QFrame):
    """Self-contained card for one SMU device."""

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._smu = name
        self.setObjectName("smublock")
        self.setStyleSheet(
            "#smublock { border: 1px solid #ccc; border-radius: 10px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._build()
        self._poll()

    def _con(self) -> _Console | None:
        w = self.parent()
        while w is not None:
            if hasattr(w, "_console"):
                return w._console  # type: ignore[attr-defined]
            w = w.parent()
        return None

    def _build(self) -> None:
        _ACCENT = "#c0392b"
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header — identical to _PSUBlock header
        hdr = QFrame()
        hdr.setStyleSheet(
            "QFrame { border-bottom: 1px solid #ccc; border-radius: 0; }"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 9, 14, 9)
        hdr_lay.setSpacing(8)
        name_lbl = QLabel(f"<b>{self._smu}</b>")
        name_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        hdr_lay.addWidget(name_lbl)
        dev = self._d.device(self._smu)
        if dev:
            disp = self._d.registry.display_name(self._smu)
            type_lbl = QLabel(disp or "")
            type_lbl.setStyleSheet("font-size: 11px;")
            hdr_lay.addWidget(type_lbl, 1)
        else:
            hdr_lay.addStretch(1)

        # Mode combo sits in the header (right-aligned)
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["VOLTAGE", "CURRENT"])
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        hdr_lay.addWidget(self._mode_combo)
        outer.addWidget(hdr)

        # Body
        body = QWidget()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(10, 10, 10, 6)
        body_lay.setSpacing(8)

        # Channel group box — same style as _PSUChannel
        self._grp = QGroupBox("VOLTAGE MODE   ±60 V / 3 A")
        self._grp.setStyleSheet(
            f"QGroupBox {{ border: 2px solid #aaa; border-radius: 7px; "
            f"margin-top: 12px; padding-top: 14px; }}"
            f"QGroupBox::title {{ color: {_ACCENT}; subcontrol-origin: margin; "
            f"left: 10px; padding: 0 6px; font-weight: bold; }}"
        )
        grp_lay = QVBoxLayout(self._grp)
        grp_lay.setSpacing(5)
        grp_lay.setContentsMargins(8, 8, 8, 8)

        # Measurement displays — same as _PSUChannel
        meas = QHBoxLayout()
        meas.setSpacing(5)
        self._v_display = QLabel("0.000")
        self._v_display.setFont(_mono(18))
        self._v_display.setStyleSheet(
            "color: #1e7a1e; border-radius: 5px; "
            "padding: 4px 8px"
        )
        self._v_display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._v_display.setMinimumHeight(42)
        meas.addWidget(self._v_display, 1)
        self._i_display = QLabel("0.000")
        self._i_display.setFont(_mono(18))
        self._i_display.setStyleSheet(
            "color: #c45c00; border-radius: 5px; "
            "padding: 4px 8px"
        )
        self._i_display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._i_display.setMinimumHeight(42)
        meas.addWidget(self._i_display, 1)
        grp_lay.addLayout(meas)

        # Setpoint row — same layout as _PSUChannel sp_row
        sp_row = QHBoxLayout()
        sp_row.setSpacing(4)
        self._set_spin = _NumSpin()
        self._set_spin.setRange(-60.0, 60.0)
        self._set_spin.setDecimals(4)
        self._set_spin.setSingleStep(0.1)
        self._set_spin.setSuffix(" V")
        self._set_spin.setMinimumWidth(88)
        sp_row.addWidget(self._set_spin, 1)
        self._lim_spin = _NumSpin()
        self._lim_spin.setRange(0.0, 3.0)
        self._lim_spin.setDecimals(4)
        self._lim_spin.setSingleStep(0.01)
        self._lim_spin.setValue(0.1)
        self._lim_spin.setSuffix(" A")
        self._lim_spin.setMinimumWidth(88)
        sp_row.addWidget(self._lim_spin, 1)
        self._apply_btn = QPushButton("Apply")
        self._apply_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {_ACCENT}; font-weight: bold; "
            f"border: 1px solid {_ACCENT}88; border-radius: 4px; padding: 4px 10px; }} "
            f"QPushButton:hover {{ background: {_ACCENT}; color: #1e1e2e; }}"
        )
        self._apply_btn.clicked.connect(self._apply)
        sp_row.addWidget(self._apply_btn)
        grp_lay.addLayout(sp_row)

        # Toggle — same style as _PSUChannel
        self._toggle_btn = QPushButton("○  OUTPUT OFF")
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setMinimumHeight(32)
        self._toggle_btn.clicked.connect(self._on_toggle)
        self._set_toggle_style(False)
        grp_lay.addWidget(self._toggle_btn)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        
        grp_lay.addWidget(sep)

        # Info row (compliance + delay + avg + temp) — styled like PSU limits row
        info_row = QHBoxLayout()
        info_row.setSpacing(4)
        comp_lbl_hdr = QLabel("Status")
        comp_lbl_hdr.setStyleSheet("font-size: 10px;")
        info_row.addWidget(comp_lbl_hdr)
        self._comp_lbl = QLabel("OK")
        self._comp_lbl.setStyleSheet("color: #155724; font-size: 10px; font-weight: bold;")
        info_row.addWidget(self._comp_lbl)
        info_row.addStretch()
        self._delay_lbl = QLabel("delay: —")
        self._delay_lbl.setStyleSheet("font-size: 10px;")
        info_row.addWidget(self._delay_lbl)
        self._avg_lbl = QLabel("avg: —")
        self._avg_lbl.setStyleSheet("font-size: 10px;")
        info_row.addWidget(self._avg_lbl)
        self._temp_lbl = QLabel("temp: —")
        self._temp_lbl.setStyleSheet("font-size: 10px;")
        info_row.addWidget(self._temp_lbl)
        grp_lay.addLayout(info_row)

        body_lay.addWidget(self._grp)

        self._status = QLabel("")
        self._status.setStyleSheet("font-size: 10px;")
        body_lay.addWidget(self._status)
        body_lay.addStretch(1)

        outer.addWidget(body, 1)

    def _set_toggle_style(self, on: bool) -> None:
        if on:
            self._toggle_btn.setText("●  OUTPUT ON")
            self._toggle_btn.setStyleSheet(
                "QPushButton { background: #d4edda; color: #155724; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #28a745; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #28a745; color: white; }"
            )
        else:
            self._toggle_btn.setText("○  OUTPUT OFF")
            self._toggle_btn.setStyleSheet(
                "QPushButton { background: transparent; color: #c0392b; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #c0392b88; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #c0392b; color: white; }"
            )

    def _on_mode_changed(self, mode: str) -> None:
        if mode == "VOLTAGE":
            self._grp.setTitle("VOLTAGE MODE   ±60 V / 3 A")
            self._set_spin.setSuffix(" V")
            self._set_spin.setRange(-60.0, 60.0)
            self._lim_spin.setSuffix(" A")
            self._lim_spin.setRange(0.0, 3.0)
        else:
            self._grp.setTitle("CURRENT MODE   ±3 A / 60 V")
            self._set_spin.setSuffix(" A")
            self._set_spin.setRange(-3.0, 3.0)
            self._lim_spin.setSuffix(" V")
            self._lim_spin.setRange(0.0, 60.0)

    def _apply(self) -> None:
        dev = self._d.device(self._smu)
        if not dev:
            return
        mode = self._mode_combo.currentText()
        val = self._set_spin.value()
        lim = self._lim_spin.value()
        try:
            if mode == "VOLTAGE":
                dev.set_voltage_mode(val, lim)
                msg = f"V mode: {val}V, I lim {lim}A"
            else:
                dev.set_current_mode(val, lim)
                msg = f"I mode: {val}A, V lim {lim}V"
            self._status.setText(msg)
            self._status.setStyleSheet("color: #155724; font-size: 10px;")
            con = self._con()
            if con:
                con.log_action(f"{self._smu} set", msg)
            self._poll()
        except Exception as exc:
            self._status.setText(str(exc))
            self._status.setStyleSheet("color: #c0392b; font-size: 10px;")

    def _on_toggle(self, checked: bool) -> None:
        dev = self._d.device(self._smu)
        if not dev:
            return
        try:
            dev.enable_output(checked)
            msg = f"Output {'enabled' if checked else 'disabled'}"
            self._status.setText(msg)
            self._status.setStyleSheet("color: #155724; font-size: 10px;")
            con = self._con()
            if con:
                con.log_action(f"{self._smu} {'on' if checked else 'off'}", msg)
            self._poll()
        except Exception as exc:
            self._status.setText(str(exc))
            self._status.setStyleSheet("color: #c0392b; font-size: 10px;")

    @Slot()
    def _poll(self) -> None:
        dev = self._d.device(self._smu)
        if not dev:
            return
        with contextlib.suppress(Exception):
            on = dev.get_output_state()
            self._toggle_btn.blockSignals(True)
            self._toggle_btn.setChecked(on)
            self._toggle_btn.blockSignals(False)
            self._set_toggle_style(on)
        with contextlib.suppress(Exception):
            mode = dev.get_output_mode().upper()
            self._mode_combo.blockSignals(True)
            idx = self._mode_combo.findText(mode)
            if idx >= 0:
                self._mode_combo.setCurrentIndex(idx)
                self._on_mode_changed(mode)
            self._mode_combo.blockSignals(False)
        with contextlib.suppress(Exception):
            v_set = dev.get_voltage_setpoint()
            i_lim = dev.get_current_limit()
            self._set_spin.blockSignals(True)
            self._lim_spin.blockSignals(True)
            if self._mode_combo.currentText() == "VOLTAGE":
                self._set_spin.setValue(v_set)
                self._lim_spin.setValue(i_lim)
            else:
                self._set_spin.setValue(i_lim)
                self._lim_spin.setValue(v_set)
            self._set_spin.blockSignals(False)
            self._lim_spin.blockSignals(False)
        with contextlib.suppress(Exception):
            result = dev.measure_vi()
            v, i = result["voltage"], result["current"]
            in_comp = result.get("in_compliance", False)
            self._v_display.setText(f"{v:10.3f} V")
            self._i_display.setText(f"{i:10.4f} A")
            if in_comp:
                self._comp_lbl.setText("COMPLIANCE")
                self._comp_lbl.setStyleSheet("color: #c0392b; font-size: 11px; font-weight: bold;")
            else:
                self._comp_lbl.setText("OK")
                self._comp_lbl.setStyleSheet("color: #155724; font-size: 11px; font-weight: bold;")
        with contextlib.suppress(Exception):
            self._delay_lbl.setText(f"delay: {dev.get_source_delay():.4f}s")
        with contextlib.suppress(Exception):
            self._avg_lbl.setText(f"avg: {dev.get_samples_to_average()}")
        with contextlib.suppress(Exception):
            self._temp_lbl.setText(f"temp: {dev.read_temperature():.1f}°C")

    def stop(self) -> None:
        pass


# -- DMM device card ---------------------------------------------------------

_DMM_MODES = [
    ("DC Voltage", "measure_dc_voltage", "V"),
    ("AC Voltage", "measure_ac_voltage", "V"),
    ("DC Current", "measure_dc_current", "A"),
    ("AC Current", "measure_ac_current", "A"),
    ("Resistance 2W", "measure_resistance_2wire", "\u03a9"),
    ("Resistance 4W", "measure_resistance_4wire", "\u03a9"),
    ("Frequency", "measure_frequency", "Hz"),
    ("Period", "measure_period", "s"),
    ("Continuity", "measure_continuity", "\u03a9"),
    ("Diode", "measure_diode", "V"),
]

_DMM_EXTRA_MODES = [
    ("Capacitance", "measure_capacitance", "F"),
    ("Temperature", "measure_temperature", "\u00b0C"),
]


class _DMMBlock(QFrame):
    """Self-contained card for one DMM device."""

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._dmm = name
        self.setObjectName("dmmblock")
        self.setStyleSheet(
            "#dmmblock { border: 1px solid #ccc; border-radius: 10px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._build()
        self._poll()

    def _con(self) -> _Console | None:
        w = self.parent()
        while w is not None:
            if hasattr(w, "_console"):
                return w._console  # type: ignore[attr-defined]
            w = w.parent()
        return None

    def _build(self) -> None:
        _ACCENT = "#c45c00"
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header — same as PSU
        hdr = QFrame()
        hdr.setStyleSheet(
            "QFrame { border-bottom: 1px solid #ccc; border-radius: 0; }"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 9, 14, 9)
        hdr_lay.setSpacing(8)
        name_lbl = QLabel(f"<b>{self._dmm}</b>")
        name_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        hdr_lay.addWidget(name_lbl)
        dev = self._d.device(self._dmm)
        if dev:
            disp = self._d.registry.display_name(self._dmm)
            type_lbl = QLabel(disp or "")
            type_lbl.setStyleSheet("font-size: 11px;")
            hdr_lay.addWidget(type_lbl, 1)
        else:
            hdr_lay.addStretch(1)
        outer.addWidget(hdr)

        # Body
        body = QWidget()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(10, 10, 10, 6)
        body_lay.setSpacing(8)

        # Group box — shows current mode
        self._grp = QGroupBox("DC VOLTAGE")
        self._grp.setStyleSheet(
            f"QGroupBox {{ border: 2px solid #aaa; border-radius: 7px; "
            f"margin-top: 12px; padding-top: 14px; }}"
            f"QGroupBox::title {{ color: {_ACCENT}; subcontrol-origin: margin; "
            f"left: 10px; padding: 0 6px; font-weight: bold; }}"
        )
        grp_lay = QVBoxLayout(self._grp)
        grp_lay.setSpacing(5)
        grp_lay.setContentsMargins(8, 8, 8, 8)

        # Measurement display
        self._reading = QLabel("-.------ V")
        self._reading.setFont(_mono(18))
        self._reading.setStyleSheet(
            "color: #1e7a1e; border-radius: 5px; padding: 4px 8px"
        )
        self._reading.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._reading.setMinimumHeight(42)
        self._reading.setMinimumWidth(90)
        grp_lay.addWidget(self._reading)

        # Mode selector + Read button
        ctrl = QHBoxLayout()
        ctrl.setSpacing(4)
        self._mode_combo = QComboBox()
        modes = list(_DMM_MODES)
        if dev:
            if hasattr(dev, "measure_capacitance"):
                modes.extend(m for m in _DMM_EXTRA_MODES if m[0] == "Capacitance")
            if hasattr(dev, "measure_temperature"):
                modes.extend(m for m in _DMM_EXTRA_MODES if m[0] == "Temperature")
        self._modes = modes
        self._mode_combo.addItems([m[0] for m in modes])
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        ctrl.addWidget(self._mode_combo, 1)

        self._read_btn = QPushButton("Read")
        self._read_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {_ACCENT}; font-weight: bold; "
            f"border: 1px solid {_ACCENT}88; border-radius: 4px; padding: 4px 10px; }} "
            f"QPushButton:hover {{ background: {_ACCENT}; color: white; }}"
        )
        self._read_btn.clicked.connect(self._on_read)
        ctrl.addWidget(self._read_btn)
        grp_lay.addLayout(ctrl)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        grp_lay.addWidget(sep)

        # Info row
        info_row = QHBoxLayout()
        info_row.setSpacing(4)
        mode_hdr = QLabel("Mode")
        mode_hdr.setStyleSheet("font-size: 10px;")
        info_row.addWidget(mode_hdr)
        self._mode_lbl = QLabel("DC Voltage")
        self._mode_lbl.setStyleSheet("color: #155724; font-size: 10px; font-weight: bold;")
        info_row.addWidget(self._mode_lbl)
        info_row.addStretch()
        self._range_lbl = QLabel("")
        self._range_lbl.setStyleSheet("font-size: 10px;")
        info_row.addWidget(self._range_lbl)
        grp_lay.addLayout(info_row)

        body_lay.addWidget(self._grp)

        self._status = QLabel("")
        self._status.setStyleSheet("font-size: 10px;")
        body_lay.addWidget(self._status)
        body_lay.addStretch(1)

        outer.addWidget(body, 1)

    def _on_mode_changed(self, idx: int) -> None:
        if 0 <= idx < len(self._modes):
            label, method, unit = self._modes[idx]
            self._grp.setTitle(label.upper())
            self._mode_lbl.setText(label)
            self._reading.setText(f"-.------ {unit}")
            self._poll()

    def _on_read(self) -> None:
        self._poll()
        con = self._con()
        idx = self._mode_combo.currentIndex()
        if con and 0 <= idx < len(self._modes):
            label, _, _ = self._modes[idx]
            con.log_action(f"{self._dmm} meas", f"Read: {self._reading.text()}")

    @Slot()
    def _poll(self) -> None:
        dev = self._d.device(self._dmm)
        if not dev:
            return
        idx = self._mode_combo.currentIndex()
        if idx < 0 or idx >= len(self._modes):
            return
        label, method, unit = self._modes[idx]
        with contextlib.suppress(Exception):
            fn = getattr(dev, method, None)
            if fn is not None:
                val = fn()
                if isinstance(val, float):
                    if unit == "Hz" and val >= 1e3:
                        self._reading.setText(f"{val / 1e3:.3f} kHz")
                    elif unit == "\u03a9" and val >= 1e3:
                        self._reading.setText(f"{val / 1e3:.3f} k\u03a9")
                    elif unit == "F" and val < 1e-6:
                        self._reading.setText(f"{val * 1e9:.2f} nF")
                    elif unit == "s" and val < 1:
                        self._reading.setText(f"{val * 1e3:.4f} ms")
                    else:
                        self._reading.setText(f"{val:.6f} {unit}")

    def stop(self) -> None:
        pass


# -- Scope device card -------------------------------------------------------

_SCOPE_MEAS = [
    ("Freq", "measure_frequency", "Hz"),
    ("Vpp", "measure_peak_to_peak", "V"),
    ("RMS", "measure_rms", "V"),
    ("Mean", "measure_mean", "V"),
]


class _ScopeBlock(QFrame):
    """Self-contained card for one oscilloscope device."""

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._scope = name
        self.setObjectName("scopeblock")
        self.setStyleSheet(
            "#scopeblock { border: 1px solid #ccc; border-radius: 10px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._build()
        self._poll()

    def _con(self) -> _Console | None:
        w = self.parent()
        while w is not None:
            if hasattr(w, "_console"):
                return w._console  # type: ignore[attr-defined]
            w = w.parent()
        return None

    def _build(self) -> None:
        _ACCENT = "#0e7a70"
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setStyleSheet(
            "QFrame { border-bottom: 1px solid #ccc; border-radius: 0; }"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 9, 14, 9)
        hdr_lay.setSpacing(8)
        name_lbl = QLabel(f"<b>{self._scope}</b>")
        name_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        hdr_lay.addWidget(name_lbl)
        dev = self._d.device(self._scope)
        if dev:
            disp = self._d.registry.display_name(self._scope)
            type_lbl = QLabel(disp or "")
            type_lbl.setStyleSheet("font-size: 11px;")
            hdr_lay.addWidget(type_lbl, 1)
        else:
            hdr_lay.addStretch(1)
        outer.addWidget(hdr)

        # Body
        body = QWidget()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(10, 10, 10, 6)
        body_lay.setSpacing(8)

        # Group box
        self._grp = QGroupBox("OSCILLOSCOPE")
        self._grp.setStyleSheet(
            f"QGroupBox {{ border: 2px solid #aaa; border-radius: 7px; "
            f"margin-top: 12px; padding-top: 14px; }}"
            f"QGroupBox::title {{ color: {_ACCENT}; subcontrol-origin: margin; "
            f"left: 10px; padding: 0 6px; font-weight: bold; }}"
        )
        grp_lay = QVBoxLayout(self._grp)
        grp_lay.setSpacing(5)
        grp_lay.setContentsMargins(8, 8, 8, 8)

        # Trigger + sample rate display
        trig_row = QHBoxLayout()
        trig_row.setSpacing(8)
        self._trig_lbl = QLabel("Trigger: ---")
        self._trig_lbl.setFont(_mono(14))
        self._trig_lbl.setStyleSheet("color: #1e7a1e; font-weight: bold;")
        trig_row.addWidget(self._trig_lbl)
        trig_row.addStretch()
        self._rate_lbl = QLabel("")
        self._rate_lbl.setFont(_mono(11))
        self._rate_lbl.setStyleSheet("color: #c45c00;")
        trig_row.addWidget(self._rate_lbl)
        grp_lay.addLayout(trig_row)

        # Channel status rows
        self._ch_labels: dict[int, QLabel] = {}
        self._ch_btns: dict[int, QPushButton] = {}
        ch_grid = QHBoxLayout()
        ch_grid.setSpacing(6)
        num_ch = getattr(dev, "num_channels", 4) if dev else 4
        ch_colors = ["#1a6bbf", "#c0392b", "#b8860b", "#7c3aed"]
        for ch in range(1, num_ch + 1):
            col = QVBoxLayout()
            col.setSpacing(2)
            btn = QPushButton(f"CH{ch}")
            btn.setCheckable(True)
            btn.setChecked(ch <= 2)
            color = ch_colors[(ch - 1) % len(ch_colors)]
            btn.setStyleSheet(
                f"QPushButton {{ border: 2px solid {color}88; color: {color}; border-radius: 4px; "
                f"padding: 3px 8px; font-weight: bold; font-size: 11px; }}"
                f"QPushButton:checked {{ background: {color}; color: white; }}"
            )
            btn.clicked.connect(lambda checked, c=ch: self._toggle_ch(c, checked))
            col.addWidget(btn)
            self._ch_btns[ch] = btn
            lbl = QLabel("---")
            lbl.setFont(_mono(10))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {color};")
            col.addWidget(lbl)
            self._ch_labels[ch] = lbl
            ch_grid.addLayout(col)
        grp_lay.addLayout(ch_grid)

        # Measurement display (CH1 measurements)
        meas_row = QHBoxLayout()
        meas_row.setSpacing(6)
        self._meas_labels: dict[str, QLabel] = {}
        for name, _, unit in _SCOPE_MEAS:
            col = QVBoxLayout()
            col.setSpacing(1)
            hdr_l = QLabel(name)
            hdr_l.setStyleSheet("font-size: 9px;")
            hdr_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(hdr_l)
            val_l = QLabel(f"--- {unit}")
            val_l.setFont(_mono(12))
            val_l.setStyleSheet("color: #1e7a1e;")
            val_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(val_l)
            self._meas_labels[name] = val_l
            meas_row.addLayout(col)
        grp_lay.addLayout(meas_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        grp_lay.addWidget(sep)

        # Control row
        ctrl = QHBoxLayout()
        ctrl.setSpacing(4)
        for text, slot in [("Run", self._run), ("Stop", self._stop), ("Single", self._single), ("AutoSet", self._autoset)]:
            b = QPushButton(text)
            b.setStyleSheet(
                f"QPushButton {{ border: 1px solid {_ACCENT}66; color: {_ACCENT}; border-radius: 4px; "
                f"padding: 4px 8px; font-weight: bold; font-size: 11px; }} "
                f"QPushButton:hover {{ background: {_ACCENT}; color: white; }}"
            )
            b.clicked.connect(slot)
            ctrl.addWidget(b)
        ctrl.addStretch()
        grp_lay.addLayout(ctrl)

        body_lay.addWidget(self._grp)

        self._status = QLabel("")
        self._status.setStyleSheet("font-size: 10px;")
        body_lay.addWidget(self._status)
        body_lay.addStretch(1)

        outer.addWidget(body, 1)

    def _cmd(self, method: str, *args) -> None:
        dev = self._d.device(self._scope)
        if not dev:
            return
        try:
            getattr(dev, method)(*args)
            self._status.setText(f"{method} OK")
            self._status.setStyleSheet("color: #155724; font-size: 10px;")
            con = self._con()
            if con:
                con.log_action(f"{self._scope} {method}", f"{method} OK")
            self._poll()
        except Exception as exc:
            self._status.setText(str(exc))
            self._status.setStyleSheet("color: #c0392b; font-size: 10px;")

    def _toggle_ch(self, ch: int, on: bool) -> None:
        dev = self._d.device(self._scope)
        if not dev:
            return
        if on:
            dev.enable_channel(ch)
        else:
            dev.disable_channel(ch)
        con = self._con()
        if con:
            con.log_action(f"{self._scope} ch{ch}", f"CH{ch} {'ON' if on else 'OFF'}")

    def _run(self) -> None:
        self._cmd("run")

    def _stop(self) -> None:
        self._cmd("stop")

    def _single(self) -> None:
        self._cmd("single")

    def _autoset(self) -> None:
        self._cmd("autoset")

    @Slot()
    def _poll(self) -> None:
        dev = self._d.device(self._scope)
        if not dev:
            return
        with contextlib.suppress(Exception):
            trig = dev.get_trigger_status()
            self._trig_lbl.setText(f"Trigger: {trig}")
            if trig == "TD":
                self._trig_lbl.setStyleSheet("color: #1e7a1e; font-weight: bold;")
            else:
                self._trig_lbl.setStyleSheet("color: #c45c00; font-weight: bold;")
        with contextlib.suppress(Exception):
            rate = dev.get_sample_rate()
            if rate >= 1e9:
                self._rate_lbl.setText(f"{rate / 1e9:.2f} GSa/s")
            elif rate >= 1e6:
                self._rate_lbl.setText(f"{rate / 1e6:.2f} MSa/s")
            else:
                self._rate_lbl.setText(f"{rate / 1e3:.2f} kSa/s")
        # CH1 measurements
        for name, method, unit in _SCOPE_MEAS:
            with contextlib.suppress(Exception):
                fn = getattr(dev, method, None)
                if fn:
                    val = fn(1)
                    if unit == "Hz" and val >= 1e3:
                        self._meas_labels[name].setText(f"{val / 1e3:.2f} kHz")
                    elif unit == "Hz" and val >= 1e6:
                        self._meas_labels[name].setText(f"{val / 1e6:.3f} MHz")
                    else:
                        self._meas_labels[name].setText(f"{val:.4f} {unit}")

    def stop(self) -> None:
        pass


# -- EV2300 device card ------------------------------------------------------


class _EV2300Block(QFrame):
    """Self-contained card for one EV2300 USB-to-I2C adapter."""

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._ev = name
        self.setObjectName("evblock")
        self.setStyleSheet(
            "#evblock { border: 1px solid #ccc; border-radius: 10px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._build()

    def _con(self) -> _Console | None:
        w = self.parent()
        while w is not None:
            if hasattr(w, "_console"):
                return w._console  # type: ignore[attr-defined]
            w = w.parent()
        return None

    def _build(self) -> None:
        _ACCENT = "#6366f1"
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header — same as PSU
        hdr = QFrame()
        hdr.setStyleSheet(
            "QFrame { border-bottom: 1px solid #ccc; border-radius: 0; }"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 9, 14, 9)
        hdr_lay.setSpacing(8)
        name_lbl = QLabel(f"<b>{self._ev}</b>")
        name_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        hdr_lay.addWidget(name_lbl)
        dev = self._d.device(self._ev)
        if dev:
            disp = self._d.registry.display_name(self._ev)
            type_lbl = QLabel(disp or "")
            type_lbl.setStyleSheet("font-size: 11px;")
            hdr_lay.addWidget(type_lbl, 1)
        else:
            hdr_lay.addStretch(1)
        outer.addWidget(hdr)

        # Body
        body = QWidget()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(10, 10, 10, 6)
        body_lay.setSpacing(8)

        # Group box
        self._grp = QGroupBox("I2C INTERFACE")
        self._grp.setStyleSheet(
            f"QGroupBox {{ border: 2px solid #aaa; border-radius: 7px; "
            f"margin-top: 12px; padding-top: 14px; }}"
            f"QGroupBox::title {{ color: {_ACCENT}; subcontrol-origin: margin; "
            f"left: 10px; padding: 0 6px; font-weight: bold; }}"
        )
        grp_lay = QVBoxLayout(self._grp)
        grp_lay.setSpacing(5)
        grp_lay.setContentsMargins(8, 8, 8, 8)

        # Device info row
        self._info_lbl = QLabel("")
        self._info_lbl.setStyleSheet("font-size: 10px;")
        grp_lay.addWidget(self._info_lbl)
        self._load_info(dev)

        # Result display
        self._result = QLabel("---")
        self._result.setFont(_mono(18))
        self._result.setStyleSheet(
            "color: #1e7a1e; border-radius: 5px; padding: 4px 8px"
        )
        self._result.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._result.setMinimumHeight(42)
        self._result.setMinimumWidth(90)
        grp_lay.addWidget(self._result)

        # Address + Register row
        addr_row = QHBoxLayout()
        addr_row.setSpacing(4)
        addr_lbl = QLabel("Addr")
        addr_lbl.setStyleSheet("font-size: 11px;")
        addr_row.addWidget(addr_lbl)
        self._addr = QLineEdit("0x08")
        self._addr.setFont(_mono(11))
        self._addr.setMaximumWidth(70)
        addr_row.addWidget(self._addr)
        reg_lbl = QLabel("Reg")
        reg_lbl.setStyleSheet("font-size: 11px;")
        addr_row.addWidget(reg_lbl)
        self._reg = QLineEdit("0x00")
        self._reg.setFont(_mono(11))
        self._reg.setMaximumWidth(70)
        addr_row.addWidget(self._reg)
        addr_row.addStretch()
        grp_lay.addLayout(addr_row)

        # Read buttons
        read_row = QHBoxLayout()
        read_row.setSpacing(4)
        for text, method in [("Read Word", "read_word"), ("Read Byte", "read_byte"), ("Read Block", "read_block")]:
            b = QPushButton(text)
            b.setStyleSheet(
                f"QPushButton {{ border: 1px solid {_ACCENT}66; color: {_ACCENT}; border-radius: 4px; "
                f"padding: 4px 8px; font-weight: bold; font-size: 11px; }} "
                f"QPushButton:hover {{ background: {_ACCENT}; color: white; }}"
            )
            b.clicked.connect(lambda _, m=method: self._do_read(m))
            read_row.addWidget(b)
        read_row.addStretch()
        grp_lay.addLayout(read_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        grp_lay.addWidget(sep)

        # Write row
        write_row = QHBoxLayout()
        write_row.setSpacing(4)
        val_lbl = QLabel("Value")
        val_lbl.setStyleSheet("font-size: 10px;")
        write_row.addWidget(val_lbl)
        self._val = QLineEdit("0x0000")
        self._val.setFont(_mono(11))
        self._val.setMaximumWidth(80)
        write_row.addWidget(self._val)
        for text, method in [("Write Word", "write_word"), ("Write Byte", "write_byte")]:
            b = QPushButton(text)
            b.setStyleSheet(
                f"QPushButton {{ border: 1px solid {_ACCENT}66; color: {_ACCENT}; border-radius: 4px; "
                f"padding: 4px 8px; font-size: 11px; }} "
                f"QPushButton:hover {{ background: {_ACCENT}; color: white; }}"
            )
            b.clicked.connect(lambda _, m=method: self._do_write(m))
            write_row.addWidget(b)
        write_row.addStretch()
        grp_lay.addLayout(write_row)

        body_lay.addWidget(self._grp)

        self._status = QLabel("")
        self._status.setStyleSheet("font-size: 10px;")
        body_lay.addWidget(self._status)
        body_lay.addStretch(1)

        outer.addWidget(body, 1)

    def _load_info(self, dev) -> None:
        if not dev:
            return
        with contextlib.suppress(Exception):
            info = dev.get_device_info()
            if info.get("ok"):
                self._info_lbl.setText(
                    f"Product: {info.get('product', '?')}  "
                    f"Serial: {info.get('serial', '?')}  "
                    f"VID: {info.get('vid', '?')}  PID: {info.get('pid', '?')}"
                )

    def _parse_hex(self, text: str) -> int:
        text = text.strip()
        return int(text, 16) if text.startswith("0x") or text.startswith("0X") else int(text)

    def _do_read(self, method: str) -> None:
        dev = self._d.device(self._ev)
        if not dev:
            return
        try:
            addr = self._parse_hex(self._addr.text())
            reg = self._parse_hex(self._reg.text())
            fn = getattr(dev, method)
            result = fn(addr, reg)
            if result.get("ok"):
                if "value" in result:
                    v = result["value"]
                    self._result.setText(f"0x{v:04X}  ({v})")
                    self._status.setText(f"{method}: addr=0x{addr:02X} reg=0x{reg:02X} → 0x{v:04X}")
                    self._status.setStyleSheet("color: #155724; font-size: 10px;")
                elif "block" in result:
                    blk = result["block"]
                    hex_str = " ".join(f"{b:02X}" for b in blk)
                    self._result.setText(f"[{len(blk)}B] {hex_str}")
                    self._status.setText(f"{method}: {hex_str}")
                    self._status.setStyleSheet("color: #155724; font-size: 10px;")
            else:
                self._result.setText("ERROR")
                self._status.setText(result.get("status_text", "Read failed"))
                self._status.setStyleSheet("color: #c0392b; font-size: 10px;")
            con = self._con()
            if con:
                con.log_action(f"{self._ev} {method}", self._status.text())
        except Exception as exc:
            self._result.setText("ERROR")
            self._status.setText(str(exc))
            self._status.setStyleSheet("color: #c0392b; font-size: 10px;")

    def _do_write(self, method: str) -> None:
        dev = self._d.device(self._ev)
        if not dev:
            return
        try:
            addr = self._parse_hex(self._addr.text())
            reg = self._parse_hex(self._reg.text())
            val = self._parse_hex(self._val.text())
            fn = getattr(dev, method)
            result = fn(addr, reg, val)
            if result.get("ok"):
                self._status.setText(f"{method}: addr=0x{addr:02X} reg=0x{reg:02X} val=0x{val:04X} OK")
                self._status.setStyleSheet("color: #155724; font-size: 10px;")
            else:
                self._status.setText(result.get("status_text", "Write failed"))
                self._status.setStyleSheet("color: #c0392b; font-size: 10px;")
            con = self._con()
            if con:
                con.log_action(f"{self._ev} {method}", self._status.text())
        except Exception as exc:
            self._status.setText(str(exc))
            self._status.setStyleSheet("color: #c0392b; font-size: 10px;")

    def stop(self) -> None:
        pass


# -- Device list panel -------------------------------------------------------


class _DevicePanel(QWidget):
    _TYPE_COLORS = {"psu": "#1a6bbf", "awg": "#7c3aed", "dmm": "#c45c00", "scope": "#0e7a70", "smu": "#c0392b", "ev": "#6366f1"}

    def __init__(self, d: _Dispatcher, main_win: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._main_win = main_win

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(6)

        self._scan_btn = QPushButton("⟳  Scan")
        self._scan_btn.clicked.connect(self._on_scan)
        lay.addWidget(self._scan_btn)

        self._list = QListWidget()
        self._list.setFont(_mono(10))
        self._list.setStyleSheet(
            "QListWidget::item { padding: 8px 10px; }"
        )
        self._list.itemClicked.connect(self._on_item_click)
        lay.addWidget(self._list, 1)

    def _on_scan(self) -> None:
        self._scan_btn.setEnabled(False)
        self._scan_btn.setText("Scanning...")
        QApplication.processEvents()
        result = self._d.run("scan")
        self._d._repl._general.safe_all()
        self._scan_btn.setEnabled(True)
        self._scan_btn.setText("⟳  Scan")
        self.refresh()
        if self._main_win:
            self._main_win._console.log_action("scan", result)
            self._main_win._console.log_action("safe_all", "All outputs set to safe state")
            self._main_win._after_scan()

    def _on_item_click(self, item: QListWidgetItem) -> None:
        name = item.data(Qt.ItemDataRole.UserRole)
        if name and self._main_win:
            self._main_win._on_device_selected(name)

    def refresh(self) -> None:
        self._list.clear()
        devices = self._d.registry.devices
        if not devices:
            placeholder = QListWidgetItem("No devices.\nClick Scan or use --mock.")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            placeholder.setForeground(Qt.GlobalColor.gray)
            self._list.addItem(placeholder)
            return
        for name in sorted(devices):
            disp = self._d.registry.display_name(name)
            base = re.sub(r"\d+$", "", name)
            color = self._TYPE_COLORS.get(base, "")
            item = QListWidgetItem(f"  {name}\n  {disp}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            item.setToolTip(f"{name}  —  {disp}  ({base.upper()})")
            self._list.addItem(item)


# -- VS Code-style panel layout ----------------------------------------------


class _DZ(Enum):
    CENTER = auto()
    LEFT   = auto()
    RIGHT  = auto()
    TOP    = auto()
    BOTTOM = auto()


_DRAG_STATE: dict = {}  # keys: active, source, tab, target, zone


class _DropOverlay(QWidget):
    """Semi-transparent overlay painted over a _PanelGroup showing drop zones."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._zone: _DZ | None = None
        self.hide()

    def show_for(self, zone: _DZ | None) -> None:
        self._zone = zone
        if zone is None:
            self.hide()
            return
        p = self.parent()
        if p:
            self.resize(p.size())
            self.move(0, 0)
        self.raise_()
        self.show()
        self.update()

    def zone_at(self, pos: QPoint) -> _DZ:
        r = self.rect()
        w, h = r.width(), r.height()
        edge_w, edge_h = max(w // 5, 40), max(h // 5, 40)  # ~20% edge zones
        x, y = pos.x(), pos.y()
        if x < edge_w:         return _DZ.LEFT
        if x > w - edge_w:     return _DZ.RIGHT
        if y < edge_h:         return _DZ.TOP
        if y > h - edge_h:     return _DZ.BOTTOM
        return _DZ.CENTER

    def paintEvent(self, _ev) -> None:  # noqa: N802
        if self._zone is None:
            return
        p = QPainter(self)
        r = self.rect()
        w, h = r.width(), r.height()
        # Highlight covers half the group for splits, full for center (VS Code style)
        highlight = {
            _DZ.LEFT:   QRect(0,      0,      w // 2,   h),
            _DZ.RIGHT:  QRect(w // 2, 0,      w // 2,   h),
            _DZ.TOP:    QRect(0,      0,      w,        h // 2),
            _DZ.BOTTOM: QRect(0,      h // 2, w,        h // 2),
            _DZ.CENTER: r,
        }[self._zone]
        hi = self.palette().color(self.palette().ColorRole.Highlight)
        bg = hi; bg.setAlpha(30)
        p.fillRect(r, bg)
        hi2 = QColor(hi); hi2.setAlpha(90)
        p.fillRect(highlight, hi2)
        hi3 = QColor(hi); hi3.setAlpha(200)
        p.setPen(QPen(hi3, 2))
        p.drawRect(highlight.adjusted(2, 2, -2, -2))
        p.end()


class _TabStrip(QWidget):
    """Custom tab bar with drag-to-split support."""

    TAB_H = 32
    DRAG_MIN = 8

    def __init__(self, group: "_PanelGroup") -> None:
        super().__init__(group)
        self._group = group
        self._tabs: list[str] = []
        self._current = 0
        self._hovered = -1
        self._drag_start: QPoint | None = None
        self._drag_tab: int = -1
        self._close_hov: int = -1
        self.setFixedHeight(self.TAB_H)
        self.setMouseTracking(True)

    # -- public API ----------------------------------------------------------

    def add_tab(self, title: str) -> int:
        self._tabs.append(title)
        self.update()
        return len(self._tabs) - 1

    def remove_tab(self, idx: int) -> None:
        if 0 <= idx < len(self._tabs):
            self._tabs.pop(idx)
            if self._current >= len(self._tabs):
                self._current = max(0, len(self._tabs) - 1)
            self.update()

    def set_current(self, idx: int) -> None:
        if 0 <= idx < len(self._tabs):
            self._current = idx
            self.update()

    def count(self) -> int:
        return len(self._tabs)

    # -- geometry ------------------------------------------------------------

    def _tab_rects(self) -> list[QRect]:
        fm = self.fontMetrics()
        rects, x = [], 0
        for t in self._tabs:
            tw = max(80, fm.horizontalAdvance(t) + 32)
            rects.append(QRect(x, 0, tw, self.TAB_H))
            x += tw
        return rects

    def tab_at(self, pos: QPoint) -> int:
        for i, r in enumerate(self._tab_rects()):
            if r.contains(pos):
                return i
        return -1

    def _close_rect(self, tab_rect: QRect) -> QRect:
        """14×14 × button, right-aligned inside the tab."""
        sz = 14
        return QRect(tab_rect.right() - sz - 5, (self.TAB_H - sz) // 2, sz, sz)

    def _close_rects(self) -> list[QRect]:
        return [self._close_rect(tr) for tr in self._tab_rects()]

    # -- mouse events --------------------------------------------------------

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            # Close button takes priority
            for i, cr in enumerate(self._close_rects()):
                if (i == self._current or i == self._hovered) and cr.contains(pos):
                    self._group.close_tab(i)
                    return
            idx = self.tab_at(pos)
            if idx >= 0:
                self._drag_start = pos
                self._drag_tab = idx
                self._group.set_current_tab(idx)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        pos = event.pos()
        new_hov = self.tab_at(pos)
        if new_hov != self._hovered:
            self._hovered = new_hov
            self.update()
        new_close = -1
        for i, cr in enumerate(self._close_rects()):
            if (i == self._current or i == self._hovered) and cr.contains(pos):
                new_close = i
                break
        if new_close != self._close_hov:
            self._close_hov = new_close
            self.update()

        if (
            self._drag_start is not None
            and self._drag_tab >= 0
            and (event.buttons() & Qt.MouseButton.LeftButton)
            and (pos - self._drag_start).manhattanLength() > self.DRAG_MIN
        ):
            if not _DRAG_STATE:
                _DRAG_STATE["active"] = True
                _DRAG_STATE["source"] = self._group
                _DRAG_STATE["tab"] = self._drag_tab
                self.grabMouse()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)

            if _DRAG_STATE.get("active"):
                self._update_drag(self.mapToGlobal(pos))

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if _DRAG_STATE.get("active"):
            self.releaseMouse()
            self.unsetCursor()
            self._finish_drag()
        self._drag_start = None
        self._drag_tab = -1

    def leaveEvent(self, event) -> None:  # noqa: N802
        if not _DRAG_STATE.get("active"):
            self._hovered = -1
            self._close_hov = -1
            self.update()

    # -- drag logic ----------------------------------------------------------

    def _update_drag(self, gpos: QPoint) -> None:
        work = self._group._work_area()
        if not work:
            return
        for g in work.all_groups():
            g._overlay.show_for(None)

        widget = QApplication.widgetAt(gpos)
        target: _PanelGroup | None = None
        w = widget
        while w:
            if isinstance(w, _PanelGroup):
                target = w
                break
            try:
                w = w.parent()
            except Exception:
                break

        if target:
            local = target.mapFromGlobal(gpos)
            zone = target._overlay.zone_at(local)
            src: _PanelGroup = _DRAG_STATE["source"]
            if target is src and src.count() == 1 and zone == _DZ.CENTER:
                zone = None  # can't merge into self with only one tab
            target._overlay.show_for(zone)
            _DRAG_STATE["target"] = target
            _DRAG_STATE["zone"] = zone
        else:
            _DRAG_STATE.pop("target", None)
            _DRAG_STATE.pop("zone", None)

    def _finish_drag(self) -> None:
        work = self._group._work_area()
        if work:
            for g in work.all_groups():
                g._overlay.show_for(None)
        target: _PanelGroup | None = _DRAG_STATE.get("target")
        zone: _DZ | None = _DRAG_STATE.get("zone")
        src: _PanelGroup | None = _DRAG_STATE.get("source")
        tab_idx: int = _DRAG_STATE.get("tab", -1)
        _DRAG_STATE.clear()
        if work and target and zone and src is not None and tab_idx >= 0:
            if not (target is src and zone == _DZ.CENTER):
                work.perform_drop(src, tab_idx, target, zone)

    # -- paint ---------------------------------------------------------------

    def paintEvent(self, _ev) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        pal = self.palette()
        bg   = pal.color(pal.ColorRole.Window)
        base = pal.color(pal.ColorRole.Base)
        text = pal.color(pal.ColorRole.WindowText)
        dim  = pal.color(pal.ColorRole.PlaceholderText)
        hi   = pal.color(pal.ColorRole.Highlight)
        p.fillRect(r, bg)
        tab_rects = self._tab_rects()
        for i, (title, tr) in enumerate(zip(self._tabs, tab_rects)):
            active  = i == self._current
            hovered = i == self._hovered and not active
            show_x  = active or hovered
            if active:
                p.fillRect(tr, base)
                p.fillRect(QRect(tr.x(), 0, tr.width(), 2), hi)
                p.setPen(text)
            elif hovered:
                hover_bg = base; hover_bg.setAlpha(180)
                p.fillRect(tr, hover_bg)
                p.setPen(text)
            else:
                p.setPen(dim)
            sep_col = pal.color(pal.ColorRole.Mid)
            p.fillRect(QRect(tr.right(), 2, 1, tr.height() - 4), sep_col)
            fm = p.fontMetrics()
            tr2 = tr.adjusted(12, 0, -26 if show_x else -8, 0)
            p.drawText(
                tr2,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                fm.elidedText(title, Qt.TextElideMode.ElideRight, tr2.width()),
            )
            if show_x:
                cr = self._close_rect(tr)
                if i == self._close_hov:
                    p.fillRect(cr, pal.color(pal.ColorRole.Midlight))
                x_pen = text if active else dim
                p.setPen(QPen(x_pen, 1.5))
                off = 4
                c = cr.center()
                p.drawLine(c.x() - off, c.y() - off, c.x() + off, c.y() + off)
                p.drawLine(c.x() + off, c.y() - off, c.x() - off, c.y() + off)
        p.fillRect(QRect(0, r.height() - 1, r.width(), 1), pal.color(pal.ColorRole.Mid))
        p.end()


class _PanelGroup(QFrame):
    """VS Code editor group: tab strip + stacked content area."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._widgets: list[tuple[str, QWidget]] = []
        self.setObjectName("panelGroup")
        self.setStyleSheet("#panelGroup { border: 1px solid #ccc; }")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._tab_strip = _TabStrip(self)
        lay.addWidget(self._tab_strip)

        self._stack = QStackedWidget()
        
        lay.addWidget(self._stack, 1)

        self._overlay = _DropOverlay(self)

    def _work_area(self) -> "_WorkArea | None":
        w = self.parent()
        while w:
            if isinstance(w, _WorkArea):
                return w  # type: ignore[return-value]
            try:
                w = w.parent()
            except Exception:
                break
        return None

    def add_widget(self, title: str, widget: QWidget) -> None:
        self._widgets.append((title, widget))
        self._stack.addWidget(widget)
        idx = self._tab_strip.add_tab(title)
        self.set_current_tab(idx)

    def remove_widget_at(self, idx: int) -> tuple[str, QWidget] | None:
        if not 0 <= idx < len(self._widgets):
            return None
        title, widget = self._widgets.pop(idx)
        self._stack.removeWidget(widget)
        self._tab_strip.remove_tab(idx)
        if self._widgets:
            new_idx = min(idx, len(self._widgets) - 1)
            self._stack.setCurrentIndex(new_idx)
            self._tab_strip.set_current(new_idx)
        return title, widget

    def set_current_tab(self, idx: int) -> None:
        if 0 <= idx < len(self._widgets):
            self._stack.setCurrentIndex(idx)
            self._tab_strip.set_current(idx)

    def count(self) -> int:
        return len(self._widgets)

    def close_tab(self, idx: int) -> None:
        item = self.remove_widget_at(idx)
        if item is None:
            return
        _title, widget = item
        win = self._find_main_win()
        if win and hasattr(win, "_on_tab_closed"):
            win._on_tab_closed(widget)
        if self.count() == 0:
            work = self._work_area()
            if work:
                work._remove_empty(self)

    def _find_main_win(self) -> QMainWindow | None:
        w = self.parent()
        while w:
            if isinstance(w, QMainWindow):
                return w  # type: ignore[return-value]
            try:
                w = w.parent()
            except Exception:
                break
        return None

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._overlay.resize(self.size())
        self._overlay.move(0, 0)


class _WorkArea(QWidget):
    """Root container managing a recursive QSplitter tree of _PanelGroups."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._root = self._mk_splitter(Qt.Orientation.Horizontal)
        lay.addWidget(self._root)
        self._default = _PanelGroup()
        self._root.addWidget(self._default)

    def _mk_splitter(self, orient: Qt.Orientation) -> QSplitter:
        s = QSplitter(orient)
        s.setHandleWidth(5)
        s.setChildrenCollapsible(False)
        s.setStyleSheet(
            "QSplitter::handle { background: #ccc; }"
            "QSplitter::handle:hover { background: #1a6bbf55; }"
        )
        return s

    def default_group(self) -> _PanelGroup:
        return self._default

    def all_groups(self) -> list[_PanelGroup]:
        result: list[_PanelGroup] = []

        def _walk(w: QWidget) -> None:
            if isinstance(w, _PanelGroup):
                result.append(w)
            elif isinstance(w, QSplitter):
                for i in range(w.count()):
                    _walk(w.widget(i))

        _walk(self._root)
        return result

    def add_widget(self, title: str, widget: QWidget) -> None:
        groups = self.all_groups()
        if groups:
            groups[-1].add_widget(title, widget)
        else:
            g = _PanelGroup()
            self._root.addWidget(g)
            self._default = g
            g.add_widget(title, widget)

    def remove_widget(self, widget: QWidget) -> None:
        for group in self.all_groups():
            for i, (_, w) in enumerate(group._widgets):
                if w is widget:
                    group.remove_widget_at(i)
                    if group.count() == 0:
                        self._remove_empty(group)
                    return

    def perform_drop(self, src: _PanelGroup, tab_idx: int, dst: _PanelGroup, zone: _DZ) -> None:
        item = src.remove_widget_at(tab_idx)
        if item is None:
            return
        title, widget = item
        if zone == _DZ.CENTER:
            dst.add_widget(title, widget)
        else:
            new_grp = _PanelGroup()
            new_grp.add_widget(title, widget)
            self._split(dst, new_grp, zone)
        if src.count() == 0:
            self._remove_empty(src)

    def _split(self, dst: _PanelGroup, new_grp: _PanelGroup, zone: _DZ) -> None:
        horiz  = zone in (_DZ.LEFT, _DZ.RIGHT)
        orient = Qt.Orientation.Horizontal if horiz else Qt.Orientation.Vertical
        before = zone in (_DZ.LEFT, _DZ.TOP)

        sp = dst.parent()
        if not isinstance(sp, QSplitter):
            return
        idx   = sp.indexOf(dst)
        sizes = sp.sizes()
        sz    = sizes[idx] if idx < len(sizes) else 400

        if sp.orientation() == orient:
            ins = idx if before else idx + 1
            sp.insertWidget(ins, new_grp)
            half = max(sz // 2, 1)
            new_s = list(sizes)
            new_s[idx] = half
            new_s.insert(ins, half)
            sp.setSizes(new_s)
        else:
            sub = self._mk_splitter(orient)
            dst.setParent(None)  # removes from sp
            if before:
                sub.addWidget(new_grp)
                sub.addWidget(dst)
            else:
                sub.addWidget(dst)
                sub.addWidget(new_grp)
            half = max(sz // 2, 1)
            sub.setSizes([half, half])
            sp.insertWidget(idx, sub)
            new_s = list(sizes)
            new_s[idx] = sz
            sp.setSizes(new_s)

    def _remove_empty(self, group: _PanelGroup) -> None:
        sp = group.parent()
        if not isinstance(sp, QSplitter):
            group.deleteLater()
            return
        group.hide()
        group.setParent(None)
        group.deleteLater()

        # Collapse single-child splitters (but never the root)
        if sp.count() == 1 and sp is not self._root:
            only = sp.widget(0)
            gp = sp.parent()
            if isinstance(gp, QSplitter):
                gp_idx   = gp.indexOf(sp)
                gp_sizes = gp.sizes()
                size     = gp_sizes[gp_idx] if gp_idx < len(gp_sizes) else 400
                only.setParent(None)
                sp.setParent(None)
                sp.deleteLater()
                gp.insertWidget(gp_idx, only)
                new_s = list(gp_sizes)
                new_s[gp_idx] = size
                gp.setSizes(new_s)

        # Always keep at least one group
        if not self.all_groups():
            g = _PanelGroup()
            self._root.addWidget(g)
            self._default = g


# -- Global stylesheet -------------------------------------------------------


# -- Main window -------------------------------------------------------------


class _MainWindow(QMainWindow):
    def __init__(self, d: _Dispatcher) -> None:
        super().__init__()
        self._d = d
        self.setWindowTitle("SCPI Instrument Toolkit")

        self._psu_blocks: dict[str, _PSUBlock] = {}
        self._psu_closed: set[str] = set()
        self._smu_blocks: dict[str, _SMUBlock] = {}
        self._smu_closed: set[str] = set()
        self._awg_blocks: dict[str, _AWGBlock] = {}
        self._awg_closed: set[str] = set()
        self._dmm_blocks: dict[str, _DMMBlock] = {}
        self._dmm_closed: set[str] = set()
        self._ev_blocks: dict[str, _EV2300Block] = {}
        self._ev_closed: set[str] = set()
        self._scope_blocks: dict[str, _ScopeBlock] = {}
        self._scope_closed: set[str] = set()

        # ── Menu bar ──────────────────────────────────────────────────
        mb = self.menuBar()
        fm = mb.addMenu("&File")
        qa = QAction("&Quit", self)
        qa.setShortcut("Ctrl+Q")
        qa.triggered.connect(self.close)
        fm.addAction(qa)

        im = mb.addMenu("&Instruments")
        sa = QAction("&Scan Devices", self)
        sa.setShortcut("Ctrl+Shift+S")
        sa.triggered.connect(self._on_scan)
        im.addAction(sa)
        ea = QAction("&Emergency Stop", self)
        ea.triggered.connect(self._on_estop)
        im.addAction(ea)

        self._view_menu = mb.addMenu("&View")

        # ── Toolbar ───────────────────────────────────────────────────
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.addAction(sa)

        et = QAction("⚡ E-STOP", self)
        et.triggered.connect(self._on_estop)
        tb.addAction(et)
        # ── Status bar ────────────────────────────────────────────────
        self._status = QLabel("Ready")
        self.statusBar().addWidget(self._status, 1)
        self._dev_count = QLabel("Devices: 0")
        self.statusBar().addPermanentWidget(self._dev_count)

        # ── Work area (central widget) ─────────────────────────────────
        self._work_area = _WorkArea()
        self.setCentralWidget(self._work_area)

        # ── Console dock (bottom) ──────────────────────────────────────
        self._console = _Console(d)
        _console_dock = QDockWidget("Console", self)
        _console_dock.setWidget(self._console)
        _console_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, _console_dock)
        self._view_menu.addAction(_console_dock.toggleViewAction())

        # ── Device list dock (left) ────────────────────────────────────
        self._device_panel = _DevicePanel(d, self)
        _devices_dock = QDockWidget("Devices", self)
        _devices_dock.setWidget(self._device_panel)
        _devices_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, _devices_dock)
        self._view_menu.addAction(_devices_dock.toggleViewAction())

        self._console.command_ran.connect(self._on_console_command)

        # ── Restore geometry ───────────────────────────────────────────
        s = QSettings("SCPIToolkit", "GUI")
        if s.contains("geometry"):
            self.restoreGeometry(s.value("geometry"))
        if s.contains("state"):
            self.restoreState(s.value("state"))

        QTimer.singleShot(200, self._init)

    def _refresh_awg_panels(self) -> None:
        awgs = self._d.devices_of_type("awg")
        names = {name for name, _ in awgs}
        for name in list(self._awg_blocks.keys()):
            if name not in names:
                block = self._awg_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._awg_closed.discard(name)
        for name, _ in awgs:
            if name not in self._awg_blocks:
                block = _AWGBlock(self._d, name)
                block.stop()
                self._awg_blocks[name] = block
                self._awg_closed.add(name)

    def _refresh_dmm_panels(self) -> None:
        dmms = self._d.devices_of_type("dmm")
        names = {name for name, _ in dmms}
        for name in list(self._dmm_blocks.keys()):
            if name not in names:
                block = self._dmm_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._dmm_closed.discard(name)
        for name, _ in dmms:
            if name not in self._dmm_blocks:
                block = _DMMBlock(self._d, name)
                block.stop()
                self._dmm_blocks[name] = block
                self._dmm_closed.add(name)

    def _refresh_ev_panels(self) -> None:
        evs = [(n, d) for n, d in self._d.registry.devices.items() if n == "ev2300" or n.startswith("ev2300_")]
        names = {name for name, _ in evs}
        for name in list(self._ev_blocks.keys()):
            if name not in names:
                block = self._ev_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._ev_closed.discard(name)
        for name, _ in evs:
            if name not in self._ev_blocks:
                block = _EV2300Block(self._d, name)
                block.stop()
                self._ev_blocks[name] = block
                self._ev_closed.add(name)

    def _refresh_scope_panels(self) -> None:
        scopes = self._d.devices_of_type("scope")
        names = {name for name, _ in scopes}
        for name in list(self._scope_blocks.keys()):
            if name not in names:
                block = self._scope_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._scope_closed.discard(name)
        for name, _ in scopes:
            if name not in self._scope_blocks:
                block = _ScopeBlock(self._d, name)
                block.stop()
                self._scope_blocks[name] = block
                self._scope_closed.add(name)

    def _refresh_smu_panels(self) -> None:
        smus = self._d.devices_of_type("smu")
        names = {name for name, _ in smus}
        for name in list(self._smu_blocks.keys()):
            if name not in names:
                block = self._smu_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._smu_closed.discard(name)
        for name, _ in smus:
            if name not in self._smu_blocks:
                block = _SMUBlock(self._d, name)
                block.stop()
                self._smu_blocks[name] = block
                self._smu_closed.add(name)

    def _refresh_psu_panels(self) -> None:
        psus = self._d.devices_of_type("psu")
        names = {name for name, _ in psus}

        # Remove blocks for devices that no longer exist on the bus
        for name in list(self._psu_blocks.keys()):
            if name not in names:
                block = self._psu_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._psu_closed.discard(name)

        # Create blocks for newly discovered devices — don't open them yet.
        # User clicks the device in the panel to open/focus it (VS Code file-explorer style).
        for name, disp in psus:
            if name not in self._psu_blocks:
                block = _PSUBlock(self._d, name)
                block.stop()  # pause polling until the tab is actually opened
                self._psu_blocks[name] = block
                self._psu_closed.add(name)

    def _init(self) -> None:
        self._d._repl._general.safe_all()
        for name, dev in self._d.registry.devices.items():
            if re.sub(r"\d+$", "", name) == "psu":
                if hasattr(dev, "set_voltage"):
                    dev.set_voltage(0)
                if hasattr(dev, "set_current_limit"):
                    dev.set_current_limit(0)
        self._device_panel.refresh()
        self._refresh_psu_panels()
        self._refresh_smu_panels()
        self._refresh_awg_panels()
        self._refresh_dmm_panels()
        self._refresh_ev_panels()
        self._refresh_scope_panels()
        n = len(self._d.registry.devices)
        self._dev_count.setText(f"Devices: {n}")
        self._status.setText(f"{n} device(s) — all outputs safe")

    def _on_tab_closed(self, widget: QWidget) -> None:
        for name, block in self._psu_blocks.items():
            if block is widget:
                block.stop()
                self._psu_closed.add(name)
                return
        for name, block in self._smu_blocks.items():
            if block is widget:
                block.stop()
                self._smu_closed.add(name)
                return
        for name, block in self._awg_blocks.items():
            if block is widget:
                block.stop()
                self._awg_closed.add(name)
                return
        for name, block in self._dmm_blocks.items():
            if block is widget:
                block.stop()
                self._dmm_closed.add(name)
                return
        for name, block in self._ev_blocks.items():
            if block is widget:
                block.stop()
                self._ev_closed.add(name)
                return
        for name, block in self._scope_blocks.items():
            if block is widget:
                block.stop()
                self._scope_closed.add(name)
                return

    def _on_device_selected(self, name: str) -> None:
        base = re.sub(r"\d+$", "", name)
        if base == "psu":
            block = self._psu_blocks.get(name)
            if not block:
                return
            for group in self._work_area.all_groups():
                for i, (_, w) in enumerate(group._widgets):
                    if w is block:
                        group.set_current_tab(i)
                        return
            self._psu_closed.discard(name)
            disp = self._d.registry.display_name(name)
            self._work_area.add_widget(disp or name, block)
        elif base == "smu":
            block = self._smu_blocks.get(name)
            if not block:
                return
            for group in self._work_area.all_groups():
                for i, (_, w) in enumerate(group._widgets):
                    if w is block:
                        group.set_current_tab(i)
                        return
            self._smu_closed.discard(name)
            disp = self._d.registry.display_name(name)
            self._work_area.add_widget(disp or name, block)
        elif base == "awg":
            block = self._awg_blocks.get(name)
            if not block:
                return
            for group in self._work_area.all_groups():
                for i, (_, w) in enumerate(group._widgets):
                    if w is block:
                        group.set_current_tab(i)
                        return
            self._awg_closed.discard(name)
            disp = self._d.registry.display_name(name)
            self._work_area.add_widget(disp or name, block)
        elif base == "dmm":
            block = self._dmm_blocks.get(name)
            if not block:
                return
            for group in self._work_area.all_groups():
                for i, (_, w) in enumerate(group._widgets):
                    if w is block:
                        group.set_current_tab(i)
                        return
            self._dmm_closed.discard(name)
            disp = self._d.registry.display_name(name)
            self._work_area.add_widget(disp or name, block)
        elif name == "ev2300" or name.startswith("ev2300_"):
            block = self._ev_blocks.get(name)
            if not block:
                return
            for group in self._work_area.all_groups():
                for i, (_, w) in enumerate(group._widgets):
                    if w is block:
                        group.set_current_tab(i)
                        return
            self._ev_closed.discard(name)
            disp = self._d.registry.display_name(name)
            self._work_area.add_widget(disp or name, block)
        elif base == "scope":
            block = self._scope_blocks.get(name)
            if not block:
                return
            for group in self._work_area.all_groups():
                for i, (_, w) in enumerate(group._widgets):
                    if w is block:
                        group.set_current_tab(i)
                        return
            self._scope_closed.discard(name)
            disp = self._d.registry.display_name(name)
            self._work_area.add_widget(disp or name, block)

    @Slot()
    def _on_console_command(self) -> None:
        """Refresh all instrument blocks immediately after any console command."""
        for block in self._psu_blocks.values():
            block._poll()
        for block in self._smu_blocks.values():
            block._poll()
        for block in self._awg_blocks.values():
            block._poll()
        for block in self._dmm_blocks.values():
            block._poll()
        for block in self._scope_blocks.values():
            block._poll()
        n = len(self._d.registry.devices)
        if n != int(self._dev_count.text().split(": ", 1)[-1]):
            self._refresh_psu_panels()
            self._refresh_smu_panels()
            self._refresh_awg_panels()
            self._refresh_dmm_panels()
            self._refresh_ev_panels()
            self._refresh_scope_panels()
            self._device_panel.refresh()
            self._dev_count.setText(f"Devices: {n}")

    def _after_scan(self) -> None:
        self._refresh_psu_panels()
        self._refresh_smu_panels()
        self._refresh_awg_panels()
        self._refresh_dmm_panels()
        self._refresh_ev_panels()
        self._refresh_scope_panels()
        n = len(self._d.registry.devices)
        self._dev_count.setText(f"Devices: {n}")
        self._status.setText(f"Scan complete: {n} device(s)")

    def _on_scan(self) -> None:
        self._status.setText("Scanning...")
        QApplication.processEvents()
        result = self._d.run("scan")
        self._d._repl._general.safe_all()
        self._console.log_action("scan", result)
        self._device_panel.refresh()
        self._after_scan()

    def _on_estop(self) -> None:
        self._d._repl._general.safe_all()
        self._console.log_action("safe_all", "All outputs disabled")
        self._status.setText("E-STOP: all outputs disabled")
        for block in self._psu_blocks.values():
            block._poll()
        for block in self._smu_blocks.values():
            block._poll()
        for block in self._awg_blocks.values():
            block._poll()
        for block in self._dmm_blocks.values():
            block._poll()
        for block in self._scope_blocks.values():
            block._poll()

    def closeEvent(self, event) -> None:  # noqa: N802
        s = QSettings("SCPIToolkit", "GUI")
        s.setValue("geometry", self.saveGeometry())
        s.setValue("state", self.saveState())
        for block in self._psu_blocks.values():
            with contextlib.suppress(Exception):
                block.stop()
        for block in self._smu_blocks.values():
            with contextlib.suppress(Exception):
                block.stop()
        for block in self._awg_blocks.values():
            with contextlib.suppress(Exception):
                block.stop()
        for block in self._dmm_blocks.values():
            with contextlib.suppress(Exception):
                block.stop()
        for block in self._ev_blocks.values():
            with contextlib.suppress(Exception):
                block.stop()
        for block in self._scope_blocks.values():
            with contextlib.suppress(Exception):
                block.stop()
        super().closeEvent(event)


# -- Entry point -------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="SCPI Instrument Toolkit GUI")
    parser.add_argument("--mock", action="store_true", help="Use mock instruments")
    args = parser.parse_args(argv)

    app = QApplication(sys.argv)
    app.setApplicationName("SCPI Instrument Toolkit")

    d = _Dispatcher(mock=args.mock)
    win = _MainWindow(d)
    win.resize(1400, 820)
    win.show()

    sys.exit(app.exec())
