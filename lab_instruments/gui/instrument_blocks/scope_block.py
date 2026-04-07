from __future__ import annotations

import contextlib

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QComboBox,
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
from ..core.helpers import _mono, _NumSpin

_SCOPE_MEAS = [
    ("Freq", "measure_frequency", "Hz"),
    ("Vpp", "measure_peak_to_peak", "V"),
    ("RMS", "measure_rms", "V"),
    ("Mean", "measure_mean", "V"),
]

_HSCALE_LABELS = [
    "1 ns", "2 ns", "5 ns",
    "10 ns", "20 ns", "50 ns",
    "100 ns", "200 ns", "500 ns",
    "1 µs", "2 µs", "5 µs",
    "10 µs", "20 µs", "50 µs",
    "100 µs", "200 µs", "500 µs",
    "1 ms", "2 ms", "5 ms",
    "10 ms", "20 ms", "50 ms",
    "100 ms", "200 ms", "500 ms",
    "1 s", "2 s", "5 s",
]
_HSCALE_SECS = [
    1e-9, 2e-9, 5e-9,
    10e-9, 20e-9, 50e-9,
    100e-9, 200e-9, 500e-9,
    1e-6, 2e-6, 5e-6,
    10e-6, 20e-6, 50e-6,
    100e-6, 200e-6, 500e-6,
    1e-3, 2e-3, 5e-3,
    10e-3, 20e-3, 50e-3,
    100e-3, 200e-3, 500e-3,
    1.0, 2.0, 5.0,
]
_VSCALE_LABELS = [
    "1 mV", "2 mV", "5 mV",
    "10 mV", "20 mV", "50 mV",
    "100 mV", "200 mV", "500 mV",
    "1 V", "2 V", "5 V",
    "10 V", "20 V", "50 V",
]
_VSCALE_VOLTS = [
    1e-3, 2e-3, 5e-3,
    10e-3, 20e-3, 50e-3,
    100e-3, 200e-3, 500e-3,
    1.0, 2.0, 5.0,
    10.0, 20.0, 50.0,
]


