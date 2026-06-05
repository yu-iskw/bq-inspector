"""Google Cloud SDK adapter for read-only Data Lineage inspection."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypeVar

from google.cloud import datacatalog_lineage_v1
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

from bq_inspector.bigquery.errors.google_api_errors import map_google_error_to_bq_inspector_failure
from bq_inspector.core.shared.errors import BqInspectFailure

_T = TypeVar("_T")

_DEFAULT_MAX_DEPTH = 5
_DEFAULT_MAX_RESULTS = 1000

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from google.auth.credentials import Credentials
    from google.cloud.datacatalog_lineage_v1.services.lineage.pagers import SearchLinksPager

    from bq_inspector.datalineage.types.requests import (
        LineageDirection,
        SearchLineageGraphRequest,
        SearchLineageGraphResult,
        SearchLinksPage,
        SearchLinksRequest,
    )


async def _invoke_sync(
    fn: Callable[[], _T],
    *,
    api: str,
) -> _T:
    try:
        return await asyncio.to_thread(fn)
    except BqInspectFailure:
        raise
    except Exception as error:
        raise map_google_error_to_bq_inspector_failure(error, api) from error


def _message_to_dict(message: object) -> dict[str, object]:
    protobuf = getattr(message, "_pb", message)
    if not isinstance(protobuf, Message):
        raise TypeError("Expected protobuf message convertible to dict")
    result = MessageToDict(protobuf, preserving_proto_field_name=False)
    if isinstance(result, dict):
        return result
    raise TypeError("Expected protobuf message convertible to dict")


def _links_to_dicts(links: Iterable[object]) -> list[dict[str, object]]:
    return [_message_to_dict(link) for link in links]


def _streaming_direction(
    direction: LineageDirection,
) -> datacatalog_lineage_v1.SearchLineageStreamingRequest.SearchDirection:
    if direction == "UPSTREAM":
        return datacatalog_lineage_v1.SearchLineageStreamingRequest.SearchDirection.UPSTREAM
    return datacatalog_lineage_v1.SearchLineageStreamingRequest.SearchDirection.DOWNSTREAM


class SdkLineageClient:
    """Data Lineage client backed by google-cloud-datacatalog-lineage."""

    def __init__(self, auth_client: Credentials) -> None:
        self._auth_client = auth_client
        self._client = datacatalog_lineage_v1.LineageClient(credentials=auth_client)

    async def search_links(self, request: SearchLinksRequest) -> SearchLinksPage:
        entity = datacatalog_lineage_v1.EntityReference(fully_qualified_name=request["fqn"])
        sdk_request = datacatalog_lineage_v1.SearchLinksRequest(parent=request["parent"])
        if request["direction"] == "UPSTREAM":
            sdk_request.target = entity
        else:
            sdk_request.source = entity

        page_size = request.get("pageSize")
        if page_size is not None:
            sdk_request.page_size = page_size

        page_token = request.get("pageToken")
        if page_token is not None:
            sdk_request.page_token = page_token

        def _call() -> SearchLinksPager:
            return self._client.search_links(request=sdk_request)

        pager = await _invoke_sync(_call, api="datalineage.locations.searchLinks")
        page: SearchLinksPage = {"links": _links_to_dicts(pager.links)}
        if pager.next_page_token:
            page["nextPageToken"] = pager.next_page_token
        return page

    async def search_lineage_graph(
        self,
        request: SearchLineageGraphRequest,
    ) -> SearchLineageGraphResult:
        location = request["location"]
        sdk_request = datacatalog_lineage_v1.SearchLineageStreamingRequest(
            parent=request["parent"],
            locations=[location],
            direction=_streaming_direction(request["direction"]),
            root_criteria=datacatalog_lineage_v1.SearchLineageStreamingRequest.RootCriteria(
                entities=datacatalog_lineage_v1.MultipleEntityReference(
                    entities=[
                        datacatalog_lineage_v1.EntityReference(
                            fully_qualified_name=request["fqn"],
                        )
                    ]
                )
            ),
            limits=datacatalog_lineage_v1.SearchLineageStreamingRequest.SearchLimits(
                max_depth=request.get("maxDepth", _DEFAULT_MAX_DEPTH),
                max_results=request.get("maxResults", _DEFAULT_MAX_RESULTS),
            ),
        )

        def _call() -> SearchLineageGraphResult:
            merged_links: list[dict[str, object]] = []
            unreachable: list[str] = []
            for chunk in self._client.search_lineage_streaming(request=sdk_request):
                merged_links.extend(_links_to_dicts(chunk.links))
                unreachable.extend(list(chunk.unreachable))
            return {"links": merged_links, "unreachable": unreachable}

        return await _invoke_sync(_call, api="datalineage.locations.searchLineageStreaming")
