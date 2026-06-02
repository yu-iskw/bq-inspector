"""List tables in a dataset."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure

if TYPE_CHECKING:
    from bq_inspector.bigquery.port.inspection_client import BigQueryInspectionClient
    from bq_inspector.bigquery.types.refs import DatasetRef
    from bq_inspector.core.shared.types import BqInspectError, TablesListResponse


async def list_tables_metadata(
    ref: DatasetRef,
    *,
    client: BigQueryInspectionClient,
    tool_version: str,
) -> TablesListResponse:
    """Return table list metadata in the tables list envelope."""
    envelope = build_tool_envelope(tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]

    try:
        tables = await client.list_tables(ref)
        return {
            "schemaVersion": schema_version,
            "tool": tool,
            "request": {
                "projectId": ref["projectId"],
                "datasetId": ref["datasetId"],
            },
            "tables": tables,
            "warnings": [],
            "errors": [],
        }
    except BqInspectFailure as error:
        errors: list[BqInspectError] = [error.details]
        return {
            "schemaVersion": schema_version,
            "tool": tool,
            "request": {
                "projectId": ref["projectId"],
                "datasetId": ref["datasetId"],
            },
            "tables": [],
            "warnings": [],
            "errors": errors,
        }
