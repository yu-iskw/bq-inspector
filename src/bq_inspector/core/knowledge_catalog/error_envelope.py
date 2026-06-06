"""Knowledge Catalog response error envelope builder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.shared.errors import BqInspectFailure

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import BqInspectError, BqInspectSchemaVersion, ToolBlock


def catalog_knowledge_error_envelope(
    schema_version: BqInspectSchemaVersion,
    tool: ToolBlock,
    request: dict[str, Any],
    error: BaseException,
    *,
    response_fields: dict[str, Any],
) -> dict[str, Any]:
    """Build a Knowledge Catalog response envelope from a BqInspectFailure."""
    errors: list[BqInspectError] = []

    if isinstance(error, BqInspectFailure):
        errors.append(error.details)
    else:
        raise error

    return {
        "schemaVersion": schema_version,
        "tool": tool,
        "request": request,
        **response_fields,
        "warnings": [],
        "errors": errors,
    }
