"""Knowledge Catalog response error envelope builder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.shared.inspection_error_envelope import inspection_error_envelope

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import BqInspectSchemaVersion, ToolBlock


def catalog_knowledge_error_envelope(
    schema_version: BqInspectSchemaVersion,
    tool: ToolBlock,
    request: dict[str, Any],
    error: BaseException,
    *,
    response_fields: dict[str, Any],
) -> dict[str, Any]:
    """Build a Knowledge Catalog response envelope from a BqInspectFailure."""
    return inspection_error_envelope(
        schema_version,
        tool,
        request,
        error,
        response_fields=response_fields,
    )
