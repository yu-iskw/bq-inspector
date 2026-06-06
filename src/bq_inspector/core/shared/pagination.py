"""Shared helpers for paginated API responses."""

from __future__ import annotations


def read_next_page_token(pager: object) -> str | None:
    """Return a non-empty next page token from a pager or iterator, if present."""
    token = getattr(pager, "next_page_token", None)
    if isinstance(token, str) and len(token) > 0:
        return token
    return None
