"""Structural types for BigQuery Job REST resources (subset used by projections)."""

from __future__ import annotations


def is_big_query_job(value: object) -> bool:
    """Return True when value looks like a BigQuery Job object."""
    return isinstance(value, dict) and not isinstance(value, list)
