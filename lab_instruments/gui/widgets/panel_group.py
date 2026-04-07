from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .work_area import _WorkArea

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QFrame,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .tab_strip import _DropOverlay, _TabStrip


class _PanelGroup(QFrame):
    """VS Code editor group: tab strip + stacked content area."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._widgets: list[tuple[str, QWidget]] = []
        self.setObjectName("panelGroup")
        self.setStyleSheet("#panelGroup { border: 1px solid #ccc; }")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._tab_strip = _TabStrip(self)
        lay.addWidget(self._tab_strip)

        self._stack = QStackedWidget()

        lay.addWidget(self._stack, 1)

        self._overlay = _DropOverlay(self)
        self.setMinimumSize(QSize(1, 1))

    def _work_area(self) -> _WorkArea | None:
        from .work_area import _WorkArea

        w = self.parent()
        while w:
            if isinstance(w, _WorkArea):
                return w  # type: ignore[return-value]
            try:
                w = w.parent()
            except Exception:
                break
        return None

    def add_widget(self, title: str, widget: QWidget) -> None:
        self._widgets.append((title, widget))
        self._stack.addWidget(widget)
        idx = self._tab_strip.add_tab(title)
        self.set_current_tab(idx)

    def remove_widget_at(self, idx: int) -> tuple[str, QWidget] | None:
        if not 0 <= idx < len(self._widgets):
            return None
        title, widget = self._widgets.pop(idx)
        self._stack.removeWidget(widget)
        self._tab_strip.remove_tab(idx)
        if self._widgets:
            new_idx = min(idx, len(self._widgets) - 1)
            self._stack.setCurrentIndex(new_idx)
            self._tab_strip.set_current(new_idx)
        return title, widget

    def set_current_tab(self, idx: int) -> None:
        if 0 <= idx < len(self._widgets):
            self._stack.setCurrentIndex(idx)
            self._tab_strip.set_current(idx)

    def count(self) -> int:
        return len(self._widgets)

    def close_tab(self, idx: int) -> None:
        item = self.remove_widget_at(idx)
        if item is None:
            return
        _title, widget = item
        win = self._find_main_win()
        if win and hasattr(win, "_on_tab_closed"):
            win._on_tab_closed(widget)
        if self.count() == 0:
            work = self._work_area()
            if work:
                work._remove_empty(self)

    def _find_main_win(self) -> QMainWindow | None:
        w = self.parent()
        while w:
            if isinstance(w, QMainWindow):
                return w  # type: ignore[return-value]
            try:
                w = w.parent()
            except Exception:
                break
        return None

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._overlay.resize(self.size())
        self._overlay.move(0, 0)
