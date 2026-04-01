"""SCPI script editor with syntax highlighting, line numbers, auto-save,
external file change detection, and inline GUI debugger."""

from __future__ import annotations

import os
import re

from PySide6.QtCore import QFileSystemWatcher, QRect, QSize, QStringListModel, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QSyntaxHighlighter, QTextBlockUserData, QTextCharFormat, QTextCursor, QTextDocument
from PySide6.QtWidgets import QCompleter, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

from ..core.helpers import _mono


# -- Syntax highlighter ------------------------------------------------------

_KEYWORDS = {
    "set", "for", "end", "repeat", "call", "import", "export", "array",
    "breakpoint", "sleep", "print", "use", "if", "else", "linspace",
    "upper_limit", "lower_limit", "record", "script", "examples", "python",
}

_DEVICE_CMDS = {"psu", "psu1", "psu2", "psu3", "awg", "awg1", "awg2", "awg3",
                "dmm", "dmm1", "dmm2", "dmm3", "smu", "scope", "scope1", "scope2", "scope3",
                "ev2300", "scan", "state", "help"}

# IntelliSense completion words
_COMPLETION_WORDS = sorted(set(
    list(_KEYWORDS) + list(_DEVICE_CMDS) + [
        # PSU sub-commands
        "psu on", "psu off", "psu set", "psu meas", "psu get", "psu chan",
        "psu track", "psu save", "psu recall", "psu state",
        "set_voltage", "set_current_limit", "measure_voltage", "measure_current",
        "enable_output", "select_channel", "get_output_state",
        # AWG sub-commands
        "awg on", "awg off", "awg chan", "awg set_frequency", "awg set_amplitude",
        "awg set_offset", "awg set_function",
        # DMM sub-commands
        "dmm read", "dmm mode", "dmm dc_voltage", "dmm ac_voltage",
        "dmm dc_current", "dmm ac_current", "dmm resistance",
        "dmm frequency", "dmm continuity", "dmm diode",
        # Scope sub-commands
        "scope run", "scope stop", "scope single", "scope autoset",
        "scope chan", "scope trigger",
        # SMU sub-commands
        "smu mode", "smu set_voltage", "smu set_current",
        "smu output", "smu voltage", "smu current",
        # EV2300 sub-commands
        "ev2300 info", "ev2300 read_word", "ev2300 write_word",
        "ev2300 read_byte", "ev2300 write_byte", "ev2300 read_block",
        "ev2300 write_block", "ev2300 scan", "ev2300 state",
        # Script directives
        "breakpoint", "sleep", "print", "use", "record",
        "upper_limit", "lower_limit", "linspace",
        # State commands
        "state on", "state off", "state safe", "state reset",
    ]
))


class _ScpiHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self._rules: list[tuple[re.Pattern, QTextCharFormat]] = []

        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#808080"))
        fmt.setFontItalic(True)
        self._rules.append((re.compile(r"#.*$"), fmt))

        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#7c3aed"))
        fmt.setFontWeight(QFont.Weight.Bold)
        self._rules.append((re.compile(r"\b(" + "|".join(_KEYWORDS) + r")\b"), fmt))

        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#1a6bbf"))
        fmt.setFontWeight(QFont.Weight.Bold)
        self._rules.append((re.compile(r"\b(" + "|".join(_DEVICE_CMDS) + r")\b"), fmt))

        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#0e7a70"))
        self._rules.append((re.compile(r"\{[^}]+\}"), fmt))

        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#c45c00"))
        self._rules.append((re.compile(r"\b\d+\.?\d*([eE][+-]?\d+)?\b"), fmt))

        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#b8860b"))
        self._rules.append((re.compile(r'"[^"]*"'), fmt))

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


# -- Line number area --------------------------------------------------------


class _LineNumberArea(QWidget):
    def __init__(self, editor: QPlainTextEdit) -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_width(), 0)

    def paintEvent(self, event) -> None:  # noqa: N802
        self._editor.paint_line_numbers(event)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        """Click on gutter toggles breakpoint."""
        if hasattr(self._editor, "_toggle_breakpoint_at_y"):
            self._editor._toggle_breakpoint_at_y(event.pos().y())


# -- Code editor with gutter -------------------------------------------------


