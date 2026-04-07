from __future__ import annotations

import contextlib
from typing import Any

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..core.dispatcher import _Dispatcher
from ..core.helpers import _CH_ACCENTS, _mono, _NumSpin


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

        for attr, _unit, color in [("v_display", "V", "#1e7a1e"), ("i_display", "A", "#c45c00")]:
            disp = QLabel("0.000")
            disp.setFont(_mono(18))
            disp.setStyleSheet(f"color: {color}; border-radius: 5px; padding: 4px 8px")
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

        self.toggle_btn = QPushButton("\u25cb  OUTPUT OFF")
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
        self.v_lim_spin.setStyleSheet("QDoubleSpinBox { font-size: 11px; }")
        lim_row.addWidget(self.v_lim_spin, 1)

        self.i_lim_spin = _NumSpin()
        self.i_lim_spin.setRange(0, self._max_i)
        self.i_lim_spin.setDecimals(4)
        self.i_lim_spin.setSingleStep(0.01)
        self.i_lim_spin.setSuffix(" A")
        self.i_lim_spin.setValue(self._max_i)
        self.i_lim_spin.setMinimumWidth(84)
        self.i_lim_spin.setStyleSheet("QDoubleSpinBox { font-size: 11px; }")
        lim_row.addWidget(self.i_lim_spin, 1)

        self.set_lim_btn = QPushButton("\u2713")
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
            self.set_lim_btn.setText("\u2713")
            self.set_lim_btn.setStyleSheet(
                "QPushButton { border: 2px solid #28a745; color: #a6e3a1; border-radius: 4px; "
                "padding: 3px; background: #d4edda; font-weight: bold; }"
                "QPushButton:hover { background: #28a745; color: white; }"
            )
        elif state == "pending":
            self.set_lim_btn.setText("!")
            self.set_lim_btn.setStyleSheet(
                "QPushButton { border: 2px solid orange; color: darkorange; border-radius: 4px; "
                "padding: 3px; font-weight: bold; }"
                "QPushButton:hover { background: orange; color: white; }"
            )
        else:
            self.set_lim_btn.setText("\u2713")
            self.set_lim_btn.setStyleSheet(
                "QPushButton { border: 1px solid #aaa; border-radius: 4px; padding: 3px; }"
                "QPushButton:hover { background: #ddd; }"
            )

    def _set_toggle_style(self, on: bool) -> None:
        if on:
            self.toggle_btn.setText("\u25cf  OUTPUT ON")
            self.toggle_btn.setStyleSheet(
                "QPushButton { background: #d4edda; color: #155724; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #28a745; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #28a745; color: white; }"
            )
        else:
            self.toggle_btn.setText("\u25cb  OUTPUT OFF")
            self.toggle_btn.setStyleSheet(
                "QPushButton { background: transparent; color: #c0392b; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #c0392b88; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #c0392b; color: white; }"
            )

    def sync_from_device(self, dev: Any, output_state: bool | None, ch_key: str | None) -> None:
        """Read device state and update UI displays. All reads wrapped in try/except."""
        try:
            if ch_key and hasattr(dev, "select_channel"):
                dev.select_channel(ch_key)
            v = dev.get_voltage_setpoint()
            i = dev.get_current_limit()
        except Exception:
            return  # device busy or errored — skip this poll

        on = output_state if output_state is not None else False
        try:
            if output_state is None:
                on = dev.get_output_state()
        except Exception:
            pass

        v_w = len(str(int(self._max_v))) + 4
        i_w = len(str(int(self._max_i))) + 5

        v_lim = self.v_lim_spin.value()
        i_lim = self.i_lim_spin.value()
        v_over = v > v_lim + 1e-9
        i_over = i > i_lim + 1e-9

        v_color = "#f38ba8" if v_over else "#1e7a1e"
        i_color = "#c0392b" if i_over else "#c45c00"
        self.v_display.setStyleSheet(f"color: {v_color}; border-radius: 5px; padding: 4px 8px")
        self.i_display.setStyleSheet(f"color: {i_color}; border-radius: 5px; padding: 4px 8px")
        self.v_display.setText(f"{v:{v_w}.3f} V")
        self.i_display.setText(f"{i:{i_w}.4f} A")

        self.toggle_btn.blockSignals(True)
        self.toggle_btn.setChecked(on)
        self.toggle_btn.blockSignals(False)
        self._set_toggle_style(on)


