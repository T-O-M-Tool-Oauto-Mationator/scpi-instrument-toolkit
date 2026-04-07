from __future__ import annotations

import pathlib
import webbrowser

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView as _QWebEngineView

    _HAS_WEBENGINE = True
except ImportError:
    _HAS_WEBENGINE = False


class DocsViewer(QWidget):
    def __init__(self, site_dir: str, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        index = pathlib.Path(site_dir) / "index.html"
        if _HAS_WEBENGINE:
            self._view = _QWebEngineView()
            lay.addWidget(self._view)
            self._view.load(QUrl.fromLocalFile(str(index)))
        else:
            lbl = QLabel(
                f"QtWebEngineWidgets not available.<br>"
                f'<a href="file://{index}">Open docs in browser</a>'
            )
            lbl.setOpenExternalLinks(False)
            lbl.linkActivated.connect(lambda _: webbrowser.open(index.as_uri()))
            lay.addWidget(lbl)
