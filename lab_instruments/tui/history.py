"""Command history for the SCPI TUI input field."""

from __future__ import annotations


class CommandHistory:
    """Ordered command history with arrow-key navigation.

    Deduplicates consecutive identical entries. The position cursor sits
    past-end by default (pointing at a blank "new command" slot). Navigating
    up walks toward index 0 (oldest); down walks back toward past-end.
    """

    def __init__(self, max_size: int = 500) -> None:
        self._max_size: int = max_size
        self._entries: list[str] = []
        self._pos: int = 0  # past-end sentinel = len(_entries)

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def push(self, cmd: str) -> None:
        """Append cmd if non-empty and different from the last entry.

        Resets the cursor to past-end so the next up-arrow starts at the
        most recently submitted command.
        """
        if not cmd:
            return
        if self._entries and self._entries[-1] == cmd:
            self._pos = len(self._entries)
            return
        self._entries.append(cmd)
        if len(self._entries) > self._max_size:
            self._entries.pop(0)
        self._pos = len(self._entries)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def up(self) -> str | None:
        """Move toward older entries. Returns the entry, or None if empty."""
        if not self._entries:
            return None
        if self._pos > 0:
            self._pos -= 1
        return self._entries[self._pos]

    def down(self) -> str | None:
        """Move toward newer entries. Returns entry, or None past-end (blank input)."""
        if not self._entries:
            return None
        if self._pos < len(self._entries):
            self._pos += 1
        if self._pos == len(self._entries):
            return None
        return self._entries[self._pos]

    def reset(self) -> None:
        """Reset cursor to past-end without clearing entries."""
        self._pos = len(self._entries)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    @property
    def entries(self) -> list[str]:
        """Read-only copy of stored entries (oldest first)."""
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)
