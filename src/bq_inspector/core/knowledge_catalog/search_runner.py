"""Shared orchestration for Knowledge Catalog search use cases."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.error_envelope import catalog_knowledge_error_envelope
from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


async def run_catalog_search(
    *,
    tool_version: str,
    request_echo: dict[str, Any],
    search: Callable[[], Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    """Run a catalog search and map failures to the standard response envelope."""
    envelope = build_tool_envelope(tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]
    try:
        return await search()
    except BqInspectFailure as error:
        return catalog_knowledge_error_envelope(
            schema_version,
            tool,
            request_echo,
            error,
            response_fields={
                "entries": [],
                "page": {"nextPageToken": None, "unreachable": []},
            },
        )
