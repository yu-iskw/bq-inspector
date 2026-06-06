"""Transport response types for Knowledge Catalog API calls."""

from __future__ import annotations

from typing_extensions import TypedDict


class SearchEntryResult(TypedDict):
    entry: dict[str, object]


class SearchEntriesPage(TypedDict, total=False):
    entries: list[SearchEntryResult]
    totalSize: int
    nextPageToken: str
    unreachable: list[str]


class ListResourcesPage(TypedDict, total=False):
    resources: list[dict[str, object]]
    nextPageToken: str
