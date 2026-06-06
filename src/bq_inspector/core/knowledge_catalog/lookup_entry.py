"""Lookup a Knowledge Catalog entry by canonical name."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.request_build import (
    build_lookup_request_echo,
    build_lookup_sdk_request,
)
from bq_inspector.core.knowledge_catalog.resource_command import fetch_catalog_resource

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import ParsedKnowledgeCatalogLookupInput
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient


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
        build_request=build_lookup_sdk_request,
        fetch=lambda catalog_client, request: catalog_client.lookup_entry(request),
    )
