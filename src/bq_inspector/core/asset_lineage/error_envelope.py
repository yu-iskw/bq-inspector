"""Asset-lineage response error envelope builder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.core.shared.types import (
    LineageGraphResponse,
    LineageLinksResponse,
    LineageRequestEcho,
)

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import (
        BqInspectError,
        BqInspectSchemaVersion,
        BqInspectWarning,
        ToolBlock,
    )


def lineage_error_envelope(
    schema_version: BqInspectSchemaVersion,
    tool: ToolBlock,
    request: LineageRequestEcho,
    error: BaseException,
    *,
    response_kind: Literal["links", "graph"],
) -> LineageLinksResponse | LineageGraphResponse:
    """Build a lineage response envelope from a BqInspectFailure."""
    errors: list[BqInspectError] = []

    if isinstance(error, BqInspectFailure):
        errors.append(error.details)
    else:
        raise error

    if response_kind == "graph":
        return LineageGraphResponse(
            schemaVersion=schema_version,
            tool=tool,
            request=request,
            links=[],
            unreachable=[],
            warnings=[],
            errors=errors,
        )

    return LineageLinksResponse(
        schemaVersion=schema_version,
        tool=tool,
        request=request,
        links=[],
        page={},
        warnings=[],
        errors=errors,
    )


def unreachable_warnings(unreachable: list[str]) -> list[BqInspectWarning]:
    """Return warnings when the lineage graph may be incomplete."""
    if len(unreachable) == 0:
        return []
    return [
        {
            "code": "LINEAGE_UNREACHABLE",
            "message": ("Some lineage locations were unreachable; the link set may be incomplete."),
        }
    ]