class _CodeEditor(QPlainTextEdit):
    """QPlainTextEdit with line numbers, breakpoint markers, and current-line highlight."""

    breakpoint_toggled = Signal(int)  # 1-indexed line number

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._line_area = _LineNumberArea(self)
        self._breakpoints: set[int] = set()  # 1-indexed
        self._current_debug_line: int = -1  # 1-indexed, -1 = not debugging
        self.blockCountChanged.connect(self._update_line_area_width)
        self.updateRequest.connect(self._update_line_area)
        self._update_line_area_width()

        # IntelliSense completer
        self._completer = QCompleter(_COMPLETION_WORDS, self)
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.activated.connect(self._insert_completion)

    def _insert_completion(self, text: str) -> None:
        tc = self.textCursor()
        # Select the current word and replace it
        tc.movePosition(QTextCursor.MoveOperation.StartOfWord, QTextCursor.MoveMode.KeepAnchor)
        tc.insertText(text)
        self.setTextCursor(tc)

    def keyPressEvent(self, event) -> None:  # noqa: N802
        # Let completer handle its keys when popup is visible
        if self._completer.popup().isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab,
                               Qt.Key.Key_Escape):
                event.ignore()
                return

        super().keyPressEvent(event)

        # Only complete the first word on the line (command position)
        tc = self.textCursor()
        line_text = tc.block().text()[:tc.positionInBlock()]
        # If there's already a space before cursor, don't complete
        # (user is typing arguments, not a command)
        if " " in line_text.strip():
            self._completer.popup().hide()
            return

        tc.movePosition(QTextCursor.MoveOperation.StartOfWord, QTextCursor.MoveMode.KeepAnchor)
        prefix = tc.selectedText().strip()
        if len(prefix) < 2:
            self._completer.popup().hide()
            return

        if prefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(prefix)
            self._completer.popup().setCurrentIndex(self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(max(300, self._completer.popup().sizeHintForColumn(0)
                    + self._completer.popup().verticalScrollBar().sizeHint().width() + 20))
        self._completer.complete(cr)

    def line_number_width(self) -> int:
        digits = max(3, len(str(self.blockCount())))
        return 18 + self.fontMetrics().horizontalAdvance("9") * digits

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_width(), cr.height()))

    def _update_line_area_width(self) -> None:
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)

    def _update_line_area(self, rect, dy) -> None:
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_area_width()

    def set_debug_line(self, line: int) -> None:
        """Highlight the current debug line (1-indexed). -1 to clear."""
        self._current_debug_line = line
        self._line_area.update()
        self.viewport().update()
        if line > 0:
            block = self.document().findBlockByLineNumber(line - 1)
            if block.isValid():
                cursor = self.textCursor()
                cursor.setPosition(block.position())
                self.setTextCursor(cursor)
                self.centerCursor()

    def _toggle_breakpoint_at_y(self, y: int) -> None:
        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        while block.isValid():
            btop = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
            bbot = btop + int(self.blockBoundingRect(block).height())
            if btop <= y < bbot:
                line = block.blockNumber() + 1
                if line in self._breakpoints:
                    self._breakpoints.discard(line)
                else:
                    self._breakpoints.add(line)
                self.breakpoint_toggled.emit(line)
                self._line_area.update()
                return
            block = block.next()

    def paint_line_numbers(self, event) -> None:
        painter = QPainter(self._line_area)
        pal = self._line_area.palette()
        painter.fillRect(event.rect(), pal.color(pal.ColorRole.Window))

        block = self.firstVisibleBlock()
        block_num = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        text_color = pal.color(pal.ColorRole.PlaceholderText)
        current_color = pal.color(pal.ColorRole.WindowText)
        current_line = self.textCursor().blockNumber()
        fh = self.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_num = block_num + 1

                # Breakpoint marker (red dot)
                if line_num in self._breakpoints:
                    painter.setBrush(QColor("#c0392b"))
                    painter.setPen(Qt.PenStyle.NoPen)
                    dot_y = top + (fh - 8) // 2
                    painter.drawEllipse(3, dot_y, 8, 8)

                # Debug current line highlight
                if line_num == self._current_debug_line:
                    painter.fillRect(0, top, self._line_area.width(), fh, QColor("#fff3cd"))

                # Line number
                if block_num == current_line or line_num == self._current_debug_line:
                    painter.setPen(current_color)
                else:
                    painter.setPen(text_color)
                painter.drawText(0, top, self._line_area.width() - 4, fh,
                                 Qt.AlignmentFlag.AlignRight, str(line_num))

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_num += 1
        painter.end()


