"""Lookup a Knowledge Catalog entry by canonical name."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.knowledge_catalog.error_envelope import catalog_knowledge_error_envelope
from bq_inspector.core.knowledge_catalog.parent import lookup_parent
from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure
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
    }
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


def _build_sdk_lookup_request(params: ParsedKnowledgeCatalogLookupInput) -> LookupEntryRequest:
    sdk_request: LookupEntryRequest = {
        "name": lookup_parent(params["projectId"], params["location"]),
        "entry": params["entry"],
    }
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


async def lookup_catalog_entry(
    params: ParsedKnowledgeCatalogLookupInput,
    *,
    client: CatalogInspectionClient,
    tool_version: str,
) -> dict[str, Any]:
    """Lookup a Knowledge Catalog entry and return a stable JSON envelope."""
    envelope = build_tool_envelope(tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]
    request_echo = build_lookup_request_echo(params)
    sdk_request = _build_sdk_lookup_request(params)

    try:
        resource = await client.lookup_entry(sdk_request)
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
