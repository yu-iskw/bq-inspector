"""Fully qualified names for Data Lineage API assets."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bq_inspector.bigquery.types.refs import TableRef


def table_ref_to_fqn(ref: TableRef) -> str:
    """Return the BigQuery table FQN used by the Data Lineage API."""
    return (
        f"bigquery:projects/{ref['projectId']}/datasets/{ref['datasetId']}/tables/{ref['tableId']}"
    )


def lineage_parent(client_project_id: str, location: str) -> str:
    """Return the parent resource for Data Lineage API calls."""
    return f"projects/{client_project_id}/locations/{location}"
