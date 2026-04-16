"""File explorer dock panel — QTreeView + QFileSystemModel."""

from __future__ import annotations

import os
import shutil
from collections import deque

from PySide6.QtCore import QDir, QModelIndex, QPoint, QRect, Qt, QTimer, QUrl, Signal
from PySide6.QtGui import (
    QColor,
    QDrag,
    QFont,
    QFontMetrics,
    QKeySequence,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileSystemModel,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

_HIDDEN_DIRS = {"__pycache__", ".git", ".svn", ".hg", "node_modules", ".venv", "venv", ".mypy_cache", ".ruff_cache"}

# Maximum number of undoable operations kept in memory
_UNDO_LIMIT = 50


def _make_ghost_pixmap(names: list[str]) -> QPixmap:
    """Build a semi-transparent pill showing the dragged file name(s)."""
    label = names[0] if len(names) == 1 else f"{names[0]} (+{len(names) - 1} more)"
    font = QFont()
    font.setPointSize(10)
    fm = QFontMetrics(font)
    pad_x, pad_y = 12, 6
    text_w = fm.horizontalAdvance(label)
    w = text_w + pad_x * 2
    h = fm.height() + pad_y * 2
    pix = QPixmap(w, h)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    bg = QColor(40, 40, 40, 200)
    p.setBrush(bg)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRect(0, 0, w, h), 6, 6)
    p.setFont(font)
    p.setPen(QColor(255, 255, 255, 230))
    p.drawText(QRect(pad_x, pad_y, text_w, fm.height()), Qt.AlignmentFlag.AlignLeft, label)
    p.end()
    return pix


class _FilteredFileSystemModel(QFileSystemModel):
    """QFileSystemModel that hides __pycache__ and other noise directories."""

    def hasChildren(self, parent=None) -> bool:  # noqa: N802
        if parent is None:
            parent = QModelIndex()
        return super().hasChildren(parent)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            name = super().data(index, role)
            if name in _HIDDEN_DIRS:
                return None
        return super().data(index, role)

    def flags(self, index):
        name = self.fileName(index)
        if name in _HIDDEN_DIRS:
            return Qt.ItemFlag.NoItemFlags
        base = super().flags(index)
        return base | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled


_HOVER_EXPAND_MS = 600  # how long to hover over a folder before it auto-expands


