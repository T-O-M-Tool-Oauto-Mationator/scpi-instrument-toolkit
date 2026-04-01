"""File explorer dock panel — QTreeView + QFileSystemModel."""

from __future__ import annotations

import os
import shutil

from PySide6.QtCore import QDir, QModelIndex, Qt, Signal
from PySide6.QtWidgets import (
    QFileSystemModel,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


_HIDDEN_DIRS = {"__pycache__", ".git", ".svn", ".hg", "node_modules", ".venv", "venv", ".mypy_cache", ".ruff_cache"}


class _FilteredFileSystemModel(QFileSystemModel):
    """QFileSystemModel that hides __pycache__ and other noise directories."""

    def hasChildren(self, parent=QModelIndex()) -> bool:  # noqa: N802
        return super().hasChildren(parent)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        # QFileSystemModel doesn't use filterAcceptsRow — we override data instead
        return True

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
        return super().flags(index)


class FileExplorer(QWidget):
    """File tree sidebar for browsing workspace files."""

    file_selected = Signal(str)  # absolute path
    run_script = Signal(str)  # absolute path of .scpi to run
    debug_script = Signal(str)  # absolute path of .scpi to debug

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._root: str | None = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)

        # Header
        hdr = QHBoxLayout()
        self._title = QLabel("No folder open")
        self._title.setStyleSheet("font-weight: bold; font-size: 11px;")
        hdr.addWidget(self._title, 1)
        lay.addLayout(hdr)

        # Tree view
        self._model = _FilteredFileSystemModel()
        self._model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        self._model.setNameFilterDisables(False)

        self._tree = QTreeView()
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
        lay.addWidget(self._tree, 1)

    def set_root(self, folder: str) -> None:
        self._root = folder
        idx = self._model.setRootPath(folder)
        self._tree.setRootIndex(idx)
        self._title.setText(os.path.basename(folder) or folder)

    def root(self) -> str | None:
        return self._root

    def _on_double_click(self, index: QModelIndex) -> None:
        path = self._model.filePath(index)
        if path and not self._model.isDir(index):
            self.file_selected.emit(path)

    def _context_dir(self, index: QModelIndex) -> str:
        """Return the directory relevant to a context menu action."""
        if index.isValid():
            path = self._model.filePath(index)
            if self._model.isDir(index):
                return path
            return os.path.dirname(path)
        return self._root or ""

    def _on_context_menu(self, pos) -> None:
        index = self._tree.indexAt(pos)
        path = self._model.filePath(index) if index.isValid() else None
        is_dir = self._model.isDir(index) if index.isValid() else False
        ctx_dir = self._context_dir(index)

        menu = QMenu(self)

        # Open (files only)
        if path and not is_dir:
            menu.addAction("Open", lambda: self.file_selected.emit(path))
            ext = os.path.splitext(path)[1].lower()
            if ext in (".scpi", ".py"):
                menu.addAction("Run Script", lambda: self.run_script.emit(path))
                menu.addAction("Debug Script", lambda: self.debug_script.emit(path))
            menu.addSeparator()

        # Create actions
        menu.addAction("New Script", lambda: self._new_file(ctx_dir, ".scpi"))
        menu.addAction("New Python File", lambda: self._new_file(ctx_dir, ".py"))
        menu.addAction("New Folder", lambda: self._new_folder(ctx_dir))
        menu.addSeparator()

        # Rename / Delete (when something is selected)
        if path:
            menu.addAction("Rename...", lambda: self._rename(path))
            menu.addAction("Delete", lambda: self._delete(path, is_dir))

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    # -- File operations -----------------------------------------------------

    def _new_file(self, parent_dir: str, ext: str) -> None:
        name, ok = QInputDialog.getText(self, "New File", f"File name (e.g. my_script{ext}):")
        if not ok or not name:
            return
        if not name.endswith(ext):
            name += ext
        path = os.path.join(parent_dir, name)
        if os.path.exists(path):
            QMessageBox.warning(self, "File Exists", f"{name} already exists.")
            return
        with open(path, "w") as f:
            if ext == ".scpi":
                f.write(f"# {name}\n\n")
            elif ext == ".py":
                f.write(f'"""Script: {name}"""\n\n')
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

    def _delete(self, path: str, is_dir: bool) -> None:
        name = os.path.basename(path)
        kind = "folder" if is_dir else "file"
        reply = QMessageBox.question(
            self,
            f"Delete {kind}",
            f"Are you sure you want to delete '{name}'?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if is_dir:
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.remove(path)
