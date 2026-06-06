"""Retrieve a Knowledge Catalog resource by canonical name."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.request_build import (
    build_get_request_echo,
    build_get_sdk_request,
)
from bq_inspector.core.knowledge_catalog.resource_command import fetch_catalog_resource

if TYPE_CHECKING:
    from collections.abc import Callable

    from bq_inspector.input.parsed_input_types import ParsedKnowledgeCatalogGetInput
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient
    from bq_inspector.knowledge_catalog.types.requests import GetByNameRequest


async def get_catalog_resource(
    params: ParsedKnowledgeCatalogGetInput,
    *,
    client: CatalogInspectionClient,
    tool_version: str,
    fetch: Callable[[CatalogInspectionClient, GetByNameRequest], Any],
) -> dict[str, Any]:
    """Retrieve a Knowledge Catalog resource and return a stable JSON envelope."""
    return await fetch_catalog_resource(
        params,
        client=client,
        tool_version=tool_version,
        build_echo=build_get_request_echo,
        build_request=build_get_sdk_request,
        fetch=fetch,
    )
