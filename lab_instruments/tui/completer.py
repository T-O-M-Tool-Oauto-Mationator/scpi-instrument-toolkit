"""Tab-completion suggester for the SCPI TUI command input."""

from textual.suggester import Suggester

from .dispatcher import CommandDispatcher


class ReplSuggester(Suggester):
    """Inline suggester that delegates to the REPL's completion machinery.

    Passes the current input value to the dispatcher's get_completions()
    and returns the first candidate that starts with the typed text.
    use_cache=False because the device list changes during a session.
    """

    def __init__(self, dispatcher: CommandDispatcher) -> None:
        super().__init__(use_cache=False, case_sensitive=False)
        self._dispatcher = dispatcher

    async def get_suggestion(self, value: str) -> str | None:
        """Return the first completion candidate for value, or None."""
        if not value:
            return None
        candidates = self._dispatcher.get_completions(value)
        lower = value.lower()
        for candidate in candidates:
            if candidate.lower().startswith(lower):
                return candidate
        return None
