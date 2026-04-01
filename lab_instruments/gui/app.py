"""SCPI Instrument Toolkit - Desktop GUI."""

from __future__ import annotations

import argparse
import contextlib
import os
import re
import sys
import threading

from PySide6.QtCore import QObject, QSettings, QThread, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QWidget,
)

from .core.dispatcher import _Dispatcher
from .core.workspace import Workspace
from .dialogs.command_palette import ActionItem, CommandPalette
from .instrument_blocks.awg_block import _AWGBlock
from .instrument_blocks.dmm_block import _DMMBlock
from .instrument_blocks.bq_eval_block import _BQEvalBlock
from .instrument_blocks.psu_block import _PSUBlock
from .instrument_blocks.scope_block import _ScopeBlock
from .instrument_blocks.smu_block import _SMUBlock
from .panels.device_panel import _DevicePanel
from .panels.file_explorer import FileExplorer
from .widgets.console import _Console
from .widgets.work_area import _WorkArea


# -- Background worker for blocking operations --------------------------------


class _Worker(QObject):
    """Runs a callable in a QThread and signals completion."""

    finished = Signal(str)  # result string

    def __init__(self, fn, parent=None):
        super().__init__(parent)
        self._fn = fn

    @Slot()
    def run(self):
        try:
            result = self._fn()
            self.finished.emit(result or "")
        except Exception as exc:
            self.finished.emit(f"[ERROR] {exc}")


# -- Main window -------------------------------------------------------------


