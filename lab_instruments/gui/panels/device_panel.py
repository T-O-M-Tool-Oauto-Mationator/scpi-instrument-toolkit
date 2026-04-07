from __future__ import annotations

import re
from typing import Any

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core.dispatcher import _Dispatcher
from ..core.helpers import _mono


class _DevicePanel(QWidget):
    _TYPE_COLORS = {
        "psu": "#1a6bbf",
        "awg": "#7c3aed",
        "dmm": "#c45c00",
        "scope": "#0e7a70",
        "smu": "#c0392b",
        "ev": "#6366f1",
    }

    def __init__(self, d: _Dispatcher, main_win: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._main_win = main_win

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(6)

        self._scan_btn = QPushButton("\u27f3  Scan")
        self._scan_btn.clicked.connect(self._on_scan)
        lay.addWidget(self._scan_btn)

        self._list = QListWidget()
        self._list.setFont(_mono(10))
        self._list.setStyleSheet("QListWidget::item { padding: 8px 10px; }")
        self._list.itemClicked.connect(self._on_item_click)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._on_context_menu)
        lay.addWidget(self._list, 1)

    def _on_scan(self) -> None:
        if self._main_win and hasattr(self._main_win, "_on_scan"):
            self._main_win._on_scan()
        # No fallback: blocking scan on main thread would freeze UI

    def _on_item_click(self, item: QListWidgetItem) -> None:
        name = item.data(Qt.ItemDataRole.UserRole)
        if name and self._main_win:
            self._main_win._on_device_selected(name)

    def _on_context_menu(self, pos: QPoint) -> None:
        item = self._list.itemAt(pos)
        if not item:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        if not name:
            return
        menu = QMenu(self)
        disconnect_action = menu.addAction("Disconnect")
        action = menu.exec(self._list.mapToGlobal(pos))
        if action == disconnect_action:
            self._disconnect_device(name)

    def _disconnect_device(self, name: str) -> None:
        # Route through the dispatcher so the lock is respected
        self._d.run(f"unscan {name}")
        if self._main_win:
            self._main_win._after_scan()
            self._main_win._console.log_action(f"disconnect {name}", f"{name} disconnected")

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
            self._TYPE_COLORS.get(base, "")
            item = QListWidgetItem(f"  {name}\n  {disp}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            item.setToolTip(f"{name}  \u2014  {disp}  ({base.upper()})")
            self._list.addItem(item)
