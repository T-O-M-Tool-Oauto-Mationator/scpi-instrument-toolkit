from __future__ import annotations

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.dispatcher import _Dispatcher
from ..core.helpers import _ansi_to_html, _esc, _mono


class _Console(QWidget):
    command_ran = Signal()  # emitted after every non-clear command

    def __init__(self, d: _Dispatcher, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._d = d
        self._history: list[str] = []
        self._hist_idx = -1

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(_mono())
        self._output.document().setMaximumBlockCount(5000)
        lay.addWidget(self._output, 1)

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
        result = self._d.run(cmd)
        if result.strip():
            self.log(_ansi_to_html(result.rstrip("\n")))
        self.command_ran.emit()

    def log(self, html: str) -> None:
        sb = self._output.verticalScrollBar()
        at_bottom = sb.value() >= sb.maximum() - 4
        self._output.append(html)
        if at_bottom:
            sb.setValue(sb.maximum())

    def log_action(self, cmd: str, result: str = "") -> None:
        self.log(f"<span style='color:#555'>[gui]</span> <b style='color:#1a6bbf'>eset&gt;</b> {_esc(cmd)}")
        if result.strip():
            self.log(_ansi_to_html(result.rstrip("\n")))
