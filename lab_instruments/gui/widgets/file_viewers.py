"""Read-only file viewers: image, CSV, PDF, DOCX, XLSX, PPTX, plain text."""

from __future__ import annotations

import csv
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
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
            self._info.setText(
                f"{self._pixmap.width()}x{self._pixmap.height()}  {os.path.getsize(file_path) // 1024} KB"
            )
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


class PdfViewer(QWidget):
    """Renders PDF pages as images using PyMuPDF."""

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path = file_path
        self._page = 0
        self._page_count = 0

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        tb = QHBoxLayout()
        tb.setContentsMargins(4, 4, 4, 4)
        self._prev_btn = QPushButton("< Prev")
        self._prev_btn.clicked.connect(self._prev)
        tb.addWidget(self._prev_btn)
        self._next_btn = QPushButton("Next >")
        self._next_btn.clicked.connect(self._next)
        tb.addWidget(self._next_btn)
        tb.addStretch()
        self._info = QLabel("")
        self._info.setStyleSheet("font-size: 10px;")
        tb.addWidget(self._info)
        lay.addLayout(tb)

        self._scroll = QScrollArea()
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setWidgetResizable(True)
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setWidget(self._label)
        lay.addWidget(self._scroll, 1)

        try:
            import fitz
            self._doc = fitz.open(file_path)
            self._page_count = len(self._doc)
            self._render()
        except ImportError:
            self._label.setText("Install pymupdf to view PDFs:\npip install pymupdf")
        except Exception as exc:
            self._label.setText(f"Error: {exc}")

    def _render(self) -> None:
        import fitz  # noqa: F811
        page = self._doc[self._page]
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for readability
        pix = page.get_pixmap(matrix=mat)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        self._label.setPixmap(QPixmap.fromImage(img))
        self._info.setText(f"Page {self._page + 1} / {self._page_count}")
        self._prev_btn.setEnabled(self._page > 0)
        self._next_btn.setEnabled(self._page < self._page_count - 1)

    def _prev(self) -> None:
        if self._page > 0:
            self._page -= 1
            self._render()

    def _next(self) -> None:
        if self._page < self._page_count - 1:
            self._page += 1
            self._render()


class DocxViewer(QWidget):
    """Displays .docx content as formatted text."""

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        from PySide6.QtWidgets import QTextEdit
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        lay.addWidget(self._text, 1)

        try:
            from docx import Document
            doc = Document(file_path)
            html_parts = []
            for para in doc.paragraphs:
                style = para.style.name if para.style else ""
                text = para.text
                if "Heading 1" in style:
                    html_parts.append(f"<h1>{text}</h1>")
                elif "Heading 2" in style:
                    html_parts.append(f"<h2>{text}</h2>")
                elif "Heading 3" in style:
                    html_parts.append(f"<h3>{text}</h3>")
                elif text.strip():
                    # Render runs with bold/italic
                    runs_html = ""
                    for run in para.runs:
                        t = run.text
                        if run.bold:
                            t = f"<b>{t}</b>"
                        if run.italic:
                            t = f"<i>{t}</i>"
                        if run.underline:
                            t = f"<u>{t}</u>"
                        runs_html += t
                    html_parts.append(f"<p>{runs_html}</p>")

            # Also extract tables
            for table in doc.tables:
                html_parts.append("<table border='1' cellpadding='4' cellspacing='0'>")
                for row in table.rows:
                    html_parts.append("<tr>")
                    for cell in row.cells:
                        html_parts.append(f"<td>{cell.text}</td>")
                    html_parts.append("</tr>")
                html_parts.append("</table><br>")

            self._text.setHtml("\n".join(html_parts))
        except ImportError:
            self._text.setPlainText("Install python-docx to view .docx files:\npip install python-docx")
        except Exception as exc:
            self._text.setPlainText(f"Error: {exc}")


class XlsxViewer(QWidget):
    """Displays .xlsx spreadsheets in a table with sheet tabs."""

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget()
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        lay.addWidget(self._table, 1)

        # Sheet selector
        tb = QHBoxLayout()
        tb.setContentsMargins(4, 2, 4, 2)
        self._sheet_label = QLabel("")
        self._sheet_label.setStyleSheet("font-size: 10px;")
        tb.addWidget(self._sheet_label)
        tb.addStretch()
        self._info = QLabel("")
        self._info.setStyleSheet("font-size: 10px;")
        tb.addWidget(self._info)
        lay.addLayout(tb)

        try:
            from openpyxl import load_workbook
            self._wb = load_workbook(file_path, read_only=True, data_only=True)
            self._sheets = self._wb.sheetnames
            if self._sheets:
                self._load_sheet(self._sheets[0])
                self._sheet_label.setText(f"Sheets: {', '.join(self._sheets)}")
        except ImportError:
            self._info.setText("Install openpyxl: pip install openpyxl")
        except Exception as exc:
            self._info.setText(f"Error: {exc}")

    def _load_sheet(self, name: str) -> None:
        ws = self._wb[name]
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            self._info.setText("Empty sheet")
            return
        ncols = max(len(r) for r in rows)
        self._table.setColumnCount(ncols)
        self._table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row or []):
                self._table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
        self._table.resizeColumnsToContents()
        self._info.setText(f"{len(rows)} rows x {ncols} columns — {name}")


