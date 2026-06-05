"""Tests for lineage FQN helpers."""

from __future__ import annotations

from bq_inspector.core.lineage.fqn import lineage_parent, table_ref_to_fqn


def test_table_ref_to_fqn() -> None:
    fqn = table_ref_to_fqn(
        {
            "projectId": "data-proj",
            "datasetId": "analytics",
            "tableId": "events",
        }
    )
    assert fqn == "bigquery:projects/data-proj/datasets/analytics/tables/events"


def test_lineage_parent() -> None:
    assert lineage_parent("billing-proj", "us") == "projects/billing-proj/locations/us"
