"""Transport request and response types for Data Lineage inspection."""

from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import NotRequired

LineageDirection = Literal["UPSTREAM", "DOWNSTREAM"]


class SearchLinksRequest(TypedDict):
    parent: str
    fqn: str
    direction: LineageDirection
    pageSize: NotRequired[int]
    pageToken: NotRequired[str]


class SearchLinksPage(TypedDict):
    links: list[dict[str, object]]
    nextPageToken: NotRequired[str]


class SearchLineageGraphRequest(TypedDict):
    parent: str
    location: str
    fqn: str
    direction: LineageDirection
    maxDepth: NotRequired[int]
    maxResults: NotRequired[int]


class SearchLineageGraphResult(TypedDict):
    links: list[dict[str, object]]
    unreachable: list[str]
