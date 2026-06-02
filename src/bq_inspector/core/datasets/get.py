"""Fetch dataset metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.core.shared.catalog_error import catalog_error_envelope
from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure

if TYPE_CHECKING:
    from bq_inspector.bigquery.port.inspection_client import BigQueryInspectionClient
    from bq_inspector.bigquery.types.refs import DatasetRef
    from bq_inspector.core.shared.types import CatalogResourceResponse


async def get_dataset_metadata(
    ref: DatasetRef,
    *,
    client: BigQueryInspectionClient,
    tool_version: str,
) -> CatalogResourceResponse:
    """Return dataset metadata in the catalog resource envelope."""
    envelope = build_tool_envelope(tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]

    try:
        resource = await client.get_dataset(ref)
        return {
            "schemaVersion": schema_version,
            "tool": tool,
            "request": {
                "projectId": ref["projectId"],
                "datasetId": ref["datasetId"],
            },
            "resource": resource,
            "warnings": [],
            "errors": [],
        }
    except BqInspectFailure as error:
        return catalog_error_envelope(
            schema_version,
            tool,
            {
                "projectId": ref["projectId"],
                "datasetId": ref["datasetId"],
            },
            error,
        )
