"""Command dispatcher abstraction.

Currently using InstrumentREPL, but in the future we can use a gRPC Dispatcher.
"""

from __future__ import annotations

import contextlib
import io
from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class CommandDispatcher(Protocol):
    """Protocol for a command dispatcher."""

    def handle_command(self, command: str, line_callback: Callable[[str], None] | None = None) -> str:
        """Handle a command and return the response.

        If *line_callback* is provided, each chunk of output is forwarded to it
        in real-time (for streaming to TUI).  The full output is still returned.
        """
        ...

    def get_completions(self, text: str) -> list[str]:
        """Return sorted completion candidates for the given text prefix."""
        ...

    def get_measurement_snapshot(self) -> list[dict]:
        """Return a copy of all recorded measurements safe to read from the event loop."""
        ...

    def get_script_names(self) -> list[str]:
        """Return sorted list of loaded script names."""
        ...

    def get_vars_snapshot(self) -> dict[str, str]:
        """Return a copy of current script variable bindings."""
        ...

    def get_safety_snapshot(self) -> dict:
        """Return a summary of current safety state."""
        ...


class _StreamingWriter(io.TextIOBase):
    """A writable stream that forwards each write to a callback AND a buffer."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self._callback = callback
        self._buf = io.StringIO()

    def write(self, s: str) -> int:
        self._buf.write(s)
        if s:
            self._callback(s)
        return len(s)

    def getvalue(self) -> str:
        return self._buf.getvalue()


class LocalDispatcher:
    """Run a command in process. One InstrumentRepl instance is reused to preserve session state."""

    def __init__(self, mock: bool = False) -> None:
        if mock:
            from lab_instruments import mock_instruments
            from lab_instruments.src import discovery as _disc

            _disc.InstrumentDiscovery.__init__ = lambda self: None
            _disc.InstrumentDiscovery.scan = lambda self, verbose=True: mock_instruments.get_mock_devices(verbose)

        from lab_instruments.repl.shell import InstrumentRepl

        self.repl = InstrumentRepl()

    def handle_command(self, command: str, line_callback: Callable[[str], None] | None = None) -> str:
        """Handle a command and return the response."""
        if line_callback is not None:
            stream = _StreamingWriter(line_callback)
            with contextlib.redirect_stdout(stream):  # type: ignore[type-var]
                self.repl.onecmd(command)
            return stream.getvalue()
        else:
            with contextlib.redirect_stdout(io.StringIO()) as f:
                self.repl.onecmd(command)
            return f.getvalue()

    def get_device_snapshot(self) -> list[dict]:
        """Return a snapshot of connected devices safe to read from the event loop.

        Each dict has: name, display_name, selected (bool), base_type.
        Returns copies of primitive values - never a live reference.
        """
        registry = self.repl.ctx.registry
        return [
            {
                "name": name,
                "display_name": registry.display_name(name),
                "selected": name == registry.selected,
                "base_type": registry.base_type(name),
            }
            for name in sorted(registry.devices)
        ]

    def get_measurement_snapshot(self) -> list[dict]:
        """Return a copy of all recorded measurements safe to read from the event loop.

        Each dict has: label, value, unit, source.
        Returns copies - never live references into MeasurementStore.
        """
        return [dict(e) for e in self.repl.ctx.measurements.entries]

    def get_script_names(self) -> list[str]:
        """Return sorted list of loaded script names."""
        return sorted(self.repl.ctx.scripts.keys())

    def get_vars_snapshot(self) -> dict[str, str]:
        """Return a copy of current script variable bindings."""
        return dict(self.repl.ctx.script_vars)

    def get_safety_snapshot(self) -> dict:
        """Return a summary of current safety state.

        Keys: limit_count (int), active_script (bool), exit_on_error (bool).
        """
        ctx = self.repl.ctx
        return {
            "limit_count": len(ctx.safety_limits),
            "active_script": ctx.in_script,
            "exit_on_error": ctx.exit_on_error,
        }

    def get_completions(self, text: str) -> list[str]:
        """Return sorted, deduplicated completion candidates for text.

        Calls both completenames (top-level verbs) and completedefault
        (sub-command arguments) to cover the full REPL command space.
        Safe to call from any thread - reads only REPL method names and
        context state, no I/O.
        """
        results: list[str] = []
        with contextlib.suppress(Exception):
            results.extend(self.repl.completenames(text, text, 0, len(text)))
        with contextlib.suppress(Exception):
            results.extend(self.repl.completedefault(text, text, 0, len(text)))
        seen: set[str] = set()
        deduped: list[str] = []
        for r in results:
            if r not in seen:
                seen.add(r)
                deduped.append(r)
        return sorted(deduped)
