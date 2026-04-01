from __future__ import annotations

import atexit
import contextlib
import io
import re
import signal
import threading
from typing import Any


class _Dispatcher:
    def __init__(self, mock: bool = False) -> None:
        from lab_instruments.repl.shell import InstrumentRepl

        saved_int = signal.getsignal(signal.SIGINT)
        saved_term = signal.getsignal(signal.SIGTERM) if hasattr(signal, "SIGTERM") else None

        if mock:
            from lab_instruments import mock_instruments
            from lab_instruments.src import discovery as _disc

            _disc.InstrumentDiscovery.__init__ = lambda self: None
            _disc.InstrumentDiscovery.scan = lambda self, verbose=True: mock_instruments.get_mock_devices(verbose)

        self._repl = InstrumentRepl(auto_scan=False)
        self._lock = threading.Lock()

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
            old_repl_stdout = self._repl.stdout
            self._repl.stdout = buf
            with contextlib.redirect_stdout(buf):
                for line in command.split("\n"):
                    line = line.strip()
                    if line:
                        self._repl.onecmd(line)
            self._repl.stdout = old_repl_stdout
            return buf.getvalue()

    @property
    def registry(self):
        return self._repl.ctx.registry

    def device(self, name: str) -> Any | None:
        return self.registry.devices.get(name)

    def devices_of_type(self, base: str) -> list[tuple[str, str]]:
        result = []
        for name in sorted(self.registry.devices):
            if re.sub(r"\d+$", "", name) == base:
                result.append((name, self.registry.display_name(name)))
        return result

    def has_cap(self, name: str, cap_name: str) -> bool:
        from lab_instruments.repl.capabilities import Capability

        cap_map = {
            "multi_channel": Capability.PSU_MULTI_CHANNEL,
            "readback": Capability.PSU_READBACK,
            "tracking": Capability.PSU_TRACKING,
            "save_recall": Capability.PSU_SAVE_RECALL,
        }
        cap = cap_map.get(cap_name)
        return bool(cap and self.registry.has_cap(name, cap))
