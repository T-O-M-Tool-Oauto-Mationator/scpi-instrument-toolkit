from __future__ import annotations

import contextlib
import ctypes
import re
import threading

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.dispatcher import _Dispatcher
from ..core.helpers import _ansi_to_html, _esc, _mono


def _force_kill_thread(thread_id: int) -> bool:
    """Raise KeyboardInterrupt in a thread to force-stop it."""
    if thread_id is None:
        return False
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_ulong(thread_id),
        ctypes.py_object(KeyboardInterrupt),
    )
    return res == 1


class _Console(QWidget):
    command_ran = Signal()  # emitted after every non-clear command

    def __init__(self, d: _Dispatcher, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._history: list[str] = []
        self._hist_idx = -1
        self._worker_thread_id: int | None = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(_mono())
        self._output.document().setMaximumBlockCount(5000)
        lay.addWidget(self._output, 1)

        ctrl_row = QHBoxLayout()
        ctrl_row.setContentsMargins(0, 0, 0, 0)
        self._autoscroll = QCheckBox("Autoscroll")
        self._autoscroll.setChecked(True)
        self._autoscroll.setFont(_mono(9))
        ctrl_row.addWidget(self._autoscroll)
        clear_btn = QPushButton("Clear")
        clear_btn.setFont(_mono(9))
        clear_btn.setFixedWidth(50)
        clear_btn.clicked.connect(self._output.clear)
        ctrl_row.addWidget(clear_btn)
        ctrl_row.addStretch()
        lay.addLayout(ctrl_row)

        # -- Running banner (hidden by default) -----------------------------
        self._run_bar = QWidget()
        self._run_bar.setStyleSheet("background: #f38ba8; border-radius: 4px;")
        rb_lay = QHBoxLayout(self._run_bar)
        rb_lay.setContentsMargins(10, 6, 10, 6)
        self._run_label = QLabel("Running...")
        self._run_label.setStyleSheet("color: #1e1e2e; font-weight: bold; font-size: 13px;")
        self._run_label.setFont(_mono(12))
        rb_lay.addWidget(self._run_label)
        rb_lay.addStretch()
        self._stop_btn = QPushButton("STOP")
        self._stop_btn.setFont(_mono(11))
        self._stop_btn.setStyleSheet(
            "QPushButton { background: #1e1e2e; color: #f38ba8; border: 2px solid #1e1e2e;"
            " border-radius: 4px; padding: 4px 16px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background: #313244; }"
        )
        self._stop_btn.clicked.connect(self._on_stop)
        rb_lay.addWidget(self._stop_btn)
        self._run_bar.setVisible(False)
        lay.addWidget(self._run_bar)

        row = QHBoxLayout()
        lbl = QLabel("eset>")
        lbl.setFont(_mono())
        lbl.setStyleSheet("color: #1a6bbf;")
        row.addWidget(lbl)
        self._input = QLineEdit()
        self._input.setFont(_mono())
        self._input.setPlaceholderText("Type a command...")
        self._input.returnPressed.connect(self._on_submit)
        row.addWidget(self._input, 1)
        lay.addLayout(row)

    def show_running(self, name: str = "") -> None:
        """Show the running banner with a STOP button."""
        self._run_label.setText(f"Running {name}..." if name else "Running...")
        self._run_bar.setVisible(True)

    def hide_running(self) -> None:
        """Hide the running banner."""
        self._run_bar.setVisible(False)
        self._stop_btn.setEnabled(True)

    def _on_stop(self) -> None:
        """Kill the running command immediately and safe all outputs."""
        # 1. Set the cooperative flag (stops sleeps, loops)
        self._d._repl.ctx.interrupt_requested = True

        # 2. Force-raise KeyboardInterrupt in the worker thread
        if self._worker_thread_id is not None:
            _force_kill_thread(self._worker_thread_id)

        # 3. Also kill any script threads started by _exec_script
        for t in threading.enumerate():
            if t.daemon and t.name.startswith("script_"):
                _force_kill_thread(t.ident)

        # 4. Safe all instrument outputs (E-STOP)
        with contextlib.suppress(Exception):
            self._d._repl._general.safe_all()

        self._run_label.setText("STOPPED — outputs safe")
        self.log(
            "<span style='color:#f38ba8; font-weight:bold'>"
            "[STOPPED] Execution killed. All outputs set to safe state.</span>"
        )

    def keyPressEvent(self, ev):  # noqa: N802
        if self._input.hasFocus():
            if ev.key() == Qt.Key.Key_Up:
                self._nav(1)
                return
            if ev.key() == Qt.Key.Key_Down:
                self._nav(-1)
                return
        super().keyPressEvent(ev)

    def _nav(self, d: int) -> None:
        if not self._history:
            return
        self._hist_idx = max(-1, min(len(self._history) - 1, self._hist_idx + d))
        self._input.setText("" if self._hist_idx == -1 else self._history[-(self._hist_idx + 1)])

    def _on_submit(self) -> None:
        cmd = self._input.text().strip()
        if not cmd:
            return
        self._history.append(cmd)
        if len(self._history) > 500:
            self._history = self._history[-500:]
        self._hist_idx = -1
        self._input.clear()
        if cmd == "clear":
            self._output.clear()
            return
        self.log(f"<b style='color:#1a6bbf'>eset&gt;</b> {_esc(cmd)}")
        # Run command in background thread to avoid blocking UI
        self._input.setEnabled(False)
        self.show_running(cmd.split()[0] if cmd else "")

        console = self

        class _CmdWorker(QThread):
            def __init__(self, d, command, parent=None):
                super().__init__(parent)
                self._d = d
                self._cmd = command
                self.result = ""

            def run(self):
                console._worker_thread_id = threading.current_thread().ident
                try:
                    self.result = self._d.run(self._cmd)
                except KeyboardInterrupt:
                    self.result = "\033[93m[STOPPED]\033[0m"
                finally:
                    console._worker_thread_id = None

        worker = _CmdWorker(self._d, cmd)

        def _done():
            if worker.result.strip():
                self.log(_ansi_to_html(worker.result.rstrip("\n")))
            self._input.setEnabled(True)
            self._input.setFocus()
            self.hide_running()
            self.command_ran.emit()

        worker.finished.connect(_done, Qt.ConnectionType.QueuedConnection)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def log(self, html: str) -> None:
        # Check for special markers before displaying.
        # _ansi_to_html converts \n to <br>, so split on both.
        lines = re.split(r"\n|<br\s*/?>", html)
        filtered = []
        for line in lines:
            # Strip HTML tags to check for markers in raw text
            plain = re.sub(r"<[^>]+>", "", line)
            if plain.strip().startswith("__PLOT__:"):
                path = plain.strip().split(":", 1)[1]
                self._handle_plot_marker(path)
                continue
            if plain.strip().startswith("__LIVEPLOT__:"):
                payload = plain.strip().split(":", 1)[1]
                # Format: patterns|title|xlabel|ylabel
                fields = payload.split("|")
                patterns = fields[0].split(",") if fields else ["*"]
                title = fields[1] if len(fields) > 1 and fields[1] else "Live Plot"
                xlabel = fields[2] if len(fields) > 2 else ""
                ylabel = fields[3] if len(fields) > 3 else ""
                self._handle_liveplot_marker(patterns, title, xlabel, ylabel)
                continue
            filtered.append(line)

        text = "<br>".join(filtered)
        if text.strip():
            self._output.append(f"<span>{text}</span>")
            if self._autoscroll.isChecked():
                self._output.moveCursor(QTextCursor.MoveOperation.End)
                self._output.ensureCursorVisible()

    def _handle_plot_marker(self, path: str) -> None:
        """Open a static plot image in a tab."""
        from PySide6.QtWidgets import QMainWindow

        w = self.parent()
        while w:
            if isinstance(w, QMainWindow) and hasattr(w, "open_file"):
                w.open_file(path)
                return
            w = w.parent() if hasattr(w, "parent") else None

    def _handle_liveplot_marker(self, patterns: list[str], title: str, xlabel: str = "", ylabel: str = "") -> None:
        """Open a live plot widget in a tab."""
        from PySide6.QtWidgets import QMainWindow

        w = self.parent()
        while w:
            if isinstance(w, QMainWindow) and hasattr(w, "_open_liveplot"):
                w._open_liveplot(patterns, title, xlabel, ylabel)
                return
            w = w.parent() if hasattr(w, "parent") else None

    def log_action(self, cmd: str, result: str = "") -> None:
        self.log(f"<span style='color:#555'>[gui]</span> <b style='color:#1a6bbf'>eset&gt;</b> {_esc(cmd)}")
        if result.strip():
            self.log(_ansi_to_html(result.rstrip("\n")))
