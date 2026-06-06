"""Tests for Data Lineage FQN helpers."""

from __future__ import annotations

from bq_inspector.core.asset_lineage.fqn import lineage_parent, table_ref_to_fqn


def test_table_ref_to_fqn_uses_dataplex_dot_format() -> None:
    fqn = table_ref_to_fqn(
        {"projectId": "my-proj", "datasetId": "analytics", "tableId": "events"},
    )
    assert fqn == "bigquery:my-proj.analytics.events"


def test_lineage_parent() -> None:
    assert lineage_parent("billing-proj", "us") == "projects/billing-proj/locations/us"
