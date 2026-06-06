"""List Knowledge Catalog resources under a parent."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.request_build import (
    build_list_request_echo,
    build_list_sdk_request,
)
from bq_inspector.core.knowledge_catalog.search_runner import run_catalog_use_case

if TYPE_CHECKING:
    from collections.abc import Callable

    from bq_inspector.core.shared.types import BqInspectSchemaVersion, ToolBlock
    from bq_inspector.input.parsed_input_types import ParsedKnowledgeCatalogListInput
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient
    from bq_inspector.knowledge_catalog.types.requests import ListByParentRequest
    from bq_inspector.knowledge_catalog.types.responses import ListResourcesPage


async def list_catalog_resources(
    params: ParsedKnowledgeCatalogListInput,
    *,
    client: CatalogInspectionClient,
    tool_version: str,
    collection_key: str,
    fetch: Callable[[CatalogInspectionClient, ListByParentRequest], Any],
) -> dict[str, Any]:
    """List Knowledge Catalog resources and return a stable JSON envelope."""
    request_echo = build_list_request_echo(params)
    sdk_request = build_list_sdk_request(params)

    async def execute(
        schema_version: BqInspectSchemaVersion,
        tool: ToolBlock,
    ) -> dict[str, Any]:
        page: ListResourcesPage = await fetch(client, sdk_request)
        next_page_token = page.get("nextPageToken")
        return {
            "schemaVersion": schema_version,
            "tool": tool,
            "request": request_echo,
            collection_key: page.get("resources", []),
            "page": {"nextPageToken": next_page_token or None},
            "warnings": [],
            "errors": [],
        }

    return await run_catalog_use_case(
        tool_version=tool_version,
        request_echo=request_echo,
        response_fields_on_error={
            collection_key: [],
            "page": {"nextPageToken": None},
        },
        execute=execute,
    )
