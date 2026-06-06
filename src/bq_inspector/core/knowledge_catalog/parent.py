"""Knowledge Catalog resource path helpers."""

from __future__ import annotations


def search_parent(project_id: str, location: str = "global") -> str:
    """Return the parent resource for Knowledge Catalog search."""
    return f"projects/{project_id}/locations/{location}"


def lookup_parent(project_id: str, location: str) -> str:
    """Return the parent resource for entry lookup."""
    return f"projects/{project_id}/locations/{location}"
