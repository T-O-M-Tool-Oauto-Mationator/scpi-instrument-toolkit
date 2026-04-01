from __future__ import annotations

import re

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDoubleSpinBox

# -- ANSI helpers ------------------------------------------------------------

_ANSI_RE = re.compile(r"\033\[([0-9;]*)m")
_ANSI_COLORS = {"91": "#f38ba8", "92": "#1e7a1e", "93": "#b8860b", "94": "#1a6bbf", "96": "#0e7a70"}


def _ansi_to_html(text: str) -> str:
    if "\033" not in text:
        return _esc(text).replace("\n", "<br>")
    parts: list[str] = []
    opens = 0
    end = 0
    for m in _ANSI_RE.finditer(text):
        parts.append(_esc(text[end : m.start()]))
        end = m.end()
        for c in (m.group(1) or "0").split(";"):
            c = c.lstrip("0") or "0"
            if c == "0":
                parts.append("</span>" * opens)
                opens = 0
            elif c == "1":
                parts.append("<span style='font-weight:bold'>")
                opens += 1
            elif c in _ANSI_COLORS:
                parts.append(f"<span style='color:{_ANSI_COLORS[c]}'>")
                opens += 1
    parts.append(_esc(text[end:]))
    parts.append("</span>" * opens)
    return "".join(parts).replace("\n", "<br>")


def _esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _mono(size: int = 11) -> QFont:
    f = QFont("Monospace", size)
    f.setStyleHint(QFont.StyleHint.Monospace)
    f.setFamilies(["JetBrains Mono", "Cascadia Code", "Consolas", "Courier New", "monospace"])
    return f


# -- Spinbox: cursor stays on the number, not the suffix ---------------------


class _NumSpin(QDoubleSpinBox):
    def _select_number(self) -> None:
        le = self.lineEdit()
        end = len(le.text()) - len(self.suffix())
        le.setSelection(0, max(end, 0))

    def focusInEvent(self, event):  # noqa: N802
        super().focusInEvent(event)
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, self._select_number)

    def mousePressEvent(self, event):  # noqa: N802
        super().mousePressEvent(event)
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, self._select_number)


# -- Channel accent colors ---------------------------------------------------

_CH_ACCENTS = [
    "#b8860b",  # ch1 – yellow  (e.g. P6V)
    "#1a6bbf",  # ch2 – blue    (e.g. P25V / P30V)
    "#7c3aed",  # ch3 – mauve   (e.g. N25V / N30V)
    "#1e7a1e",  # ch4 – green
    "#0e7a70",  # ch5 – teal
    "#c45c00",  # ch6 – peach
]
