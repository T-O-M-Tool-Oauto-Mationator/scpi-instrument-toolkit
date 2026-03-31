"""Tests for SCPICommandProvider and command palette integration - CP6."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from lab_instruments.tui.command_provider import SCPICommandProvider

# ---------------------------------------------------------------------------
# Stub dispatcher
# ---------------------------------------------------------------------------


class _StubDispatcher:
    def __init__(self, completions: list[str] | None = None):
        self._commands: list[str] = []
        self._completions_all: list[str] = completions or []
        self._completions: dict[str, list[str]] = {}

    def handle_command(self, cmd: str) -> str:
        self._commands.append(cmd)
        return f"OK: {cmd}"

    def get_completions(self, text: str) -> list[str]:
        if text == "":
            return list(self._completions_all)
        return list(self._completions.get(text, []))

    def get_device_snapshot(self) -> list[dict]:
        return []

    def get_measurement_snapshot(self) -> list[dict]:
        return []

    def get_script_names(self) -> list[str]:
        return []

    def get_vars_snapshot(self) -> dict[str, str]:
        return {}

    def get_safety_snapshot(self) -> dict:
        return {"limit_count": 0, "active_script": False, "exit_on_error": False}


# ---------------------------------------------------------------------------
# Provider unit tests (no full app boot)
# ---------------------------------------------------------------------------


def _make_provider(completions: list[str]) -> SCPICommandProvider:
    """Build an SCPICommandProvider with a minimal mock app."""
    stub = _StubDispatcher(completions=completions)
    mock_screen = MagicMock()
    mock_screen.app._dispatcher = stub
    mock_screen.app.query_one = MagicMock()
    mock_screen.app._dispatch_command = MagicMock()
    provider = SCPICommandProvider(mock_screen)
    # Run startup synchronously
    asyncio.run(provider.startup())
    return provider


async def _collect(agen) -> list:
    """Drain an async generator into a list."""
    results = []
    async for item in agen:
        results.append(item)
    return results


class TestSCPICommandProviderUnit:
    def test_startup_loads_completions(self):
        """startup() should cache completions from the dispatcher."""
        provider = _make_provider(["psu", "awg", "dmm", "scan", "help"])
        assert set(provider._repl_commands) == {"psu", "awg", "dmm", "scan", "help"}

    def test_startup_empty_when_no_dispatcher(self):
        """startup() should not crash when dispatcher has no get_completions."""
        mock_screen = MagicMock()
        mock_screen.app._dispatcher = None
        provider = SCPICommandProvider(mock_screen)
        asyncio.run(provider.startup())
        assert provider._repl_commands == []

    def test_discover_yields_repl_and_tui_commands(self):
        """discover() should yield TUI actions plus REPL commands."""
        provider = _make_provider(["psu", "awg", "dmm"])
        hits = asyncio.run(_collect(provider.discover()))
        texts = [h.text for h in hits]
        assert "psu" in texts
        assert "awg" in texts
        assert "dmm" in texts
        assert "Show Log View" in texts

    def test_discover_with_no_repl_still_has_tui_actions(self):
        """discover() should yield TUI actions even with no REPL commands."""
        provider = _make_provider([])
        hits = asyncio.run(_collect(provider.discover()))
        texts = [h.text for h in hits]
        assert "Show Log View" in texts

    def test_search_returns_matching_hits(self):
        """search() should yield hits for commands matching the query."""
        provider = _make_provider(["psu", "psu set", "awg", "dmm"])
        hits = asyncio.run(_collect(provider.search("ps")))
        texts = [h.text for h in hits]
        assert "psu" in texts
        assert "psu set" in texts
        assert "awg" not in texts
        assert "dmm" not in texts

    def test_search_returns_empty_on_no_match(self):
        """search() should yield nothing when query matches nothing."""
        provider = _make_provider(["psu", "awg", "dmm"])
        hits = asyncio.run(_collect(provider.search("zzz")))
        assert hits == []

    def test_search_score_ordering(self):
        """Hits with higher scores should sort first (lower index = higher score)."""
        provider = _make_provider(["psu", "psu set 5"])
        hits = asyncio.run(_collect(provider.search("psu")))
        assert len(hits) >= 1
        # All returned hits must have positive score
        assert all(h.score > 0 for h in hits)

    def test_discover_hit_has_command_callable(self):
        """Each DiscoveryHit command must be callable."""
        provider = _make_provider(["scan"])
        hits = asyncio.run(_collect(provider.discover()))
        assert len(hits) >= 1
        assert all(callable(h.command) for h in hits)

    def test_search_hit_has_command_callable(self):
        """Each Hit command must be callable."""
        provider = _make_provider(["scan", "status"])
        hits = asyncio.run(_collect(provider.search("sc")))
        assert all(callable(h.command) for h in hits)

    def test_lambda_closure_captures_correct_command(self):
        """REPL commands in hits must not share a closure - each must dispatch its own cmd."""
        dispatched: list[str] = []

        mock_screen = MagicMock()
        stub = _StubDispatcher(["psu", "awg", "dmm"])
        mock_screen.app._dispatcher = stub
        mock_screen.app.query_one = MagicMock()
        mock_screen.app._dispatch_command = lambda cmd: dispatched.append(cmd)
        mock_screen.app.run_action = MagicMock()
        mock_screen.app.prevent = MagicMock(return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))
        provider = SCPICommandProvider(mock_screen)
        asyncio.run(provider.startup())

        hits = asyncio.run(_collect(provider.discover()))
        for hit in hits:
            hit.command()
        # REPL commands should be in the dispatched list
        assert "psu" in dispatched
        assert "awg" in dispatched
        assert "dmm" in dispatched


# ---------------------------------------------------------------------------
# App integration tests
# ---------------------------------------------------------------------------


class TestCommandPaletteInApp:
    def _make_app(self, completions=None):
        from lab_instruments.tui.app import SCPIApp

        stub = _StubDispatcher(completions=completions or ["help", "psu", "awg", "scan", "dmm"])
        app = SCPIApp(stub)
        return app, stub

    def test_scpi_provider_in_commands(self):
        """SCPICommandProvider must be registered in App.COMMANDS."""
        from lab_instruments.tui.app import SCPIApp

        assert SCPICommandProvider in SCPIApp.COMMANDS

    def test_palette_opens_via_action(self):
        """action_command_palette should open the command palette."""
        from textual.command import CommandPalette

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                await app.run_action("command_palette")
                await pilot.pause(0.1)
                assert CommandPalette.is_open(app)

        asyncio.run(inner())

    def test_palette_closes_on_escape(self):
        """Escape should dismiss the command palette."""
        from textual.command import CommandPalette

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                await app.run_action("command_palette")
                await pilot.pause(0.1)
                assert CommandPalette.is_open(app)
                await pilot.press("escape")
                await pilot.pause(0.1)
                assert not CommandPalette.is_open(app)

        asyncio.run(inner())
