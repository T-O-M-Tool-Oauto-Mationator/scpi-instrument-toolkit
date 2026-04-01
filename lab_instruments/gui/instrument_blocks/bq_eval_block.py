"""BQ Evaluation Software — unified EV2300 + BQ76920EVM panel."""

from __future__ import annotations

import contextlib
import csv
import struct
import time
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.dispatcher import _Dispatcher
from ..core.helpers import _mono

# ---------------------------------------------------------------------------
# BQ76920 register map
# ---------------------------------------------------------------------------
REG_SYS_STAT = 0x00
REG_CELLBAL1 = 0x01
REG_CELLBAL2 = 0x02
REG_CELLBAL3 = 0x03
REG_SYS_CTRL1 = 0x04
REG_SYS_CTRL2 = 0x05
REG_PROTECT1 = 0x06
REG_PROTECT2 = 0x07
REG_PROTECT3 = 0x08
REG_OV_TRIP = 0x09
REG_UV_TRIP = 0x0A
REG_CC_CFG = 0x0B

# Cell voltage word registers (hi byte address; lo byte = addr+1)
REG_VC1_HI = 0x0C
REG_VC2_HI = 0x0E
REG_VC3_HI = 0x10
REG_VC4_HI = 0x12
REG_VC5_HI = 0x14
REG_VC6_HI = 0x16
REG_VC7_HI = 0x18
REG_VC8_HI = 0x1A
REG_VC9_HI = 0x1C
REG_VC10_HI = 0x1E
REG_VC11_HI = 0x20
REG_VC12_HI = 0x22
REG_VC13_HI = 0x24
REG_VC14_HI = 0x26
REG_VC15_HI = 0x28

REG_BAT_HI = 0x2A
REG_TS1_HI = 0x2C
REG_TS2_HI = 0x2E
REG_TS3_HI = 0x30
REG_CC_HI = 0x32

REG_ADCGAIN1 = 0x50
REG_ADCOFFSET = 0x51
REG_ADCGAIN2 = 0x59

CELL_REGS = [
    REG_VC1_HI, REG_VC2_HI, REG_VC3_HI, REG_VC4_HI, REG_VC5_HI,
    REG_VC6_HI, REG_VC7_HI, REG_VC8_HI, REG_VC9_HI, REG_VC10_HI,
    REG_VC11_HI, REG_VC12_HI, REG_VC13_HI, REG_VC14_HI, REG_VC15_HI,
]

VTI_PARAMS = (
    [f"Voltage Cell {i}" for i in range(1, 16)]
    + ["Battery Voltage", "Temp Sensor 1", "Temp Sensor 2", "Temp Sensor 3", "Coulomb Counter"]
)
VTI_UNITS = ["Volts"] * 15 + ["Volts", "Volts", "Volts", "Volts", "Volts"]
VTI_REGS = CELL_REGS + [REG_BAT_HI, REG_TS1_HI, REG_TS2_HI, REG_TS3_HI, REG_CC_HI]

# ---------------------------------------------------------------------------
# Register bit definitions for the bit-level editor
# ---------------------------------------------------------------------------


@dataclass
class RegisterDef:
    name: str
    addr: int
    num_bits: int
    bit_names: list[str]  # MSB-first


