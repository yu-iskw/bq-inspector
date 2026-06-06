"""Search Knowledge Catalog entries."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.parent import search_parent
from bq_inspector.core.knowledge_catalog.search_runner import run_catalog_search
from bq_inspector.core.knowledge_catalog.warnings import unreachable_search_warnings
from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.impersonation_fields import merge_impersonation_into
from bq_inspector.knowledge_catalog.defaults import (
    CATALOG_SEARCH_LOCATION,
    DEFAULT_CATALOG_SEARCH_PAGE_SIZE,
)

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import ParsedKnowledgeCatalogSearchInput
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient
    from bq_inspector.knowledge_catalog.types.requests import SearchEntriesRequest


def build_search_request_echo(params: ParsedKnowledgeCatalogSearchInput) -> dict[str, Any]:
    """Build the request echo for catalog search."""
    echo: dict[str, Any] = {
        "projectId": params["projectId"],
        "location": params.get("location", CATALOG_SEARCH_LOCATION),
        "query": params["query"],
        "pageSize": params.get("pageSize", DEFAULT_CATALOG_SEARCH_PAGE_SIZE),
    }
    scope = params.get("scope")
    if scope is not None:
        echo["scope"] = scope
    semantic_search = params.get("semanticSearch")
    if semantic_search is not None:
        echo["semanticSearch"] = semantic_search
    order_by = params.get("orderBy")
    if order_by is not None:
        echo["orderBy"] = order_by
    page_token = params.get("pageToken")
    if page_token is not None:
        echo["pageToken"] = page_token
    return merge_impersonation_into(echo, params)


def _build_sdk_search_request(params: ParsedKnowledgeCatalogSearchInput) -> SearchEntriesRequest:
    location = params.get("location", CATALOG_SEARCH_LOCATION)
    sdk_request: SearchEntriesRequest = {
        "name": search_parent(params["projectId"], location),
        "query": params["query"],
        "pageSize": params.get("pageSize", DEFAULT_CATALOG_SEARCH_PAGE_SIZE),
    }
    scope = params.get("scope")
    if scope is not None:
        sdk_request["scope"] = scope
    semantic_search = params.get("semanticSearch")
    if semantic_search is not None:
        sdk_request["semanticSearch"] = semantic_search
    order_by = params.get("orderBy")
    if order_by is not None:
        sdk_request["orderBy"] = order_by
    page_token = params.get("pageToken")
    if page_token is not None:
        sdk_request["pageToken"] = page_token
    return sdk_request


async def search_catalog_entries(
    params: ParsedKnowledgeCatalogSearchInput,
    *,
    client: CatalogInspectionClient,
    tool_version: str,
) -> dict[str, Any]:
    """Search Knowledge Catalog entries and return a stable JSON envelope."""
    request_echo = build_search_request_echo(params)
    sdk_request = _build_sdk_search_request(params)

    async def search() -> dict[str, Any]:
        envelope = build_tool_envelope(tool_version)
        page = await client.search_entries(sdk_request)
        unreachable = list(page.get("unreachable", []))
        page_block: dict[str, Any] = {
            "unreachable": unreachable,
        }
        total_size = page.get("totalSize")
        if total_size is not None:
            page_block["totalSize"] = total_size
        next_page_token = page.get("nextPageToken")
        page_block["nextPageToken"] = next_page_token or None

        return {
            "schemaVersion": envelope["schemaVersion"],
            "tool": envelope["tool"],
            "request": request_echo,
            "entries": page.get("entries", []),
            "page": page_block,
            "warnings": unreachable_search_warnings(unreachable),
            "errors": [],
        }

    return await run_catalog_search(
        tool_version=tool_version,
        request_echo=request_echo,
        search=search,
    )