class _MainWindow(QMainWindow):
    def __init__(self, d: _Dispatcher) -> None:
        super().__init__()
        self._d = d
        self.setWindowTitle("SCPI Instrument Toolkit")
        self._floating_windows: list[QWidget] = []

        self._psu_blocks: dict[str, _PSUBlock] = {}
        self._psu_closed: set[str] = set()
        self._smu_blocks: dict[str, _SMUBlock] = {}
        self._smu_closed: set[str] = set()
        self._awg_blocks: dict[str, _AWGBlock] = {}
        self._awg_closed: set[str] = set()
        self._dmm_blocks: dict[str, _DMMBlock] = {}
        self._dmm_closed: set[str] = set()
        self._ev_blocks: dict[str, _BQEvalBlock] = {}
        self._ev_closed: set[str] = set()
        self._scope_blocks: dict[str, _ScopeBlock] = {}
        self._scope_closed: set[str] = set()
        self._open_files: dict[str, QWidget] = {}
        self._workspace = Workspace()

        # Restore last workspace folder
        last = Workspace.last_folder()
        if last:
            self._workspace.folder = last

        # ── Menu bar ──────────────────────────────────────────────────
        mb = self.menuBar()
        fm = mb.addMenu("&File")
        nf = QAction("&New Script", self)
        nf.setShortcut("Ctrl+N")
        nf.triggered.connect(self._on_new_script)
        fm.addAction(nf)
        opf = QAction("&Open File...", self)
        opf.setShortcut("Ctrl+O")
        opf.triggered.connect(self._on_open_file)
        fm.addAction(opf)
        of = QAction("Open F&older...", self)
        of.setShortcut("Ctrl+Shift+O")
        of.triggered.connect(self._on_open_folder)
        fm.addAction(of)
        sv = QAction("&Save", self)
        sv.setShortcut("Ctrl+S")
        sv.triggered.connect(self._save_current)
        fm.addAction(sv)
        fm.addSeparator()
        qa = QAction("&Quit", self)
        qa.setShortcut("Ctrl+Q")
        qa.triggered.connect(self.close)
        fm.addAction(qa)

        im = mb.addMenu("&Instruments")
        sa = QAction("&Scan Devices", self)
        sa.setShortcut("Ctrl+Shift+S")
        sa.triggered.connect(self._on_scan)
        im.addAction(sa)
        ea = QAction("&Emergency Stop", self)
        ea.triggered.connect(self._on_estop)
        im.addAction(ea)

        self._view_menu = mb.addMenu("&View")

        # ── Toolbar ───────────────────────────────────────────────────
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.setObjectName("main_toolbar")
        tb.addAction(sa)

        et = QAction("\u26a1 E-STOP", self)
        et.triggered.connect(self._on_estop)
        tb.addAction(et)
        # ── Status bar ────────────────────────────────────────────────
        self._status = QLabel("Ready")
        self.statusBar().addWidget(self._status, 1)
        self._dev_count = QLabel("Devices: 0")
        self.statusBar().addPermanentWidget(self._dev_count)

        # ── Work area (central widget) ─────────────────────────────────
        self._work_area = _WorkArea()
        self.setCentralWidget(self._work_area)

        # ── Console dock (bottom) ──────────────────────────────────────
        self._console = _Console(d)
        _console_dock = QDockWidget("Console", self)
        _console_dock.setWidget(self._console)
        _console_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, _console_dock)
        self._view_menu.addAction(_console_dock.toggleViewAction())

        # ── Device list dock (left) ────────────────────────────────────
        self._device_panel = _DevicePanel(d, self)
        _devices_dock = QDockWidget("Devices", self)
        _devices_dock.setWidget(self._device_panel)
        _devices_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, _devices_dock)
        self._view_menu.addAction(_devices_dock.toggleViewAction())

        # ── File explorer dock (left, tabbed with devices) ─────────────
        self._file_explorer = FileExplorer()
        self._file_explorer.file_selected.connect(self.open_file)
        self._file_explorer.run_script.connect(self._run_script)
        self._file_explorer.debug_script.connect(self._debug_script)
        _explorer_dock = QDockWidget("Explorer", self)
        _explorer_dock.setWidget(self._file_explorer)
        _explorer_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, _explorer_dock)
        self.tabifyDockWidget(_devices_dock, _explorer_dock)
        _devices_dock.raise_()
        self._view_menu.addAction(_explorer_dock.toggleViewAction())

        if self._workspace.folder:
            self._file_explorer.set_root(self._workspace.folder)

        self._console.command_ran.connect(self._on_console_command)

        # ── Command palette ────────────────────────────────────────────
        self._palette = CommandPalette(self)

        # ── VS Code keybinds ───────────────────────────────────────────
        from PySide6.QtGui import QShortcut, QKeySequence

        QShortcut(QKeySequence("Ctrl+Shift+P"), self, self._show_palette)
        QShortcut(QKeySequence("Ctrl+P"), self, self._quick_open)
        QShortcut(QKeySequence("Ctrl+W"), self, self._close_current_tab)
        QShortcut(QKeySequence("Ctrl+G"), self, self._goto_line)
        QShortcut(QKeySequence("F5"), self, lambda: self._run_current_script(debug=False))
        QShortcut(QKeySequence("Shift+F5"), self, lambda: self._run_current_script(debug=True))

        # ── Restore geometry ───────────────────────────────────────────
        s = QSettings("SCPIToolkit", "GUI")
        if s.contains("geometry"):
            self.restoreGeometry(s.value("geometry"))
        if s.contains("state"):
            self.restoreState(s.value("state"))

        QTimer.singleShot(200, self._init)

    # -- Background worker helper -----------------------------------------------

    def _run_in_background(self, fn, on_done=None, status_msg="Working..."):
        """Run *fn* in a QThread. Calls *on_done(result_str)* on completion."""
        self._status.setText(status_msg)
        thread = QThread(self)
        worker = _Worker(fn)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        def _finished(result):
            if on_done:
                on_done(result)
            thread.quit()
            thread.wait()
            thread.deleteLater()
            worker.deleteLater()

        worker.finished.connect(_finished)
        thread.start()

    # -- Workspace / file handling -------------------------------------------

    def _on_new_script(self) -> None:
        """Create a new untitled .scpi script in the workspace folder."""
        folder = self._workspace.folder
        if not folder:
            folder = QFileDialog.getExistingDirectory(self, "Choose folder for new script")
            if not folder:
                return
            self._workspace.folder = folder
            Workspace.save_last_folder(folder)
            self._file_explorer.set_root(folder)

        # Find next available name
        i = 1
        while True:
            name = f"untitled_{i}.scpi" if i > 1 else "untitled.scpi"
            path = os.path.join(folder, name)
            if not os.path.exists(path):
                break
            i += 1

        # Create the file
        with open(path, "w") as f:
            f.write("# New SCPI script\n\n")
        self.open_file(path)
        self._status.setText(f"Created: {name}")

    def _on_open_file(self) -> None:
        """Open a file via dialog."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", self._workspace.folder or "",
            "SCPI Scripts (*.scpi);;Python Files (*.py);;All Files (*)"
        )
        if path:
            self.open_file(path)

    def _on_open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Open Folder", self._workspace.folder or "")
        if not folder:
            return
        self._workspace.folder = folder
        Workspace.save_last_folder(folder)
        self._file_explorer.set_root(folder)
        self._status.setText(f"Opened: {folder}")

    def open_file(self, path: str) -> None:
        """Open a file in the work area. Dispatches by extension."""
        if path in self._open_files:
            # Focus existing tab
            widget = self._open_files[path]
            for group in self._work_area.all_groups():
                for i, (_, w) in enumerate(group._widgets):
                    if w is widget:
                        group.set_current_tab(i)
                        return
            return
        ext = os.path.splitext(path)[1].lower()
        if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
            from .widgets.file_viewers import ImageViewer
            widget = ImageViewer(path)
        elif ext == ".csv":
            from .widgets.file_viewers import CsvViewer
            widget = CsvViewer(path)
        elif ext in (".scpi", ".py", ".txt", ".md", ".json", ".toml", ".cfg", ".ini", ".sh"):
            from .widgets.editor import ScpiEditor
            widget = ScpiEditor(path)
            widget.run_requested.connect(self._run_script)
            widget.debug_requested.connect(self._debug_script)
        else:
            from .widgets.file_viewers import TextViewer
            widget = TextViewer(path)
        self._open_files[path] = widget
        self._work_area.add_widget(os.path.basename(path), widget)

    def _on_tab_closed_file(self, widget: QWidget) -> None:
        """Clean up _open_files when a file tab is closed."""
        for path, w in list(self._open_files.items()):
            if w is widget:
                if hasattr(w, "stop"):
                    w.stop()
                del self._open_files[path]
                return

    def _run_script(self, path: str) -> None:
        """Run a .scpi script."""
        self._exec_script(path, debug=False)

    def _debug_script(self, path: str) -> None:
        """Debug a .scpi script."""
        self._exec_script(path, debug=True)

    def _exec_script(self, path: str, debug: bool = False) -> None:
        """Load and execute a script file. Dispatches .scpi vs .py."""
        name = os.path.basename(path)
        ext = os.path.splitext(path)[1].lower()
        mode = "debug" if debug else "run"
        self._console.log_action(f"script {mode} {name}", f"Running {name}...")

        if ext == ".py":
            output = self._d.run(f"python {path}")
            if output.strip():
                from .core.helpers import _ansi_to_html
                self._console.log(_ansi_to_html(output))
            self._console.log(f"<span style='color:#155724'>[DONE] {name}</span>")
            self._on_console_command()
            return

        # .scpi files
        try:
            with open(path, encoding="utf-8") as f:
                raw_lines = f.read().splitlines()
        except Exception as exc:
            self._console.log(f"<span style='color:#c0392b'>[ERROR] Cannot read {path}: {exc}</span>")
            return

        try:
            from lab_instruments.repl.script_engine.expander import expand_script_lines
            expanded = expand_script_lines(raw_lines, {}, self._d._repl.ctx)
        except Exception as exc:
            self._console.log(f"<span style='color:#c0392b'>[ERROR] Expansion failed: {exc}</span>")
            return

        # Separate commands and source display strings
        lines = [cmd for cmd, _ in expanded]
        source_lines = [src for _, src in expanded]

        # Collect breakpoints from __BREAKPOINT__ markers
        breakpoints: set[int] = set()
        clean_lines = []
        clean_sources = []
        for i, (cmd, src) in enumerate(zip(lines, source_lines)):
            if cmd == "__BREAKPOINT__":
                breakpoints.add(len(clean_lines) + 1)
            else:
                clean_lines.append(cmd)
                clean_sources.append(src)

        if debug:
            # Also collect breakpoints set in the editor gutter
            editor = self._open_files.get(path)
            if not editor:
                self.open_file(path)
                editor = self._open_files.get(path)
            if editor and hasattr(editor, "start_debug"):
                # Merge gutter breakpoints with script breakpoints
                if hasattr(editor, "editor") and hasattr(editor.editor(), "_breakpoints"):
                    breakpoints |= editor.editor()._breakpoints
                editor.start_debug(clean_lines, clean_sources, breakpoints)
                return

        # Normal run (not debug)
        try:
            import io
            from lab_instruments.repl.script_engine.runner import run_expanded

            buf = io.StringIO()
            old_stdout = self._d._repl.stdout
            self._d._repl.stdout = buf
            with contextlib.redirect_stdout(buf):
                run_expanded(expanded, self._d._repl, self._d._repl.ctx, debug=False)
            self._d._repl.stdout = old_stdout

            output = buf.getvalue()
            if output.strip():
                from .core.helpers import _ansi_to_html
                self._console.log(_ansi_to_html(output))
            self._console.log(f"<span style='color:#155724'>[DONE] {name}</span>")
        except Exception as exc:
            self._console.log(f"<span style='color:#c0392b'>[ERROR] {exc}</span>")

        self._on_console_command()

    # -- Keybind handlers ----------------------------------------------------

    def _current_editor(self):
        """Return the currently focused ScpiEditor, or None."""
        from .widgets.editor import ScpiEditor
        for group in self._work_area.all_groups():
            idx = group._strip._current if hasattr(group, "_strip") else -1
            if 0 <= idx < len(group._widgets):
                _, w = group._widgets[idx]
                if isinstance(w, ScpiEditor):
                    return w
        return None

    def _save_current(self) -> None:
        ed = self._current_editor()
        if ed and ed.save():
            self._status.setText(f"Saved: {ed.file_path()}")

    def _close_current_tab(self) -> None:
        for group in self._work_area.all_groups():
            if group._strip._current >= 0 and group._strip.count() > 0:
                group.close_tab(group._strip._current)
                return

    def _goto_line(self) -> None:
        ed = self._current_editor()
        if not ed:
            return
        from PySide6.QtWidgets import QInputDialog
        line, ok = QInputDialog.getInt(self, "Go to Line", "Line number:", 1, 1, 999999)
        if ok:
            ed.goto_line(line)

    def _run_current_script(self, debug: bool = False) -> None:
        ed = self._current_editor()
        if ed and ed.file_path() and ed.file_path().endswith(".scpi"):
            if debug:
                self._debug_script(ed.file_path())
            else:
                self._run_script(ed.file_path())

    def _show_palette(self) -> None:
        actions = [
            ActionItem("open_folder", "Open Folder", "Ctrl+Shift+O", self._on_open_folder, "File"),
            ActionItem("save", "Save", "Ctrl+S", self._save_current, "File"),
            ActionItem("close_tab", "Close Tab", "Ctrl+W", self._close_current_tab, "File"),
            ActionItem("goto_line", "Go to Line", "Ctrl+G", self._goto_line, "Go"),
            ActionItem("run_script", "Run Script", "F5", lambda: self._run_current_script(False), "Script"),
            ActionItem("debug_script", "Debug Script", "Shift+F5", lambda: self._run_current_script(True), "Script"),
            ActionItem("scan", "Scan Devices", "Ctrl+Shift+S", self._on_scan, "Instruments"),
            ActionItem("estop", "Emergency Stop", "", self._on_estop, "Instruments"),
        ]
        self._palette.show_palette(actions)

    def _quick_open(self) -> None:
        """Ctrl+P \u2014 quick file open from workspace."""
        if not self._workspace.folder:
            return
        import glob
        files = glob.glob(os.path.join(self._workspace.folder, "**", "*"), recursive=True)
        files = [f for f in files if os.path.isfile(f)]
        actions = []
        for f in sorted(files)[:500]:
            rel = os.path.relpath(f, self._workspace.folder)
            actions.append(ActionItem(f"file:{f}", rel, "", lambda p=f: self.open_file(p), ""))
        self._palette.show_palette(actions)

    # -- Pop-out windows -------------------------------------------------------

    def pop_out_widget(self, title: str, widget: QWidget) -> None:
        """Detach a widget from the work area into a floating window."""
        # Remove from work area first
        self._work_area.remove_widget(widget)
        # Create floating window
        win = QMainWindow(self)
        win.setWindowTitle(f"{title} \u2014 SCPI Toolkit")
        win.setCentralWidget(widget)
        win.resize(600, 500)
        win.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self._floating_windows.append(win)

        def _on_close(event, w=win, wdg=widget, t=title):
            # Re-dock into work area when floating window is closed
            w.setCentralWidget(None)
            self._work_area.add_widget(t, wdg)
            self._floating_windows.remove(w)
            event.accept()

        win.closeEvent = _on_close
        win.show()

    # -- Panel refresh helpers -----------------------------------------------

    def _refresh_psu_panels(self) -> None:
        psus = self._d.devices_of_type("psu")
        names = {name for name, _ in psus}
        for name in list(self._psu_blocks.keys()):
            if name not in names:
                block = self._psu_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._psu_closed.discard(name)
        for name, disp in psus:
            if name not in self._psu_blocks:
                block = _PSUBlock(self._d, name)
                block.stop()
                self._psu_blocks[name] = block
                self._psu_closed.add(name)

    def _refresh_smu_panels(self) -> None:
        smus = self._d.devices_of_type("smu")
        names = {name for name, _ in smus}
        for name in list(self._smu_blocks.keys()):
            if name not in names:
                block = self._smu_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._smu_closed.discard(name)
        for name, _ in smus:
            if name not in self._smu_blocks:
                block = _SMUBlock(self._d, name)
                block.stop()
                self._smu_blocks[name] = block
                self._smu_closed.add(name)

    def _refresh_awg_panels(self) -> None:
        awgs = self._d.devices_of_type("awg")
        names = {name for name, _ in awgs}
        for name in list(self._awg_blocks.keys()):
            if name not in names:
                block = self._awg_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._awg_closed.discard(name)
        for name, _ in awgs:
            if name not in self._awg_blocks:
                block = _AWGBlock(self._d, name)
                block.stop()
                self._awg_blocks[name] = block
                self._awg_closed.add(name)

    def _refresh_dmm_panels(self) -> None:
        dmms = self._d.devices_of_type("dmm")
        names = {name for name, _ in dmms}
        for name in list(self._dmm_blocks.keys()):
            if name not in names:
                block = self._dmm_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._dmm_closed.discard(name)
        for name, _ in dmms:
            if name not in self._dmm_blocks:
                block = _DMMBlock(self._d, name)
                block.stop()
                self._dmm_blocks[name] = block
                self._dmm_closed.add(name)

    def _refresh_ev_panels(self) -> None:
        evs = [(n, d) for n, d in self._d.registry.devices.items() if n == "ev2300" or n.startswith("ev2300_")]
        names = {name for name, _ in evs}
        for name in list(self._ev_blocks.keys()):
            if name not in names:
                block = self._ev_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._ev_closed.discard(name)
        for name, _ in evs:
            if name not in self._ev_blocks:
                block = _BQEvalBlock(self._d, name)
                block.stop()
                self._ev_blocks[name] = block
                self._ev_closed.add(name)

    def _refresh_scope_panels(self) -> None:
        scopes = self._d.devices_of_type("scope")
        names = {name for name, _ in scopes}
        for name in list(self._scope_blocks.keys()):
            if name not in names:
                block = self._scope_blocks.pop(name)
                block.stop()
                self._work_area.remove_widget(block)
                self._scope_closed.discard(name)
        for name, _ in scopes:
            if name not in self._scope_blocks:
                block = _ScopeBlock(self._d, name)
                block.stop()
                self._scope_blocks[name] = block
                self._scope_closed.add(name)

    # -- Lifecycle -----------------------------------------------------------

    def _init(self) -> None:
        # Prompt for folder on first launch (no previous workspace)
        if not self._workspace.folder:
            folder = QFileDialog.getExistingDirectory(
                self, "Select a Workspace Folder to Get Started"
            )
            if folder:
                self._workspace.folder = folder
                Workspace.save_last_folder(folder)
                self._file_explorer.set_root(folder)

        self._d._repl._general.safe_all()
        self._device_panel.refresh()
        self._refresh_psu_panels()
        self._refresh_smu_panels()
        self._refresh_awg_panels()
        self._refresh_dmm_panels()
        self._refresh_ev_panels()
        self._refresh_scope_panels()
        n = len(self._d.registry.devices)
        self._dev_count.setText(f"Devices: {n}")
        self._status.setText(f"{n} device(s) \u2014 all outputs safe")

    def _on_tab_closed(self, widget: QWidget) -> None:
        # Check instrument blocks
        for blocks, closed in [
            (self._psu_blocks, self._psu_closed),
            (self._smu_blocks, self._smu_closed),
            (self._awg_blocks, self._awg_closed),
            (self._dmm_blocks, self._dmm_closed),
            (self._ev_blocks, self._ev_closed),
            (self._scope_blocks, self._scope_closed),
        ]:
            for name, block in blocks.items():
                if block is widget:
                    block.stop()
                    closed.add(name)
                    return
        # Check open files
        self._on_tab_closed_file(widget)

    def _on_device_selected(self, name: str) -> None:
        base = re.sub(r"\d+$", "", name)
        block_map = {
            "psu": (self._psu_blocks, self._psu_closed),
            "smu": (self._smu_blocks, self._smu_closed),
            "awg": (self._awg_blocks, self._awg_closed),
            "dmm": (self._dmm_blocks, self._dmm_closed),
            "scope": (self._scope_blocks, self._scope_closed),
        }
        entry = block_map.get(base)
        if entry is None and (name == "ev2300" or name.startswith("ev2300_")):
            entry = (self._ev_blocks, self._ev_closed)
        if entry is None:
            return
        blocks, closed = entry
        block = blocks.get(name)
        if not block:
            return
        for group in self._work_area.all_groups():
            for i, (_, w) in enumerate(group._widgets):
                if w is block:
                    group.set_current_tab(i)
                    return
        closed.discard(name)
        disp = self._d.registry.display_name(name)
        self._work_area.add_widget(disp or name, block)

    @Slot()
    def _on_console_command(self) -> None:
        """Refresh all instrument blocks immediately after any console command."""
        for blocks in [self._psu_blocks, self._smu_blocks, self._awg_blocks,
                       self._dmm_blocks, self._scope_blocks]:
            for block in blocks.values():
                block._poll()
        n = len(self._d.registry.devices)
        if n != int(self._dev_count.text().split(": ", 1)[-1]):
            self._refresh_psu_panels()
            self._refresh_smu_panels()
            self._refresh_awg_panels()
            self._refresh_dmm_panels()
            self._refresh_ev_panels()
            self._refresh_scope_panels()
            self._device_panel.refresh()
            self._dev_count.setText(f"Devices: {n}")

    def _after_scan(self) -> None:
        self._refresh_psu_panels()
        self._refresh_smu_panels()
        self._refresh_awg_panels()
        self._refresh_dmm_panels()
        self._refresh_ev_panels()
        self._refresh_scope_panels()
        self._device_panel.refresh()
        n = len(self._d.registry.devices)
        self._dev_count.setText(f"Devices: {n}")
        self._status.setText(f"Scan complete: {n} device(s)")

    def _on_scan(self) -> None:
        """Non-blocking scan using a background thread."""
        self._status.setText("Scanning...")

        def _do_scan():
            result = self._d.run("scan")
            self._d._repl._general.safe_all()
            return result

        def _scan_done(result):
            self._console.log_action("scan", result)
            self._device_panel.refresh()
            self._after_scan()

        self._run_in_background(_do_scan, _scan_done, "Scanning for instruments...")

    def _on_estop(self) -> None:
        self._d._repl._general.safe_all()
        self._console.log_action("safe_all", "All outputs disabled")
        self._status.setText("E-STOP: all outputs disabled")
        for blocks in [self._psu_blocks, self._smu_blocks, self._awg_blocks,
                       self._dmm_blocks, self._scope_blocks]:
            for block in blocks.values():
                block._poll()

    def closeEvent(self, event) -> None:  # noqa: N802
        s = QSettings("SCPIToolkit", "GUI")
        s.setValue("geometry", self.saveGeometry())
        s.setValue("state", self.saveState())
        for blocks in [self._psu_blocks, self._smu_blocks, self._awg_blocks,
                       self._dmm_blocks, self._ev_blocks, self._scope_blocks]:
            for block in blocks.values():
                with contextlib.suppress(Exception):
                    block.stop()
        # Close floating windows
        for win in list(self._floating_windows):
            win.close()
        super().closeEvent(event)


# -- Entry point -------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="SCPI Instrument Toolkit GUI")
    parser.add_argument("--mock", action="store_true", help="Use mock instruments")
    args = parser.parse_args(argv)

    app = QApplication(sys.argv)
    app.setApplicationName("SCPI Instrument Toolkit")

    d = _Dispatcher(mock=args.mock)
    win = _MainWindow(d)
    win.resize(1400, 820)
    win.show()

    sys.exit(app.exec())
