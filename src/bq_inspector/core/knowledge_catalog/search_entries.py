"""Search Knowledge Catalog entries."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.request_build import (
    build_search_request_echo,
    build_search_sdk_request,
)
from bq_inspector.core.knowledge_catalog.search_runner import run_catalog_use_case
from bq_inspector.core.knowledge_catalog.warnings import unreachable_search_warnings

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import BqInspectSchemaVersion, ToolBlock
    from bq_inspector.input.parsed_input_types import ParsedKnowledgeCatalogSearchInput
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient


async def search_catalog_entries(
    params: ParsedKnowledgeCatalogSearchInput,
    *,
    client: CatalogInspectionClient,
    tool_version: str,
) -> dict[str, Any]:
    """Search Knowledge Catalog entries and return a stable JSON envelope."""
    request_echo = build_search_request_echo(params)
    sdk_request = build_search_sdk_request(params)

    async def execute(
        schema_version: BqInspectSchemaVersion,
        tool: ToolBlock,
    ) -> dict[str, Any]:
        page = await client.search_entries(sdk_request)
        unreachable = list(page.get("unreachable", []))
        page_block: dict[str, Any] = {"unreachable": unreachable}
        total_size = page.get("totalSize")
        if total_size is not None:
            page_block["totalSize"] = total_size
        page_block["nextPageToken"] = page.get("nextPageToken") or None

        return {
            "schemaVersion": schema_version,
            "tool": tool,
            "request": request_echo,
            "entries": page.get("entries", []),
            "page": page_block,
            "warnings": unreachable_search_warnings(unreachable),
            "errors": [],
        }

    return await run_catalog_use_case(
        tool_version=tool_version,
        request_echo=request_echo,
        response_fields_on_error={
            "entries": [],
            "page": {"nextPageToken": None, "unreachable": []},
        },
        execute=execute,
    )
