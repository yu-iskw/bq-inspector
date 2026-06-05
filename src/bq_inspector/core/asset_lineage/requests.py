"""Asset-lineage use-case request types."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from bq_inspector.bigquery.types.refs import TableRef
    from bq_inspector.datalineage.types.requests import LineageDirection


class TableLineageRequest(TypedDict):
    clientProjectId: str
    location: str
    table: TableRef
    direction: LineageDirection


class LineageLinksRequest(TableLineageRequest):
    pageSize: NotRequired[int]
    pageToken: NotRequired[str]


class LineageGraphRequest(TableLineageRequest):
    maxDepth: NotRequired[int]
    maxResults: NotRequired[int]
