"""Structural types for BigQuery Job REST resources (subset used by projections)."""

from __future__ import annotations

from typing import Any

BigQueryJobDict = dict[str, Any]


def is_big_query_job(value: object) -> value is BigQueryJobDict:
    """Return True when value looks like a BigQuery Job object."""
    return isinstance(value, dict) and not isinstance(value, list)
