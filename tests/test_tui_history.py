"""Unit and integration tests for CommandHistory - CP2."""

from __future__ import annotations

import asyncio

from lab_instruments.tui.history import CommandHistory

# ---------------------------------------------------------------------------
# Pure unit tests - no Textual dependency
# ---------------------------------------------------------------------------


class TestCommandHistory:
    def test_push_basic(self):
        h = CommandHistory()
        h.push("scan")
        h.push("psu set 5")
        h.push("dmm read")
        assert len(h) == 3

    def test_push_empty_string_ignored(self):
        h = CommandHistory()
        h.push("")
        h.push("   ")
        assert len(h) == 1  # whitespace is not stripped here; only empty str ignored

    def test_push_truly_empty_ignored(self):
        h = CommandHistory()
        h.push("")
        assert len(h) == 0

    def test_push_deduplicates_consecutive(self):
        h = CommandHistory()
        h.push("psu set 5")
        h.push("psu set 5")
        assert len(h) == 1

    def test_push_allows_non_consecutive_duplicate(self):
        h = CommandHistory()
        h.push("scan")
        h.push("psu set 5")
        h.push("scan")
        assert len(h) == 3

    def test_up_returns_most_recent_first(self):
        h = CommandHistory()
        h.push("scan")
        h.push("psu set 5")
        assert h.up() == "psu set 5"

    def test_up_walks_backwards(self):
        h = CommandHistory()
        h.push("scan")
        h.push("psu set 5")
        h.up()
        assert h.up() == "scan"

    def test_up_clamps_at_oldest(self):
        h = CommandHistory()
        h.push("scan")
        h.up()
        # Extra up() beyond oldest should stay clamped and return oldest
        assert h.up() == "scan"

    def test_up_returns_none_when_empty(self):
        h = CommandHistory()
        assert h.up() is None

    def test_down_after_up_walks_forward(self):
        h = CommandHistory()
        h.push("scan")
        h.push("psu set 5")
        h.up()  # psu set 5
        h.up()  # scan
        assert h.down() == "psu set 5"

    def test_down_past_newest_returns_none(self):
        h = CommandHistory()
        h.push("scan")
        h.up()
        assert h.down() is None  # past-end = blank input

    def test_down_returns_none_when_empty(self):
        h = CommandHistory()
        assert h.down() is None

    def test_down_at_past_end_stays_past_end(self):
        h = CommandHistory()
        h.push("scan")
        # Already at past-end; down should not crash and return None
        assert h.down() is None

    def test_push_resets_cursor(self):
        h = CommandHistory()
        h.push("scan")
        h.up()  # move cursor back
        h.push("psu set 5")  # should reset cursor
        # First up() should now return most recent entry
        assert h.up() == "psu set 5"

    def test_reset_moves_cursor_to_past_end(self):
        h = CommandHistory()
        h.push("scan")
        h.push("psu set 5")
        h.up()
        h.reset()
        assert h.down() is None  # already at past-end after reset

    def test_max_size_evicts_oldest(self):
        h = CommandHistory(max_size=3)
        for i in range(4):
            h.push(f"cmd{i}")
        assert len(h) == 3
        assert "cmd0" not in h.entries
        assert h.entries[0] == "cmd1"

    def test_entries_returns_copy(self):
        h = CommandHistory()
        h.push("scan")
        copy = h.entries
        copy.append("injected")
        assert len(h) == 1  # internal list unaffected


# ---------------------------------------------------------------------------
# Integration tests - Textual Pilot
# ---------------------------------------------------------------------------


class _StubDispatcher:
    def __init__(self):
        self._commands: list[str] = []
        self._completions: dict[str, list[str]] = {}

    def handle_command(self, cmd: str) -> str:
        self._commands.append(cmd)
        return f"OK: {cmd}"

    def get_completions(self, text: str) -> list[str]:
        return list(self._completions.get(text, []))


class TestCommandHistoryInApp:
    def _make_app(self):
        from lab_instruments.tui.app import SCPIApp

        stub = _StubDispatcher()
        return SCPIApp(stub), stub

    def test_history_populated_after_submit(self):
        """Submitted commands must appear in app._history."""

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                for cmd in ("scan", "psu set 5"):
                    await pilot.click("#cmd_input")
                    for ch in cmd:
                        await pilot.press(ch)
                    await pilot.press("enter")
                    await pilot.pause(0.05)
                assert app._history.entries == ["scan", "psu set 5"]

        asyncio.run(inner())

    def test_up_arrow_fills_input_with_last_command(self):
        """Arrow-up after a submit should restore the last command."""
        from textual.widgets import Input

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                await pilot.click("#cmd_input")
                for ch in "scan":
                    await pilot.press(ch)
                await pilot.press("enter")
                await pilot.pause(0.05)
                await pilot.press("up")
                await pilot.pause(0.05)
                inp = app.query_one("#cmd_input", Input)
                assert inp.value == "scan"

        asyncio.run(inner())

    def test_down_arrow_clears_after_history(self):
        """Arrow-up then arrow-down should restore blank input."""
        from textual.widgets import Input

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                await pilot.click("#cmd_input")
                for ch in "scan":
                    await pilot.press(ch)
                await pilot.press("enter")
                await pilot.pause(0.05)
                await pilot.press("up")
                await pilot.pause(0.05)
                await pilot.press("down")
                await pilot.pause(0.05)
                inp = app.query_one("#cmd_input", Input)
                assert inp.value == ""

        asyncio.run(inner())

    def test_consecutive_duplicate_not_double_stored(self):
        """Submitting the same command twice should store it only once."""

        async def inner():
            app, _ = self._make_app()
            async with app.run_test(size=(80, 24)) as pilot:
                for _ in range(2):
                    await pilot.click("#cmd_input")
                    for ch in "scan":
                        await pilot.press(ch)
                    await pilot.press("enter")
                    await pilot.pause(0.05)
                assert len(app._history) == 1

        asyncio.run(inner())
