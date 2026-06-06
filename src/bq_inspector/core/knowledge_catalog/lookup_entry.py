"""Lookup a Knowledge Catalog entry by canonical name."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.entry_view_fields import entry_view_fields_from
from bq_inspector.core.knowledge_catalog.parent import catalog_parent
from bq_inspector.core.knowledge_catalog.resource_command import fetch_catalog_resource
from bq_inspector.core.shared.impersonation_fields import merge_impersonation_into

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import ParsedKnowledgeCatalogLookupInput
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient
    from bq_inspector.knowledge_catalog.types.requests import LookupEntryRequest


def build_lookup_request_echo(params: ParsedKnowledgeCatalogLookupInput) -> dict[str, Any]:
    """Build the request echo for catalog entry lookup."""
    echo: dict[str, Any] = {
        "projectId": params["projectId"],
        "location": params["location"],
        "entry": params["entry"],
        **entry_view_fields_from(params),
    }
    return merge_impersonation_into(echo, params)


def _build_sdk_lookup_request(params: ParsedKnowledgeCatalogLookupInput) -> LookupEntryRequest:
    return {
        "name": catalog_parent(params["projectId"], params["location"]),
        "entry": params["entry"],
        **entry_view_fields_from(params),
    }


async def lookup_catalog_entry(
    params: ParsedKnowledgeCatalogLookupInput,
    *,
    client: CatalogInspectionClient,
    tool_version: str,
) -> dict[str, Any]:
    """Lookup a Knowledge Catalog entry and return a stable JSON envelope."""
    return await fetch_catalog_resource(
        params,
        client=client,
        tool_version=tool_version,
        build_echo=build_lookup_request_echo,
        build_request=_build_sdk_lookup_request,
        fetch=lambda catalog_client, request: catalog_client.lookup_entry(request),
    )
