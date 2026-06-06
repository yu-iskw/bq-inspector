"""Shared inspection response error envelope builder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.shared.errors import BqInspectFailure

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import BqInspectError, BqInspectSchemaVersion, ToolBlock


def inspection_error_envelope(
    schema_version: BqInspectSchemaVersion,
    tool: ToolBlock,
    request: dict[str, Any],
    error: BaseException,
    *,
    response_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a standard inspection response envelope from a BqInspectFailure."""
    errors: list[BqInspectError] = []

    if isinstance(error, BqInspectFailure):
        errors.append(error.details)
    else:
        raise error

    envelope: dict[str, Any] = {
        "schemaVersion": schema_version,
        "tool": tool,
        "request": request,
        "warnings": [],
        "errors": errors,
    }
    if response_fields is not None:
        envelope.update(response_fields)
    return envelope
