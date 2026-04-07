"""SCPI Instrument Toolkit - Desktop GUI."""

from __future__ import annotations

import argparse
import contextlib
import glob
import io
import os
import re
import sys
import threading

from PySide6.QtCore import QObject, QSettings, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QWidget,
)

from lab_instruments.repl.script_engine.expander import expand_script_lines
from lab_instruments.repl.script_engine.runner import run_expanded

from .core.dispatcher import _Dispatcher
from .core.helpers import _ansi_to_html, _esc
from .core.workspace import Workspace
from .dialogs.command_palette import ActionItem, CommandPalette
from .instrument_blocks.awg_block import _AWGBlock
from .instrument_blocks.bq_eval_block import _BQEvalBlock
from .instrument_blocks.dmm_block import _DMMBlock
from .instrument_blocks.psu_block import _PSUBlock
from .instrument_blocks.scope_block import _ScopeBlock
from .instrument_blocks.smu_block import _SMUBlock
from .panels.device_panel import _DevicePanel
from .panels.file_explorer import FileExplorer
from .widgets.console import _Console
from .widgets.docs_viewer import DocsViewer
from .widgets.editor import ScpiEditor
from .widgets.file_viewers import (
    CsvViewer,
    DocxViewer,
    ImageViewer,
    PdfViewer,
    PptxViewer,
    TextViewer,
    XlsxViewer,
    _OfficeViewerBase,
    preconvert_office_files,
)
from .widgets.work_area import _WorkArea

# -- Background worker for blocking operations --------------------------------


class _BgSignal(QObject):
    """Bridge to deliver a background thread result to the main Qt thread."""

    finished = Signal(str)


