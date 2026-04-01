from __future__ import annotations

from enum import Enum, auto

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMenu, QWidget


class _DZ(Enum):
    CENTER = auto()
    LEFT   = auto()
    RIGHT  = auto()
    TOP    = auto()
    BOTTOM = auto()


_DRAG_STATE: dict = {}  # keys: active, source, tab, target, zone


class _DropOverlay(QWidget):
    """Semi-transparent overlay painted over a _PanelGroup showing drop zones."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._zone: _DZ | None = None
        self.hide()

    def show_for(self, zone: _DZ | None) -> None:
        self._zone = zone
        if zone is None:
            self.hide()
            return
        p = self.parent()
        if p:
            self.resize(p.size())
            self.move(0, 0)
        self.raise_()
        self.show()
        self.update()

    def zone_at(self, pos: QPoint) -> _DZ:
        r = self.rect()
        w, h = r.width(), r.height()
        edge_w, edge_h = max(w // 5, 40), max(h // 5, 40)  # ~20% edge zones
        x, y = pos.x(), pos.y()
        if x < edge_w:         return _DZ.LEFT
        if x > w - edge_w:     return _DZ.RIGHT
        if y < edge_h:         return _DZ.TOP
        if y > h - edge_h:     return _DZ.BOTTOM
        return _DZ.CENTER

    def paintEvent(self, _ev) -> None:  # noqa: N802
        if self._zone is None:
            return
        p = QPainter(self)
        r = self.rect()
        w, h = r.width(), r.height()
        # Highlight covers half the group for splits, full for center (VS Code style)
        highlight = {
            _DZ.LEFT:   QRect(0,      0,      w // 2,   h),
            _DZ.RIGHT:  QRect(w // 2, 0,      w // 2,   h),
            _DZ.TOP:    QRect(0,      0,      w,        h // 2),
            _DZ.BOTTOM: QRect(0,      h // 2, w,        h // 2),
            _DZ.CENTER: r,
        }[self._zone]
        hi = self.palette().color(self.palette().ColorRole.Highlight)
        bg = hi; bg.setAlpha(30)
        p.fillRect(r, bg)
        hi2 = QColor(hi); hi2.setAlpha(90)
        p.fillRect(highlight, hi2)
        hi3 = QColor(hi); hi3.setAlpha(200)
        p.setPen(QPen(hi3, 2))
        p.drawRect(highlight.adjusted(2, 2, -2, -2))
        p.end()


class _TabStrip(QWidget):
    """Custom tab bar with drag-to-split support."""

    TAB_H = 32
    DRAG_MIN = 8

    def __init__(self, group: "PanelGroup") -> None:
        super().__init__(group)
        self._group = group
        self._tabs: list[str] = []
        self._current = 0
        self._hovered = -1
        self._drag_start: QPoint | None = None
        self._drag_tab: int = -1
        self._close_hov: int = -1
        self.setFixedHeight(self.TAB_H)
        self.setMouseTracking(True)

    # -- public API ----------------------------------------------------------

    def add_tab(self, title: str) -> int:
        self._tabs.append(title)
        self.update()
        return len(self._tabs) - 1

    def remove_tab(self, idx: int) -> None:
        if 0 <= idx < len(self._tabs):
            self._tabs.pop(idx)
            if self._current >= len(self._tabs):
                self._current = max(0, len(self._tabs) - 1)
            self.update()

    def set_current(self, idx: int) -> None:
        if 0 <= idx < len(self._tabs):
            self._current = idx
            self.update()

    def count(self) -> int:
        return len(self._tabs)

    # -- geometry ------------------------------------------------------------

    def _tab_rects(self) -> list[QRect]:
        fm = self.fontMetrics()
        rects, x = [], 0
        for t in self._tabs:
            tw = max(80, fm.horizontalAdvance(t) + 32)
            rects.append(QRect(x, 0, tw, self.TAB_H))
            x += tw
        return rects

    def tab_at(self, pos: QPoint) -> int:
        for i, r in enumerate(self._tab_rects()):
            if r.contains(pos):
                return i
        return -1

    def _close_rect(self, tab_rect: QRect) -> QRect:
        """14x14 x button, right-aligned inside the tab."""
        sz = 14
        return QRect(tab_rect.right() - sz - 5, (self.TAB_H - sz) // 2, sz, sz)

    def _close_rects(self) -> list[QRect]:
        return [self._close_rect(tr) for tr in self._tab_rects()]

    # -- mouse events --------------------------------------------------------

    def contextMenuEvent(self, event) -> None:  # noqa: N802
        idx = self.tab_at(event.pos())
        if idx < 0:
            return
        menu = QMenu(self)
        pop_out = menu.addAction("Pop Out")
        menu.addSeparator()
        close = menu.addAction("Close")
        action = menu.exec(event.globalPos())
        if action == pop_out:
            self._pop_out_tab(idx)
        elif action == close:
            self._group.close_tab(idx)

    def _pop_out_tab(self, idx: int) -> None:
        if not 0 <= idx < len(self._group._widgets):
            return
        title, widget = self._group._widgets[idx]
        # Find main window
        from PySide6.QtWidgets import QMainWindow
        w = self._group.parent()
        while w:
            if isinstance(w, QMainWindow) and hasattr(w, "pop_out_widget"):
                self._group.remove_widget_at(idx)
                if self._group.count() == 0:
                    work = self._group._work_area()
                    if work:
                        work._remove_empty(self._group)
                w.pop_out_widget(title, widget)
                return
            try:
                w = w.parent()
            except Exception:
                break

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            # Close button takes priority
            for i, cr in enumerate(self._close_rects()):
                if (i == self._current or i == self._hovered) and cr.contains(pos):
                    self._group.close_tab(i)
                    return
            idx = self.tab_at(pos)
            if idx >= 0:
                self._drag_start = pos
                self._drag_tab = idx
                self._group.set_current_tab(idx)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        pos = event.pos()
        new_hov = self.tab_at(pos)
        if new_hov != self._hovered:
            self._hovered = new_hov
            self.update()
        new_close = -1
        for i, cr in enumerate(self._close_rects()):
            if (i == self._current or i == self._hovered) and cr.contains(pos):
                new_close = i
                break
        if new_close != self._close_hov:
            self._close_hov = new_close
            self.update()

        if (
            self._drag_start is not None
            and self._drag_tab >= 0
            and (event.buttons() & Qt.MouseButton.LeftButton)
            and (pos - self._drag_start).manhattanLength() > self.DRAG_MIN
        ):
            if not _DRAG_STATE:
                _DRAG_STATE["active"] = True
                _DRAG_STATE["source"] = self._group
                _DRAG_STATE["tab"] = self._drag_tab
                self.grabMouse()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)

            if _DRAG_STATE.get("active"):
                self._update_drag(self.mapToGlobal(pos))

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if _DRAG_STATE.get("active"):
            self.releaseMouse()
            self.unsetCursor()
            self._finish_drag()
        self._drag_start = None
        self._drag_tab = -1

    def leaveEvent(self, event) -> None:  # noqa: N802
        if not _DRAG_STATE.get("active"):
            self._hovered = -1
            self._close_hov = -1
            self.update()

    # -- drag logic ----------------------------------------------------------

    def _update_drag(self, gpos: QPoint) -> None:
        from .panel_group import _PanelGroup

        work = self._group._work_area()
        if not work:
            return
        for g in work.all_groups():
            g._overlay.show_for(None)

        widget = QApplication.widgetAt(gpos)
        target: _PanelGroup | None = None
        w = widget
        while w:
            if isinstance(w, _PanelGroup):
                target = w
                break
            try:
                w = w.parent()
            except Exception:
                break

        if target:
            local = target.mapFromGlobal(gpos)
            zone = target._overlay.zone_at(local)
            src: _PanelGroup = _DRAG_STATE["source"]
            if target is src and src.count() == 1 and zone == _DZ.CENTER:
                zone = None  # can't merge into self with only one tab
            target._overlay.show_for(zone)
            _DRAG_STATE["target"] = target
            _DRAG_STATE["zone"] = zone
        else:
            _DRAG_STATE.pop("target", None)
            _DRAG_STATE.pop("zone", None)

    def _finish_drag(self) -> None:
        from .panel_group import _PanelGroup

        work = self._group._work_area()
        if work:
            for g in work.all_groups():
                g._overlay.show_for(None)
        target: _PanelGroup | None = _DRAG_STATE.get("target")
        zone: _DZ | None = _DRAG_STATE.get("zone")
        src: _PanelGroup | None = _DRAG_STATE.get("source")
        tab_idx: int = _DRAG_STATE.get("tab", -1)
        _DRAG_STATE.clear()
        if work and target and zone and src is not None and tab_idx >= 0:
            if not (target is src and zone == _DZ.CENTER):
                work.perform_drop(src, tab_idx, target, zone)

    # -- paint ---------------------------------------------------------------

    def paintEvent(self, _ev) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        pal = self.palette()
        bg   = pal.color(pal.ColorRole.Window)
        base = pal.color(pal.ColorRole.Base)
        text = pal.color(pal.ColorRole.WindowText)
        dim  = pal.color(pal.ColorRole.PlaceholderText)
        hi   = pal.color(pal.ColorRole.Highlight)
        p.fillRect(r, bg)
        tab_rects = self._tab_rects()
        for i, (title, tr) in enumerate(zip(self._tabs, tab_rects)):
            active  = i == self._current
            hovered = i == self._hovered and not active
            show_x  = active or hovered
            if active:
                p.fillRect(tr, base)
                p.fillRect(QRect(tr.x(), 0, tr.width(), 2), hi)
                p.setPen(text)
            elif hovered:
                hover_bg = base; hover_bg.setAlpha(180)
                p.fillRect(tr, hover_bg)
                p.setPen(text)
            else:
                p.setPen(dim)
            sep_col = pal.color(pal.ColorRole.Mid)
            p.fillRect(QRect(tr.right(), 2, 1, tr.height() - 4), sep_col)
            fm = p.fontMetrics()
            tr2 = tr.adjusted(12, 0, -26 if show_x else -8, 0)
            p.drawText(
                tr2,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                fm.elidedText(title, Qt.TextElideMode.ElideRight, tr2.width()),
            )
            if show_x:
                cr = self._close_rect(tr)
                if i == self._close_hov:
                    p.fillRect(cr, pal.color(pal.ColorRole.Midlight))
                x_pen = text if active else dim
                p.setPen(QPen(x_pen, 1.5))
                off = 4
                c = cr.center()
                p.drawLine(c.x() - off, c.y() - off, c.x() + off, c.y() + off)
                p.drawLine(c.x() + off, c.y() - off, c.x() - off, c.y() + off)
        p.fillRect(QRect(0, r.height() - 1, r.width(), 1), pal.color(pal.ColorRole.Mid))
        p.end()
