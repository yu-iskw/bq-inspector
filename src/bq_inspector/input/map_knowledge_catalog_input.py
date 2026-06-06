"""Map validated Knowledge Catalog JSON params to domain input types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.shared.errors import create_input_failure
from bq_inspector.input.map_input import _parse_impersonation_fields
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
    from bq_inspector.knowledge_catalog.types.requests import CatalogEntryView


def _parse_entry_view(raw: object) -> CatalogEntryView:
    view = str(raw).strip()
    if view in ("BASIC", "FULL", "CUSTOM", "ALL"):
        return view  # type: ignore[return-value]
    raise create_input_failure('view must be "BASIC", "FULL", "CUSTOM", or "ALL".')


def _parse_string_list(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]


def _set_trimmed_string(
    obj: dict[str, Any],
    result: ParsedKnowledgeCatalogSearchInput,
    key: str,
) -> None:
    value = obj.get(key)
    if isinstance(value, str) and value.strip():
        result[key] = value.strip()  # type: ignore[literal-required]


def _apply_optional_search_fields(
    obj: dict[str, Any],
    result: ParsedKnowledgeCatalogSearchInput,
) -> None:
    for key in ("location", "scope", "orderBy", "pageToken"):
        _set_trimmed_string(obj, result, key)

    semantic_search = obj.get("semanticSearch")
    if isinstance(semantic_search, bool):
        result["semanticSearch"] = semantic_search

    page_size = obj.get("pageSize")
    if isinstance(page_size, int):
        result["pageSize"] = page_size


def map_knowledge_catalog_search_input(obj: dict[str, Any]) -> ParsedKnowledgeCatalogSearchInput:
    """Map catalog search params to domain input."""
    result: ParsedKnowledgeCatalogSearchInput = {
        "projectId": str(obj["projectId"]).strip(),
        "query": str(obj["query"]).strip(),
        "location": CATALOG_SEARCH_LOCATION,
        "semanticSearch": False,
        "pageSize": DEFAULT_CATALOG_SEARCH_PAGE_SIZE,
        **_parse_impersonation_fields(obj),
    }
    _apply_optional_search_fields(obj, result)
    return result


def map_knowledge_catalog_lookup_input(
    obj: dict[str, Any],
) -> ParsedKnowledgeCatalogLookupInput:
    """Map catalog entries lookup params to domain input."""
    result: ParsedKnowledgeCatalogLookupInput = {
        "projectId": str(obj["projectId"]).strip(),
        "location": str(obj["location"]).strip(),
        "entry": str(obj["entry"]).strip(),
        **_parse_impersonation_fields(obj),
    }

    view = obj.get("view")
    if view is not None:
        result["view"] = _parse_entry_view(view)

    aspect_types = obj.get("aspectTypes")
    if aspect_types is not None:
        result["aspectTypes"] = _parse_string_list(aspect_types)

    paths = obj.get("paths")
    if paths is not None:
        result["paths"] = _parse_string_list(paths)

    return result


def map_knowledge_catalog_get_input(obj: dict[str, Any]) -> ParsedKnowledgeCatalogGetInput:
    """Map catalog get-by-name params to domain input."""
    result: ParsedKnowledgeCatalogGetInput = {
        "name": str(obj["name"]).strip(),
        **_parse_impersonation_fields(obj),
    }

    view = obj.get("view")
    if view is not None:
        result["view"] = _parse_entry_view(view)

    aspect_types = obj.get("aspectTypes")
    if aspect_types is not None:
        result["aspectTypes"] = _parse_string_list(aspect_types)

    paths = obj.get("paths")
    if paths is not None:
        result["paths"] = _parse_string_list(paths)

    return result


def map_knowledge_catalog_list_input(obj: dict[str, Any]) -> ParsedKnowledgeCatalogListInput:
    """Map catalog list-by-parent params to domain input."""
    result: ParsedKnowledgeCatalogListInput = {
        "parent": str(obj["parent"]).strip(),
        "pageSize": DEFAULT_CATALOG_LIST_PAGE_SIZE,
        **_parse_impersonation_fields(obj),
    }

    page_size = obj.get("pageSize")
    if isinstance(page_size, int):
        result["pageSize"] = page_size

    page_token = obj.get("pageToken")
    if isinstance(page_token, str) and page_token.strip():
        result["pageToken"] = page_token.strip()

    filter_value = obj.get("filter")
    if isinstance(filter_value, str) and filter_value.strip():
        result["filter"] = filter_value.strip()

    order_by = obj.get("orderBy")
    if isinstance(order_by, str) and order_by.strip():
        result["orderBy"] = order_by.strip()

    return result
