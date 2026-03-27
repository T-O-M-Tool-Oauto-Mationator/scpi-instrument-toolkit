"""Command palette provider for the SCPI TUI.

Exposes all REPL command completions in the Textual command palette (Ctrl+P).
Selecting a command dispatches it directly into the log view.
"""

from __future__ import annotations

from textual.command import DiscoveryHit, Hit, Hits, Provider


class SCPICommandProvider(Provider):
    """Fuzzy-searchable provider that surfaces REPL command completions.

    - discover(): shows all commands when the palette opens with no input
    - search(query): fuzzy-filters using Textual's built-in Matcher
    - Selecting a command switches to log-view and dispatches it
    """

    async def startup(self) -> None:
        """Pre-warm the completion list from the dispatcher."""
        dispatcher = getattr(self.app, "_dispatcher", None)
        if dispatcher is not None and hasattr(dispatcher, "get_completions"):
            self._all_commands: list[str] = dispatcher.get_completions("")
        else:
            self._all_commands = []

    async def discover(self) -> Hits:
        """Yield every command when the palette opens with an empty query."""
        for cmd in self._all_commands:
            yield DiscoveryHit(
                display=cmd,
                command=lambda c=cmd: self._run(c),
                text=cmd,
            )

    async def search(self, query: str) -> Hits:
        """Yield fuzzy-matched commands for the given query."""
        matcher = self.matcher(query)
        for cmd in self._all_commands:
            score = matcher.match(cmd)
            if score > 0:
                yield Hit(
                    score=score,
                    match_display=matcher.highlight(cmd),
                    command=lambda c=cmd: self._run(c),
                    text=cmd,
                )

    def _run(self, cmd: str) -> None:
        """Dispatch cmd and ensure the log view is visible."""
        from textual.widgets import ContentSwitcher

        app = self.app
        with app.prevent():
            app.query_one("#main-content", ContentSwitcher).current = "log-view"
        app._dispatch_command(cmd)