class _FileTree(QTreeView):
    """QTreeView with ghost drag preview, drag-and-drop, Delete key, and Ctrl+Z."""

    delete_requested = Signal(list)  # list[str] paths
    move_requested = Signal(list, str)  # (src_paths, dest_dir)
    copy_requested = Signal(list, str)  # (src_paths, dest_dir)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        # Hover-to-expand during drag
        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._expand_hovered)
        self._hover_index: QModelIndex | None = None

    # -- keyboard -------------------------------------------------------------

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            paths = self._selected_paths()
            if paths:
                self.delete_requested.emit(paths)
                return
        super().keyPressEvent(event)

    def _selected_paths(self) -> list[str]:
        model = self.model()
        paths: list[str] = []
        for idx in self.selectedIndexes():
            if idx.column() != 0:
                continue
            p = model.filePath(idx)
            if p and p not in paths:
                paths.append(p)
        return paths

    # -- ghost drag -----------------------------------------------------------

    def startDrag(self, supported_actions) -> None:  # noqa: N802
        paths = self._selected_paths()
        if not paths:
            super().startDrag(supported_actions)
            return

        names = [os.path.basename(p) for p in paths]
        ghost = _make_ghost_pixmap(names)

        drag = QDrag(self)
        # Populate MIME with the selected paths so the model can process them,
        # and also add URLs so OS targets work.
        mime = self.model().mimeData(self.selectedIndexes())
        if mime is None:
            from PySide6.QtCore import QMimeData

            mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(p) for p in paths])
        drag.setMimeData(mime)
        drag.setPixmap(ghost)
        drag.setHotSpot(QPoint(ghost.width() // 2, ghost.height() // 2))
        drag.exec(supported_actions, Qt.DropAction.MoveAction)

    # -- drag-and-drop --------------------------------------------------------

    def _expand_hovered(self) -> None:
        if (
            self._hover_index is not None and self._hover_index.isValid() and self.model().isDir(self._hover_index)  # type: ignore[union-attr]
        ):
            self.expand(self._hover_index)

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:  # noqa: N802
        # Hover-to-expand: restart timer whenever cursor moves to a new index
        idx = self.indexAt(event.position().toPoint())
        if idx != self._hover_index:
            self._hover_index = idx
            self._hover_timer.stop()
            if idx.isValid() and self.model().isDir(idx):  # type: ignore[union-attr]
                self._hover_timer.start(_HOVER_EXPAND_MS)

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dragLeaveEvent(self, event) -> None:  # noqa: N802
        self._hover_timer.stop()
        self._hover_index = None
        super().dragLeaveEvent(event)

    def dropEvent(self, event) -> None:  # noqa: N802
        self._hover_timer.stop()
        self._hover_index = None
        md = event.mimeData()

        if md.hasUrls():
            dest_dir = self._drop_dest_dir(event.position().toPoint())
            if not dest_dir:
                event.ignore()
                return
            src_paths = [u.toLocalFile() for u in md.urls() if u.isLocalFile()]
            if src_paths:
                modifiers = QApplication.keyboardModifiers()
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    self.copy_requested.emit(src_paths, dest_dir)
                else:
                    self.move_requested.emit(src_paths, dest_dir)
            event.acceptProposedAction()
            return

        super().dropEvent(event)

    def _drop_dest_dir(self, pos: QPoint) -> str | None:
        model = self.model()
        idx = self.indexAt(pos)
        if idx.isValid():
            path = model.filePath(idx)
            return path if model.isDir(idx) else os.path.dirname(path)
        root_idx = self.rootIndex()
        if root_idx.isValid():
            return model.filePath(root_idx)
        return None


class FileExplorer(QWidget):
    """File tree sidebar for browsing workspace files."""

    file_selected = Signal(str)  # absolute path
    run_script = Signal(str)  # absolute path of .scpi to run
    debug_script = Signal(str)  # absolute path of .scpi to debug
    files_deleted = Signal(list)  # list[str] of absolute paths that were deleted

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._root: str | None = None
        # Undo stack: each entry is a callable that reverses the last operation.
        self._undo_stack: deque = deque(maxlen=_UNDO_LIMIT)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)

        hdr = QHBoxLayout()
        self._title = QLabel("No folder open")
        self._title.setStyleSheet("font-weight: bold; font-size: 11px;")
        hdr.addWidget(self._title, 1)
        lay.addLayout(hdr)

        self._model = _FilteredFileSystemModel()
        self._model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        self._model.setNameFilterDisables(False)
        self._model.setReadOnly(False)

        self._tree = _FileTree()
        self._tree.setModel(self._model)
        self._tree.setHeaderHidden(True)
        self._tree.setColumnHidden(1, True)
        self._tree.setColumnHidden(2, True)
        self._tree.setColumnHidden(3, True)
        self._tree.setAnimated(True)
        self._tree.setIndentation(16)
        self._tree.doubleClicked.connect(self._on_double_click)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)

        self._tree.delete_requested.connect(self._delete_paths)
        self._tree.move_requested.connect(self._move_paths)
        self._tree.copy_requested.connect(self._copy_paths)

        # Ctrl+Z inside the explorer panel
        from PySide6.QtGui import QShortcut

        undo_sc = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_sc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        undo_sc.activated.connect(self._undo)

        lay.addWidget(self._tree, 1)

    def set_root(self, folder: str) -> None:
        self._root = folder
        idx = self._model.setRootPath(folder)
        self._tree.setRootIndex(idx)
        self._title.setText(os.path.basename(folder) or folder)

    def root(self) -> str | None:
        return self._root

    # -- undo -----------------------------------------------------------------

    def _push_undo(self, fn) -> None:
        self._undo_stack.append(fn)

    def _undo(self) -> None:
        if not self._undo_stack:
            return
        fn = self._undo_stack.pop()
        try:
            fn()
        except Exception as exc:
            QMessageBox.warning(self, "Undo Failed", str(exc))

    # -- helpers --------------------------------------------------------------

    def _selected_paths(self) -> list[str]:
        return self._tree._selected_paths()

    def _on_double_click(self, index: QModelIndex) -> None:
        path = self._model.filePath(index)
        if path and not self._model.isDir(index):
            self.file_selected.emit(path)

    def _context_dir(self, index: QModelIndex) -> str:
        if index.isValid():
            path = self._model.filePath(index)
            return path if self._model.isDir(index) else os.path.dirname(path)
        return self._root or ""

    # -- context menu ---------------------------------------------------------

    def _on_context_menu(self, pos) -> None:
        index = self._tree.indexAt(pos)
        path = self._model.filePath(index) if index.isValid() else None
        is_dir = self._model.isDir(index) if index.isValid() else False
        ctx_dir = self._context_dir(index)
        selected = self._selected_paths()
        multi = len(selected) > 1

        menu = QMenu(self)

        if path and not is_dir and not multi:
            menu.addAction("Open", lambda: self.file_selected.emit(path))
            ext = os.path.splitext(path)[1].lower()
            if ext in (".scpi", ".py"):
                menu.addAction("Run Script", lambda: self.run_script.emit(path))
                menu.addAction("Debug Script", lambda: self.debug_script.emit(path))
            menu.addSeparator()

        if not multi:
            menu.addAction("New File…", lambda: self._new_file(ctx_dir, None))
            menu.addAction("New Script", lambda: self._new_file(ctx_dir, ".scpi"))
            menu.addAction("New Python File", lambda: self._new_file(ctx_dir, ".py"))
            menu.addAction("New Folder", lambda: self._new_folder(ctx_dir))
            menu.addSeparator()

        targets = selected if selected else ([path] if path else [])
        if targets:
            if not multi and path:
                menu.addAction("Rename…", lambda: self._rename(path))
            lbl = f"Delete {len(targets)} items" if multi else "Delete"
            menu.addAction(lbl, lambda: self._delete_paths(targets))
            if not multi and path:
                menu.addSeparator()
                menu.addAction("Copy Path", lambda: self._copy_to_clipboard(os.path.abspath(path)))
                menu.addAction("Copy Relative Path", lambda: self._copy_to_clipboard(os.path.relpath(path)))

        if self._undo_stack:
            menu.addSeparator()
            menu.addAction("Undo", self._undo)

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    # -- file operations ------------------------------------------------------

    @staticmethod
    def _copy_to_clipboard(text: str) -> None:
        QApplication.clipboard().setText(text)

    def _new_file(self, parent_dir: str, ext: str | None) -> None:
        if ext is None:
            # Generic file — user provides full name including extension
            name, ok = QInputDialog.getText(self, "New File", "File name (e.g. notes.txt, data.csv):")
        else:
            name, ok = QInputDialog.getText(self, "New File", f"File name (e.g. my_script{ext}):")
        if not ok or not name:
            return
        if ext and not name.endswith(ext):
            name += ext
        path = os.path.join(parent_dir, name)
        if os.path.exists(path):
            QMessageBox.warning(self, "File Exists", f"{name} already exists.")
            return
        with open(path, "w") as f:
            if name.endswith(".scpi"):
                f.write(f"# {name}\n\n")
            elif name.endswith(".py"):
                f.write(f'"""Script: {name}"""\n\n')
        self._push_undo(lambda p=path: os.remove(p) if os.path.isfile(p) else None)
        self.file_selected.emit(path)

    def _new_folder(self, parent_dir: str) -> None:
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if not ok or not name:
            return
        path = os.path.join(parent_dir, name)
        if os.path.exists(path):
            QMessageBox.warning(self, "Folder Exists", f"{name} already exists.")
            return
        os.makedirs(path)
        self._push_undo(lambda p=path: shutil.rmtree(p, ignore_errors=True))

    def _rename(self, path: str) -> None:
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
        if not ok or not new_name or new_name == old_name:
            return
        new_path = os.path.join(os.path.dirname(path), new_name)
        if os.path.exists(new_path):
            QMessageBox.warning(self, "Name Taken", f"{new_name} already exists.")
            return
        os.rename(path, new_path)
        self._push_undo(lambda old=path, new=new_path: os.rename(new, old) if os.path.exists(new) else None)

    def _delete_paths(self, paths: list[str]) -> None:
        names = "\n".join(f"  • {os.path.basename(p)}" for p in paths)
        kind = "items" if len(paths) > 1 else ("folder" if os.path.isdir(paths[0]) else "file")
        reply = QMessageBox.question(
            self,
            f"Delete {kind}",
            f"Permanently delete:\n{names}\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        deleted: list[str] = []
        for path in paths:
            try:
                if os.path.isdir(path):
                    # collect all files inside the directory before removing
                    for root, _dirs, files in os.walk(path):
                        for f in files:
                            deleted.append(os.path.join(root, f))
                    deleted.append(path)
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
                    deleted.append(path)
            except Exception as exc:
                QMessageBox.warning(self, "Delete Failed", f"Could not delete {os.path.basename(path)}:\n{exc}")
        if deleted:
            self.files_deleted.emit(deleted)

    def _move_paths(self, src_paths: list[str], dest_dir: str) -> None:
        moved: list[tuple[str, str]] = []
        for src in src_paths:
            if os.path.dirname(os.path.abspath(src)) == os.path.abspath(dest_dir) or os.path.abspath(
                src
            ) == os.path.abspath(dest_dir):
                continue
            dest = os.path.join(dest_dir, os.path.basename(src))
            if os.path.exists(dest):
                reply = QMessageBox.question(
                    self,
                    "Overwrite?",
                    f"'{os.path.basename(src)}' already exists in the destination.\nOverwrite?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    continue
            try:
                shutil.move(src, dest)
                moved.append((dest, os.path.dirname(src)))
            except Exception as exc:
                QMessageBox.warning(self, "Move Failed", f"Could not move {os.path.basename(src)}:\n{exc}")
        if moved:

            def _undo_move(pairs=moved):
                for dest_path, orig_dir in reversed(pairs):
                    back = os.path.join(orig_dir, os.path.basename(dest_path))
                    if os.path.exists(dest_path):
                        shutil.move(dest_path, back)

            self._push_undo(_undo_move)

    def _copy_paths(self, src_paths: list[str], dest_dir: str) -> None:
        copied: list[str] = []
        for src in src_paths:
            dest = os.path.join(dest_dir, os.path.basename(src))
            try:
                if os.path.isdir(src):
                    if os.path.exists(dest):
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                else:
                    shutil.copy2(src, dest)
                copied.append(dest)
            except Exception as exc:
                QMessageBox.warning(self, "Copy Failed", f"Could not copy {os.path.basename(src)}:\n{exc}")
        if copied:

            def _undo_copy(paths=copied):
                for p in paths:
                    if os.path.isdir(p):
                        shutil.rmtree(p, ignore_errors=True)
                    elif os.path.isfile(p):
                        os.remove(p)

            self._push_undo(_undo_copy)
