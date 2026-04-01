from __future__ import annotations

import contextlib

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

from ..core.helpers import _mono
from ..core.dispatcher import _Dispatcher

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

    def _con(self):
        from ..widgets.console import _Console

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
