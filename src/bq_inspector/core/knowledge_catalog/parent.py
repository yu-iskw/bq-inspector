"""Knowledge Catalog resource path helpers."""

from __future__ import annotations


def catalog_parent(project_id: str, location: str) -> str:
    """Return a Dataplex location parent resource path."""
    return f"projects/{project_id}/locations/{location}"
