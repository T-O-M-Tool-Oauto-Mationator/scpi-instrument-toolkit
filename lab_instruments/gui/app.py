"""SCPI Instrument Toolkit - Desktop GUI."""

from __future__ import annotations

import argparse
import atexit
import contextlib
import io
import re
import signal
import sys
from typing import Any

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
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
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# -- ANSI helpers ------------------------------------------------------------

_ANSI_RE = re.compile(r"\033\[([0-9;]*)m")
_ANSI_COLORS = {"91": "#f38ba8", "92": "#a6e3a1", "93": "#f9e2af", "94": "#89b4fa", "96": "#94e2d5"}


def _ansi_to_html(text: str) -> str:
    if "\033" not in text:
        return _esc(text)
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
    return "".join(parts)


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
        with contextlib.redirect_stdout(buf):
            self._repl.onecmd(command)
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


class _Console(QDockWidget):
    def __init__(self, d: _Dispatcher, parent: QWidget | None = None) -> None:
        super().__init__("Console", parent)
        self.setObjectName("console")
        self._d = d
        self._history: list[str] = []
        self._hist_idx = -1

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(4, 4, 4, 4)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(_mono())
        self._output.document().setMaximumBlockCount(5000)
        lay.addWidget(self._output, 1)

        row = QHBoxLayout()
        lbl = QLabel("eset>")
        lbl.setFont(_mono())
        lbl.setStyleSheet("color: #89b4fa; background: transparent;")
        row.addWidget(lbl)
        self._input = QLineEdit()
        self._input.setFont(_mono())
        self._input.setPlaceholderText("Type a command...")
        self._input.returnPressed.connect(self._on_submit)
        row.addWidget(self._input, 1)
        lay.addLayout(row)
        self.setWidget(w)

    def keyPressEvent(self, ev):  # noqa: N802
        if self._input.hasFocus():
            if ev.key() == Qt.Key.Key_Up:
                self._nav(-1)
                return
            if ev.key() == Qt.Key.Key_Down:
                self._nav(1)
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
        self.log(f"<b style='color:#89b4fa'>eset&gt;</b> {_esc(cmd)}")
        result = self._d.run(cmd)
        if result.strip():
            self.log(_ansi_to_html(result.rstrip("\n")))

    def log(self, html: str) -> None:
        self._output.append(html)
        self._output.verticalScrollBar().setValue(self._output.verticalScrollBar().maximum())

    def log_action(self, cmd: str, result: str = "") -> None:
        self.log(f"<span style='color:#6c7086'>[gui]</span> <b style='color:#89b4fa'>eset&gt;</b> {_esc(cmd)}")
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
    "#f9e2af",  # ch1 – yellow  (e.g. P6V)
    "#89b4fa",  # ch2 – blue    (e.g. P25V / P30V)
    "#cba6f7",  # ch3 – mauve   (e.g. N25V / N30V)
    "#a6e3a1",  # ch4 – green
    "#94e2d5",  # ch5 – teal
    "#fab387",  # ch6 – peach
]


# -- PSU channel widget ------------------------------------------------------


