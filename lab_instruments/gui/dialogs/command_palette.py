"""Command palette (Ctrl+Shift+P) — fuzzy-search action launcher."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)


@dataclass
class ActionItem:
    id: str
    label: str
    shortcut: str
    callback: Callable
    category: str = ""


def _fuzzy_score(query: str, text: str) -> int:
    """Score how well query matches text. Higher = better. 0 = no match."""
    query = query.lower()
    text_lower = text.lower()
    qi = 0
    score = 0
    last_match = -1
    for ti, ch in enumerate(text_lower):
        if qi < len(query) and ch == query[qi]:
            score += 1
            # Bonus for consecutive matches
            if ti == last_match + 1:
                score += 2
            # Bonus for word-start match
            if ti == 0 or text[ti - 1] in " :_-":
                score += 3
            last_match = ti
            qi += 1
    if qi < len(query):
        return 0  # not all chars matched
    return score


class CommandPalette(QWidget):
    """Floating command palette with fuzzy search."""

    action_triggered = Signal(str)  # action ID

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._actions: list[ActionItem] = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(4)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a command...")
        self._input.setFont(QFont("monospace", 12))
        self._input.textChanged.connect(self._filter)
        lay.addWidget(self._input)

        self._list = QListWidget()
        self._list.setFont(QFont("monospace", 11))
        self._list.itemActivated.connect(self._on_activate)
        lay.addWidget(self._list, 1)

        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.hide()

    def show_palette(self, actions: list[ActionItem]) -> None:
        self._actions = actions
        self._input.clear()
        self._populate(actions)

        # Center in parent
        pw = self.parent().width() if self.parent() else 600
        w = min(pw * 2 // 3, 600)
        self.setFixedWidth(w)

        parent = self.parent()
        if parent:
            px = parent.mapToGlobal(parent.rect().center())
            self.move(px.x() - w // 2, px.y() - 200)

        self.show()
        self._input.setFocus()

    def _populate(self, actions: list[ActionItem]) -> None:
        self._list.clear()
        for a in actions:
            text = f"{a.category}: {a.label}" if a.category else a.label
            if a.shortcut:
                text += f"  ({a.shortcut})"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, a.id)
            self._list.addItem(item)
        if self._list.count():
            self._list.setCurrentRow(0)

    def _filter(self, query: str) -> None:
        if not query:
            self._populate(self._actions)
            return
        scored = []
        for a in self._actions:
            text = f"{a.category}: {a.label}" if a.category else a.label
            s = _fuzzy_score(query, text)
            if s > 0:
                scored.append((s, a))
        scored.sort(key=lambda x: -x[0])
        self._populate([a for _, a in scored])

    def _on_activate(self, item: QListWidgetItem) -> None:
        action_id = item.data(Qt.ItemDataRole.UserRole)
        self.hide()
        if action_id:
            self.action_triggered.emit(action_id)
            for a in self._actions:
                if a.id == action_id:
                    a.callback()
                    break

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            return
        if event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            self._list.keyPressEvent(event)
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current = self._list.currentItem()
            if current:
                self._on_activate(current)
            return
        super().keyPressEvent(event)