class _PSUBlock(QFrame):
    """Self-contained card for one PSU device.

    All writes route through self._d.run() so they go through the REPL
    command handler with its safety checks.  Reads (polling) call device
    methods directly for structured data.
    """

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._psu = name
        self._chs: dict[int, _PSUChannel] = {}
        self._ch_output: dict[int, bool] = {}
        self._ch_keys: dict[int, str | None] = {}
        self.setObjectName("psublock")
        self.setStyleSheet("#psublock { border: 1px solid #ccc; border-radius: 10px; }")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._build()
        self._rebuild()
        self._init_channels()
        # NOTE: do NOT call _poll() here — device may still be busy from scan

    def _con(self):

        w = self.parent()
        while w is not None:
            if hasattr(w, "_console"):
                return w._console
            w = w.parent()
        return None

    def _run(self, cmd: str) -> str:
        """Execute a REPL command through the dispatcher (unified safety path)."""
        result = self._d.run(f"use {self._psu}\n{cmd}")
        con = self._con()
        if con:
            con.log_action(f"{self._psu}: {cmd}", result.strip() if result.strip() else "OK")
        return result

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        hdr = QFrame()
        hdr.setStyleSheet("QFrame { border-bottom: 1px solid #ccc; border-radius: 0; }")
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
        ch_from_num = getattr(dev.__class__, "CHANNEL_FROM_NUMBER", None)
        ch_map = getattr(dev, "CHANNEL_MAP", None)
        ch_limits = getattr(dev, "CHANNEL_LIMITS", {})
        dev_max_v: float | None = getattr(dev, "MAX_VOLTAGE", None)
        dev_max_i: float | None = getattr(dev, "MAX_CURRENT", None)

        if multi and ch_from_num:
            defs = [(n, ch.value, ch) for n, ch in ch_from_num.items()]
        elif multi and ch_map:
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
        self._ch_output = {num: False for num in self._chs}
        ctx_limits = self._d._repl.ctx.safety_limits
        for num, w in self._chs.items():
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
        global_state: bool | None = None
        if multi:
            with contextlib.suppress(Exception):
                global_state = dev.get_output_state()
        for ch_num, w in self._chs.items():
            ch_key = self._ch_keys.get(ch_num)
            state = global_state if multi else None
            if state is not None:
                self._ch_output[ch_num] = state
            w.sync_from_device(dev, state, ch_key)

    # -- Writes: all routed through REPL for unified safety --------------------

    def _apply(self, ch_num: int) -> None:
        w = self._chs.get(ch_num)
        if not w:
            return
        v, i = w.v_spin.value(), w.i_spin.value()
        multi = self._d.has_cap(self._psu, "multi_channel")
        if multi:
            self._run(f"psu set {ch_num} {v} {i}")
        else:
            self._run(f"psu set {v} {i}")
        self._status.setText(f"Applied: {v}V @ {i}A")
        self._status.setStyleSheet("color: #155724; font-size: 10px;")
        self._poll()

    def _set_limit(self, ch_num: int) -> None:
        w = self._chs.get(ch_num)
        if not w:
            return
        v_lim, i_lim = w.v_lim_spin.value(), w.i_lim_spin.value()
        multi = self._d.has_cap(self._psu, "multi_channel")
        if multi:
            self._run(f"upper_limit {self._psu} chan {ch_num} voltage {v_lim}")
            self._run(f"upper_limit {self._psu} chan {ch_num} current {i_lim}")
        else:
            self._run(f"upper_limit {self._psu} voltage {v_lim}")
            self._run(f"upper_limit {self._psu} current {i_lim}")
        w.v_spin.setMaximum(v_lim)
        w.i_spin.setMaximum(i_lim)
        w._set_lim_state("active")
        self._status.setText(f"CH{ch_num} limits: \u2264{v_lim}V / \u2264{i_lim}A")
        self._status.setStyleSheet("color: darkorange; font-size: 10px;")

    def _output(self, ch_num: int, on: bool) -> None:
        multi = self._d.has_cap(self._psu, "multi_channel")
        state = "on" if on else "off"
        if multi:
            self._run(f"psu chan {ch_num} {state}")
        else:
            self._run(f"psu chan {state}")
        self._poll()

    @Slot()
    def _all_on(self) -> None:
        self._run("psu on")
        self._poll()

    @Slot()
    def _all_off(self) -> None:
        self._run("psu off")
        self._poll()

    @Slot(bool)
    def _on_track(self, on: bool) -> None:
        self._run(f"psu track {'on' if on else 'off'}")
        self._track_btn.setText(f"Track: {'ON' if on else 'OFF'}")
        self._poll()

    def _save_recall(self, action: str) -> None:
        self._run(f"psu {action} 1")
        self._poll()

    def stop(self) -> None:
        pass
