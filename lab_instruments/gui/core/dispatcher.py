from __future__ import annotations

import atexit
import builtins as _builtins
import contextlib
import io
import re
import signal
import threading
from typing import Any

from PySide6.QtCore import QMetaObject, QObject, Qt, Signal, Slot
from PySide6.QtWidgets import QInputDialog

from lab_instruments.repl.capabilities import Capability
from lab_instruments.repl.shell import InstrumentRepl


class _InputBridge(QObject):
    """Thread-safe bridge for showing an input dialog from a background thread."""

    request = Signal(str)  # prompt text
    response = Signal(str)  # user's answer

    def __init__(self, parent=None):
        super().__init__(parent)
        self._event = threading.Event()
        self._result = ""
        self.request.connect(self._show_dialog, Qt.ConnectionType.BlockingQueuedConnection)

    @Slot(str)
    def _show_dialog(self, prompt: str) -> None:
        from PySide6.QtWidgets import QApplication
        # Strip ANSI escape codes from the prompt
        clean = re.sub(r"\x1b\[[0-9;]*m", "", prompt or "")
        parent = QApplication.activeWindow()
        text, ok = QInputDialog.getText(parent, "Input Required", clean or "Enter value:")
        self._result = text if ok else ""

    def ask(self, prompt: str) -> str:
        """Call from any thread — blocks until user responds."""
        self._result = ""
        self.request.emit(prompt)
        return self._result


class _Dispatcher(QObject):
    def __init__(self, mock: bool = False, parent=None) -> None:
        super().__init__(parent)
        saved_int = signal.getsignal(signal.SIGINT)
        saved_term = signal.getsignal(signal.SIGTERM) if hasattr(signal, "SIGTERM") else None

        if mock:
            from lab_instruments import mock_instruments
            from lab_instruments.src import discovery as _disc

            _disc.InstrumentDiscovery.__init__ = lambda self: None
            _disc.InstrumentDiscovery.scan = lambda self, verbose=True: mock_instruments.get_mock_devices(verbose)

        self._repl = InstrumentRepl(auto_scan=False)
        self._lock = threading.Lock()
        self._input_bridge = _InputBridge(self)

        signal.signal(signal.SIGINT, saved_int)
        if saved_term is not None:
            signal.signal(signal.SIGTERM, saved_term)

        atexit.unregister(self._repl._cleanup_on_exit)
        self._repl._cleanup_done = True
        self._repl._term_fd = None
        self._repl._term_settings = None

        if mock:
            self.run("scan")

    def run(self, command: str) -> str:
        """Execute a REPL command. Thread-safe via lock."""
        with self._lock:
            buf = io.StringIO()

            def _gui_input(prompt=""):
                return self._input_bridge.ask(str(prompt).strip())

            old_input = _builtins.input
            _builtins.input = _gui_input
            old_repl_stdout = self._repl.stdout
            self._repl.stdout = buf
            try:
                with contextlib.redirect_stdout(buf):
                    for line in command.split("\n"):
                        line = line.strip()
                        if line:
                            self._repl.onecmd(line)
            finally:
                _builtins.input = old_input
                self._repl.stdout = old_repl_stdout
            return buf.getvalue()

    @property
    def registry(self):
        return self._repl.ctx.registry

    def device(self, name: str) -> Any | None:
        return self.registry.devices.get(name)

    def is_busy(self) -> bool:
        """Return True if the dispatcher lock is currently held by a background thread."""
        acquired = self._lock.acquire(blocking=False)
        if acquired:
            self._lock.release()
        return not acquired

    def devices_of_type(self, base: str) -> list[tuple[str, str]]:
        devices = dict(self.registry.devices)  # snapshot to avoid race with scan worker
        result = []
        for name in sorted(devices):
            if re.sub(r"\d+$", "", name) == base:
                result.append((name, self.registry.display_name(name)))
        return result

    def has_cap(self, name: str, cap_name: str) -> bool:
        cap_map = {
            "multi_channel": Capability.PSU_MULTI_CHANNEL,
            "readback": Capability.PSU_READBACK,
            "tracking": Capability.PSU_TRACKING,
            "save_recall": Capability.PSU_SAVE_RECALL,
        }
        cap = cap_map.get(cap_name)
        return bool(cap and self.registry.has_cap(name, cap))
