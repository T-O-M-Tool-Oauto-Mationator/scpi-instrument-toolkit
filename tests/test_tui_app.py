"""Smoke tests for SCPIApp - CP1: test harness + tab completion."""

from __future__ import annotations

import asyncio

from textual.widgets import Input, RichLog

from lab_instruments.tui.app import SCPIApp


class _StubDispatcher:
    """State-tracking stub dispatcher. Tracks commands issued; never returns constants."""

    def __init__(self):
        self._commands: list[str] = []
        self._completions: dict[str, list[str]] = {}

    def handle_command(self, cmd: str, line_callback=None) -> str:
        self._commands.append(cmd)
        return f"OK: {cmd}"

    def get_completions(self, text: str) -> list[str]:
        return list(self._completions.get(text, []))


class TestSCPIAppCP1:
    def test_app_mounts_expected_widgets(self):
        """App should mount RichLog and Input on startup."""

        async def inner():
            stub = _StubDispatcher()
            app = SCPIApp(stub)
            async with app.run_test(size=(80, 24)):
                assert app.query_one("#log-output", RichLog) is not None
                assert app.query_one("#cmd_input", Input) is not None

        asyncio.run(inner())

    def test_input_submitted_calls_dispatcher(self):
        """Submitting a command should call dispatcher.handle_command."""

        async def inner():
            stub = _StubDispatcher()
            app = SCPIApp(stub)
            async with app.run_test(size=(80, 24)) as pilot:
                await pilot.click("#cmd_input")
                await pilot.press("p", "s", "u")
                await pilot.press("enter")
                await pilot.pause(0.1)
                assert "psu" in stub._commands

        asyncio.run(inner())

    def test_clear_log_binding(self):
        """Ctrl+L should clear the output log."""

        async def inner():
            stub = _StubDispatcher()
            app = SCPIApp(stub)
            async with app.run_test(size=(80, 24)) as pilot:
                log = app.query_one("#log-output", RichLog)
                log.write("some output")
                await pilot.press("ctrl+l")
                await pilot.pause(0.05)
                # After clear, the log should have no lines
                assert len(log.lines) == 0

        asyncio.run(inner())

    def test_quit_action(self):
        """action_quit should exit the app cleanly."""

        async def inner():
            stub = _StubDispatcher()
            app = SCPIApp(stub)
            async with app.run_test(size=(80, 24)) as pilot:
                await app.run_action("quit")
                await pilot.pause(0.05)
                assert app.return_code is not None

        asyncio.run(inner())

    def test_input_has_suggester(self):
        """The Input widget should be configured with a ReplSuggester."""

        async def inner():
            from lab_instruments.tui.completer import ReplSuggester

            stub = _StubDispatcher()
            app = SCPIApp(stub)
            async with app.run_test(size=(80, 24)):
                inp = app.query_one("#cmd_input", Input)
                assert isinstance(inp.suggester, ReplSuggester)

        asyncio.run(inner())

    def test_empty_command_not_dispatched(self):
        """Submitting an empty/whitespace command should not call dispatcher."""

        async def inner():
            stub = _StubDispatcher()
            app = SCPIApp(stub)
            async with app.run_test(size=(80, 24)) as pilot:
                await pilot.click("#cmd_input")
                await pilot.press("enter")
                await pilot.press("space")
                await pilot.press("enter")
                await pilot.pause(0.05)
                assert stub._commands == []

        asyncio.run(inner())
