"""Tests for the Google Cloud SDK Data Lineage client adapter."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import PermissionDenied

from bq_inspector.core.shared.errors import BqInspectFailure, create_bq_inspector_error
from bq_inspector.datalineage.adapters.google_cloud.sdk_lineage_client import SdkLineageClient
from bq_inspector.datalineage.defaults import (
    DEFAULT_LINEAGE_GRAPH_MAX_DEPTH,
    DEFAULT_LINEAGE_GRAPH_MAX_RESULTS,
)


@pytest.fixture
def mock_auth_client_fx() -> MagicMock:
    return MagicMock()


@pytest.fixture
def lineage_client_mock_fx() -> MagicMock:
    client = MagicMock()
    client.search_links = MagicMock()
    client.search_lineage_streaming = MagicMock()
    return client


@pytest.fixture
def sdk_lineage_client_fx(
    mock_auth_client_fx: MagicMock,
    lineage_client_mock_fx: MagicMock,
) -> SdkLineageClient:
    with patch(
        "bq_inspector.datalineage.adapters.google_cloud.sdk_lineage_client."
        "datacatalog_lineage_v1.LineageClient",
        return_value=lineage_client_mock_fx,
    ):
        yield SdkLineageClient(mock_auth_client_fx)


@pytest.mark.asyncio
async def test_search_links_upstream_sets_target_entity(
    sdk_lineage_client_fx: SdkLineageClient,
    lineage_client_mock_fx: MagicMock,
) -> None:
    pager = MagicMock()
    pager.links = []
    pager.next_page_token = None
    lineage_client_mock_fx.search_links.return_value = pager
    sdk_request = MagicMock()

    with patch(
        "bq_inspector.datalineage.adapters.google_cloud.sdk_lineage_client."
        "datacatalog_lineage_v1.SearchLinksRequest",
        return_value=sdk_request,
    ):
        await sdk_lineage_client_fx.search_links(
            {
                "parent": "projects/p/locations/us",
                "fqn": "bigquery:p.d.t",
                "direction": "UPSTREAM",
            }
        )

    assert sdk_request.target is not None
    lineage_client_mock_fx.search_links.assert_called_once_with(request=sdk_request)


@pytest.mark.asyncio
async def test_search_links_downstream_sets_source_entity(
    sdk_lineage_client_fx: SdkLineageClient,
    lineage_client_mock_fx: MagicMock,
) -> None:
    pager = MagicMock()
    pager.links = []
    pager.next_page_token = None
    lineage_client_mock_fx.search_links.return_value = pager
    sdk_request = MagicMock()

    with patch(
        "bq_inspector.datalineage.adapters.google_cloud.sdk_lineage_client."
        "datacatalog_lineage_v1.SearchLinksRequest",
        return_value=sdk_request,
    ):
        await sdk_lineage_client_fx.search_links(
            {
                "parent": "projects/p/locations/us",
                "fqn": "bigquery:p.d.t",
                "direction": "DOWNSTREAM",
            }
        )

    assert sdk_request.source is not None
    lineage_client_mock_fx.search_links.assert_called_once_with(request=sdk_request)


@pytest.mark.asyncio
async def test_search_lineage_graph_merges_stream_chunks(
    sdk_lineage_client_fx: SdkLineageClient,
    lineage_client_mock_fx: MagicMock,
) -> None:
    chunk_one = MagicMock()
    chunk_one.links = [MagicMock(_pb=MagicMock())]
    chunk_one.unreachable = ["projects/x/locations/us"]
    chunk_two = MagicMock()
    chunk_two.links = [MagicMock(_pb=MagicMock())]
    chunk_two.unreachable = []
    lineage_client_mock_fx.search_lineage_streaming.return_value = [chunk_one, chunk_two]

    with patch(
        "bq_inspector.datalineage.adapters.google_cloud.sdk_lineage_client._message_to_dict",
        return_value={"link": "stub"},
    ):
        result = await sdk_lineage_client_fx.search_lineage_graph(
            {
                "parent": "projects/p/locations/us",
                "location": "us",
                "fqn": "bigquery:p.d.t",
                "direction": "DOWNSTREAM",
            }
        )

    assert result["links"] == [{"link": "stub"}, {"link": "stub"}]
    assert result["unreachable"] == ["projects/x/locations/us"]


@pytest.mark.asyncio
async def test_search_lineage_graph_uses_default_limits(
    sdk_lineage_client_fx: SdkLineageClient,
    lineage_client_mock_fx: MagicMock,
) -> None:
    lineage_client_mock_fx.search_lineage_streaming.return_value = []

    with patch(
        "bq_inspector.datalineage.adapters.google_cloud.sdk_lineage_client."
        "datacatalog_lineage_v1.SearchLineageStreamingRequest",
        return_value=MagicMock(),
    ), patch(
        "bq_inspector.datalineage.adapters.google_cloud.sdk_lineage_client."
        "datacatalog_lineage_v1.SearchLineageStreamingRequest.SearchLimits",
    ) as limits_cls:
        await sdk_lineage_client_fx.search_lineage_graph(
            {
                "parent": "projects/p/locations/us",
                "location": "us",
                "fqn": "bigquery:p.d.t",
                "direction": "UPSTREAM",
            }
        )

    limits_cls.assert_called_once_with(
        max_depth=DEFAULT_LINEAGE_GRAPH_MAX_DEPTH,
        max_results=DEFAULT_LINEAGE_GRAPH_MAX_RESULTS,
    )


@pytest.mark.asyncio
async def test_invoke_sync_preserves_bq_inspector_failure(
    sdk_lineage_client_fx: SdkLineageClient,
    lineage_client_mock_fx: MagicMock,
) -> None:
    structured = BqInspectFailure(
        create_bq_inspector_error(
            code="BQINSPECTOR_PERMISSION_DENIED",
            message="Denied.",
            source={"api": "datalineage.locations.searchLinks", "status": 403},
        )
    )
    lineage_client_mock_fx.search_links.side_effect = structured

    with pytest.raises(BqInspectFailure) as exc_info:
        await sdk_lineage_client_fx.search_links(
            {
                "parent": "projects/p/locations/us",
                "fqn": "bigquery:p.d.t",
                "direction": "UPSTREAM",
            }
        )

    assert exc_info.value.details["code"] == "BQINSPECTOR_PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_search_links_maps_permission_denied(
    sdk_lineage_client_fx: SdkLineageClient,
    lineage_client_mock_fx: MagicMock,
) -> None:
    lineage_client_mock_fx.search_links.side_effect = PermissionDenied("denied")

    with pytest.raises(BqInspectFailure) as exc_info:
        await sdk_lineage_client_fx.search_links(
            {
                "parent": "projects/p/locations/us",
                "fqn": "bigquery:p.d.t",
                "direction": "UPSTREAM",
            }
        )

    assert exc_info.value.details["code"] == "BQINSPECTOR_PERMISSION_DENIED"
