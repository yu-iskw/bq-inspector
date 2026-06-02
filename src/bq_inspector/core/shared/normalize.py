"""String normalization helpers."""

from __future__ import annotations


def normalize_optional_trimmed(value: str | None) -> str | None:
    """Trim a string; return None for undefined, blank, or whitespace-only values."""
    if value is None:
        return None
    trimmed = value.strip()
    return None if len(trimmed) == 0 else trimmed


def normalize_delegate_list(value: list[str] | str | None) -> list[str]:
    """Normalize delegate service accounts to a trimmed, non-empty list."""
    if value is None:
        return []
    entries = value if isinstance(value, list) else [value]
    return [entry.strip() for entry in entries if entry.strip()]
