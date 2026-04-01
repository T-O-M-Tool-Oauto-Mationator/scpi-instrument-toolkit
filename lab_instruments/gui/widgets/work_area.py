from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from .panel_group import _PanelGroup
from .tab_strip import _DZ


class _WorkArea(QWidget):
    """Root container managing a recursive QSplitter tree of _PanelGroups."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._root = self._mk_splitter(Qt.Orientation.Horizontal)
        lay.addWidget(self._root)
        self._default = _PanelGroup()
        self._root.addWidget(self._default)

    def _mk_splitter(self, orient: Qt.Orientation) -> QSplitter:
        s = QSplitter(orient)
        s.setHandleWidth(5)
        s.setChildrenCollapsible(False)
        s.setStyleSheet("QSplitter::handle { background: #ccc; }QSplitter::handle:hover { background: #1a6bbf55; }")
        return s

    def default_group(self) -> _PanelGroup:
        return self._default

    def all_groups(self) -> list[_PanelGroup]:
        result: list[_PanelGroup] = []

        def _walk(w: QWidget) -> None:
            if isinstance(w, _PanelGroup):
                result.append(w)
            elif isinstance(w, QSplitter):
                for i in range(w.count()):
                    _walk(w.widget(i))

        _walk(self._root)
        return result

    def add_widget(self, title: str, widget: QWidget) -> None:
        groups = self.all_groups()
        if groups:
            groups[-1].add_widget(title, widget)
        else:
            g = _PanelGroup()
            self._root.addWidget(g)
            self._default = g
            g.add_widget(title, widget)

    def remove_widget(self, widget: QWidget) -> None:
        for group in self.all_groups():
            for i, (_, w) in enumerate(group._widgets):
                if w is widget:
                    group.remove_widget_at(i)
                    if group.count() == 0:
                        self._remove_empty(group)
                    return

    def perform_drop(self, src: _PanelGroup, tab_idx: int, dst: _PanelGroup, zone: _DZ) -> None:
        item = src.remove_widget_at(tab_idx)
        if item is None:
            return
        title, widget = item
        if zone == _DZ.CENTER:
            dst.add_widget(title, widget)
        else:
            new_grp = _PanelGroup()
            new_grp.add_widget(title, widget)
            self._split(dst, new_grp, zone)
        if src.count() == 0:
            self._remove_empty(src)

    def _split(self, dst: _PanelGroup, new_grp: _PanelGroup, zone: _DZ) -> None:
        horiz = zone in (_DZ.LEFT, _DZ.RIGHT)
        orient = Qt.Orientation.Horizontal if horiz else Qt.Orientation.Vertical
        before = zone in (_DZ.LEFT, _DZ.TOP)

        sp = dst.parent()
        if not isinstance(sp, QSplitter):
            return
        idx = sp.indexOf(dst)
        sizes = sp.sizes()
        sz = sizes[idx] if idx < len(sizes) else 400

        if sp.orientation() == orient:
            ins = idx if before else idx + 1
            sp.insertWidget(ins, new_grp)
            half = max(sz // 2, 1)
            new_s = list(sizes)
            new_s[idx] = half
            new_s.insert(ins, half)
            sp.setSizes(new_s)
        else:
            sub = self._mk_splitter(orient)
            dst.setParent(None)  # removes from sp
            if before:
                sub.addWidget(new_grp)
                sub.addWidget(dst)
            else:
                sub.addWidget(dst)
                sub.addWidget(new_grp)
            half = max(sz // 2, 1)
            sub.setSizes([half, half])
            sp.insertWidget(idx, sub)
            new_s = list(sizes)
            new_s[idx] = sz
            sp.setSizes(new_s)

    def _remove_empty(self, group: _PanelGroup) -> None:
        sp = group.parent()
        if not isinstance(sp, QSplitter):
            group.deleteLater()
            return
        group.hide()
        group.setParent(None)
        group.deleteLater()

        # Collapse single-child splitters (but never the root)
        if sp.count() == 1 and sp is not self._root:
            only = sp.widget(0)
            gp = sp.parent()
            if isinstance(gp, QSplitter):
                gp_idx = gp.indexOf(sp)
                gp_sizes = gp.sizes()
                size = gp_sizes[gp_idx] if gp_idx < len(gp_sizes) else 400
                only.setParent(None)
                sp.setParent(None)
                sp.deleteLater()
                gp.insertWidget(gp_idx, only)
                new_s = list(gp_sizes)
                new_s[gp_idx] = size
                gp.setSizes(new_s)

        # Always keep at least one group
        if not self.all_groups():
            g = _PanelGroup()
            self._root.addWidget(g)
            self._default = g