def _run_bg(fn, signal):
    """Target for threading.Thread: run *fn* and emit result via *signal*."""
    try:
        result = fn()
        signal.finished.emit(result or "")
    except Exception as exc:
        signal.finished.emit(f"[ERROR] {exc}")


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
        self._docs_tabs: dict[str, QWidget] = {}
        self._last_device_count: int = 0
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

        # ── Examples menu ─────────────────────────────────────────────
        em = mb.addMenu("&Examples")
        try:
            from lab_instruments.examples import EXAMPLES as _EXAMPLES

            scpi_menu = em.addMenu("SCPI Scripts")
            py_menu = em.addMenu("Python Scripts")
            for ex_name, ex_info in _EXAMPLES.items():
                is_python = ex_info.get("type") == "python"
                display = ex_name
                desc = ex_info.get("description", "").removeprefix("Python: ")
                act = QAction(f"{display}  —  {desc}", self)
                act.triggered.connect(lambda checked, n=ex_name: self._import_example(n))
                (py_menu if is_python else scpi_menu).addAction(act)
        except ImportError:
            na = QAction("(no examples available)", self)
            na.setEnabled(False)
            em.addAction(na)

        # ── Viewer menu ───────────────────────────────────────────────
        vm = mb.addMenu("&Viewer")

        def _va(label: str, shortcut: str | None, fn) -> QAction:
            a = QAction(label, self)
            if shortcut:
                a.setShortcut(shortcut)
            a.triggered.connect(fn)
            return a

        vm.addSection("Navigation  (PDF / DOCX / PPTX)")
        self._vm_prev = _va("Previous Page", "Left", lambda: self._viewer_call("_prev"))
        self._vm_next = _va("Next Page", "Right", lambda: self._viewer_call("_next"))
        self._vm_first = _va("First Page", "Home", lambda: self._viewer_call("_go_to", 0))
        vm.addAction(self._vm_prev)
        vm.addAction(self._vm_next)
        vm.addAction(self._vm_first)

        vm.addSeparator()
        vm.addSection("Zoom  (PDF / DOCX / PPTX / Image)")
        self._vm_zoom_in = _va("Zoom In", "=", self._viewer_zoom_in)
        self._vm_zoom_out = _va("Zoom Out", "-", self._viewer_zoom_out)
        self._vm_fit_w = _va("Fit Width  [W]", None, lambda: self._viewer_call("_fit_width"))
        self._vm_fit_h = _va("Fit Height  [H]", None, lambda: self._viewer_call("_fit_height"))
        self._vm_fit = _va("Fit  [F]", None, lambda: self._viewer_call("_zoom", 0))
        vm.addAction(self._vm_zoom_in)
        vm.addAction(self._vm_zoom_out)
        vm.addAction(self._vm_fit_w)
        vm.addAction(self._vm_fit_h)
        vm.addAction(self._vm_fit)

        vm.addSeparator()
        vm.addSection("Search")
        self._vm_find = _va("Find…  Ctrl+F", None, self._viewer_find)
        self._vm_replace = _va("Find && Replace…  Ctrl+H", None, self._viewer_find_replace)
        vm.addAction(self._vm_find)
        vm.addAction(self._vm_replace)

        vm.aboutToShow.connect(self._update_viewer_menu)

        # ── Help menu ─────────────────────────────────────────────────
        hm = mb.addMenu("&Help")
        _pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        _repl_docs = os.path.join(_pkg_root, "site")
        ra = QAction("Documentation", self)
        ra.triggered.connect(lambda: self._open_docs(_repl_docs, "Docs"))
        hm.addAction(ra)

        # ── Toolbar ───────────────────────────────────────────────────
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.setObjectName("main_toolbar")
        tb.toggleViewAction().setVisible(False)  # hide from right-click context menu
        tb.addAction(sa)

        et = QAction("\u26a1 E-STOP", self)
        et.triggered.connect(self._on_estop)
        tb.addAction(et)
        # ── Status bar ────────────────────────────────────────────────
        self._status = QLabel("Ready")
        self.statusBar().addWidget(self._status, 1)
        self._dev_count = QLabel("")
        self.statusBar().addPermanentWidget(self._dev_count)

        # ── Work area (central widget) ─────────────────────────────────
        self._work_area = _WorkArea()
        self.setCentralWidget(self._work_area)

        # ── Console dock (bottom) ──────────────────────────────────────
        self._console = _Console(d)
        _console_dock = QDockWidget("Console", self)
        _console_dock.setObjectName("ConsoleDock")
        _console_dock.setWidget(self._console)
        _console_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, _console_dock)
        self._view_menu.addAction(_console_dock.toggleViewAction())

        # ── Device list dock (left) ────────────────────────────────────
        self._device_panel = _DevicePanel(d, self)
        _devices_dock = QDockWidget("Devices", self)
        _devices_dock.setObjectName("DevicesDock")
        _devices_dock.setWidget(self._device_panel)
        _devices_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, _devices_dock)
        self._view_menu.addAction(_devices_dock.toggleViewAction())

        # ── File explorer dock (left, tabbed with devices) ─────────────
        self._file_explorer = FileExplorer()
        self._file_explorer.file_selected.connect(self.open_file)
        self._file_explorer.run_script.connect(self._run_script)
        self._file_explorer.debug_script.connect(self._debug_script)
        _explorer_dock = QDockWidget("Explorer", self)
        _explorer_dock.setObjectName("ExplorerDock")
        _explorer_dock.setWidget(self._file_explorer)
        _explorer_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, _explorer_dock)
        self.tabifyDockWidget(_devices_dock, _explorer_dock)
        _devices_dock.raise_()
        self._view_menu.addAction(_explorer_dock.toggleViewAction())

        self._preconvert_worker = None
        if self._workspace.folder:
            self._file_explorer.set_root(self._workspace.folder)
            self._preconvert_worker = preconvert_office_files(self._workspace.folder)

        self._console.command_ran.connect(self._on_console_command)

        # ── Command palette ────────────────────────────────────────────
        self._palette = CommandPalette(self)

        # ── VS Code keybinds ───────────────────────────────────────────
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
        """Run *fn* on a background thread. Calls *on_done(result_str)* on the main thread."""
        self._status.setText(status_msg)

        sig = _BgSignal(self)  # parent=self keeps it alive

        def _on_finished(result):
            if on_done:
                on_done(result)
            sig.deleteLater()

        sig.finished.connect(_on_finished, Qt.ConnectionType.QueuedConnection)
        t = threading.Thread(target=_run_bg, args=(fn, sig), daemon=True)
        t.start()

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
            self, "Open File", self._workspace.folder or "", "SCPI Scripts (*.scpi);;Python Files (*.py);;All Files (*)"
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

    def _import_example(self, name: str) -> None:
        """Copy a bundled example to the workspace examples/ folder and open it."""
        from lab_instruments.examples import EXAMPLES

        info = EXAMPLES.get(name)
        if not info:
            self._status.setText(f"Example '{name}' not found")
            return
        folder = self._workspace.folder
        if not folder:
            folder = os.path.expanduser("~")
        is_python = info.get("type") == "python"
        subdir = "python" if is_python else "scpi"
        ext = ".py" if is_python else ".scpi"
        examples_dir = os.path.join(folder, "examples", subdir)
        os.makedirs(examples_dir, exist_ok=True)
        path = os.path.join(examples_dir, f"{name}{ext}")
        if os.path.exists(path):
            reply = QMessageBox.question(
                self,
                "Replace example?",
                f"{os.path.basename(path)} already exists in your workspace.\n\n"
                "Replace it with the bundled version? Your changes will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                self.open_file(path)
                return
        with open(path, "w", encoding="utf-8") as f:
            if is_python:
                f.write(info.get("code", ""))
            else:
                f.write("\n".join(info.get("lines", [])) + "\n")
        self._file_explorer.set_root(folder)
        self._status.setText(f"Imported example: {name}")
        self.open_file(path)

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
            widget = ImageViewer(path)
        elif ext == ".csv":
            widget = CsvViewer(path)
        elif ext == ".pdf":
            widget = PdfViewer(path)
        elif ext in (".docx", ".doc"):
            widget = DocxViewer(path)
        elif ext == ".xlsx":
            widget = XlsxViewer(path)
        elif ext == ".pptx":
            widget = PptxViewer(path)
        elif ext in (".scpi", ".py", ".txt", ".md", ".json", ".toml", ".cfg", ".ini", ".sh"):
            widget = ScpiEditor(path)
            widget.run_requested.connect(self._run_script)
            widget.debug_requested.connect(self._debug_script)
        else:
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

    def _open_docs(self, site_dir: str, tab_title: str) -> None:
        """Open a DocsViewer tab; focus it if already open."""
        if tab_title in self._docs_tabs:
            widget = self._docs_tabs[tab_title]
            for group in self._work_area.all_groups():
                for i, (_, w) in enumerate(group._widgets):
                    if w is widget:
                        group.set_current_tab(i)
                        return
        viewer = DocsViewer(site_dir)
        self._docs_tabs[tab_title] = viewer
        self._work_area.add_widget(tab_title, viewer)

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
            self._console._input.setEnabled(False)

            def _py_done(output):
                if output.strip():
                    self._console.log(_ansi_to_html(output))
                self._console.log(f"<span style='color:#155724'>[DONE] {name}</span>")
                self._console._input.setEnabled(True)
                self._on_console_command()

            self._run_in_background(lambda: self._d.run(f"python {path}"), _py_done, f"Running {name}...")
            return

        # .scpi files
        try:
            with open(path, encoding="utf-8") as f:
                raw_lines = f.read().splitlines()
        except Exception as exc:
            self._console.log(f"<span style='color:#c0392b'>[ERROR] Cannot read {path}: {exc}</span>")
            return

        try:
            expand_buf = io.StringIO()
            with contextlib.redirect_stdout(expand_buf):
                expanded = expand_script_lines(raw_lines, {}, self._d._repl.ctx)
            expand_output = expand_buf.getvalue().strip()
            if expand_output:
                self._console.log(_ansi_to_html(expand_output))
        except Exception as exc:
            self._console.log(f"<span style='color:#c0392b'>[ERROR] Expansion failed: {exc}</span>")
            return

        # Separate commands and source display strings
        lines = [cmd for cmd, _ in expanded]
        source_lines = [src for _, src in expanded]

        # Convert __BREAKPOINT__ markers to __NOP__ and record their 1-indexed positions
        breakpoints: set[int] = set()
        for i, cmd in enumerate(lines):
            if cmd == "__BREAKPOINT__":
                breakpoints.add(i + 1)  # 1-indexed (matches editor line numbers)
                lines[i] = "__NOP__"

        if debug:
            # Merge gutter breakpoints (already 1-indexed editor line numbers)
            editor = self._open_files.get(path)
            if not editor:
                self.open_file(path)
                editor = self._open_files.get(path)
            if editor and hasattr(editor, "start_debug"):
                if hasattr(editor, "editor") and hasattr(editor.editor(), "_breakpoints"):
                    breakpoints |= editor.editor()._breakpoints
                editor.start_debug(lines, source_lines, breakpoints)
                return

        # Normal run (not debug) — run each command and stream output to console
        run_cmds = [cmd for cmd, _ in expanded if cmd.strip() and cmd != "__BREAKPOINT__" and cmd != "__NOP__"]
        self._console._input.setEnabled(False)

        def _run_all():
            output_parts = []
            for cmd in run_cmds:
                result = self._d.run(cmd)
                if result.strip():
                    output_parts.append(result.rstrip("\n"))
                    # Emit output to console via signal (thread-safe)
                    _sig.finished.emit(result.rstrip("\n"))
                # Stop on error if set -e is active
                if self._d._repl.ctx.exit_on_error and self._d._repl.ctx.command_had_error:
                    _sig.finished.emit("[ERROR] Script stopped (set -e)")
                    break
            return ""

        def _line_output(text):
            if text:
                self._console.log(_ansi_to_html(text))

        def _all_done(_):
            self._console.log(f"<span style='color:#155724'>[DONE] {name}</span>")
            self._console._input.setEnabled(True)
            self._on_console_command()

        _sig = _BgSignal(self)
        _done_sig = _BgSignal(self)
        _sig.finished.connect(_line_output, Qt.ConnectionType.QueuedConnection)
        _done_sig.finished.connect(_all_done, Qt.ConnectionType.QueuedConnection)

        import threading

        def _worker():
            _run_all()
            _done_sig.finished.emit("")

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        self._status.setText(f"Running {name}...")

    # -- Keybind handlers ----------------------------------------------------

    def _current_editor(self):
        """Return the currently focused ScpiEditor, or None."""
        for group in self._work_area.all_groups():
            idx = group._tab_strip._current if hasattr(group, "_tab_strip") else -1
            if 0 <= idx < len(group._widgets):
                _, w = group._widgets[idx]
                if isinstance(w, ScpiEditor):
                    return w
        return None

    def _save_current(self) -> None:
        ed = self._current_editor()
        if ed and ed.save():
            self._status.setText(f"Saved: {ed.file_path()}")

    # ── Viewer dispatch helpers ────────────────────────────────────────────────

    def _focused_viewer(self):
        """Walk focus chain to find the innermost known viewer widget."""
        _types = (PdfViewer, _OfficeViewerBase, ImageViewer, TextViewer, CsvViewer, XlsxViewer, ScpiEditor)
        w = QApplication.focusWidget()
        while w:
            if isinstance(w, _types):
                return w
            w = w.parent()
        return None

    def _update_viewer_menu(self) -> None:
        """Enable/disable Viewer menu actions based on the focused viewer type."""
        v = self._focused_viewer()
        is_paged = isinstance(v, (PdfViewer, _OfficeViewerBase))
        is_zoomable = isinstance(v, (PdfViewer, _OfficeViewerBase, ImageViewer))
        has_fit_wh = isinstance(v, (PdfViewer, _OfficeViewerBase))
        has_fit = isinstance(v, ImageViewer)
        has_find = isinstance(v, (TextViewer, ScpiEditor, CsvViewer, XlsxViewer))
        has_replace = isinstance(v, (TextViewer, ScpiEditor))

        self._vm_prev.setEnabled(is_paged)
        self._vm_next.setEnabled(is_paged)
        self._vm_first.setEnabled(is_paged)
        self._vm_zoom_in.setEnabled(is_zoomable)
        self._vm_zoom_out.setEnabled(is_zoomable)
        self._vm_fit_w.setEnabled(has_fit_wh)
        self._vm_fit_h.setEnabled(has_fit_wh)
        self._vm_fit.setEnabled(has_fit)
        self._vm_find.setEnabled(has_find)
        self._vm_replace.setEnabled(has_replace)

    def _viewer_call(self, method: str, *args) -> None:
        v = self._focused_viewer()
        if v and hasattr(v, method):
            getattr(v, method)(*args)

    def _viewer_zoom_in(self) -> None:
        v = self._focused_viewer()
        if isinstance(v, (PdfViewer, _OfficeViewerBase)):
            v._zoom_by(1.25)
        elif isinstance(v, ImageViewer):
            v._zoom(0.25)

    def _viewer_zoom_out(self) -> None:
        v = self._focused_viewer()
        if isinstance(v, (PdfViewer, _OfficeViewerBase)):
            v._zoom_by(1 / 1.25)
        elif isinstance(v, ImageViewer):
            v._zoom(-0.25)

    def _viewer_find(self) -> None:
        v = self._focused_viewer()
        if isinstance(v, (TextViewer, ScpiEditor)):
            v._find_bar.open_find()
        elif isinstance(v, (CsvViewer, XlsxViewer)):
            v._find_bar.open()

    def _viewer_find_replace(self) -> None:
        v = self._focused_viewer()
        if isinstance(v, (TextViewer, ScpiEditor)):
            v._find_bar.open_replace()

    def _close_current_tab(self) -> None:
        for group in self._work_area.all_groups():
            if hasattr(group, "_tab_strip") and group._tab_strip._current >= 0 and group._tab_strip.count() > 0:
                group.close_tab(group._tab_strip._current)
                return

    def _goto_line(self) -> None:
        ed = self._current_editor()
        if not ed:
            return
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
        files = glob.glob(os.path.join(self._workspace.folder, "**", "*"), recursive=True)
        files = [f for f in files if os.path.isfile(f)]
        actions = []
        for f in sorted(files)[:500]:
            rel = os.path.relpath(f, self._workspace.folder)
            actions.append(ActionItem(f"file:{f}", rel, "", lambda p=f: self.open_file(p), ""))
        self._palette.show_palette(actions)

    # -- Pop-out windows -------------------------------------------------------

    def pop_out_widget(self, title: str, widget: QWidget) -> None:
        """Detach a widget into a floating QDockWidget (draggable back in)."""
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock.setFloating(True)
        dock.resize(700, 550)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        self._floating_windows.append(dock)

        def _on_close():
            widget_ref = dock.widget()
            if widget_ref is not None:
                dock.setWidget(None)
                self._work_area.add_widget(title, widget_ref)
            if dock in self._floating_windows:
                self._floating_windows.remove(dock)

        dock.visibilityChanged.connect(lambda vis: None if vis else QTimer.singleShot(0, _on_close))

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
        for name, _disp in psus:
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
            folder = QFileDialog.getExistingDirectory(self, "Select a Workspace Folder to Get Started")
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
        if n > 0:
            label = "device" if n == 1 else "devices"
            self._dev_count.setText(f"Devices: {n}")
            self._status.setText(f"{n} {label} \u2014 all outputs safe")
        else:
            self._dev_count.setText("Scanning...")
            self._status.setText("Scanning for instruments...")

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
        base = self._d.registry.base_type(name)
        block_map = {
            "psu": (self._psu_blocks, self._psu_closed),
            "smu": (self._smu_blocks, self._smu_closed),
            "awg": (self._awg_blocks, self._awg_closed),
            "dmm": (self._dmm_blocks, self._dmm_closed),
            "scope": (self._scope_blocks, self._scope_closed),
            "ev2300": (self._ev_blocks, self._ev_closed),
        }
        entry = block_map.get(base)
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
        """Refresh all instrument blocks after any console command."""
        # Skip entirely if a background op (scan, script) is running to avoid racing on hardware
        if self._d.is_busy():
            return
        for blocks in [self._psu_blocks, self._smu_blocks, self._awg_blocks, self._dmm_blocks, self._scope_blocks]:
            for block in blocks.values():
                block._poll()
        n = len(self._d.registry.devices)
        if n != self._last_device_count:
            self._last_device_count = n
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
        # Auto-open any newly detected instrument blocks
        self._auto_open_blocks()
        n = len(self._d.registry.devices)
        self._dev_count.setText(f"Devices: {n}")
        label = "device" if n == 1 else "devices"
        self._status.setText(f"Scan complete: {n} {label}")

    def _auto_open_blocks(self) -> None:
        """Open instrument blocks that are in the closed set (newly detected)."""
        for blocks, closed in [
            (self._psu_blocks, self._psu_closed),
            (self._smu_blocks, self._smu_closed),
            (self._awg_blocks, self._awg_closed),
            (self._dmm_blocks, self._dmm_closed),
            (self._ev_blocks, self._ev_closed),
            (self._scope_blocks, self._scope_closed),
        ]:
            for name in list(closed):
                block = blocks.get(name)
                if block:
                    disp = self._d.registry.display_name(name)
                    self._work_area.add_widget(disp or name, block)
                    closed.discard(name)

    def _on_scan(self) -> None:
        """Non-blocking scan. Disables all interactive controls while running."""
        self._status.setText("Scanning for instruments...")
        self._dev_count.setText("Scanning...")
        # Disable console and all instrument blocks to prevent lock contention
        self._console._input.setEnabled(False)
        self._device_panel._scan_btn.setEnabled(False)
        self._device_panel._force_scan_btn.setEnabled(False)
        for blocks in [
            self._psu_blocks,
            self._smu_blocks,
            self._awg_blocks,
            self._dmm_blocks,
            self._ev_blocks,
            self._scope_blocks,
        ]:
            for block in blocks.values():
                block.setEnabled(False)

        def _do_scan():
            return self._d.run("scan")

        def _scan_done(result):
            self._console._input.setEnabled(True)
            self._device_panel._scan_btn.setEnabled(True)
            self._device_panel._force_scan_btn.setEnabled(True)
            for blocks in [
                self._psu_blocks,
                self._smu_blocks,
                self._awg_blocks,
                self._dmm_blocks,
                self._ev_blocks,
                self._scope_blocks,
            ]:
                for block in blocks.values():
                    block.setEnabled(True)
            if result.startswith("[ERROR]"):
                self._status.setText("Scan failed")
                self._console.log(f"<span style='color:#c0392b'>{_esc(result)}</span>")
            else:
                self._console.log_action("scan", result)
                self._device_panel.refresh()
                self._after_scan()

        self._run_in_background(_do_scan, _scan_done, "Scanning for instruments...")

    def _on_force_scan(self) -> None:
        """Force rescan — disconnect all instruments and re-scan from scratch."""
        self._status.setText("Force rescanning...")
        self._dev_count.setText("Scanning...")
        self._console._input.setEnabled(False)
        self._device_panel._scan_btn.setEnabled(False)
        self._device_panel._force_scan_btn.setEnabled(False)
        for blocks in [
            self._psu_blocks,
            self._smu_blocks,
            self._awg_blocks,
            self._dmm_blocks,
            self._ev_blocks,
            self._scope_blocks,
        ]:
            for block in blocks.values():
                block.setEnabled(False)

        def _do_force_scan():
            return self._d.run("force_scan")

        def _force_scan_done(result):
            self._console._input.setEnabled(True)
            self._device_panel._scan_btn.setEnabled(True)
            self._device_panel._force_scan_btn.setEnabled(True)
            for blocks in [
                self._psu_blocks,
                self._smu_blocks,
                self._awg_blocks,
                self._dmm_blocks,
                self._ev_blocks,
                self._scope_blocks,
            ]:
                for block in blocks.values():
                    block.setEnabled(True)
            if result.startswith("[ERROR]"):
                self._status.setText("Force rescan failed")
                self._console.log(f"<span style='color:#c0392b'>{_esc(result)}</span>")
            else:
                self._console.log_action("force_scan", result)
                self._device_panel.refresh()
                self._after_scan()

        self._run_in_background(_do_force_scan, _force_scan_done, "Force rescanning (resetting all outputs)...")

    def _on_estop(self) -> None:
        # Route through dispatcher so the lock is respected
        self._d.run("state safe")
        self._console.log_action("safe_all", "All outputs disabled")
        self._status.setText("E-STOP: all outputs disabled")
        # Defer poll briefly — safe_all just released the lock and instruments need a moment
        if not self._d.is_busy():
            for blocks in [self._psu_blocks, self._smu_blocks, self._awg_blocks, self._dmm_blocks, self._scope_blocks]:
                for block in blocks.values():
                    block._poll()

    def closeEvent(self, event) -> None:  # noqa: N802
        s = QSettings("SCPIToolkit", "GUI")
        s.setValue("geometry", self.saveGeometry())
        s.setValue("state", self.saveState())
        for blocks in [
            self._psu_blocks,
            self._smu_blocks,
            self._awg_blocks,
            self._dmm_blocks,
            self._ev_blocks,
            self._scope_blocks,
        ]:
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

    import signal

    # Suppress harmless Qt font database warnings on Windows
    os.environ.setdefault("QT_LOGGING_RULES", "qt.text.font.db=false")
    app = QApplication(sys.argv)
    app.setApplicationName("SCPI Instrument Toolkit")

    # Let Ctrl+C in the terminal kill the app
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    # Qt needs a timer to process Python signals
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(200)

    d = _Dispatcher(mock=args.mock)
    win = _MainWindow(d)
    win.resize(1400, 820)
    win.show()

    # Kick off an initial scan after the window is visible
    if not args.mock:
        QTimer.singleShot(100, win._on_scan)

    sys.exit(app.exec())