REGISTER_DEFS: list[RegisterDef] = [
    RegisterDef("System Status", 0x00, 8,
                ["CCRDY", "RSVD", "DEV_XD", "OVRDAL", "UV", "OV", "SCD", "OCD"]),
    RegisterDef("System Control1", 0x04, 8,
                ["LOAD_P", "RSVD", "RSVD", "ADC_EN", "TEMP_S", "RSVD", "SHUT_A", "SHUT_B"]),
    RegisterDef("System Control2", 0x05, 8,
                ["DLY_DIS", "CC_EN", "CC_ONE", "RSVD", "RSVD", "RSVD", "DSG_ON", "CHG_ON"]),
    RegisterDef("Cell Balance 1", 0x01, 5,
                ["CB5", "CB4", "CB3", "CB2", "CB1"]),
    RegisterDef("Cell Balance 2", 0x02, 5,
                ["CB10", "CB9", "CB8", "CB7", "CB6"]),
    RegisterDef("Cell Balance 3", 0x03, 5,
                ["CB15", "CB14", "CB13", "CB12", "CB11"]),
    RegisterDef("Protection 1", 0x06, 8,
                ["RSNS", "RSVD", "RSVD", "SCD_D1", "SCD_D0", "SCD_T2", "SCD_T1", "SCD_T0"]),
    RegisterDef("Protection 2", 0x07, 7,
                ["OCD_D2", "OCD_D1", "OCD_D0", "OCD_T3", "OCD_T2", "OCD_T1", "OCD_T0"]),
    RegisterDef("Protection 3", 0x08, 8,
                ["UV_D2", "UV_D1", "OV_D1", "OV_D0", "RSVD", "RSVD", "RSVD", "RSVD"]),
    RegisterDef("OV_TRIP", 0x09, 8,
                ["OV_T7", "OV_T6", "OV_T5", "OV_T4", "OV_T3", "OV_T2", "OV_T1", "OV_T0"]),
    RegisterDef("UV_TRIP", 0x0A, 8,
                ["UV_T7", "UV_T6", "UV_T5", "UV_T4", "UV_T3", "UV_T2", "UV_T1", "UV_T0"]),
    RegisterDef("CC_CFG", 0x0B, 6,
                ["CC_CFG5", "CC_CFG4", "CC_CFG3", "CC_CFG2", "CC_CFG1", "CC_CFG0"]),
]

_ACCENT = "#6366f1"

_GRP_SS = (
    f"QGroupBox {{ border: 2px solid #aaa; border-radius: 7px; "
    f"margin-top: 12px; padding-top: 14px; }}"
    f"QGroupBox::title {{ color: {_ACCENT}; subcontrol-origin: margin; "
    f"left: 10px; padding: 0 6px; font-weight: bold; }}"
)

_BTN_SS = (
    f"QPushButton {{ border: 1px solid {_ACCENT}66; color: {_ACCENT}; border-radius: 4px; "
    f"padding: 4px 8px; font-weight: bold; font-size: 11px; }} "
    f"QPushButton:hover {{ background: {_ACCENT}; color: white; }}"
)

_BIT_LOW_SS = (
    "QPushButton { background: #28a745; color: white; border: 1px solid #1e7a1e; "
    "border-radius: 3px; padding: 2px 4px; font-size: 10px; font-weight: bold; "
    "min-width: 52px; } QPushButton:hover { background: #218838; }"
)
_BIT_HIGH_SS = (
    "QPushButton { background: #dc3545; color: white; border: 1px solid #c0392b; "
    "border-radius: 3px; padding: 2px 4px; font-size: 10px; font-weight: bold; "
    "min-width: 52px; } QPushButton:hover { background: #c82333; }"
)
_BIT_UNKNOWN_SS = (
    "QPushButton { background: #6c757d; color: white; border: 1px solid #5a6268; "
    "border-radius: 3px; padding: 2px 4px; font-size: 10px; font-weight: bold; "
    "min-width: 52px; }"
)


