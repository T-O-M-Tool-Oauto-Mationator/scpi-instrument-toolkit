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

from lab_instruments.enums import SMUSourceMode

from ..core.dispatcher import _Dispatcher
from ..core.helpers import _mono, _NumSpin


class _SMUBlock(QFrame):
    """Self-contained card for one SMU device."""

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._smu = name
        self.setObjectName("smublock")
        self.setStyleSheet("#smublock { border: 1px solid #ccc; border-radius: 10px; }")
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
        _ACCENT = "#c0392b"
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header -- identical to _PSUBlock header
        hdr = QFrame()
        hdr.setStyleSheet("QFrame { border-bottom: 1px solid #ccc; border-radius: 0; }")
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
        self._mode_combo.addItems([SMUSourceMode.VOLTAGE, SMUSourceMode.CURRENT])
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        hdr_lay.addWidget(self._mode_combo)
        outer.addWidget(hdr)

        # Body
        body = QWidget()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(10, 10, 10, 6)
        body_lay.setSpacing(8)

        # Channel group box -- same style as _PSUChannel
        self._grp = QGroupBox("VOLTAGE MODE   \u00b160 V / 3 A")
        self._grp.setStyleSheet(
            f"QGroupBox {{ border: 2px solid #aaa; border-radius: 7px; "
            f"margin-top: 12px; padding-top: 14px; }}"
            f"QGroupBox::title {{ color: {_ACCENT}; subcontrol-origin: margin; "
            f"left: 10px; padding: 0 6px; font-weight: bold; }}"
        )
        grp_lay = QVBoxLayout(self._grp)
        grp_lay.setSpacing(5)
        grp_lay.setContentsMargins(8, 8, 8, 8)

        # Measurement displays -- same as _PSUChannel
        meas = QHBoxLayout()
        meas.setSpacing(5)
        self._v_display = QLabel("0.000")
        self._v_display.setFont(_mono(18))
        self._v_display.setStyleSheet("color: #1e7a1e; border-radius: 5px; padding: 4px 8px")
        self._v_display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._v_display.setMinimumHeight(42)
        meas.addWidget(self._v_display, 1)
        self._i_display = QLabel("0.000")
        self._i_display.setFont(_mono(18))
        self._i_display.setStyleSheet("color: #c45c00; border-radius: 5px; padding: 4px 8px")
        self._i_display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._i_display.setMinimumHeight(42)
        meas.addWidget(self._i_display, 1)
        grp_lay.addLayout(meas)

        # Setpoint row -- same layout as _PSUChannel sp_row
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

        # Toggle -- same style as _PSUChannel
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

        # Info row (compliance + delay + avg + temp) -- styled like PSU limits row
        info_row = QHBoxLayout()
        info_row.setSpacing(4)
        comp_lbl_hdr = QLabel("Status")
        comp_lbl_hdr.setStyleSheet("font-size: 10px;")
        info_row.addWidget(comp_lbl_hdr)
        self._comp_lbl = QLabel("OK")
        self._comp_lbl.setStyleSheet("color: #155724; font-size: 10px; font-weight: bold;")
        info_row.addWidget(self._comp_lbl)
        info_row.addStretch()
        self._delay_lbl = QLabel("delay: \u2014")
        self._delay_lbl.setStyleSheet("font-size: 10px;")
        info_row.addWidget(self._delay_lbl)
        self._avg_lbl = QLabel("avg: \u2014")
        self._avg_lbl.setStyleSheet("font-size: 10px;")
        info_row.addWidget(self._avg_lbl)
        self._temp_lbl = QLabel("temp: \u2014")
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
            self._grp.setTitle("VOLTAGE MODE   \u00b160 V / 3 A")
            self._set_spin.setSuffix(" V")
            self._set_spin.setRange(-60.0, 60.0)
            self._lim_spin.setSuffix(" A")
            self._lim_spin.setRange(0.0, 3.0)
        else:
            self._grp.setTitle("CURRENT MODE   \u00b13 A / 60 V")
            self._set_spin.setSuffix(" A")
            self._set_spin.setRange(-3.0, 3.0)
            self._lim_spin.setSuffix(" V")
            self._lim_spin.setRange(0.0, 60.0)

    def _run(self, cmd: str) -> str:
        result = self._d.run(f"use {self._smu}\n{cmd}")
        con = self._con()
        if con:
            con.log_action(f"{self._smu}: {cmd}", result.strip() if result.strip() else "OK")
        return result

    def _apply(self) -> None:
        mode = self._mode_combo.currentText()
        val = self._set_spin.value()
        lim = self._lim_spin.value()
        if mode == "VOLTAGE":
            self._run("smu mode voltage")
            self._run(f"smu set {val} {lim}")
        else:
            self._run("smu mode current")
            self._run(f"smu set {val} {lim}")
        self._poll()

    def _on_toggle(self, checked: bool) -> None:
        self._run(f"smu {'on' if checked else 'off'}")
        self._poll()

    @Slot()
    def _poll(self) -> None:
        if self._d.is_busy():
            return
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
            self._temp_lbl.setText(f"temp: {dev.read_temperature():.1f}\u00b0C")

    def stop(self) -> None:
        pass
