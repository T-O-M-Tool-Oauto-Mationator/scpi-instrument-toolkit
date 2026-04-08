from __future__ import annotations

import pathlib
import webbrowser

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

try:
    from PySide6.QtWebEngineCore import QWebEnginePage as _QWebEnginePage
    from PySide6.QtWebEngineWidgets import QWebEngineView as _QWebEngineView

    class _SilentPage(_QWebEnginePage):
        """Suppress noisy JS console messages (e.g. missing search_index.js)."""
        def javaScriptConsoleMessage(self, level, message, line, source):
            pass  # drop all JS console output from the docs viewer

    _HAS_WEBENGINE = True
except ImportError:
    _HAS_WEBENGINE = False


class DocsViewer(QWidget):
    def __init__(self, site_dir: str, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        index = pathlib.Path(site_dir) / "index.html"

        if _HAS_WEBENGINE:
            self._view = _QWebEngineView()
            self._view.setPage(_SilentPage(self._view))
            lay.addWidget(self._view, 1)
            self._view.load(QUrl.fromLocalFile(str(index)))

            # ── Find bar ──────────────────────────────────────────────
            self._find_bar = QWidget()
            self._find_bar.setStyleSheet(
                "background:#313244; border-top:1px solid #45475a;"
            )
            fb_lay = QHBoxLayout(self._find_bar)
            fb_lay.setContentsMargins(8, 4, 8, 4)
            fb_lay.setSpacing(6)

            self._find_input = QLineEdit()
            self._find_input.setPlaceholderText("Find in page…")
            self._find_input.setStyleSheet(
                "QLineEdit { background:#1e1e2e; color:#cdd6f4; "
                "border:1px solid #45475a; border-radius:3px; padding:3px 6px; }"
                "QLineEdit:focus { border-color:#89b4fa; }"
            )
            self._find_input.setFixedWidth(260)
            fb_lay.addWidget(self._find_input)

            self._find_label = QLabel("")
            self._find_label.setStyleSheet("color:#a6adc8; font-size:11px;")
            fb_lay.addWidget(self._find_label)

            btn_style = (
                "QPushButton { background:#45475a; color:#cdd6f4; border:none; "
                "border-radius:3px; padding:3px 10px; font-size:11px; }"
                "QPushButton:hover { background:#585b70; }"
            )
            prev_btn = QPushButton("▲")
            prev_btn.setFixedWidth(28)
            prev_btn.setStyleSheet(btn_style)
            prev_btn.setToolTip("Previous match")
            prev_btn.clicked.connect(self._find_prev)
            fb_lay.addWidget(prev_btn)

            next_btn = QPushButton("▼")
            next_btn.setFixedWidth(28)
            next_btn.setStyleSheet(btn_style)
            next_btn.setToolTip("Next match")
            next_btn.clicked.connect(self._find_next)
            fb_lay.addWidget(next_btn)

            close_btn = QPushButton("✕")
            close_btn.setFixedWidth(28)
            close_btn.setStyleSheet(btn_style)
            close_btn.setToolTip("Close (Esc)")
            close_btn.clicked.connect(self._close_find)
            fb_lay.addWidget(close_btn)

            fb_lay.addStretch()
            self._find_bar.hide()
            lay.addWidget(self._find_bar)

            # Wire up text changes → live search
            self._find_input.textChanged.connect(self._find_next)
            self._find_input.returnPressed.connect(self._find_next)

            # Ctrl+F opens the bar
            QShortcut(QKeySequence("Ctrl+F"), self, self._open_find)
            # Escape closes it
            QShortcut(QKeySequence("Escape"), self._find_bar, self._close_find)

        else:
            lbl = QLabel(
                f'QtWebEngineWidgets not available.<br>'
                f'<a href="file://{index}">Open docs in browser</a>'
            )
            lbl.setOpenExternalLinks(False)
            lbl.linkActivated.connect(lambda _: webbrowser.open(index.as_uri()))
            lay.addWidget(lbl)

    # ── Find helpers ──────────────────────────────────────────────────────

    def _open_find(self) -> None:
        self._find_bar.show()
        self._find_input.setFocus()
        self._find_input.selectAll()

    def _close_find(self) -> None:
        self._find_bar.hide()
        self._view.findText("")  # clear highlight
        self._find_label.setText("")
        self._view.setFocus()

    def _on_find_result(self, result) -> None:
        if not self._find_input.text():
            self._find_label.setText("")
            return
        try:
            total = result.numberOfMatches()
            active = result.activeMatch()
            if total == 0:
                self._find_label.setText("No results")
                self._find_label.setStyleSheet("color:#f38ba8; font-size:11px;")
            else:
                self._find_label.setText(f"{active}/{total}")
                self._find_label.setStyleSheet("color:#a6adc8; font-size:11px;")
        except AttributeError:
            # Older Qt: result is a bool (found/not-found)
            if result:
                self._find_label.setText("Found")
                self._find_label.setStyleSheet("color:#a6adc8; font-size:11px;")
            else:
                self._find_label.setText("No results")
                self._find_label.setStyleSheet("color:#f38ba8; font-size:11px;")

    def _find_next(self) -> None:
        text = self._find_input.text()
        try:
            self._view.findText(text, 0, self._on_find_result)
        except TypeError:
            self._view.findText(text)

    def _find_prev(self) -> None:
        from PySide6.QtWebEngineCore import QWebEnginePage
        text = self._find_input.text()
        try:
            self._view.findText(text, QWebEnginePage.FindFlag.FindBackward, self._on_find_result)
        except TypeError:
            self._view.findText(text, QWebEnginePage.FindFlag.FindBackward)
