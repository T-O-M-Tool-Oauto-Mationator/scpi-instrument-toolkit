"""Read-only file viewers: image, CSV, PDF, DOCX, XLSX, PPTX, plain text."""

from __future__ import annotations

import contextlib
import csv
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


@contextlib.contextmanager
def _silence_mupdf():
    """Suppress MuPDF C-level stderr spam (e.g. structure tree warnings)."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    saved = os.dup(2)
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(saved, 2)
        os.close(saved)

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
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

            with _silence_mupdf():
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


# ---------------------------------------------------------------------------
# Shared helpers for Office document viewers (DOCX, XLSX, PPTX)
# ---------------------------------------------------------------------------


def _find_soffice() -> str | None:
    """Return the path to a working LibreOffice ``soffice`` binary, or None."""
    for name in ("soffice", "libreoffice"):
        p = shutil.which(name)
        if p:
            return p
    for fixed in (
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/soffice",
        "/usr/local/bin/soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ):
        if os.path.isfile(fixed):
            return fixed
    return None


def _office_cache_dir(file_path: str) -> Path:
    """Return a per-file cache directory for converted pages.

    The cache is keyed on path + mtime so edits to the source file
    automatically invalidate stale PNGs.
    """
    mtime = int(os.path.getmtime(file_path))
    key = f"{file_path}\0{mtime}"
    digest = hashlib.md5(key.encode()).hexdigest()[:16]  # noqa: S324
    d = Path(tempfile.gettempdir()) / "office_viewer_cache" / digest
    d.mkdir(parents=True, exist_ok=True)
    return d


def _soffice_user_profile() -> str:
    """Return a unique LibreOffice user-profile URI to avoid lock conflicts.

    soffice hangs when another instance is already running and they share
    the default profile.  Using a disposable profile per-process avoids this.
    """
    d = Path(tempfile.gettempdir()) / "office_viewer_profile" / str(os.getpid())
    d.mkdir(parents=True, exist_ok=True)
    return d.as_uri()


def _soffice_cmd(soffice_bin: str, cache_dir: Path, file_path: str) -> list[str]:
    """Build the soffice conversion command with a unique user profile."""
    return [
        soffice_bin,
        "--headless",
        "--nolockcheck",
        f"-env:UserInstallation={_soffice_user_profile()}",
        "--convert-to",
        "pdf",
        "--outdir",
        str(cache_dir),
        file_path,
    ]


class _OfficeConversionWorker(QThread):
    """Background thread: soffice -> PDF -> PyMuPDF -> QImage list."""

    pages_ready = Signal(list)
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, file_path: str, soffice_bin: str, cache_dir: Path) -> None:
        super().__init__()
        self._file_path = file_path
        self._soffice = soffice_bin
        self._cache_dir = cache_dir

    def run(self) -> None:  # noqa: C901
        try:
            # 1. Cache hit?
            cached = sorted(self._cache_dir.glob("page_*.png"))
            if cached:
                images = []
                for p in cached:
                    img = QImage(str(p))
                    if not img.isNull():
                        images.append(img)
                if images:
                    self.pages_ready.emit(images)
                    return

            # 2. Convert to PDF via LibreOffice
            self.progress.emit("Converting with LibreOffice...")
            result = subprocess.run(
                _soffice_cmd(self._soffice, self._cache_dir, self._file_path),
                capture_output=True,
                timeout=180,
            )
            if result.returncode != 0:
                stderr = result.stderr.decode(errors="replace")[:400]
                self.error.emit(f"LibreOffice failed (exit {result.returncode}):\n{stderr}")
                return

            # 3. Find the PDF
            pdfs = list(self._cache_dir.glob("*.pdf"))
            if not pdfs:
                self.error.emit("LibreOffice did not produce a PDF file.")
                return
            pdf_path = pdfs[0]

            # 4. Render with PyMuPDF
            try:
                import fitz
            except ImportError:
                self.error.emit("pymupdf is not installed. Run: pip install pymupdf")
                return

            with _silence_mupdf():
                doc = fitz.open(str(pdf_path))
            images: list[QImage] = []
            for i, page in enumerate(doc):
                self.progress.emit(f"Rendering page {i + 1} of {len(doc)}...")
                mat = fitz.Matrix(2.0, 2.0)  # 144 DPI
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = QImage(
                    pix.samples,
                    pix.width,
                    pix.height,
                    pix.stride,
                    QImage.Format.Format_RGB888,
                ).copy()
                img.save(str(self._cache_dir / f"page_{i:04d}.png"))
                images.append(img)
            doc.close()

            self.pages_ready.emit(images)
        except Exception as exc:
            self.error.emit(str(exc))


class _OfficeViewerBase(QWidget):
    """Base viewer for Office documents rendered via LibreOffice + PyMuPDF."""

    def __init__(self, file_path: str, page_label: str = "Page", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path = file_path
        self._page_label = page_label
        self._pages: list[QImage] = []
        self._current = 0
        self._worker: _OfficeConversionWorker | None = None

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        # -- toolbar --
        tb = QHBoxLayout()
        tb.setContentsMargins(4, 4, 4, 4)

        self._prev_btn = QPushButton("\u2039")
        self._prev_btn.setFixedWidth(32)
        self._prev_btn.setEnabled(False)
        self._prev_btn.clicked.connect(self._prev)
        tb.addWidget(self._prev_btn)

        self._page_info = QLabel("")
        self._page_info.setMinimumWidth(120)
        self._page_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tb.addWidget(self._page_info)

        self._next_btn = QPushButton("\u203a")
        self._next_btn.setFixedWidth(32)
        self._next_btn.setEnabled(False)
        self._next_btn.clicked.connect(self._next)
        tb.addWidget(self._next_btn)

        tb.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        tb.addWidget(QLabel("Zoom:"))
        self._zoom_combo = QComboBox()
        self._zoom_combo.addItems(["Fit Width", "50%", "75%", "100%", "150%", "200%"])
        self._zoom_combo.setCurrentIndex(0)
        self._zoom_combo.currentTextChanged.connect(lambda _: self._apply_zoom())
        tb.addWidget(self._zoom_combo)

        lay.addLayout(tb)

        # -- scroll area --
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setWidget(self._label)
        lay.addWidget(self._scroll, 1)

        # -- kick off --
        soffice = _find_soffice()
        if soffice is None:
            self._label.setText(
                "LibreOffice is required to render Office documents.\n\n"
                "Install it from https://www.libreoffice.org -- it's free.\n"
                "Restart the app after installing."
            )
            self._label.setWordWrap(True)
            return

        self._label.setText("Converting... this may take a moment on first open.")
        cache = _office_cache_dir(file_path)
        self._worker = _OfficeConversionWorker(file_path, soffice, cache)
        self._worker.pages_ready.connect(self._on_pages_ready)
        self._worker.error.connect(self._on_error)
        self._worker.progress.connect(self._on_progress)
        self._worker.start()

    # -- slots --

    def _on_pages_ready(self, images: list[QImage]) -> None:
        self._pages = images
        self._current = 0
        self._go_to(0)

    def _on_error(self, msg: str) -> None:
        self._label.setText(msg)
        self._label.setWordWrap(True)
        self._label.setStyleSheet("color: #c0392b;")

    def _on_progress(self, msg: str) -> None:
        self._label.setText(msg)

    # -- navigation --

    def _go_to(self, index: int) -> None:
        if not self._pages:
            return
        self._current = max(0, min(index, len(self._pages) - 1))
        self._apply_zoom()
        total = len(self._pages)
        self._page_info.setText(f"{self._page_label} {self._current + 1} of {total}")
        self._prev_btn.setEnabled(self._current > 0)
        self._next_btn.setEnabled(self._current < total - 1)

    def _apply_zoom(self) -> None:
        if not self._pages:
            return
        src = self._pages[self._current]
        pix = QPixmap.fromImage(src)
        choice = self._zoom_combo.currentText()
        if choice == "Fit Width":
            vp_w = self._scroll.viewport().width() - 4
            if vp_w > 0 and pix.width() > 0:
                pix = pix.scaledToWidth(vp_w, Qt.TransformationMode.SmoothTransformation)
        else:
            pct = int(choice.replace("%", ""))
            target_w = int(src.width() * pct / 100)
            if target_w > 0:
                pix = pix.scaledToWidth(target_w, Qt.TransformationMode.SmoothTransformation)
        self._label.setPixmap(pix)

    def _prev(self) -> None:
        if self._current > 0:
            self._go_to(self._current - 1)

    def _next(self) -> None:
        if self._pages and self._current < len(self._pages) - 1:
            self._go_to(self._current + 1)

    # -- events --

    def resizeEvent(self, event) -> None:
        if self._zoom_combo.currentText() == "Fit Width":
            self._apply_zoom()
        super().resizeEvent(event)

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Up):
            self._prev()
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_Down):
            self._next()
        elif key == Qt.Key.Key_Home:
            self._go_to(0)
        elif key == Qt.Key.Key_End:
            self._go_to(len(self._pages) - 1)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait(3000)
        super().closeEvent(event)


# ---------------------------------------------------------------------------
# Public viewer classes (thin wrappers preserving original constructor API)
# ---------------------------------------------------------------------------


class DocxViewer(_OfficeViewerBase):
    """Displays .docx documents via LibreOffice PDF conversion."""

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(file_path, page_label="Page", parent=parent)


class XlsxViewer(QWidget):
    """Displays .xlsx spreadsheets in a read-only table with sheet tabs."""

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget()
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        lay.addWidget(self._table, 1)

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
        self._info.setText(f"{len(rows)} rows x {ncols} columns - {name}")


class PptxViewer(_OfficeViewerBase):
    """Renders .pptx slides via LibreOffice PDF conversion."""

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(file_path, page_label="Slide", parent=parent)


# ---------------------------------------------------------------------------
# Background pre-conversion of all Office files in a workspace
# ---------------------------------------------------------------------------

_OFFICE_EXTS = {".docx", ".doc", ".pptx"}


class _PreconvertWorker(QThread):
    """Walks a folder tree, converts every Office file to cached PNGs."""

    finished_all = Signal()

    def __init__(self, folder: str, soffice_bin: str) -> None:
        super().__init__()
        self._folder = folder
        self._soffice = soffice_bin

    def run(self) -> None:
        try:
            import fitz  # noqa: F401
        except ImportError:
            return

        for root, _, files in os.walk(self._folder):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in _OFFICE_EXTS:
                    continue
                fpath = os.path.join(root, fname)
                cache = _office_cache_dir(fpath)
                # Skip if already cached
                if list(cache.glob("page_*.png")):
                    continue
                self._convert_one(fpath, cache, fitz)
        self.finished_all.emit()

    def _convert_one(self, file_path: str, cache_dir: Path, fitz) -> None:  # type: ignore[type-arg]
        try:
            result = subprocess.run(
                _soffice_cmd(self._soffice, cache_dir, file_path),
                capture_output=True,
                timeout=120,
            )
            if result.returncode != 0:
                return
            pdfs = list(cache_dir.glob("*.pdf"))
            if not pdfs:
                return
            with _silence_mupdf():
                doc = fitz.open(str(pdfs[0]))
            for i, page in enumerate(doc):
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = QImage(
                    pix.samples,
                    pix.width,
                    pix.height,
                    pix.stride,
                    QImage.Format.Format_RGB888,
                ).copy()
                img.save(str(cache_dir / f"page_{i:04d}.png"))
            doc.close()
        except Exception:
            pass


def preconvert_office_files(folder: str) -> _PreconvertWorker | None:
    """Start background pre-conversion of all Office files under *folder*.

    Returns the worker thread (caller must keep a reference to prevent GC),
    or ``None`` if LibreOffice is not installed.
    """
    soffice = _find_soffice()
    if soffice is None:
        return None
    worker = _PreconvertWorker(folder, soffice)
    worker.start()
    return worker
