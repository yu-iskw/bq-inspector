"""List Knowledge Catalog resources under a parent."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.error_envelope import catalog_knowledge_error_envelope
from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.core.shared.impersonation_fields import merge_impersonation_into
from bq_inspector.knowledge_catalog.defaults import DEFAULT_CATALOG_LIST_PAGE_SIZE

if TYPE_CHECKING:
    from collections.abc import Callable

    from bq_inspector.input.parsed_input_types import ParsedKnowledgeCatalogListInput
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient
    from bq_inspector.knowledge_catalog.types.requests import ListByParentRequest
    from bq_inspector.knowledge_catalog.types.responses import ListResourcesPage


def build_list_request_echo(params: ParsedKnowledgeCatalogListInput) -> dict[str, Any]:
    """Build the request echo for a catalog list command."""
    echo: dict[str, Any] = {
        "parent": params["parent"],
        "pageSize": params.get("pageSize", DEFAULT_CATALOG_LIST_PAGE_SIZE),
    }
    page_token = params.get("pageToken")
    if page_token is not None:
        echo["pageToken"] = page_token
    filter_value = params.get("filter")
    if filter_value is not None:
        echo["filter"] = filter_value
    order_by = params.get("orderBy")
    if order_by is not None:
        echo["orderBy"] = order_by
    return merge_impersonation_into(echo, params)


def _build_sdk_list_request(params: ParsedKnowledgeCatalogListInput) -> ListByParentRequest:
    sdk_request: ListByParentRequest = {
        "parent": params["parent"],
        "pageSize": params.get("pageSize", DEFAULT_CATALOG_LIST_PAGE_SIZE),
    }
    page_token = params.get("pageToken")
    if page_token is not None:
        sdk_request["pageToken"] = page_token
    filter_value = params.get("filter")
    if filter_value is not None:
        sdk_request["filter"] = filter_value
    order_by = params.get("orderBy")
    if order_by is not None:
        sdk_request["orderBy"] = order_by
    return sdk_request


async def list_catalog_resources(
    params: ParsedKnowledgeCatalogListInput,
    *,
    client: CatalogInspectionClient,
    tool_version: str,
    collection_key: str,
    fetch: Callable[[CatalogInspectionClient, ListByParentRequest], Any],
) -> dict[str, Any]:
    """List Knowledge Catalog resources and return a stable JSON envelope."""
    envelope = build_tool_envelope(tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]
    request_echo = build_list_request_echo(params)
    sdk_request = _build_sdk_list_request(params)

    try:
        page: ListResourcesPage = await fetch(client, sdk_request)
        page_block: dict[str, Any] = {}
        next_page_token = page.get("nextPageToken")
        page_block["nextPageToken"] = next_page_token or None

        return {
            "schemaVersion": schema_version,
            "tool": tool,
            "request": request_echo,
            collection_key: page.get("resources", []),
            "page": page_block,
            "warnings": [],
            "errors": [],
        }
    except BqInspectFailure as error:
        return catalog_knowledge_error_envelope(
            schema_version,
            tool,
            request_echo,
            error,
            response_fields={
                collection_key: [],
                "page": {"nextPageToken": None},
            },
        )
