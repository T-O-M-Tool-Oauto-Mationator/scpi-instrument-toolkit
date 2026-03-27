"""Unit tests for ReplSuggester - CP1."""

from __future__ import annotations

import asyncio


class _StubDispatcher:
    """Minimal stub with controllable completions."""

    def __init__(self):
        self._completions: dict[str, list[str]] = {}

    def handle_command(self, cmd: str) -> str:
        return ""

    def get_completions(self, text: str) -> list[str]:
        return list(self._completions.get(text, []))


class TestReplSuggester:
    def _make_suggester(self, completions: dict[str, list[str]] = None):
        from lab_instruments.tui.completer import ReplSuggester

        stub = _StubDispatcher()
        if completions:
            stub._completions = completions
        return ReplSuggester(stub)

    def test_returns_none_on_empty_input(self):
        """Empty string should always return None."""
        suggester = self._make_suggester()
        result = asyncio.run(suggester.get_suggestion(""))
        assert result is None

    def test_returns_first_prefix_match(self):
        """Should return the first candidate that starts with the typed text."""
        suggester = self._make_suggester({"ps": ["psu", "psu2"]})
        result = asyncio.run(suggester.get_suggestion("ps"))
        assert result == "psu"

    def test_returns_none_when_no_match(self):
        """Should return None when no candidate starts with typed text."""
        suggester = self._make_suggester({"ps": ["psu", "psu2"]})
        result = asyncio.run(suggester.get_suggestion("zzz"))
        assert result is None

    def test_returns_none_when_completions_empty(self):
        """Should return None when dispatcher returns empty list."""
        suggester = self._make_suggester({"psu": []})
        result = asyncio.run(suggester.get_suggestion("psu"))
        assert result is None

    def test_case_insensitive_match(self):
        """Candidate matching is case-insensitive even when candidate is lowercase."""
        # Dispatcher returns lowercase candidates; typed text is uppercase.
        # Suggester must still match "psu" against "PS".
        suggester = self._make_suggester({"PS": ["psu"]})
        result = asyncio.run(suggester.get_suggestion("PS"))
        assert result == "psu"

    def test_returns_none_on_unknown_prefix(self):
        """Returns None when dispatcher has no key for this prefix."""
        suggester = self._make_suggester({"awg": ["awg", "awg wave"]})
        result = asyncio.run(suggester.get_suggestion("ps"))
        assert result is None

    def test_exact_match_returns_candidate(self):
        """Exact match on a full command should still return the candidate."""
        suggester = self._make_suggester({"psu": ["psu"]})
        result = asyncio.run(suggester.get_suggestion("psu"))
        assert result == "psu"