class _BQEvalBlock(QFrame):
    """Unified EV2300 + BQ76920 evaluation panel."""

    def __init__(self, d: _Dispatcher, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._ev = name
        self.setObjectName("bqblock")
        self.setStyleSheet(
            "#bqblock { border: 1px solid #ccc; border-radius: 10px; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self._register_cache: dict[int, int] = {}
        self._vti_cache: dict[int, int] = {}
        self._scan_timer: QTimer | None = None
        self._logging = False
        self._log_file = None
        self._log_writer = None
        self._bit_buttons: dict[tuple[int, int], QPushButton] = {}
        self._reg_hex_edits: dict[int, QLineEdit] = {}
        self._vti_table: QTableWidget | None = None

        self._build()

    # -- Console access --------------------------------------------------------

    def _con(self):
        from ..widgets.console import _Console

        w = self.parent()
        while w is not None:
            if hasattr(w, "_console"):
                return w._console
            w = w.parent()
        return None

    # -- Device helpers --------------------------------------------------------

    def _get_dev(self):
        return self._d.device(self._ev)

    def _get_i2c_addr(self) -> int:
        text = self._i2c_addr_input.text().strip()
        try:
            return int(text, 16) if text.lower().startswith("0x") else int(text)
        except ValueError:
            return 0x08

    def _read_byte(self, reg: int) -> int | None:
        dev = self._get_dev()
        if not dev:
            return None
        result = dev.read_byte(self._get_i2c_addr(), reg)
        if result.get("ok") and result.get("value") is not None:
            return result["value"]
        return None

    def _write_byte(self, reg: int, val: int) -> bool:
        dev = self._get_dev()
        if not dev:
            return False
        result = dev.write_byte(self._get_i2c_addr(), reg, val)
        return bool(result.get("ok"))

    def _read_word(self, reg: int) -> int | None:
        dev = self._get_dev()
        if not dev:
            return None
        result = dev.read_word(self._get_i2c_addr(), reg)
        if result.get("ok") and result.get("value") is not None:
            return result["value"]
        return None

    # -- Build UI --------------------------------------------------------------

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setStyleSheet("QFrame { border-bottom: 1px solid #ccc; border-radius: 0; }")
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 9, 14, 9)
        hdr_lay.setSpacing(8)
        name_lbl = QLabel(f"<b>BQ Evaluation Software — {self._ev}</b>")
        name_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        hdr_lay.addWidget(name_lbl)
        self._info_lbl = QLabel("")
        self._info_lbl.setStyleSheet("font-size: 10px;")
        hdr_lay.addWidget(self._info_lbl, 1)
        outer.addWidget(hdr)

        # Load device info
        dev = self._get_dev()
        if dev:
            with contextlib.suppress(Exception):
                info = dev.get_device_info()
                if info.get("ok"):
                    self._info_lbl.setText(
                        f"Product: {info.get('product', '?')}  "
                        f"Serial: {info.get('serial', '?')}  "
                        f"VID: {info.get('vid', '?')}  PID: {info.get('pid', '?')}"
                    )

        # Scroll area for body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(10, 10, 10, 6)
        body_lay.setSpacing(8)

        self._build_i2c_address(body_lay)
        self._build_base_config(body_lay)
        self._build_rw_hex_byte(body_lay)
        self._build_read_device(body_lay)
        self._build_logging(body_lay)
        self._build_data_scanning(body_lay)
        self._build_vti(body_lay)
        self._build_register_editor(body_lay)

        body_lay.addStretch(1)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

    # -- Section: I2C Address --------------------------------------------------

    def _build_i2c_address(self, parent: QVBoxLayout) -> None:
        grp = QGroupBox("I2C Target Device Address")
        grp.setStyleSheet(_GRP_SS)
        lay = QHBoxLayout(grp)
        lay.addWidget(QLabel("I2C Device Address (hex):"))
        self._i2c_addr_input = QLineEdit("0x08")
        self._i2c_addr_input.setFont(_mono(11))
        self._i2c_addr_input.setMaximumWidth(80)
        lay.addWidget(self._i2c_addr_input)
        lay.addStretch()
        parent.addWidget(grp)

    # -- Section: Base Configuration -------------------------------------------

    def _build_base_config(self, parent: QVBoxLayout) -> None:
        grp = QGroupBox("Base Configuration")
        grp.setStyleSheet(_GRP_SS)
        lay = QHBoxLayout(grp)

        # Coulomb Counter
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("Coulomb Counter"))
        self._cc_combo = QComboBox()
        self._cc_combo.addItems(["Continuous", "One Shot", "Off"])
        self._cc_combo.setCurrentIndex(2)
        self._cc_combo.currentIndexChanged.connect(self._apply_base_config)
        v1.addWidget(self._cc_combo)
        lay.addLayout(v1)

        # ADC
        v2 = QVBoxLayout()
        v2.addWidget(QLabel("ADC"))
        self._adc_combo = QComboBox()
        self._adc_combo.addItems(["On", "Off"])
        self._adc_combo.setCurrentIndex(1)
        self._adc_combo.currentIndexChanged.connect(self._apply_base_config)
        v2.addWidget(self._adc_combo)
        lay.addLayout(v2)

        # Temperature Sensor
        v3 = QVBoxLayout()
        v3.addWidget(QLabel("Temperature Sensor"))
        self._temp_combo = QComboBox()
        self._temp_combo.addItems(["Internal", "External"])
        self._temp_combo.currentIndexChanged.connect(self._apply_base_config)
        v3.addWidget(self._temp_combo)
        lay.addLayout(v3)

        lay.addStretch()
        parent.addWidget(grp)

    # -- Section: Read/Write One Hex Byte --------------------------------------

    def _build_rw_hex_byte(self, parent: QVBoxLayout) -> None:
        grp = QGroupBox("Read/Write One Hex Byte to a Register")
        grp.setStyleSheet(_GRP_SS)
        lay = QHBoxLayout(grp)

        lay.addWidget(QLabel("Address (hex):"))
        self._rw_addr = QLineEdit("0x00")
        self._rw_addr.setFont(_mono(11))
        self._rw_addr.setMaximumWidth(70)
        lay.addWidget(self._rw_addr)

        lay.addWidget(QLabel("Data (hex):"))
        self._rw_data = QLineEdit("0x00")
        self._rw_data.setFont(_mono(11))
        self._rw_data.setMaximumWidth(70)
        lay.addWidget(self._rw_data)

        read_btn = QPushButton("Read")
        read_btn.setStyleSheet(_BTN_SS)
        read_btn.clicked.connect(self._rw_read_byte)
        lay.addWidget(read_btn)

        write_btn = QPushButton("Write")
        write_btn.setStyleSheet(_BTN_SS)
        write_btn.clicked.connect(self._rw_write_byte)
        lay.addWidget(write_btn)

        self._rw_result = QLabel("")
        self._rw_result.setFont(_mono(11))
        lay.addWidget(self._rw_result)
        lay.addStretch()
        parent.addWidget(grp)

    # -- Section: Read Device --------------------------------------------------

    def _build_read_device(self, parent: QVBoxLayout) -> None:
        grp = QGroupBox("Read Dev")
        grp.setStyleSheet(_GRP_SS)
        lay = QHBoxLayout(grp)
        btn = QPushButton("Read Device")
        btn.setStyleSheet(_BTN_SS)
        btn.clicked.connect(self._read_all_registers)
        lay.addWidget(btn)
        lay.addWidget(QLabel("Detect CRC mode read corrections"))
        lay.addStretch()
        parent.addWidget(grp)

    # -- Section: Logging ------------------------------------------------------

    def _build_logging(self, parent: QVBoxLayout) -> None:
        grp = QGroupBox("Logging")
        grp.setStyleSheet(_GRP_SS)
        lay = QHBoxLayout(grp)
        self._log_btn = QPushButton("Start Logging")
        self._log_btn.setStyleSheet(_BTN_SS)
        self._log_btn.clicked.connect(self._toggle_logging)
        lay.addWidget(self._log_btn)
        lay.addWidget(QLabel("UI is disabled during logging"))
        lay.addStretch()
        parent.addWidget(grp)

    # -- Section: Data Scanning ------------------------------------------------

    def _build_data_scanning(self, parent: QVBoxLayout) -> None:
        grp = QGroupBox("Data Scanning")
        grp.setStyleSheet(_GRP_SS)
        lay = QHBoxLayout(grp)

        lay.addWidget(QLabel("Interval:"))
        self._scan_interval_input = QLineEdit("500")
        self._scan_interval_input.setFont(_mono(11))
        self._scan_interval_input.setMaximumWidth(70)
        lay.addWidget(self._scan_interval_input)
        lay.addWidget(QLabel("msec"))

        change_btn = QPushButton("Change Interval")
        change_btn.setStyleSheet(_BTN_SS)
        change_btn.clicked.connect(self._change_scan_interval)
        lay.addWidget(change_btn)

        self._scan_btn = QPushButton("Scan")
        self._scan_btn.setStyleSheet(_BTN_SS)
        self._scan_btn.clicked.connect(self._start_scan)
        lay.addWidget(self._scan_btn)

        stop_btn = QPushButton("Stop")
        stop_btn.setStyleSheet(_BTN_SS)
        stop_btn.clicked.connect(self._stop_scan)
        lay.addWidget(stop_btn)

        lay.addStretch()
        parent.addWidget(grp)

    # -- Section: Stack V/T/I -------------------------------------------------

    def _build_vti(self, parent: QVBoxLayout) -> None:
        grp = QGroupBox("Stack V/T/I")
        grp.setStyleSheet(_GRP_SS)
        lay = QVBoxLayout(grp)

        # ADC corrections note
        lay.addWidget(QLabel("ADC Corrections read from registers"))

        # ADC Gain / Offset row
        adc_row = QHBoxLayout()
        adc_row.addWidget(QLabel("ADC Gain:"))
        self._adc_gain_input = QLineEdit("365")
        self._adc_gain_input.setFont(_mono(11))
        self._adc_gain_input.setMaximumWidth(80)
        adc_row.addWidget(self._adc_gain_input)
        adc_row.addWidget(QLabel("uV/LSB"))

        adc_row.addWidget(QLabel("ADC Offset:"))
        self._adc_offset_input = QLineEdit("0")
        self._adc_offset_input.setFont(_mono(11))
        self._adc_offset_input.setMaximumWidth(80)
        adc_row.addWidget(self._adc_offset_input)
        adc_row.addWidget(QLabel("mV"))
        adc_row.addStretch()
        lay.addLayout(adc_row)

        # Raw display checkbox
        self._raw_checkbox = QCheckBox("Display raw data read from device below")
        lay.addWidget(self._raw_checkbox)

        # V/T/I table
        self._vti_table = QTableWidget(len(VTI_PARAMS), 3)
        self._vti_table.setHorizontalHeaderLabels(["Parameter", "Value", "Units"])
        self._vti_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._vti_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._vti_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._vti_table.verticalHeader().setVisible(False)
        self._vti_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._vti_table.setAlternatingRowColors(True)
        # Show all 20 rows without scrolling — compute height from row/header sizes
        row_h = self._vti_table.verticalHeader().defaultSectionSize()
        header_h = self._vti_table.horizontalHeader().height()
        self._vti_table.setMinimumHeight(row_h * len(VTI_PARAMS) + header_h + 4)
        for i, (param, unit) in enumerate(zip(VTI_PARAMS, VTI_UNITS)):
            self._vti_table.setItem(i, 0, QTableWidgetItem(param))
            self._vti_table.setItem(i, 1, QTableWidgetItem(""))
            self._vti_table.setItem(i, 2, QTableWidgetItem(unit))
        lay.addWidget(self._vti_table)

        parent.addWidget(grp)

    # -- Section: All Read/Write Registers (bit editor) ------------------------

    def _build_register_editor(self, parent: QVBoxLayout) -> None:
        grp = QGroupBox("All Read/Write Registers")
        grp.setStyleSheet(_GRP_SS)
        lay = QVBoxLayout(grp)

        note = QLabel("Green bits are low. Red bits are high. Click on a bit to change value.")
        note.setStyleSheet("font-size: 10px; color: #666;")
        lay.addWidget(note)

        for rdef in REGISTER_DEFS:
            row = QHBoxLayout()
            row.setSpacing(3)

            # Bit label (e.g. "Bit7:")
            top_bit = rdef.num_bits - 1
            bit_label = QLabel(f"Bit{top_bit}:")
            bit_label.setStyleSheet("font-size: 10px; font-weight: bold; min-width: 30px;")
            row.addWidget(bit_label)

            # Bit buttons
            for bit_idx, bit_name in enumerate(rdef.bit_names):
                bit_pos = top_bit - bit_idx  # MSB-first → actual bit position
                btn = QPushButton(bit_name)
                btn.setStyleSheet(_BIT_UNKNOWN_SS)
                btn.setFixedHeight(26)
                btn.clicked.connect(
                    lambda _, r=rdef.addr, b=bit_pos: self._on_bit_clicked(r, b)
                )
                row.addWidget(btn)
                self._bit_buttons[(rdef.addr, bit_pos)] = btn

            # Separator + register name + hex edit
            row.addWidget(QLabel("|"))
            reg_label = QLabel(f"{rdef.name} (0x{rdef.addr:X})")
            reg_label.setStyleSheet("font-size: 10px; font-weight: bold;")
            row.addWidget(reg_label)

            hex_edit = QLineEdit("")
            hex_edit.setFont(_mono(10))
            hex_edit.setMaximumWidth(40)
            hex_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hex_edit.returnPressed.connect(
                lambda r=rdef.addr, e=hex_edit: self._on_hex_edit(r, e)
            )
            row.addWidget(hex_edit)
            self._reg_hex_edits[rdef.addr] = hex_edit

            row.addStretch()
            lay.addLayout(row)

        parent.addWidget(grp)

    # -- Actions: Base Configuration -------------------------------------------

    def _apply_base_config(self) -> None:
        # Read current register values (or use cache)
        ctrl1 = self._register_cache.get(REG_SYS_CTRL1, 0)
        ctrl2 = self._register_cache.get(REG_SYS_CTRL2, 0)

        # ADC: bit 4 of SYS_CTRL1
        if self._adc_combo.currentIndex() == 0:  # On
            ctrl1 |= 1 << 4
        else:  # Off
            ctrl1 &= ~(1 << 4)

        # Temp Sensor: bit 3 of SYS_CTRL1
        if self._temp_combo.currentIndex() == 1:  # External
            ctrl1 |= 1 << 3
        else:  # Internal
            ctrl1 &= ~(1 << 3)

        # Coulomb Counter: bits 6 (CC_EN) and 5 (CC_ONE) of SYS_CTRL2
        cc_idx = self._cc_combo.currentIndex()
        ctrl2 &= ~(0x03 << 5)  # clear CC_EN and CC_ONE
        if cc_idx == 0:  # Continuous
            ctrl2 |= 1 << 6
        elif cc_idx == 1:  # One Shot
            ctrl2 |= 1 << 5

        self._write_byte(REG_SYS_CTRL1, ctrl1 & 0xFF)
        self._write_byte(REG_SYS_CTRL2, ctrl2 & 0xFF)
        self._register_cache[REG_SYS_CTRL1] = ctrl1 & 0xFF
        self._register_cache[REG_SYS_CTRL2] = ctrl2 & 0xFF
        self._update_register_display(REG_SYS_CTRL1)
        self._update_register_display(REG_SYS_CTRL2)

        con = self._con()
        if con:
            con.log_action(f"{self._ev} base_config",
                           f"CTRL1=0x{ctrl1 & 0xFF:02X} CTRL2=0x{ctrl2 & 0xFF:02X}")

    # -- Actions: Read/Write Hex Byte ------------------------------------------

    def _rw_read_byte(self) -> None:
        try:
            addr = int(self._rw_addr.text().strip(), 0)
        except ValueError:
            self._rw_result.setText("Invalid address")
            return
        val = self._read_byte(addr)
        if val is not None:
            self._rw_data.setText(f"0x{val:02X}")
            self._rw_result.setText(f"Read: 0x{val:02X} ({val})")
            self._rw_result.setStyleSheet("color: #155724; font-size: 10px;")
            # Update cache if it's a known register
            if addr in self._reg_hex_edits:
                self._register_cache[addr] = val
                self._update_register_display(addr)
        else:
            self._rw_result.setText("Read failed")
            self._rw_result.setStyleSheet("color: #c0392b; font-size: 10px;")

    def _rw_write_byte(self) -> None:
        try:
            addr = int(self._rw_addr.text().strip(), 0)
            data = int(self._rw_data.text().strip(), 0)
        except ValueError:
            self._rw_result.setText("Invalid address/data")
            return
        ok = self._write_byte(addr, data)
        if ok:
            self._rw_result.setText(f"Wrote 0x{data:02X} to 0x{addr:02X}")
            self._rw_result.setStyleSheet("color: #155724; font-size: 10px;")
            if addr in self._reg_hex_edits:
                self._register_cache[addr] = data
                self._update_register_display(addr)
        else:
            self._rw_result.setText("Write failed")
            self._rw_result.setStyleSheet("color: #c0392b; font-size: 10px;")

    # -- Actions: Read All Registers -------------------------------------------

    def _read_all_registers(self) -> None:
        # Read ADC gain/offset first
        g1 = self._read_byte(REG_ADCGAIN1)
        g2 = self._read_byte(REG_ADCGAIN2)
        off = self._read_byte(REG_ADCOFFSET)
        if g1 is not None and g2 is not None:
            gain_uV = 365 + (((g1 & 0x0C) << 1) | ((g2 & 0xE0) >> 5))
            self._adc_gain_input.setText(str(gain_uV))
        if off is not None:
            offset_mV = struct.unpack("b", bytes([off]))[0]
            self._adc_offset_input.setText(str(offset_mV))

        # Read all config registers (byte reads)
        for rdef in REGISTER_DEFS:
            val = self._read_byte(rdef.addr)
            if val is not None:
                self._register_cache[rdef.addr] = val
                self._update_register_display(rdef.addr)

        # Sync base config combos from register cache
        self._sync_combos_from_cache()

        # Read voltage/temp/CC registers (word reads)
        for reg in VTI_REGS:
            val = self._read_word(reg)
            if val is not None:
                self._vti_cache[reg] = val

        self._update_vti_table()

        con = self._con()
        if con:
            con.log_action(f"{self._ev} read_device", "All registers read")

    def _sync_combos_from_cache(self) -> None:
        """Update combo boxes to reflect cached register values."""
        ctrl1 = self._register_cache.get(REG_SYS_CTRL1, 0)
        ctrl2 = self._register_cache.get(REG_SYS_CTRL2, 0)

        # Block signals to avoid triggering _apply_base_config
        self._adc_combo.blockSignals(True)
        self._temp_combo.blockSignals(True)
        self._cc_combo.blockSignals(True)

        self._adc_combo.setCurrentIndex(0 if ctrl1 & (1 << 4) else 1)
        self._temp_combo.setCurrentIndex(1 if ctrl1 & (1 << 3) else 0)

        cc_en = bool(ctrl2 & (1 << 6))
        cc_one = bool(ctrl2 & (1 << 5))
        if cc_en:
            self._cc_combo.setCurrentIndex(0)  # Continuous
        elif cc_one:
            self._cc_combo.setCurrentIndex(1)  # One Shot
        else:
            self._cc_combo.setCurrentIndex(2)  # Off

        self._adc_combo.blockSignals(False)
        self._temp_combo.blockSignals(False)
        self._cc_combo.blockSignals(False)

    # -- Actions: Scanning -----------------------------------------------------

    def _change_scan_interval(self) -> None:
        if self._scan_timer and self._scan_timer.isActive():
            self._stop_scan()
            self._start_scan()

    def _start_scan(self) -> None:
        try:
            ms = int(self._scan_interval_input.text().strip())
        except ValueError:
            ms = 500
        ms = max(ms, 100)
        if self._scan_timer:
            self._scan_timer.stop()
        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self._scan_tick)
        self._scan_timer.start(ms)
        self._scan_btn.setText("Scanning...")
        self._scan_btn.setEnabled(False)

    def _stop_scan(self) -> None:
        if self._scan_timer:
            self._scan_timer.stop()
            self._scan_timer = None
        self._scan_btn.setText("Scan")
        self._scan_btn.setEnabled(True)

    def _scan_tick(self) -> None:
        self._read_all_registers()
        if self._logging and self._log_writer:
            row = [time.strftime("%H:%M:%S")]
            for reg in VTI_REGS:
                raw = self._vti_cache.get(reg)
                row.append(str(raw) if raw is not None else "")
            self._log_writer.writerow(row)

    # -- Actions: Logging ------------------------------------------------------

    def _toggle_logging(self) -> None:
        if self._logging:
            self._stop_logging()
        else:
            self._start_logging()

    def _start_logging(self) -> None:
        log_path = Path.home() / f"bq_eval_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        self._log_file = open(log_path, "w", newline="")  # noqa: SIM115
        self._log_writer = csv.writer(self._log_file)
        header = ["Time"] + VTI_PARAMS
        self._log_writer.writerow(header)
        self._logging = True
        self._log_btn.setText("Stop Logging")

        con = self._con()
        if con:
            con.log_action(f"{self._ev} logging", f"Started → {log_path}")

    def _stop_logging(self) -> None:
        self._logging = False
        if self._log_file:
            self._log_file.close()
            self._log_file = None
        self._log_writer = None
        self._log_btn.setText("Start Logging")

        con = self._con()
        if con:
            con.log_action(f"{self._ev} logging", "Stopped")

    # -- V/T/I Table Update ----------------------------------------------------

    def _update_vti_table(self) -> None:
        if not self._vti_table:
            return
        try:
            gain_uV = float(self._adc_gain_input.text().strip())
        except ValueError:
            gain_uV = 365.0
        try:
            offset_mV = float(self._adc_offset_input.text().strip())
        except ValueError:
            offset_mV = 0.0

        show_raw = self._raw_checkbox.isChecked()

        for i, reg in enumerate(VTI_REGS):
            raw = self._vti_cache.get(reg)
            if raw is None:
                self._vti_table.setItem(i, 1, QTableWidgetItem(""))
                continue
            if show_raw:
                self._vti_table.setItem(i, 1, QTableWidgetItem(f"0x{raw:04X} ({raw})"))
            else:
                adc_val = raw & 0x3FFF
                voltage_mV = gain_uV * adc_val / 1000.0 + offset_mV
                voltage_V = voltage_mV / 1000.0
                self._vti_table.setItem(i, 1, QTableWidgetItem(f"{voltage_V:.4f}"))

    # -- Register Bit Display/Toggle -------------------------------------------

    def _update_register_display(self, reg_addr: int) -> None:
        val = self._register_cache.get(reg_addr)
        # Update hex edit
        hex_edit = self._reg_hex_edits.get(reg_addr)
        if hex_edit:
            if val is not None:
                hex_edit.setText(f"{val:02X}")
            else:
                hex_edit.setText("")

        # Find register definition to know bit count
        rdef = None
        for rd in REGISTER_DEFS:
            if rd.addr == reg_addr:
                rdef = rd
                break
        if not rdef:
            return

        top_bit = rdef.num_bits - 1
        for bit_idx, _bit_name in enumerate(rdef.bit_names):
            bit_pos = top_bit - bit_idx
            btn = self._bit_buttons.get((reg_addr, bit_pos))
            if not btn:
                continue
            if val is None:
                btn.setStyleSheet(_BIT_UNKNOWN_SS)
            elif val & (1 << bit_pos):
                btn.setStyleSheet(_BIT_HIGH_SS)
            else:
                btn.setStyleSheet(_BIT_LOW_SS)

    def _on_bit_clicked(self, reg_addr: int, bit_pos: int) -> None:
        val = self._register_cache.get(reg_addr)
        if val is None:
            # Try to read it first
            val = self._read_byte(reg_addr)
            if val is None:
                return
            self._register_cache[reg_addr] = val

        # Toggle bit
        val ^= 1 << bit_pos
        val &= 0xFF
        ok = self._write_byte(reg_addr, val)
        if ok:
            self._register_cache[reg_addr] = val
            self._update_register_display(reg_addr)
            con = self._con()
            if con:
                con.log_action(
                    f"{self._ev} bit_toggle",
                    f"Reg 0x{reg_addr:02X} bit {bit_pos} → 0x{val:02X}",
                )

    def _on_hex_edit(self, reg_addr: int, edit: QLineEdit) -> None:
        try:
            val = int(edit.text().strip(), 16)
        except ValueError:
            return
        ok = self._write_byte(reg_addr, val & 0xFF)
        if ok:
            self._register_cache[reg_addr] = val & 0xFF
            self._update_register_display(reg_addr)

    # -- Cleanup ---------------------------------------------------------------

    def stop(self) -> None:
        self._stop_scan()
        if self._logging:
            self._stop_logging()