# -- Editor widget -----------------------------------------------------------


class ScpiEditor(QWidget):
    """Editor with syntax highlighting, auto-save, file watching, and inline debugger."""

    file_modified = Signal(bool)
    run_requested = Signal(str)
    debug_requested = Signal(str)

    def __init__(self, file_path: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._file_path = file_path
        self._dirty = False
        self._debugging = False
        self._debug_state = None  # dict with idx, lines, source_lines, breakpoints
        self._last_mtime: float = 0.0

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # -- Run/Debug toolbar (for scripts only) ----------------------------
        is_scpi = file_path and file_path.endswith(".scpi") if file_path else False
        is_py = file_path and file_path.endswith(".py") if file_path else False

        if is_scpi or is_py:
            self._toolbar = QHBoxLayout()
            self._toolbar.setContentsMargins(4, 4, 4, 4)
            self._toolbar.setSpacing(4)

            self._run_btn = QPushButton("Run (F5)")
            self._run_btn.setStyleSheet(
                "QPushButton { color: #155724; border: 1px solid #28a74588; border-radius: 4px; "
                "padding: 4px 12px; font-weight: bold; }"
                "QPushButton:hover { background: #28a745; color: white; }"
            )
            self._run_btn.clicked.connect(lambda: self._on_run(debug=False))
            self._toolbar.addWidget(self._run_btn)

            if is_scpi:
                self._debug_btn = QPushButton("Debug")
                self._debug_btn.setStyleSheet(
                    "QPushButton { color: #c45c00; border: 1px solid #c45c0088; border-radius: 4px; "
                    "padding: 4px 12px; font-weight: bold; }"
                    "QPushButton:hover { background: #c45c00; color: white; }"
                )
                self._debug_btn.clicked.connect(lambda: self._on_run(debug=True))
                self._toolbar.addWidget(self._debug_btn)

            # Debug controls (hidden until debugging)
            self._step_btn = QPushButton("Step (F10)")
            self._step_btn.setStyleSheet(
                "QPushButton { color: #1a6bbf; border: 1px solid #1a6bbf88; border-radius: 4px; "
                "padding: 4px 10px; font-weight: bold; }"
                "QPushButton:hover { background: #1a6bbf; color: white; }"
            )
            self._step_btn.clicked.connect(self._debug_step)
            self._step_btn.setVisible(False)
            self._toolbar.addWidget(self._step_btn)

            self._cont_btn = QPushButton("Continue (F5)")
            self._cont_btn.setStyleSheet(
                "QPushButton { color: #155724; border: 1px solid #28a74588; border-radius: 4px; "
                "padding: 4px 10px; font-weight: bold; }"
                "QPushButton:hover { background: #28a745; color: white; }"
            )
            self._cont_btn.clicked.connect(self._debug_continue)
            self._cont_btn.setVisible(False)
            self._toolbar.addWidget(self._cont_btn)

            self._stop_btn = QPushButton("Stop")
            self._stop_btn.setStyleSheet(
                "QPushButton { color: #c0392b; border: 1px solid #c0392b88; border-radius: 4px; "
                "padding: 4px 10px; font-weight: bold; }"
                "QPushButton:hover { background: #c0392b; color: white; }"
            )
            self._stop_btn.clicked.connect(self._debug_stop)
            self._stop_btn.setVisible(False)
            self._toolbar.addWidget(self._stop_btn)

            # Extra debug controls (hidden until debugging)
            self._back_btn = QPushButton("Back")
            self._back_btn.setStyleSheet(
                "QPushButton { color: #7c3aed; border: 1px solid #7c3aed88; border-radius: 4px; "
                "padding: 4px 10px; font-weight: bold; }"
                "QPushButton:hover { background: #7c3aed; color: white; }"
            )
            self._back_btn.clicked.connect(self._debug_back)
            self._back_btn.setVisible(False)
            self._toolbar.addWidget(self._back_btn)

            self._goto_btn = QPushButton("Goto")
            self._goto_btn.setStyleSheet(
                "QPushButton { color: #0e7a70; border: 1px solid #0e7a7088; border-radius: 4px; "
                "padding: 4px 10px; font-weight: bold; }"
                "QPushButton:hover { background: #0e7a70; color: white; }"
            )
            self._goto_btn.clicked.connect(self._debug_goto)
            self._goto_btn.setVisible(False)
            self._toolbar.addWidget(self._goto_btn)

            self._toolbar.addStretch()

            self._dbg_label = QLabel("")
            self._dbg_label.setStyleSheet("font-size: 10px; font-weight: bold;")
            self._toolbar.addWidget(self._dbg_label)

            self._file_label = QLabel(os.path.basename(file_path) if file_path else "")
            self._file_label.setStyleSheet("font-size: 10px;")
            self._toolbar.addWidget(self._file_label)

            lay.addLayout(self._toolbar)
        else:
            self._toolbar = None

        # -- Editor ----------------------------------------------------------
        self._editor = _CodeEditor()
        self._editor.setFont(_mono(11))
        self._editor.setTabStopDistance(self._editor.fontMetrics().horizontalAdvance(" ") * 4)
        self._editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self._highlighter = _ScpiHighlighter(self._editor.document())
        self._editor.document().contentsChanged.connect(self._on_contents_changed)

        # Auto-save timer (500ms debounce)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self._auto_save)

        # File watcher for external changes
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_file_changed_externally)
        self._suppress_reload = False

        lay.addWidget(self._editor, 1)

        # Load file
        self._loading = True
        if file_path:
            self._load_from_disk(file_path)
            if os.path.isfile(file_path):
                self._watcher.addPath(file_path)
                self._last_mtime = os.path.getmtime(file_path)
        self._loading = False

    # -- File I/O ------------------------------------------------------------

    def _load_from_disk(self, path: str) -> None:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                self._editor.setPlainText(f.read())
            self._editor.document().setModified(False)
            self._dirty = False
        except Exception as exc:
            self._editor.setPlainText(f"Error reading file: {exc}")

    def _on_file_changed_externally(self, path: str) -> None:
        """Reload if the file was changed by another process."""
        if self._suppress_reload:
            return
        if not os.path.isfile(path):
            return
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            return
        if mtime <= self._last_mtime:
            return
        self._last_mtime = mtime
        self._loading = True
        cursor_pos = self._editor.textCursor().position()
        with open(path, encoding="utf-8", errors="replace") as f:
            self._editor.setPlainText(f.read())
        self._editor.document().setModified(False)
        self._dirty = False
        # Restore cursor position
        cursor = self._editor.textCursor()
        cursor.setPosition(min(cursor_pos, len(self._editor.toPlainText())))
        self._editor.setTextCursor(cursor)
        self._loading = False
        # Re-add to watcher (Qt removes it after notification)
        if path not in self._watcher.files():
            self._watcher.addPath(path)

    def _on_contents_changed(self) -> None:
        if self._loading:
            return
        self._dirty = True
        self._save_timer.start()

    def _auto_save(self) -> None:
        if self._dirty and self._file_path:
            self.save()

    def save(self) -> bool:
        if not self._file_path:
            return False
        try:
            self._suppress_reload = True
            with open(self._file_path, "w", encoding="utf-8") as f:
                f.write(self._editor.toPlainText())
            self._last_mtime = os.path.getmtime(self._file_path)
            self._editor.document().setModified(False)
            self._dirty = False
            self.file_modified.emit(False)
            # Re-add to watcher if needed
            if self._file_path not in self._watcher.files():
                self._watcher.addPath(self._file_path)
            self._suppress_reload = False
            return True
        except Exception:
            self._suppress_reload = False
            return False

    # -- Run / Debug ---------------------------------------------------------

    def _on_run(self, debug: bool = False) -> None:
        self._save_timer.stop()
        self.save()
        if self._file_path:
            if debug:
                self.debug_requested.emit(self._file_path)
            else:
                self.run_requested.emit(self._file_path)

    # -- Inline Debugger -----------------------------------------------------

    def start_debug(self, lines: list[str], source_lines: list[str], breakpoints: set[int]) -> None:
        """Enter debug mode with expanded script lines."""
        self._debugging = True
        self._debug_state = {
            "idx": 0,
            "lines": lines,
            "source_lines": source_lines,
            "breakpoints": breakpoints,
        }
        self._editor._breakpoints = breakpoints
        self._editor.setReadOnly(True)
        self._show_debug_ui(True)
        self._debug_update_position()

    def _show_debug_ui(self, show: bool) -> None:
        if self._toolbar is None:
            return
        if hasattr(self, "_run_btn"):
            self._run_btn.setVisible(not show)
        if hasattr(self, "_debug_btn"):
            self._debug_btn.setVisible(not show)
        self._step_btn.setVisible(show)
        self._cont_btn.setVisible(show)
        self._stop_btn.setVisible(show)
        if hasattr(self, "_back_btn"):
            self._back_btn.setVisible(show)
        if hasattr(self, "_goto_btn"):
            self._goto_btn.setVisible(show)

    def _debug_update_position(self) -> None:
        if not self._debug_state:
            return
        idx = self._debug_state["idx"]
        total = len(self._debug_state["lines"])
        if idx < total:
            self._editor.set_debug_line(idx + 1)
            src = self._debug_state["source_lines"][idx] if idx < len(self._debug_state["source_lines"]) else ""
            self._dbg_label.setText(f"[{idx + 1}/{total}] {src}")
        else:
            self._debug_stop()

    def _debug_step(self) -> None:
        """Execute current line and advance."""
        if not self._debug_state:
            return
        st = self._debug_state
        idx = st["idx"]
        if idx >= len(st["lines"]):
            self._debug_stop()
            return
        line = st["lines"][idx]
        # Execute (skip __NOP__)
        if line != "__NOP__":
            self._debug_exec_line(line)
        st["idx"] += 1
        # Skip __NOP__ lines automatically
        while st["idx"] < len(st["lines"]) and st["lines"][st["idx"]] == "__NOP__":
            st["idx"] += 1
        if st["idx"] >= len(st["lines"]):
            self._debug_stop()
        else:
            self._debug_update_position()

    def _debug_continue(self) -> None:
        """Execute until next breakpoint or end."""
        if not self._debug_state:
            return
        st = self._debug_state
        # Execute current line first
        self._debug_step()
        # Keep stepping until breakpoint or end
        while self._debugging and st["idx"] < len(st["lines"]):
            if (st["idx"] + 1) in st["breakpoints"]:
                self._debug_update_position()
                return
            line = st["lines"][st["idx"]]
            if line != "__NOP__":
                self._debug_exec_line(line)
            st["idx"] += 1
            while st["idx"] < len(st["lines"]) and st["lines"][st["idx"]] == "__NOP__":
                st["idx"] += 1
        self._debug_stop()

    def _debug_back(self) -> None:
        """Move back one line (state NOT reversed)."""
        if not self._debug_state:
            return
        st = self._debug_state
        if st["idx"] > 0:
            st["idx"] -= 1
            # Skip back over __NOP__ lines
            while st["idx"] > 0 and st["lines"][st["idx"]] == "__NOP__":
                st["idx"] -= 1
            self._debug_update_position()

    def _debug_goto(self) -> None:
        """Jump to a specific line."""
        if not self._debug_state:
            return
        from PySide6.QtWidgets import QInputDialog
        total = len(self._debug_state["lines"])
        line, ok = QInputDialog.getInt(self, "Go to Line", f"Line number (1-{total}):", 1, 1, total)
        if ok:
            self._debug_state["idx"] = line - 1
            self._debug_update_position()

    def _debug_exec_line(self, line: str) -> None:
        """Execute a single SCPI command and show output in console."""
        # Walk up to find _MainWindow and use its dispatcher
        w = self.parent()
        while w is not None:
            if hasattr(w, "_d"):
                output = w._d.run(line)
                if output.strip() and hasattr(w, "_console"):
                    from ..core.helpers import _ansi_to_html
                    w._console.log(_ansi_to_html(output))
                return
            if hasattr(w, "_console"):
                break
            w = w.parent()

    def _debug_stop(self) -> None:
        """Exit debug mode."""
        self._debugging = False
        self._debug_state = None
        self._editor.setReadOnly(False)
        self._editor.set_debug_line(-1)
        self._show_debug_ui(False)
        if hasattr(self, "_dbg_label"):
            self._dbg_label.setText("")

    @property
    def debugging(self) -> bool:
        return self._debugging

    # -- Public API ----------------------------------------------------------

    def file_path(self) -> str | None:
        return self._file_path

    def is_dirty(self) -> bool:
        return self._dirty

    def editor(self) -> _CodeEditor:
        return self._editor

    def goto_line(self, line: int) -> None:
        block = self._editor.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            cursor = self._editor.textCursor()
            cursor.setPosition(block.position())
            self._editor.setTextCursor(cursor)
            self._editor.centerCursor()
