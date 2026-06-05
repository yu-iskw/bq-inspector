"""Tests for asset-lineage warning helpers."""

from __future__ import annotations

from bq_inspector.core.asset_lineage.warnings import unreachable_warnings


def test_unreachable_warnings_empty_when_all_locations_reachable() -> None:
    assert unreachable_warnings([]) == []


def test_unreachable_warnings_reports_incomplete_graph() -> None:
    warnings = unreachable_warnings(["projects/p/locations/us-east1"])
    assert len(warnings) == 1
    assert warnings[0]["code"] == "LINEAGE_UNREACHABLE"
