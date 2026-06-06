"""Canonical Knowledge Catalog request builders from parsed input."""

from __future__ import annotations

from collections.abc import Mapping  # noqa: TC003
from typing import TYPE_CHECKING, Any, cast

from bq_inspector.core.knowledge_catalog.entry_view_fields import entry_view_fields_from
from bq_inspector.core.knowledge_catalog.parent import catalog_parent
from bq_inspector.core.shared.impersonation_fields import merge_impersonation_into
from bq_inspector.knowledge_catalog.defaults import (
    CATALOG_SEARCH_LOCATION,
    DEFAULT_CATALOG_LIST_PAGE_SIZE,
    DEFAULT_CATALOG_SEARCH_PAGE_SIZE,
)

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import (
        ParsedKnowledgeCatalogGetInput,
        ParsedKnowledgeCatalogListInput,
        ParsedKnowledgeCatalogLookupInput,
        ParsedKnowledgeCatalogSearchInput,
    )
    from bq_inspector.knowledge_catalog.types.requests import (
        GetByNameRequest,
        ListByParentRequest,
        LookupEntryRequest,
        SearchEntriesRequest,
    )

_LIST_OPTIONAL_KEYS = ("pageToken", "filter", "orderBy")
_SEARCH_OPTIONAL_KEYS = ("scope", "orderBy", "pageToken")


def _copy_optional_fields(
    source: Mapping[str, Any],
    target: dict[str, Any],
    keys: tuple[str, ...],
) -> None:
    for key in keys:
        value = source.get(key)
        if value is not None:
            target[key] = value


def build_search_request_echo(params: ParsedKnowledgeCatalogSearchInput) -> dict[str, Any]:
    """Build the request echo for catalog search."""
    echo: dict[str, Any] = {
        "projectId": params["projectId"],
        "location": params.get("location", CATALOG_SEARCH_LOCATION),
        "query": params["query"],
        "pageSize": params.get("pageSize", DEFAULT_CATALOG_SEARCH_PAGE_SIZE),
    }
    _copy_optional_fields(cast("dict[str, Any]", params), echo, _SEARCH_OPTIONAL_KEYS)
    semantic_search = params.get("semanticSearch")
    if semantic_search is not None:
        echo["semanticSearch"] = semantic_search
    return merge_impersonation_into(echo, params)


def build_search_sdk_request(params: ParsedKnowledgeCatalogSearchInput) -> SearchEntriesRequest:
    """Build the SDK search request for catalog search."""
    location = params.get("location", CATALOG_SEARCH_LOCATION)
    sdk_request: SearchEntriesRequest = {
        "name": catalog_parent(params["projectId"], location),
        "query": params["query"],
        "pageSize": params.get("pageSize", DEFAULT_CATALOG_SEARCH_PAGE_SIZE),
    }
    _copy_optional_fields(
        cast("dict[str, Any]", params),
        cast("dict[str, Any]", sdk_request),
        _SEARCH_OPTIONAL_KEYS,
    )
    semantic_search = params.get("semanticSearch")
    if semantic_search is not None:
        sdk_request["semanticSearch"] = semantic_search
    return sdk_request


def build_lookup_request_echo(params: ParsedKnowledgeCatalogLookupInput) -> dict[str, Any]:
    """Build the request echo for catalog entry lookup."""
    echo: dict[str, Any] = {
        "projectId": params["projectId"],
        "location": params["location"],
        "entry": params["entry"],
        **entry_view_fields_from(params),
    }
    return merge_impersonation_into(echo, params)


def build_lookup_sdk_request(params: ParsedKnowledgeCatalogLookupInput) -> LookupEntryRequest:
    """Build the SDK lookup request for catalog entry lookup."""
    return {
        "name": catalog_parent(params["projectId"], params["location"]),
        "entry": params["entry"],
        **entry_view_fields_from(params),
    }


def build_get_request_echo(params: ParsedKnowledgeCatalogGetInput) -> dict[str, Any]:
    """Build the request echo for a catalog get command."""
    echo: dict[str, Any] = {"name": params["name"], **entry_view_fields_from(params)}
    return merge_impersonation_into(echo, params)


def build_get_sdk_request(params: ParsedKnowledgeCatalogGetInput) -> GetByNameRequest:
    """Build the SDK get-by-name request."""
    return {
        "name": params["name"],
        **entry_view_fields_from(params),
    }


def _list_request_fields(params: ParsedKnowledgeCatalogListInput) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "parent": params["parent"],
        "pageSize": params.get("pageSize", DEFAULT_CATALOG_LIST_PAGE_SIZE),
    }
    _copy_optional_fields(cast("dict[str, Any]", params), fields, _LIST_OPTIONAL_KEYS)
    return fields


def build_list_request_echo(params: ParsedKnowledgeCatalogListInput) -> dict[str, Any]:
    """Build the request echo for a catalog list command."""
    return merge_impersonation_into(_list_request_fields(params), params)


def build_list_sdk_request(params: ParsedKnowledgeCatalogListInput) -> ListByParentRequest:
    """Build the SDK list-by-parent request."""
    return _list_request_fields(params)  # type: ignore[return-value]
