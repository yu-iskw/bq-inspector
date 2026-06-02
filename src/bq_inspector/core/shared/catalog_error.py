"""Catalog resource error envelope builder."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

from bq_inspector.core.shared.errors import BqInspectFailure

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import (
        BqInspectError,
        BqInspectSchemaVersion,
        CatalogResourceResponse,
        ToolBlock,
    )


class CatalogResourceRequest(TypedDict):
    """Catalog resource identifiers echoed in error responses."""

    projectId: str
    datasetId: str
    tableId: NotRequired[str]


def catalog_error_envelope(
    schema_version: BqInspectSchemaVersion,
    tool: ToolBlock,
    request: CatalogResourceRequest,
    error: BaseException,
) -> CatalogResourceResponse:
    """Build a catalog response envelope from a BqInspectFailure."""
    errors: list[BqInspectError] = []

    if isinstance(error, BqInspectFailure):
        errors.append(error.details)
    else:
        raise error

    echo_request: dict[str, str] = {
        "projectId": request["projectId"],
        "datasetId": request["datasetId"],
    }
    table_id = request.get("tableId")
    if table_id is not None and table_id:
        echo_request["tableId"] = table_id

    return {
        "schemaVersion": schema_version,
        "tool": tool,
        "request": echo_request,
        "warnings": [],
        "errors": errors,
    }
