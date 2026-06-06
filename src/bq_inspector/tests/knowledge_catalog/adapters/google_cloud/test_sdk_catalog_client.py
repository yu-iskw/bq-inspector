"""SDK adapter tests for Knowledge Catalog pagination behavior."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from google.protobuf.message import Message

from bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client import (
    SdkCatalogClient,
)


@pytest.mark.asyncio
async def test_search_entries_returns_first_page_only() -> None:
    mock_pager = MagicMock()
    mock_result = MagicMock()
    mock_entry = MagicMock(spec=Message)
    mock_result.dataplex_entry = mock_entry
    mock_pager.results = [mock_result]
    mock_pager.total_size = 100
    mock_pager.next_page_token = "token-abc"
    mock_pager.unreachable = ["us-west1"]

    mock_catalog = MagicMock()
    mock_catalog.search_entries.return_value = mock_pager

    with (
        patch(
            "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client.dataplex_v1"
        ) as dataplex_v1,
        patch(
            "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client."
            "message_to_dict",
            return_value={"name": "example-entry"},
        ),
        patch(
            "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client.invoke_sync",
            side_effect=lambda fn, **_: fn(),
        ),
    ):
        dataplex_v1.CatalogServiceClient.return_value = mock_catalog
        dataplex_v1.BusinessGlossaryServiceClient.return_value = MagicMock()
        dataplex_v1.SearchEntriesRequest = MagicMock()
        client = SdkCatalogClient(MagicMock())

        page = await client.search_entries(
            {
                "name": "projects/p/locations/global",
                "query": "test",
                "pageSize": 50,
            }
        )

    mock_catalog.search_entries.assert_called_once()
    assert len(page["entries"]) == 1
    assert page["nextPageToken"] == "token-abc"
    assert page["unreachable"] == ["us-west1"]