class _PSUChannel(QGroupBox):
    def __init__(
        self,
        channel: int,
        label: str,
        max_v: float | None = None,
        max_i: float | None = None,
        accent: str = "#89b4fa",
        parent: QWidget | None = None,
    ) -> None:
        title = f"{label}   {max_v:g} V / {max_i:g} A" if max_v is not None and max_i is not None else label
        super().__init__(title, parent)
        self.channel = channel
        self._accent = accent
        self._max_v = max_v if max_v is not None else 60.0
        self._max_i = max_i if max_i is not None else 10.0
        self.setStyleSheet(
            f"QGroupBox {{ border: 2px solid {accent}55; border-radius: 7px; "
            f"margin-top: 12px; padding-top: 14px; background: #1a1a28; }}"
            f"QGroupBox::title {{ color: {accent}; subcontrol-origin: margin; "
            f"left: 10px; padding: 0 6px; font-weight: bold; }}"
        )
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(8, 8, 8, 8)

        # ── Measurement displays ──────────────────────────────────────
        meas = QHBoxLayout()
        meas.setSpacing(5)

        for attr, unit, color in [("v_display", "V", "#a6e3a1"), ("i_display", "A", "#fab387")]:
            col = QVBoxLayout()
            col.setSpacing(2)

            hdr = QLabel(unit)
            hdr.setStyleSheet(f"color: {color}88; font-size: 9px; font-weight: bold; background: transparent;")
            hdr.setAlignment(Qt.AlignmentFlag.AlignRight)
            col.addWidget(hdr)

            disp = QLabel("0.000")
            disp.setFont(_mono(21))
            disp.setStyleSheet(
                f"color: {color}; background: #0d0d1a; border-radius: 5px; "
                f"padding: 7px 8px; border: 1px solid #2a2a3f;"
            )
            disp.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            disp.setMinimumHeight(54)
            disp.setMinimumWidth(90)
            setattr(self, attr, disp)
            col.addWidget(disp)
            meas.addLayout(col, 1)

        layout.addLayout(meas)

        # ── Setpoints ─────────────────────────────────────────────────
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

        # ── Output toggle ─────────────────────────────────────────────
        self.toggle_btn = QPushButton("○  OUTPUT OFF")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setMinimumHeight(32)
        self._set_toggle_style(False)
        layout.addWidget(self.toggle_btn)

        # ── Safety limits (compact) ───────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #f9e2af33;")
        layout.addWidget(sep)

        lim_row = QHBoxLayout()
        lim_row.setSpacing(4)

        lim_lbl = QLabel("Limits")
        lim_lbl.setStyleSheet("color: #f9e2af99; font-size: 10px; background: transparent;")
        lim_row.addWidget(lim_lbl)

        self.v_lim_spin = _NumSpin()
        self.v_lim_spin.setRange(0, self._max_v)
        self.v_lim_spin.setDecimals(3)
        self.v_lim_spin.setSingleStep(0.1)
        self.v_lim_spin.setSuffix(" V")
        self.v_lim_spin.setValue(self._max_v)
        self.v_lim_spin.setMinimumWidth(84)
        self.v_lim_spin.setStyleSheet(
            "QDoubleSpinBox { border-color: #f9e2af44; font-size: 11px; }"
            "QDoubleSpinBox:focus { border-color: #f9e2af; }"
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
            "QDoubleSpinBox { border-color: #f9e2af44; font-size: 11px; }"
            "QDoubleSpinBox:focus { border-color: #f9e2af; }"
        )
        lim_row.addWidget(self.i_lim_spin, 1)

        self.set_lim_btn = QPushButton("✓")
        self.set_lim_btn.setFixedWidth(28)
        self.set_lim_btn.setStyleSheet(
            "QPushButton { border: 1px solid #f9e2af55; color: #f9e2af; border-radius: 4px; padding: 3px; }"
            "QPushButton:hover { background: #f9e2af; color: #1e1e2e; }"
        )
        lim_row.addWidget(self.set_lim_btn)
        layout.addLayout(lim_row)

    def _set_toggle_style(self, on: bool) -> None:
        if on:
            self.toggle_btn.setText("●  OUTPUT ON")
            self.toggle_btn.setStyleSheet(
                "QPushButton { background: #a6e3a122; color: #a6e3a1; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #a6e3a1; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #a6e3a1; color: #1e1e2e; }"
            )
        else:
            self.toggle_btn.setText("○  OUTPUT OFF")
            self.toggle_btn.setStyleSheet(
                "QPushButton { background: transparent; color: #f38ba8; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #f38ba855; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #f38ba8; color: #1e1e2e; }"
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

        v_color = "#f38ba8" if v_over else "#a6e3a1"
        i_color = "#f38ba8" if i_over else "#fab387"
        self.v_display.setStyleSheet(
            f"color: {v_color}; background: #0d0d1a; border-radius: 5px; "
            f"padding: 7px 8px; border: 1px solid #2a2a3f;"
        )
        self.i_display.setStyleSheet(
            f"color: {i_color}; background: #0d0d1a; border-radius: 5px; "
            f"padding: 7px 8px; border: 1px solid #2a2a3f;"
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
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)
        self.setObjectName("psublock")
        self.setStyleSheet(
            "#psublock { background: #20202f; border: 1px solid #3a3a5c; border-radius: 10px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self._build()
        self._rebuild()
        self._init_channels()
        self._poll()
        self._timer.start(1000)

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

        # ── Header ──────────────────────────────────────────────────
        hdr = QFrame()
        hdr.setStyleSheet(
            "QFrame { background: #2a2a42; border-bottom: 1px solid #3a3a5c; "
            "border-top-left-radius: 10px; border-top-right-radius: 10px; "
            "border-bottom-left-radius: 0; border-bottom-right-radius: 0; }"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 9, 14, 9)
        hdr_lay.setSpacing(8)

        name_lbl = QLabel(f"<b>{self._psu}</b>")
        name_lbl.setStyleSheet("background: transparent; font-size: 14px; color: #cdd6f4; letter-spacing: 0.5px;")
        hdr_lay.addWidget(name_lbl)

        dev = self._d.device(self._psu)
        if dev:
            disp_name = self._d.registry.display_name(self._psu)
            type_lbl = QLabel(disp_name)
            type_lbl.setStyleSheet("background: transparent; color: #585b70; font-size: 11px;")
            hdr_lay.addWidget(type_lbl, 1)
        else:
            hdr_lay.addStretch(1)

        outer.addWidget(hdr)

        # ── Body ──────────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(10, 10, 10, 6)
        body_lay.setSpacing(8)

        # Channel widgets go here (populated by _rebuild)
        self._ch_row_w = QWidget()
        self._ch_row_w.setStyleSheet("background: transparent;")
        self._ch_row_lay = QHBoxLayout(self._ch_row_w)
        self._ch_row_lay.setContentsMargins(0, 0, 0, 0)
        self._ch_row_lay.setSpacing(8)
        body_lay.addWidget(self._ch_row_w)

        # ── Footer buttons ────────────────────────────────────────────
        foot = QHBoxLayout()
        foot.setSpacing(6)

        for text, color, slot in [
            ("All ON", "#a6e3a1", self._all_on),
            ("All OFF", "#f38ba8", self._all_off),
        ]:
            b = QPushButton(text)
            b.setStyleSheet(
                f"QPushButton {{ border: 1px solid {color}66; color: {color}; border-radius: 4px; "
                f"padding: 4px 12px; font-weight: bold; font-size: 11px; background: transparent; }} "
                f"QPushButton:hover {{ background: {color}; color: #1e1e2e; }}"
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
        self._status.setStyleSheet("color: #585b70; font-size: 10px; background: transparent;")
        body_lay.addWidget(self._status)

        outer.addWidget(body, 1)

    # -- Device setup --------------------------------------------------------

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

    # -- Polling -------------------------------------------------------------

    @Slot()
    def _poll(self) -> None:
        dev = self._d.device(self._psu)
        if not dev:
            return
        multi = self._d.has_cap(self._psu, "multi_channel")
        for ch_num, w in self._chs.items():
            state = self._ch_output.get(ch_num) if multi else None
            ch_key = self._ch_keys.get(ch_num)
            w.sync_from_device(dev, state, ch_key)

    # -- Actions -------------------------------------------------------------

    def _apply(self, ch_num: int) -> None:
        dev = self._d.device(self._psu)
        w = self._chs.get(ch_num)
        if not dev or not w:
            return
        v, i = w.v_spin.value(), w.i_spin.value()
        v_lim, i_lim = w.v_lim_spin.value(), w.i_lim_spin.value()

        if v > v_lim + 1e-9:
            self._status.setText(f"BLOCKED: {v}V > limit {v_lim}V")
            self._status.setStyleSheet("color: #f38ba8; font-size: 10px; font-weight: bold;")
            con = self._con()
            if con:
                con.log_action(f"{self._psu} ch{ch_num}", f"[BLOCKED] {v}V > limit {v_lim}V")
            return
        if i > i_lim + 1e-9:
            self._status.setText(f"BLOCKED: {i}A > limit {i_lim}A")
            self._status.setStyleSheet("color: #f38ba8; font-size: 10px; font-weight: bold;")
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
        self._status.setStyleSheet("color: #a6e3a1; font-size: 10px;")
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
        self._status.setText(f"CH{ch_num} limits: ≤{v_lim}V / ≤{i_lim}A")
        self._status.setStyleSheet("color: #f9e2af; font-size: 10px;")
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
        self._timer.stop()


# -- PSU panel (central widget: horizontal scroll of all PSU cards) ----------


class _PSUPanel(QWidget):
    def __init__(self, d: _Dispatcher, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._blocks: dict[str, _PSUBlock] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._inner = QWidget()
        self._inner.setStyleSheet("background: transparent;")
        self._inner_lay = QHBoxLayout(self._inner)
        self._inner_lay.setContentsMargins(12, 12, 12, 12)
        self._inner_lay.setSpacing(12)
        self._inner_lay.addStretch()
        self._scroll.setWidget(self._inner)
        outer.addWidget(self._scroll, 1)

        self._empty_lbl = QLabel("No PSU devices found.\nClick Scan or launch with --mock.")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.setStyleSheet("color: #585b70; font-size: 16px;")
        self._empty_lbl.hide()
        outer.addWidget(self._empty_lbl, 1)

    def refresh_devices(self) -> None:
        psus = self._d.devices_of_type("psu")
        names = {name for name, _ in psus}

        for name in list(self._blocks.keys()):
            if name not in names:
                b = self._blocks.pop(name)
                b.stop()
                self._inner_lay.removeWidget(b)
                b.deleteLater()

        for name, _ in psus:
            if name not in self._blocks:
                b = _PSUBlock(self._d, name, self._inner)
                count = self._inner_lay.count()
                self._inner_lay.insertWidget(count - 1, b)  # before stretch
                self._blocks[name] = b

        has = bool(self._blocks)
        self._scroll.setVisible(has)
        self._empty_lbl.setVisible(not has)

    def select_device(self, name: str) -> None:
        b = self._blocks.get(name)
        if b:
            self._scroll.ensureWidgetVisible(b)

    def _poll_all(self) -> None:
        for b in self._blocks.values():
            b._poll()

    def stop(self) -> None:
        for b in self._blocks.values():
            b.stop()


# -- Device list panel -------------------------------------------------------


class _DevicePanel(QDockWidget):
    _TYPE_COLORS = {"psu": "#89b4fa", "awg": "#cba6f7", "dmm": "#fab387", "scope": "#94e2d5", "smu": "#f38ba8"}

    def __init__(self, d: _Dispatcher, parent: QWidget | None = None) -> None:
        super().__init__("Devices", parent)
        self.setObjectName("devices")
        self._d = d

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(6)

        self._scan_btn = QPushButton("⟳  Scan")
        self._scan_btn.setStyleSheet(
            "QPushButton { background: #313155; color: #89b4fa; border: 1px solid #89b4fa55; "
            "border-radius: 5px; padding: 6px 14px; font-weight: bold; }"
            "QPushButton:hover { background: #89b4fa; color: #1e1e2e; }"
        )
        self._scan_btn.clicked.connect(self._on_scan)
        lay.addWidget(self._scan_btn)

        self._list = QListWidget()
        self._list.setFont(_mono(10))
        self._list.setStyleSheet(
            "QListWidget { background: #181825; border: 1px solid #313155; border-radius: 6px; }"
            "QListWidget::item { padding: 8px 10px; border-bottom: 1px solid #1e1e2e; }"
            "QListWidget::item:hover { background: #252540; }"
            "QListWidget::item:selected { background: #313155; border-left: 3px solid #89b4fa; }"
        )
        self._list.itemClicked.connect(self._on_item_click)
        lay.addWidget(self._list, 1)
        self.setWidget(w)

    def _on_scan(self) -> None:
        self._scan_btn.setEnabled(False)
        self._scan_btn.setText("Scanning...")
        QApplication.processEvents()
        result = self._d.run("scan")
        self._d._repl._general.safe_all()
        self._scan_btn.setEnabled(True)
        self._scan_btn.setText("⟳  Scan")
        self.refresh()
        con = getattr(self.parent(), "_console", None)
        if con:
            con.log_action("scan", result)
            con.log_action("safe_all", "All outputs set to safe state")
        win = self.parent()
        if isinstance(win, _MainWindow):
            win._after_scan()

    def _on_item_click(self, item: QListWidgetItem) -> None:
        name = item.data(Qt.ItemDataRole.UserRole)
        if name:
            win = self.parent()
            if isinstance(win, _MainWindow):
                win._on_device_selected(name)

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
            color = self._TYPE_COLORS.get(base, "#cdd6f4")
            item = QListWidgetItem(f"  {name}\n  {disp}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            item.setToolTip(f"{name}  —  {disp}  ({base.upper()})")
            self._list.addItem(item)


# -- Global stylesheet -------------------------------------------------------

_STYLE = """
QMainWindow, QWidget {
    background: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Ubuntu", "Noto Sans", sans-serif;
    font-size: 13px;
}
QDockWidget {
    color: #cdd6f4;
}
QDockWidget::title {
    background: #252536;
    border: 1px solid #313155;
    border-radius: 0;
    padding: 7px 10px;
    font-weight: bold;
    color: #a6adc8;
}
QMenuBar {
    background: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313155;
    padding: 2px;
}
QMenuBar::item:selected { background: #89b4fa; color: #1e1e2e; border-radius: 4px; }
QMenu {
    background: #252536;
    color: #cdd6f4;
    border: 1px solid #313155;
    padding: 4px;
}
QMenu::item { padding: 5px 20px; border-radius: 3px; }
QMenu::item:selected { background: #89b4fa; color: #1e1e2e; }
QToolBar {
    background: #181825;
    border-bottom: 1px solid #313155;
    spacing: 6px;
    padding: 3px 6px;
}
QStatusBar {
    background: #181825;
    color: #585b70;
    border-top: 1px solid #313155;
    font-size: 12px;
}
QPushButton {
    background: #252536;
    color: #cdd6f4;
    border: 1px solid #313155;
    border-radius: 5px;
    padding: 5px 12px;
}
QPushButton:hover { border-color: #89b4fa; color: #89b4fa; }
QPushButton:disabled { color: #45475a; border-color: #313155; }
QLineEdit, QDoubleSpinBox, QComboBox {
    background: #252536;
    color: #cdd6f4;
    border: 1px solid #313155;
    border-radius: 5px;
    padding: 4px 8px;
    selection-background-color: #89b4fa44;
}
QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus { border-color: #89b4fa; }
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: #313155;
    border: none;
    width: 16px;
    border-radius: 2px;
}
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover { background: #45475a; }
QGroupBox {
    border: 1px solid #313155;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 14px;
}
QGroupBox::title {
    color: #89b4fa;
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QTextEdit {
    background: #181825;
    color: #cdd6f4;
    border: 1px solid #313155;
    border-radius: 5px;
    selection-background-color: #89b4fa44;
}
QScrollBar:vertical {
    background: #181825;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #313155;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #181825;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #313155;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #585b70; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QLabel { background: transparent; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox::down-arrow { width: 10px; }
QComboBox QAbstractItemView {
    background: #252536;
    color: #cdd6f4;
    border: 1px solid #313155;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
    border-radius: 4px;
}
QScrollArea { background: transparent; border: none; }
QFrame { background: transparent; border: none; }
QSplitter::handle { background: #313155; }
"""


# -- Main window -------------------------------------------------------------


class _MainWindow(QMainWindow):
    def __init__(self, d: _Dispatcher) -> None:
        super().__init__()
        self._d = d
        self.setWindowTitle("SCPI Instrument Toolkit")
        self.setStyleSheet(_STYLE)
        self._panels: list = []

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

        # ── Toolbar ───────────────────────────────────────────────────
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.addAction(sa)

        et = QAction("⚡ E-STOP", self)
        et.triggered.connect(self._on_estop)
        tb.addAction(et)
        ew = tb.widgetForAction(et)
        if ew:
            ew.setStyleSheet(
                "QToolButton { color: #f38ba8; font-weight: bold; font-size: 13px; "
                "border: 2px solid #f38ba888; border-radius: 5px; padding: 4px 14px; "
                "background: #f38ba811; }"
                "QToolButton:hover { background: #f38ba8; color: #1e1e2e; border-color: #f38ba8; }"
            )

        # ── Status bar ────────────────────────────────────────────────
        self._status = QLabel("Ready")
        self.statusBar().addWidget(self._status, 1)
        self._dev_count = QLabel("Devices: 0")
        self.statusBar().addPermanentWidget(self._dev_count)

        # ── Central widget: PSU cards ─────────────────────────────────
        self._psu_panel = _PSUPanel(d, self)
        self.setCentralWidget(self._psu_panel)
        self._panels.append(self._psu_panel)

        # ── Dock: device list (left) ───────────────────────────────────
        self._device_panel = _DevicePanel(d, self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._device_panel)
        self._panels.append(self._device_panel)

        # ── Dock: console (bottom) ─────────────────────────────────────
        self._console = _Console(d, self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._console)
        self._panels.append(self._console)

        QTimer.singleShot(200, self._init)

    def _init(self) -> None:
        self._d._repl._general.safe_all()
        for name, dev in self._d.registry.devices.items():
            if re.sub(r"\d+$", "", name) == "psu":
                if hasattr(dev, "set_voltage"):
                    dev.set_voltage(0)
                if hasattr(dev, "set_current_limit"):
                    dev.set_current_limit(0)
        self._device_panel.refresh()
        self._psu_panel.refresh_devices()
        n = len(self._d.registry.devices)
        self._dev_count.setText(f"Devices: {n}")
        self._status.setText(f"{n} device(s) — all outputs safe")

    def _on_device_selected(self, name: str) -> None:
        base = re.sub(r"\d+$", "", name)
        if base == "psu":
            self._psu_panel.select_device(name)

    def _after_scan(self) -> None:
        self._psu_panel.refresh_devices()
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
        self._psu_panel._poll_all()

    def closeEvent(self, event):  # noqa: N802
        for p in self._panels:
            if hasattr(p, "stop"):
                with contextlib.suppress(Exception):
                    p.stop()
        super().closeEvent(event)


# -- Entry point -------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SCPI Instrument Toolkit GUI")
    parser.add_argument("--mock", action="store_true", help="Use mock instruments")
    args = parser.parse_args(argv)

    app = QApplication(sys.argv)
    app.setApplicationName("SCPI Instrument Toolkit")

    d = _Dispatcher(mock=args.mock)
    win = _MainWindow(d)
    win.resize(1400, 820)
    win.show()

    rc = app.exec()
    del win
    del app
    return rc
