"""Workspace state management."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from PySide6.QtCore import QSettings


@dataclass
class Workspace:
    """Tracks the current workspace folder and open file state."""

    folder: str | None = None
    open_files: list[str] = field(default_factory=list)
    active_file: str | None = None

    # -- Persistence ---------------------------------------------------------

    def save(self, path: str) -> None:
        """Write workspace state to a .scpi-workspace JSON file."""
        data = {
            "version": 1,
            "folder": self.folder,
            "openFiles": self.open_files,
            "activeFile": self.active_file,
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str) -> Workspace:
        """Read workspace state from a .scpi-workspace JSON file."""
        with open(path) as f:
            data = json.load(f)
        return cls(
            folder=data.get("folder"),
            open_files=data.get("openFiles", []),
            active_file=data.get("activeFile"),
        )

    # -- QSettings helpers ---------------------------------------------------

    @staticmethod
    def save_last_folder(folder: str) -> None:
        s = QSettings("SCPIToolkit", "GUI")
        s.setValue("lastWorkspaceFolder", folder)

    @staticmethod
    def last_folder() -> str | None:
        s = QSettings("SCPIToolkit", "GUI")
        val = s.value("lastWorkspaceFolder")
        if val and os.path.isdir(val):
            return val
        return None

    # -- Helpers -------------------------------------------------------------

    def abs_path(self, rel: str) -> str:
        """Resolve a relative path against the workspace folder."""
        if self.folder and not os.path.isabs(rel):
            return os.path.join(self.folder, rel)
        return rel

    def rel_path(self, abs_path: str) -> str:
        """Make an absolute path relative to the workspace folder."""
        if self.folder:
            try:
                return os.path.relpath(abs_path, self.folder)
            except ValueError:
                pass
        return abs_path
