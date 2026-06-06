"""Retrieve a Knowledge Catalog resource by canonical name."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.entry_view_fields import entry_view_fields_from
from bq_inspector.core.knowledge_catalog.resource_command import fetch_catalog_resource
from bq_inspector.core.shared.impersonation_fields import merge_impersonation_into

if TYPE_CHECKING:
    from collections.abc import Callable

    from bq_inspector.input.parsed_input_types import ParsedKnowledgeCatalogGetInput
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient
    from bq_inspector.knowledge_catalog.types.requests import GetByNameRequest


def build_get_request_echo(params: ParsedKnowledgeCatalogGetInput) -> dict[str, Any]:
    """Build the request echo for a catalog get command."""
    echo: dict[str, Any] = {"name": params["name"], **entry_view_fields_from(params)}
    return merge_impersonation_into(echo, params)


def _build_sdk_get_request(params: ParsedKnowledgeCatalogGetInput) -> GetByNameRequest:
    return {
        "name": params["name"],
        **entry_view_fields_from(params),
    }


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
        build_request=_build_sdk_get_request,
        fetch=fetch,
    )
