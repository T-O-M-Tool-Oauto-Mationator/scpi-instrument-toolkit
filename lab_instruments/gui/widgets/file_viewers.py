"""Read-only file viewers: image, CSV, plain text."""

from __future__ import annotations

import csv
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.helpers import _mono


class ImageViewer(QWidget):
    """Displays an image file (PNG, JPG, etc.) with basic zoom."""

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path = file_path
        self._scale = 1.0

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        tb = QHBoxLayout()
        tb.setContentsMargins(4, 4, 4, 4)
        for text, delta in [("Zoom In (+)", 0.25), ("Zoom Out (-)", -0.25), ("Fit", 0)]:
            b = QPushButton(text)
            b.clicked.connect(lambda _, d=delta: self._zoom(d))
            tb.addWidget(b)
        tb.addStretch()
        self._info = QLabel("")
        self._info.setStyleSheet("font-size: 10px;")
        tb.addWidget(self._info)
        lay.addLayout(tb)

        # Scroll area with image
        self._scroll = QScrollArea()
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setWidget(self._label)
        self._scroll.setWidgetResizable(False)
        lay.addWidget(self._scroll, 1)

        self._pixmap = QPixmap(file_path)
        if not self._pixmap.isNull():
            self._info.setText(f"{self._pixmap.width()}x{self._pixmap.height()}  {os.path.getsize(file_path) // 1024} KB")
            self._label.setPixmap(self._pixmap)
            self._label.resize(self._pixmap.size())

    def _zoom(self, delta: float) -> None:
        if delta == 0:
            # Fit to viewport
            vp = self._scroll.viewport().size()
            pw, ph = self._pixmap.width(), self._pixmap.height()
            if pw > 0 and ph > 0:
                self._scale = min(vp.width() / pw, vp.height() / ph)
        else:
            self._scale = max(0.1, min(5.0, self._scale + delta))
        scaled = self._pixmap.scaled(
            int(self._pixmap.width() * self._scale),
            int(self._pixmap.height() * self._scale),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)
        self._label.resize(scaled.size())


class CsvViewer(QWidget):
    """Displays a CSV file in a read-only table."""

    MAX_ROWS = 10000

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path = file_path

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget()
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        lay.addWidget(self._table, 1)

        self._info = QLabel("")
        self._info.setStyleSheet("font-size: 10px; padding: 2px 6px;")
        lay.addWidget(self._info)

        self._load()

    def _load(self) -> None:
        try:
            with open(self._path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = []
                for i, row in enumerate(reader):
                    rows.append(row)
                    if i >= self.MAX_ROWS:
                        break
            if not rows:
                self._info.setText("Empty CSV")
                return
            # Use first row as header
            headers = rows[0]
            data = rows[1:]
            self._table.setColumnCount(len(headers))
            self._table.setHorizontalHeaderLabels(headers)
            self._table.setRowCount(len(data))
            for r, row in enumerate(data):
                for c, val in enumerate(row):
                    self._table.setItem(r, c, QTableWidgetItem(val))
            self._table.resizeColumnsToContents()
            self._info.setText(f"{len(data)} rows x {len(headers)} columns")
        except Exception as exc:
            self._info.setText(f"Error: {exc}")


class TextViewer(QWidget):
    """Read-only plain text viewer with monospace font."""

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path = file_path

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        self._editor.setFont(_mono())
        self._editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        lay.addWidget(self._editor, 1)

        try:
            with open(file_path, encoding="utf-8", errors="replace") as f:
                self._editor.setPlainText(f.read())
        except Exception as exc:
            self._editor.setPlainText(f"Error reading file: {exc}")
