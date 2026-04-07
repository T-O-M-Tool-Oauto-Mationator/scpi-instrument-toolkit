from __future__ import annotations

import contextlib
from typing import Any

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

from lab_instruments.enums import WaveformType

from ..core.dispatcher import _Dispatcher
from ..core.helpers import _mono, _NumSpin

_AWG_WAVEFORMS = [
    w.value
    for w in (
        WaveformType.SIN,
        WaveformType.SQU,
        WaveformType.RAMP,
        WaveformType.PULS,
        WaveformType.NOIS,
        WaveformType.DC,
    )
]
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
    def __init__(
        self, channel: int, accent: str, waveforms: list[str] | None = None, parent: QWidget | None = None
    ) -> None:
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

        meas = QHBoxLayout()
        meas.setSpacing(5)
        self.freq_display = QLabel("10000.000 Hz")
        self.freq_display.setFont(_mono(18))
        self.freq_display.setStyleSheet("color: #1e7a1e; border-radius: 5px; padding: 4px 8px")
        self.freq_display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.freq_display.setMinimumHeight(42)
        meas.addWidget(self.freq_display, 2)
        self.amp_display = QLabel("5.0000 Vpp")
        self.amp_display.setFont(_mono(18))
        self.amp_display.setStyleSheet("color: #c45c00; border-radius: 5px; padding: 4px 8px")
        self.amp_display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.amp_display.setMinimumHeight(42)
        meas.addWidget(self.amp_display, 1)
        layout.addLayout(meas)

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

        self.toggle_btn = QPushButton(f"\u25cb  CH{self.channel} OFF")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setMinimumHeight(32)
        self._set_toggle_style(False)
        layout.addWidget(self.toggle_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

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
        self.offset_spin.setStyleSheet("QDoubleSpinBox { font-size: 11px; }")
        off_row.addWidget(self.offset_spin)
        off_row.addStretch()
        layout.addLayout(off_row)

        extras_row = QHBoxLayout()
        extras_row.setSpacing(4)
        duty_lbl = QLabel("Duty")
        duty_lbl.setStyleSheet("font-size: 10px;")
        extras_row.addWidget(duty_lbl)
        self.duty_spin = _NumSpin()
        self.duty_spin.setRange(0.0, 100.0)
        self.duty_spin.setDecimals(1)
        self.duty_spin.setSuffix(" %")
        self.duty_spin.setMinimumWidth(75)
        self.duty_spin.setStyleSheet("QDoubleSpinBox { font-size: 11px; }")
        extras_row.addWidget(self.duty_spin)
        phase_lbl = QLabel("Phase")
        phase_lbl.setStyleSheet("font-size: 10px;")
        extras_row.addWidget(phase_lbl)
        self.phase_spin = _NumSpin()
        self.phase_spin.setRange(-360.0, 360.0)
        self.phase_spin.setDecimals(1)
        self.phase_spin.setSuffix(" °")
        self.phase_spin.setMinimumWidth(75)
        self.phase_spin.setStyleSheet("QDoubleSpinBox { font-size: 11px; }")
        extras_row.addWidget(self.phase_spin)
        extras_row.addStretch()
        layout.addLayout(extras_row)

    def _set_toggle_style(self, on: bool) -> None:
        if on:
            self.toggle_btn.setText(f"\u25cf  CH{self.channel} ON")
            self.toggle_btn.setStyleSheet(
                "QPushButton { background: #d4edda; color: #155724; font-weight: bold; "
                "border-radius: 4px; border: 2px solid #28a745; padding: 6px; font-size: 11px; }"
                "QPushButton:hover { background: #28a745; color: white; }"
            )
        else:
            self.toggle_btn.setText(f"\u25cb  CH{self.channel} OFF")
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
        with contextlib.suppress(Exception):
            if hasattr(dev, "get_duty_cycle"):
                self.duty_spin.blockSignals(True)
                self.duty_spin.setValue(dev.get_duty_cycle(self.channel))
                self.duty_spin.blockSignals(False)
        with contextlib.suppress(Exception):
            if hasattr(dev, "get_phase"):
                self.phase_spin.blockSignals(True)
                self.phase_spin.setValue(dev.get_phase(self.channel))
                self.phase_spin.blockSignals(False)
        self.toggle_btn.blockSignals(True)
        self.toggle_btn.setChecked(on)
        self.toggle_btn.blockSignals(False)
        self._set_toggle_style(on)


class _AWGBlock(QFrame):
    """Self-contained card for one AWG device.

    All writes route through self._run() -> REPL command handler.
    Reads (polling) call device methods directly.
    """

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._awg = name
        self._chs: dict[int, _AWGChannel] = {}
        self.setObjectName("awgblock")
        self.setStyleSheet("#awgblock { border: 1px solid #ccc; border-radius: 10px; }")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._build()

    def _con(self):
        w = self.parent()
        while w is not None:
            if hasattr(w, "_console"):
                return w._console
            w = w.parent()
        return None

    def _run(self, cmd: str) -> str:
        result = self._d.run(f"use {self._awg}\n{cmd}")
        con = self._con()
        if con:
            con.log_action(f"{self._awg}: {cmd}", result.strip() if result.strip() else "OK")
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

    # -- Writes: route through REPL --------------------------------------------

    def _apply(self, ch: int) -> None:
        w = self._chs.get(ch)
        if not w:
            return
        wave = w.wave_combo.currentText().lower()
        freq = w.freq_spin.value()
        amp = w.amp_spin.value()
        offset = w.offset_spin.value()
        self._run(f"awg chan {ch} set_function {wave}")
        self._run(f"awg chan {ch} set_frequency {freq}")
        self._run(f"awg chan {ch} set_amplitude {amp}")
        self._run(f"awg chan {ch} set_offset {offset}")
        self._run(f"awg chan {ch} duty {w.duty_spin.value()}")
        self._run(f"awg chan {ch} phase {w.phase_spin.value()}")
        self._status.setText(f"CH{ch}: {wave.upper()} {freq:.1f}Hz {amp:.4f}Vpp")
        self._status.setStyleSheet("color: #155724; font-size: 10px;")
        self._poll()

    def _output(self, ch: int, on: bool) -> None:
        self._run(f"awg chan {ch} {'on' if on else 'off'}")
        self._poll()

    def _all_on(self) -> None:
        for ch in self._chs:
            self._run(f"awg chan {ch} on")
        self._poll()

    def _all_off(self) -> None:
        for ch in self._chs:
            self._run(f"awg chan {ch} off")
        self._poll()

    # -- Reads (polling) -------------------------------------------------------

    @Slot()
    def _poll(self) -> None:
        if self._d.is_busy():
            return
        dev = self._d.device(self._awg)
        if not dev:
            return
        for ch_num, w in self._chs.items():
            with contextlib.suppress(Exception):
                on = dev.get_output_state(ch_num)
                w.sync_from_device(dev, on)

    def stop(self) -> None:
        pass
