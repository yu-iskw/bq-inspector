"""Lineage response error envelope builder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from bq_inspector.core.shared.errors import BqInspectFailure

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
    request: dict[str, object],
    error: BaseException,
    *,
    response_kind: Literal["links", "graph"],
) -> dict[str, object]:
    """Build a lineage response envelope from a BqInspectFailure."""
    errors: list[BqInspectError] = []

    if isinstance(error, BqInspectFailure):
        errors.append(error.details)
    else:
        raise error

    envelope: dict[str, object] = {
        "schemaVersion": schema_version,
        "tool": tool,
        "request": request,
        "links": [],
        "warnings": [],
        "errors": errors,
    }
    if response_kind == "graph":
        envelope["unreachable"] = []
    else:
        envelope["page"] = {}
    return envelope


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
