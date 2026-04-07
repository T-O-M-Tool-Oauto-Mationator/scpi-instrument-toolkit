"""Measurement recording and access for the REPL."""

import time
from typing import Any


class MeasurementStore:
    """Stores labeled measurements taken during a REPL session."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._t0: float = time.monotonic()

    def record(self, label: str, value: Any, unit: str = "", source: str = "") -> None:
        """Record a new measurement."""
        self._entries.append(
            {
                "label": label,
                "value": value,
                "unit": unit,
                "source": source,
                "time": time.monotonic() - self._t0,
            }
        )

    def clear(self) -> None:
        """Remove all stored measurements."""
        self._entries.clear()

    def get_last(self) -> dict[str, Any] | None:
        """Return the most recent measurement, or None."""
        return self._entries[-1] if self._entries else None

    def get_by_label(self, label: str) -> dict[str, Any] | None:
        """Return the last measurement with the given label, or None."""
        for entry in reversed(self._entries):
            if entry["label"] == label:
                return entry
        return None

    def as_value_dict(self) -> dict[str, Any]:
        """Return {label: value} mapping (last wins for duplicate labels)."""
        return {e["label"]: e["value"] for e in self._entries}

    @property
    def entries(self) -> list[dict[str, Any]]:
        """Direct access to the underlying list (for backward compat)."""
        return self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def __bool__(self) -> bool:
        return bool(self._entries)
