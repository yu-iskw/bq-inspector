"""Shared orchestration for asset-lineage search use cases."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from bq_inspector.core.asset_lineage.error_envelope import lineage_error_envelope
from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bq_inspector.core.shared.types import (
        BqInspectSchemaVersion,
        LineageGraphResponse,
        LineageLinksResponse,
        LineageRequestEcho,
        ToolBlock,
    )


def _tool_envelope(tool_version: str) -> tuple[BqInspectSchemaVersion, ToolBlock]:
    envelope = build_tool_envelope(tool_version)
    return envelope["schemaVersion"], envelope["tool"]


@overload
async def run_asset_lineage_search(
    *,
    tool_version: str,
    request_echo: LineageRequestEcho,
    response_kind: Literal["links"],
    search: Callable[
        [BqInspectSchemaVersion, ToolBlock],
        Awaitable[LineageLinksResponse],
    ],
) -> LineageLinksResponse:
    """Overload stub for links search."""


@overload
async def run_asset_lineage_search(
    *,
    tool_version: str,
    request_echo: LineageRequestEcho,
    response_kind: Literal["graph"],
    search: Callable[
        [BqInspectSchemaVersion, ToolBlock],
        Awaitable[LineageGraphResponse],
    ],
) -> LineageGraphResponse:
    """Overload stub for graph search."""


async def run_asset_lineage_search(
    *,
    tool_version: str,
    request_echo: LineageRequestEcho,
    response_kind: Literal["links", "graph"],
    search: Callable[
        [BqInspectSchemaVersion, ToolBlock],
        Awaitable[LineageLinksResponse | LineageGraphResponse],
    ],
) -> LineageLinksResponse | LineageGraphResponse:
    """Run a lineage search and map failures to the standard response envelope."""
    schema_version, tool = _tool_envelope(tool_version)
    try:
        return await search(schema_version, tool)
    except BqInspectFailure as error:
        return lineage_error_envelope(
            schema_version,
            tool,
            request_echo,
            error,
            response_kind=response_kind,
        )
