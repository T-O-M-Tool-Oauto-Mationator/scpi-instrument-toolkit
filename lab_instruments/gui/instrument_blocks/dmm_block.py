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

from ..core.helpers import _mono
from ..core.dispatcher import _Dispatcher

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

    def _con(self):
        from ..widgets.console import _Console

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

        # Header -- same as PSU
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

        # Group box -- shows current mode
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
