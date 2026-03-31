"""Command palette provider for the SCPI TUI.

Exposes all REPL command completions in the Textual command palette (Ctrl+P).
Selecting a command dispatches it directly into the log view.
"""

from __future__ import annotations

from textual.command import DiscoveryHit, Hit, Hits, Provider

_TUI_ACTIONS: list[tuple[str, str, str]] = [
    # (display_text, help_text, action_or_command)
    # -- View navigation --
    ("Show Log View", "Switch to command output log", "action:clear_log_view"),
    ("Show Measurements", "Switch to measurement table", "action:toggle_measurements"),
    ("Show Plot", "Switch to plot panel", "action:show_plot"),
    ("Show Safety Limits", "Switch to safety limits panel", "action:show_limits"),
    ("Show Instrument Detail", "Switch to instrument detail", "action:show_detail"),
    ("Show Scripts", "Switch to script browser", "action:show_scripts"),
    ("Show Variables", "Switch to variable inspector", "action:show_vars"),
    ("Toggle Device Sidebar", "Show or hide the device sidebar", "action:toggle_sidebar"),
    ("Clear Log", "Clear the output log", "action:clear_log"),
    # -- Bulk operations --
    ("All Instruments OFF", "Turn off all instrument outputs", "cmd:state off"),
    ("All Instruments Safe", "Set all instruments to safe state", "cmd:state safe"),
    ("All Instruments Reset", "Reset all instruments", "cmd:state reset"),
    # -- Data operations --
    ("Clear Measurements", "Erase all logged measurements", "cmd:log clear"),
    ("Generate Report", "Create a test report", "cmd:report save"),
    # -- Utility --
    ("Scan for Instruments", "Discover connected instruments", "cmd:scan"),
    ("Open Documentation", "Open docs in browser", "cmd:docs"),
]


class SCPICommandProvider(Provider):
    """Fuzzy-searchable provider that surfaces REPL commands and TUI actions.

    - discover(): shows TUI actions + REPL commands when the palette opens
    - search(query): fuzzy-filters using Textual's built-in Matcher
    - Selecting a command dispatches it or runs a TUI action
    """

    async def startup(self) -> None:
        """Pre-warm the completion list from the dispatcher."""
        dispatcher = getattr(self.app, "_dispatcher", None)
        if dispatcher is not None and hasattr(dispatcher, "get_completions"):
            self._repl_commands: list[str] = dispatcher.get_completions("")
        else:
            self._repl_commands = []

    async def discover(self) -> Hits:
        """Yield TUI actions first, then REPL commands."""
        for display, _help_text, target in _TUI_ACTIONS:
            yield DiscoveryHit(
                display=display,
                command=lambda t=target: self._execute(t),
                text=display,
            )
        for cmd in self._repl_commands:
            yield DiscoveryHit(
                display=cmd,
                command=lambda c=cmd: self._run(c),
                text=cmd,
            )

    async def search(self, query: str) -> Hits:
        """Yield fuzzy-matched commands for the given query."""
        matcher = self.matcher(query)
        for display, _help_text, target in _TUI_ACTIONS:
            score = matcher.match(display)
            if score > 0:
                yield Hit(
                    score=score,
                    match_display=matcher.highlight(display),
                    command=lambda t=target: self._execute(t),
                    text=display,
                )
        for cmd in self._repl_commands:
            score = matcher.match(cmd)
            if score > 0:
                yield Hit(
                    score=score,
                    match_display=matcher.highlight(cmd),
                    command=lambda c=cmd: self._run(c),
                    text=cmd,
                )

    def _execute(self, target: str) -> None:
        """Run a TUI action or dispatch a REPL command."""
        if target.startswith("action:"):
            action_name = target[7:]
            if action_name == "clear_log_view":
                from textual.widgets import TabbedContent

                self.app.query_one("#main-content", TabbedContent).active = "log-view"
            else:
                self.app.run_action(action_name)
        elif target.startswith("cmd:"):
            self._run(target[4:])

    def _run(self, cmd: str) -> None:
        """Dispatch cmd and ensure the log view is visible."""
        from textual.widgets import TabbedContent

        app = self.app
        with app.prevent():
            app.query_one("#main-content", TabbedContent).active = "log-view"
        app._dispatch_command(cmd)
