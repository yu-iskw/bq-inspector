"""Shared orchestration for Knowledge Catalog use cases."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.core.shared.inspection_error_envelope import inspection_error_envelope

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bq_inspector.core.shared.types import BqInspectSchemaVersion, ToolBlock


async def run_catalog_use_case(
    *,
    tool_version: str,
    request_echo: dict[str, Any],
    response_fields_on_error: dict[str, Any],
    execute: Callable[
        [BqInspectSchemaVersion, ToolBlock],
        Awaitable[dict[str, Any]],
    ],
) -> dict[str, Any]:
    """Run a catalog use case and map failures to the standard response envelope."""
    envelope = build_tool_envelope(tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]
    try:
        return await execute(schema_version, tool)
    except BqInspectFailure as error:
        return inspection_error_envelope(
            schema_version,
            tool,
            request_echo,
            error,
            response_fields=response_fields_on_error,
        )
