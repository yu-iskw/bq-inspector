"""Retrieve a Knowledge Catalog resource by canonical name."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.error_envelope import catalog_knowledge_error_envelope
from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.core.shared.impersonation_fields import merge_impersonation_into

if TYPE_CHECKING:
    from collections.abc import Callable

    from bq_inspector.input.parsed_input_types import ParsedKnowledgeCatalogGetInput
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient
    from bq_inspector.knowledge_catalog.types.requests import GetByNameRequest


def build_get_request_echo(params: ParsedKnowledgeCatalogGetInput) -> dict[str, Any]:
    """Build the request echo for a catalog get command."""
    echo: dict[str, Any] = {"name": params["name"]}
    view = params.get("view")
    if view is not None:
        echo["view"] = view
    aspect_types = params.get("aspectTypes")
    if aspect_types is not None:
        echo["aspectTypes"] = aspect_types
    paths = params.get("paths")
    if paths is not None:
        echo["paths"] = paths
    return merge_impersonation_into(echo, params)


def _build_sdk_get_request(params: ParsedKnowledgeCatalogGetInput) -> GetByNameRequest:
    sdk_request: GetByNameRequest = {"name": params["name"]}
    view = params.get("view")
    if view is not None:
        sdk_request["view"] = view
    aspect_types = params.get("aspectTypes")
    if aspect_types is not None:
        sdk_request["aspectTypes"] = aspect_types
    paths = params.get("paths")
    if paths is not None:
        sdk_request["paths"] = paths
    return sdk_request


async def get_catalog_resource(
    params: ParsedKnowledgeCatalogGetInput,
    *,
    client: CatalogInspectionClient,
    tool_version: str,
    fetch: Callable[[CatalogInspectionClient, GetByNameRequest], Any],
) -> dict[str, Any]:
    """Retrieve a Knowledge Catalog resource and return a stable JSON envelope."""
    envelope = build_tool_envelope(tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]
    request_echo = build_get_request_echo(params)
    sdk_request = _build_sdk_get_request(params)

    try:
        resource = await fetch(client, sdk_request)
    except BqInspectFailure as error:
        return catalog_knowledge_error_envelope(
            schema_version,
            tool,
            request_echo,
            error,
            response_fields={"resource": {}},
        )

    return {
        "schemaVersion": schema_version,
        "tool": tool,
        "request": request_echo,
        "resource": resource,
        "warnings": [],
        "errors": [],
    }