class _ScopeBlock(QFrame):
    """Self-contained card for one oscilloscope device."""

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._scope = name
        self.setObjectName("scopeblock")
        self.setStyleSheet("#scopeblock { border: 1px solid #ccc; border-radius: 10px; }")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._build()

    def _con(self):

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
        hdr.setStyleSheet("QFrame { border-bottom: 1px solid #ccc; border-radius: 0; }")
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

        # H-scale row
        hscale_row = QHBoxLayout()
        hscale_row.setSpacing(4)
        hscale_row.addWidget(QLabel("H Scale"))
        self._hscale_combo = QComboBox()
        self._hscale_combo.addItems(_HSCALE_LABELS)
        self._hscale_combo.setCurrentIndex(18)  # 1 ms default
        self._hscale_combo.activated.connect(lambda i: self._repl(f"scope hscale {_HSCALE_SECS[i]}"))
        hscale_row.addWidget(self._hscale_combo)
        hmove_left = QPushButton("◄")
        hmove_left.setFixedWidth(28)
        hmove_left.clicked.connect(lambda: self._repl("scope hmove -1"))
        hscale_row.addWidget(hmove_left)
        hmove_right = QPushButton("►")
        hmove_right.setFixedWidth(28)
        hmove_right.clicked.connect(lambda: self._repl("scope hmove 1"))
        hscale_row.addWidget(hmove_right)
        hscale_row.addStretch()
        grp_lay.addLayout(hscale_row)

        # Trigger config row
        trig_cfg = QHBoxLayout()
        trig_cfg.setSpacing(4)
        trig_cfg.addWidget(QLabel("Trig"))
        self._trig_src_combo = QComboBox()
        self._trig_src_combo.addItems(["CH1", "CH2", "CH3", "CH4"])
        trig_cfg.addWidget(self._trig_src_combo)
        trig_cfg.addWidget(QLabel("Level"))
        self._trig_level_spin = _NumSpin()
        self._trig_level_spin.setRange(-50.0, 50.0)
        self._trig_level_spin.setDecimals(3)
        self._trig_level_spin.setSuffix(" V")
        self._trig_level_spin.setMinimumWidth(88)
        trig_cfg.addWidget(self._trig_level_spin)
        set_trig_btn = QPushButton("Set Trig")
        set_trig_btn.clicked.connect(self._set_trigger)
        trig_cfg.addWidget(set_trig_btn)
        trig_cfg.addStretch()
        grp_lay.addLayout(trig_cfg)

        # Channel status rows
        self._ch_labels: dict[int, QLabel] = {}
        self._ch_btns: dict[int, QPushButton] = {}
        self._ch_vscale: dict[int, QComboBox] = {}
        self._ch_coupling: dict[int, QComboBox] = {}
        self._ch_probe: dict[int, QComboBox] = {}
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
            vscale = QComboBox()
            vscale.addItems(_VSCALE_LABELS)
            vscale.setCurrentIndex(9)  # 1 V default
            vscale.activated.connect(lambda i, c=ch: self._repl(f"scope vscale {c} {_VSCALE_VOLTS[i]}"))
            col.addWidget(vscale)
            self._ch_vscale[ch] = vscale
            coupling = QComboBox()
            coupling.addItems(["DC", "AC", "GND"])
            coupling.activated.connect(lambda i, c=ch, cb=coupling: self._repl(f"scope coupling {c} {cb.currentText()}"))
            col.addWidget(coupling)
            self._ch_coupling[ch] = coupling
            probe = QComboBox()
            probe.addItems(["1X", "10X", "100X"])
            probe.activated.connect(lambda i, c=ch, cb=probe: self._repl(f"scope probe {c} {cb.currentText()}"))
            col.addWidget(probe)
            self._ch_probe[ch] = probe
            ch_grid.addLayout(col)
        grp_lay.addLayout(ch_grid)

        # Measurement channel selector
        meas_ch_row = QHBoxLayout()
        meas_ch_row.setSpacing(4)
        meas_ch_row.addWidget(QLabel("Measure"))
        self._meas_ch_combo = QComboBox()
        self._meas_ch_combo.addItems(["CH1", "CH2", "CH3", "CH4"])
        meas_ch_row.addWidget(self._meas_ch_combo)
        meas_ch_row.addStretch()
        grp_lay.addLayout(meas_ch_row)

        # Measurement display
        meas_row = QHBoxLayout()
        meas_row.setSpacing(6)
        self._meas_labels: dict[str, QLabel] = {}
        for meas_name, _, unit in _SCOPE_MEAS:
            col = QVBoxLayout()
            col.setSpacing(1)
            hdr_l = QLabel(meas_name)
            hdr_l.setStyleSheet("font-size: 9px;")
            hdr_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(hdr_l)
            val_l = QLabel(f"--- {unit}")
            val_l.setFont(_mono(12))
            val_l.setStyleSheet("color: #1e7a1e;")
            val_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(val_l)
            self._meas_labels[meas_name] = val_l
            meas_row.addLayout(col)
        grp_lay.addLayout(meas_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        grp_lay.addWidget(sep)

        # Control row
        ctrl = QHBoxLayout()
        ctrl.setSpacing(4)
        for text, slot in [
            ("Run", self._run),
            ("Stop", self._stop),
            ("Single", self._single),
            ("AutoSet", self._autoset),
            ("Screenshot", self._screenshot),
        ]:
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

    def _repl(self, cmd: str) -> str:
        result = self._d.run(f"use {self._scope}\n{cmd}")
        con = self._con()
        if con:
            con.log_action(f"{self._scope}: {cmd}", result.strip() if result.strip() else "OK")
        return result

    def _toggle_ch(self, ch: int, on: bool) -> None:
        self._repl(f"scope chan {ch} {'on' if on else 'off'}")

    def _run(self) -> None:
        self._repl("scope run")
        self._poll()

    def _stop(self) -> None:
        self._repl("scope stop")
        self._poll()

    def _single(self) -> None:
        self._repl("scope single")
        self._poll()

    def _autoset(self) -> None:
        self._repl("scope autoset")
        self._poll()

    def _set_trigger(self) -> None:
        src = self._trig_src_combo.currentText()
        level = self._trig_level_spin.value()
        self._repl(f"scope trigger {src} {level}")

    def _screenshot(self) -> None:
        self._repl("scope screenshot")

    @Slot()
    def _poll(self) -> None:
        if self._d.is_busy():
            return
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
        with contextlib.suppress(Exception):
            tb = dev.get_timebase()
            if tb is not None:
                closest = min(range(len(_HSCALE_SECS)), key=lambda i: abs(_HSCALE_SECS[i] - tb))
                self._hscale_combo.blockSignals(True)
                self._hscale_combo.setCurrentIndex(closest)
                self._hscale_combo.blockSignals(False)
        # Measurements on the selected channel
        meas_ch = self._meas_ch_combo.currentIndex() + 1
        for meas_name, method, unit in _SCOPE_MEAS:
            with contextlib.suppress(Exception):
                fn = getattr(dev, method, None)
                if fn:
                    val = fn(meas_ch)
                    if unit == "Hz" and val >= 1e6:
                        self._meas_labels[meas_name].setText(f"{val / 1e6:.3f} MHz")
                    elif unit == "Hz" and val >= 1e3:
                        self._meas_labels[meas_name].setText(f"{val / 1e3:.2f} kHz")
                    else:
                        self._meas_labels[meas_name].setText(f"{val:.4f} {unit}")

    def stop(self) -> None:
        pass
