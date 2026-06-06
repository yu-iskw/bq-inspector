"""Transport request types for Knowledge Catalog API calls."""

from __future__ import annotations

from typing import Literal

from typing_extensions import NotRequired, TypedDict

CatalogEntryView = Literal["BASIC", "FULL", "CUSTOM", "ALL"]
CatalogSearchOrderBy = Literal[
    "relevance",
    "last_modified_timestamp",
    "last_modified_timestamp asc",
]


class SearchEntriesRequest(TypedDict):
    name: str
    query: str
    pageSize: NotRequired[int]
    pageToken: NotRequired[str]
    scope: NotRequired[str]
    orderBy: NotRequired[str]
    semanticSearch: NotRequired[bool]


class LookupEntryRequest(TypedDict):
    name: str
    entry: str
    view: NotRequired[CatalogEntryView]
    aspectTypes: NotRequired[list[str]]
    paths: NotRequired[list[str]]


class GetByNameRequest(TypedDict):
    name: str
    view: NotRequired[CatalogEntryView]
    aspectTypes: NotRequired[list[str]]
    paths: NotRequired[list[str]]


class ListByParentRequest(TypedDict):
    parent: str
    pageSize: NotRequired[int]
    pageToken: NotRequired[str]
    filter: NotRequired[str]
    orderBy: NotRequired[str]