class PptxViewer(QWidget):
    """Renders .pptx slides as images with prev/next navigation.

    Uses python-pptx to read shapes and paints them onto a QImage canvas
    with proper positioning, text rendering, and embedded image support.
    """

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._slides: list[QPixmap] = []
        self._page = 0

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        tb = QHBoxLayout()
        tb.setContentsMargins(4, 4, 4, 4)
        self._prev_btn = QPushButton("< Prev")
        self._prev_btn.clicked.connect(self._prev)
        tb.addWidget(self._prev_btn)
        self._next_btn = QPushButton("Next >")
        self._next_btn.clicked.connect(self._next)
        tb.addWidget(self._next_btn)
        tb.addStretch()
        self._info = QLabel("")
        self._info.setStyleSheet("font-size: 10px;")
        tb.addWidget(self._info)
        lay.addLayout(tb)

        self._scroll = QScrollArea()
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setWidgetResizable(True)
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setWidget(self._label)
        lay.addWidget(self._scroll, 1)

        try:
            self._render_all(file_path)
            if self._slides:
                self._show_slide()
        except ImportError:
            self._label.setText("Install python-pptx to view .pptx files:\npip install python-pptx")
        except Exception as exc:
            self._label.setText(f"Error: {exc}")

    def _render_all(self, file_path: str) -> None:
        from pptx import Presentation
        from pptx.util import Emu
        from PySide6.QtGui import QColor, QFont, QPainter

        prs = Presentation(file_path)
        sw = prs.slide_width or Emu(9144000)   # default 10"
        sh = prs.slide_height or Emu(6858000)  # default 7.5"

        # Scale: 1 inch = 914400 EMU, render at ~1.5x for readability
        scale = 1.5
        px_w = int(sw / 914400 * 96 * scale)
        px_h = int(sh / 914400 * 96 * scale)

        for slide in prs.slides:
            img = QImage(px_w, px_h, QImage.Format.Format_ARGB32)
            img.fill(QColor(255, 255, 255))
            painter = QPainter(img)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            for shape in slide.shapes:
                x = int(shape.left / 914400 * 96 * scale) if shape.left else 0
                y = int(shape.top / 914400 * 96 * scale) if shape.top else 0
                w = int(shape.width / 914400 * 96 * scale) if shape.width else 0
                h = int(shape.height / 914400 * 96 * scale) if shape.height else 0

                # Draw embedded images
                if shape.shape_type is not None and hasattr(shape, "image"):
                    try:
                        blob = shape.image.blob
                        pix = QPixmap()
                        pix.loadFromData(blob)
                        if not pix.isNull():
                            painter.drawPixmap(x, y, w, h, pix)
                            continue
                    except Exception:
                        pass

                # Draw text
                if shape.has_text_frame:
                    ty = y + 4
                    for para in shape.text_frame.paragraphs:
                        text = para.text.strip()
                        if not text:
                            ty += 16
                            continue
                        # Estimate font size from paragraph runs
                        font_size = 14
                        bold = False
                        for run in para.runs:
                            if run.font.size:
                                font_size = int(run.font.size / 12700 * scale)
                            if run.font.bold:
                                bold = True
                        font = QFont("Arial", max(8, min(font_size, 48)))
                        font.setBold(bold)
                        painter.setFont(font)
                        painter.setPen(QColor(0, 0, 0))
                        from PySide6.QtCore import QRect
                        rect = QRect(x + 4, ty, w - 8, font_size + 8)
                        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, text)
                        ty += font_size + 6

                # Draw tables
                if shape.has_table:
                    table = shape.table
                    nrows = len(table.rows)
                    ncols = len(table.columns)
                    if nrows > 0 and ncols > 0:
                        cw = w // ncols
                        rh = h // nrows
                        painter.setPen(QColor(100, 100, 100))
                        font = QFont("Arial", int(10 * scale))
                        painter.setFont(font)
                        for ri, row in enumerate(table.rows):
                            for ci, cell in enumerate(row.cells):
                                cx = x + ci * cw
                                cy = y + ri * rh
                                painter.drawRect(cx, cy, cw, rh)
                                from PySide6.QtCore import QRect
                                painter.drawText(QRect(cx + 2, cy + 2, cw - 4, rh - 4),
                                                 Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                                                 cell.text)

            painter.end()
            self._slides.append(QPixmap.fromImage(img))

    def _show_slide(self) -> None:
        if not self._slides:
            return
        self._label.setPixmap(self._slides[self._page])
        self._info.setText(f"Slide {self._page + 1} / {len(self._slides)}")
        self._prev_btn.setEnabled(self._page > 0)
        self._next_btn.setEnabled(self._page < len(self._slides) - 1)

    def _prev(self) -> None:
        if self._page > 0:
            self._page -= 1
            self._show_slide()

    def _next(self) -> None:
        if self._page < len(self._slides) - 1:
            self._page += 1
            self._show_slide()
