"""Command dispatcher abstraction.

Currently using InstrumentREPL, but in the future we can use a gRPC Dispatcher.
"""

import contextlib
import io
from typing import Protocol, runtime_checkable


@runtime_checkable
class CommandDispatcher(Protocol):
    """Protocol for a command dispatcher."""

    def handle_command(self, command: str) -> str:
        """Handle a command and return the response."""
        ...


class LocalDispatcher:
    """Run a command in process. One InstrumentRepl isntance is resued to preserver session state."""

    def __init__(self) -> None:
        from lab_instruments.repl.shell import InstrumentRepl

        self.repl = InstrumentRepl()

    def handle_command(self, command: str) -> str:
        """Handle a command and return the response."""
        with contextlib.redirect_stdout(io.StringIO()) as f:
            self.repl.onecmd(command)
        return f.getvalue()
