"""SCPI script editor with syntax highlighting, line numbers, auto-save,
external file change detection, and inline GUI debugger."""

from __future__ import annotations

import os
import re

from PySide6.QtCore import QFileSystemWatcher, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
)
from PySide6.QtWidgets import (
    QCompleter,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core.helpers import _ansi_to_html, _mono

# -- Syntax highlighter ------------------------------------------------------

_KEYWORDS = {
    "set", "for", "end", "repeat", "call", "import", "export", "array",
    "breakpoint", "sleep", "print", "use", "if", "else", "linspace",
    "upper_limit", "lower_limit", "record", "script", "examples", "python",
    "input", "unset",
}

_DEVICE_CMDS = {
    "psu", "psu1", "psu2", "psu3", "awg", "awg1", "awg2", "awg3",
    "dmm", "dmm1", "dmm2", "dmm3", "smu", "scope", "scope1", "scope2",
    "scope3", "ev2300", "scan", "force_scan", "state", "help", "all",
    "disconnect", "docs", "list", "idn", "raw", "reload", "status",
    "log", "calc", "data", "plot", "check", "report", "clear", "close",
    "version", "exit", "pause",
}

# Context-aware sub-command completions for each device/command prefix
_SUB_COMMANDS: dict[str, list[str]] = {
    "psu": ["set", "meas", "chan", "on", "off", "get", "state", "track", "save", "recall"],
    "awg": ["chan", "wave", "freq", "amp", "offset", "duty", "phase", "on", "off", "sync", "state"],
    "dmm": ["config", "read", "meas", "display", "text", "state"],
    "scope": ["run", "stop", "single", "autoset", "chan", "coupling", "probe",
              "vscale", "vpos", "hscale", "trigger", "meas", "label", "invert",
              "bwlimit", "force", "state"],
    "smu": ["set", "meas", "on", "off", "mode", "state", "compliance", "delay"],
    "ev2300": ["info", "read_word", "write_word", "read_byte", "write_byte",
               "read_block", "write_block", "send_byte", "scan", "probe", "fix", "state"],
    "state": ["on", "off", "safe", "reset"],
    "log": ["print", "save", "clear", "delete"],
    "script": ["run", "list", "show", "delete", "save"],
    "record": ["start", "stop", "show"],
    "examples": ["load"],
    "dmm config": ["vdc", "vac", "idc", "iac", "res", "freq", "cont", "diode"],
    "psu chan": ["1", "2", "3", "all", "on", "off"],
    "psu set": ["1", "2", "3"],
    "psu meas": ["1", "2", "3"],
    "awg chan": ["1", "2", "all", "on", "off"],
    "awg wave": ["1", "2", "all"],
    "scope chan": ["1", "2", "3", "4", "all", "on", "off"],
}

# Top-level command list for first-word completion
_TOP_COMMANDS = sorted(_KEYWORDS | _DEVICE_CMDS)

# Python keywords and builtins for .py file completions
_PY_KEYWORDS = {
    "def", "class", "return", "if", "else", "elif", "for", "while", "try",
    "except", "finally", "with", "as", "import", "from", "True", "False",
    "None", "and", "or", "not", "in", "is", "lambda", "pass", "break",
    "continue", "raise", "yield", "global", "nonlocal", "del", "assert",
}

_PY_BUILTINS = {
    "print", "len", "range", "str", "int", "float", "list", "dict", "set",
    "tuple", "open", "isinstance", "type", "super", "enumerate", "zip",
    "map", "filter", "sorted", "reversed", "abs", "max", "min", "sum",
    "any", "all", "hasattr", "getattr", "setattr", "input", "bool", "hex",
    "oct", "bin", "round", "format",
}

# Injected context vars available in scripts run via `python <file>`
_PY_CONTEXT = [
    "devices", "repl", "measurements", "ColorPrinter", "time", "os", "sys",
    "json", "lab_instruments",
    # Common device access patterns
    'devices.get("psu")', 'devices.get("dmm")', 'devices.get("awg")',
    'devices.get("scope")', 'devices.get("smu")', 'devices.get("ev2300")',
    # Common driver methods
    "set_output_channel", "measure_voltage", "measure_current",
    "enable_output", "set_waveform", "set_frequency", "set_amplitude",
    "get_output_state", "select_channel", "set_voltage", "set_current_limit",
    "read_byte", "write_byte", "read_word", "write_word",
]

_PY_COMPLETIONS = sorted(_PY_KEYWORDS | _PY_BUILTINS | set(_PY_CONTEXT))


def _get_scpi_completions(line_text: str) -> list[str]:
    """Return context-aware completions for the current SCPI line."""
    stripped = line_text.strip()
    if not stripped or " " not in stripped:
        return _TOP_COMMANDS

    # Try progressively shorter prefixes for sub-command lookup
    # e.g. "psu chan 1" → try "psu chan 1", then "psu chan", then "psu"
    parts = stripped.split()
    for n in range(len(parts), 0, -1):
        prefix = " ".join(parts[:n]).lower()
        if prefix in _SUB_COMMANDS:
            return _SUB_COMMANDS[prefix]

    # Also try base device type (psu1 → psu)
    base = re.sub(r"\d+$", "", parts[0].lower())
    remaining = " ".join(parts[1:]).lower() if len(parts) > 1 else ""
    for n in range(len(parts), 0, -1):
        prefix = base + (" " + " ".join(parts[1:n]).lower() if n > 1 else "")
        prefix = prefix.strip()
        if prefix in _SUB_COMMANDS:
            return _SUB_COMMANDS[prefix]

    return _TOP_COMMANDS


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
        self._rules.append((re.compile(r"""("[^"]*"|'[^']*')"""), fmt))

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


class _PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self._rules: list[tuple[re.Pattern, QTextCharFormat]] = []

        # Comments
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#808080"))
        fmt.setFontItalic(True)
        self._rules.append((re.compile(r"#.*$"), fmt))

        # Keywords
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#7c3aed"))
        fmt.setFontWeight(QFont.Weight.Bold)
        self._rules.append((re.compile(r"\b(" + "|".join(_PY_KEYWORDS) + r")\b"), fmt))

        # Built-in functions
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#1a6bbf"))
        self._rules.append((re.compile(r"\b(" + "|".join(_PY_BUILTINS) + r")\b"), fmt))

        # self
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#c0392b"))
        fmt.setFontItalic(True)
        self._rules.append((re.compile(r"\bself\b"), fmt))

        # Decorators
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#0e7a70"))
        self._rules.append((re.compile(r"@\w+"), fmt))

        # Numbers
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#c45c00"))
        self._rules.append((re.compile(r"\b\d+\.?\d*([eE][+-]?\d+)?\b"), fmt))

        # Strings (single, double, triple)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#b8860b"))
        self._rules.append((re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''), fmt))
        self._rules.append((re.compile(r"""f?("[^"\\]*(?:\\.[^"\\]*)*"|'[^'\\]*(?:\\.[^'\\]*)*')"""), fmt))

        # Function/method definitions
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#1a6bbf"))
        fmt.setFontWeight(QFont.Weight.Bold)
        self._rules.append((re.compile(r"\bdef\s+(\w+)"), fmt))

        # Class definitions
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#1a6bbf"))
        fmt.setFontWeight(QFont.Weight.Bold)
        self._rules.append((re.compile(r"\bclass\s+(\w+)"), fmt))

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
        self._is_python = False  # set by ScpiEditor based on file extension
        self._completer = QCompleter([], self)
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.activated.connect(self._insert_completion)
        self._update_completions(_TOP_COMMANDS)

    def _update_completions(self, words: list[str]) -> None:
        """Replace the completer's word list."""
        from PySide6.QtCore import QStringListModel
        model = self._completer.model()
        if isinstance(model, QStringListModel):
            model.setStringList(words)
        else:
            self._completer.setModel(QStringListModel(words, self._completer))

    def _insert_completion(self, text: str) -> None:
        tc = self.textCursor()
        # Select the current word and replace it
        tc.movePosition(QTextCursor.MoveOperation.StartOfWord, QTextCursor.MoveMode.KeepAnchor)
        tc.insertText(text)
        self.setTextCursor(tc)

    def keyPressEvent(self, event) -> None:  # noqa: N802
        # Let completer handle its keys when popup is visible
        if self._completer.popup().isVisible() and event.key() in (
            Qt.Key.Key_Enter,
            Qt.Key.Key_Return,
            Qt.Key.Key_Tab,
            Qt.Key.Key_Escape,
        ):
            event.ignore()
            return

        super().keyPressEvent(event)

        tc = self.textCursor()
        line_text = tc.block().text()[: tc.positionInBlock()]

        # Update completions based on context
        if self._is_python:
            self._update_completions(_PY_COMPLETIONS)
        else:
            completions = _get_scpi_completions(line_text)
            self._update_completions(completions)

        # Get the current word being typed (last word on line)
        tc.movePosition(QTextCursor.MoveOperation.StartOfWord, QTextCursor.MoveMode.KeepAnchor)
        prefix = tc.selectedText().strip()
        if len(prefix) < 1:
            self._completer.popup().hide()
            return

        if prefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(prefix)
            self._completer.popup().setCurrentIndex(self._completer.completionModel().index(0, 0))

        # Don't show popup if there's only one match and it equals what we typed
        if self._completer.completionCount() == 0:
            self._completer.popup().hide()
            return

        cr = self.cursorRect()
        cr.setWidth(
            max(
                300,
                self._completer.popup().sizeHintForColumn(0)
                + self._completer.popup().verticalScrollBar().sizeHint().width()
                + 20,
            )
        )
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
                painter.drawText(0, top, self._line_area.width() - 4, fh, Qt.AlignmentFlag.AlignRight, str(line_num))

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

        if is_py:
            self._highlighter = _PythonHighlighter(self._editor.document())
            self._editor._is_python = True
        else:
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

    def _next_real_line(self, from_idx: int) -> int:
        """Return index of next non-__NOP__ line at or after from_idx, or len(lines) if none."""
        st = self._debug_state
        if not st:
            return from_idx
        lines = st["lines"]
        i = from_idx
        while i < len(lines) and lines[i] == "__NOP__":
            i += 1
        return i

    def _debug_step(self) -> None:
        """Execute current line and advance to next real command. Skips comments/NOPs."""
        if not self._debug_state or self._debug_state.get("busy"):
            return
        st = self._debug_state

        # Skip to the next real command
        idx = self._next_real_line(st["idx"])
        if idx >= len(st["lines"]):
            self._debug_stop()
            return

        st["idx"] = idx
        self._debug_update_position()
        line = st["lines"][idx]

        # Run the command in background so sleep/long ops don't freeze UI
        st["busy"] = True
        self._step_btn.setEnabled(False)
        self._cont_btn.setEnabled(False)

        import threading

        def _run():
            self._debug_exec_line(line)

        def _done():
            if not self._debug_state:
                return
            self._debug_state["busy"] = False
            self._step_btn.setEnabled(True)
            self._cont_btn.setEnabled(True)
            # Advance past current line and skip to next real command
            next_idx = self._next_real_line(self._debug_state["idx"] + 1)
            self._debug_state["idx"] = next_idx
            if next_idx >= len(self._debug_state["lines"]):
                self._debug_stop()
            else:
                self._debug_update_position()

        from ..app import _BgSignal
        sig = _BgSignal(self)
        sig.finished.connect(lambda _: _done())
        t = threading.Thread(target=lambda: (_run(), sig.finished.emit("")), daemon=True)
        t.start()

    def _debug_continue(self) -> None:
        """Execute until next breakpoint or end."""
        if not self._debug_state:
            return
        # Mark start so continue doesn't immediately stop on current breakpoint
        self._debug_state["_cont_start"] = self._debug_state["idx"]
        self._debug_step()
        self._debug_schedule_continue()

    def _debug_schedule_continue(self) -> None:
        QTimer.singleShot(0, self._debug_continue_step)

    def _has_breakpoint_in_range(self, start: int, end: int) -> bool:
        """Check if any breakpoint (1-indexed) falls in the range [start, end)."""
        if not self._debug_state:
            return False
        bps = self._debug_state["breakpoints"]
        # Breakpoints on NOP lines should trigger at the next real line
        return any((i + 1) in bps for i in range(start, end))

    def _debug_continue_step(self) -> None:
        if not self._debugging or not self._debug_state:
            return
        st = self._debug_state
        if st.get("busy"):
            # Previous step still running — wait and retry
            QTimer.singleShot(50, self._debug_continue_step)
            return
        idx = st["idx"]
        if idx >= len(st["lines"]):
            self._debug_stop()
            return

        # Check for breakpoint: a breakpoint on any line from current position
        # through the next NOP block should stop at the next real line
        next_real = self._next_real_line(idx)
        if next_real >= len(st["lines"]):
            self._debug_stop()
            return

        # Check if any breakpoint falls in the NOP range or on the real line itself
        if self._has_breakpoint_in_range(idx, next_real + 1) and idx != st.get("_cont_start", -1):
            st["idx"] = next_real
            self._debug_update_position()
            return

        # Execute and advance
        st["idx"] = next_real
        line = st["lines"][next_real]
        self._debug_exec_line(line)
        st["idx"] = self._next_real_line(next_real + 1)
        if st["idx"] >= len(st["lines"]):
            self._debug_stop()
        else:
            self._debug_schedule_continue()

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
