"""SDK adapter tests for Knowledge Catalog client behavior."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest
from google.protobuf.message import Message

from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client import (
    SdkCatalogClient,
)
from bq_inspector.knowledge_catalog.resource_specs import (
    KNOWLEDGE_CATALOG_GET_RESOURCES,
    KNOWLEDGE_CATALOG_LIST_RESOURCES,
    KnowledgeCatalogGetDispatch,
    KnowledgeCatalogListDispatch,
)


def _entries_get_dispatch() -> KnowledgeCatalogGetDispatch:
    return next(
        spec.dispatch for spec in KNOWLEDGE_CATALOG_GET_RESOURCES if spec.subgroup == "entries"
    )


def _entries_list_dispatch() -> KnowledgeCatalogListDispatch:
    return next(
        spec.dispatch for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES if spec.subgroup == "entries"
    )


def _entry_groups_list_dispatch() -> KnowledgeCatalogListDispatch:
    return next(
        spec.dispatch
        for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES
        if spec.subgroup == "entry-groups"
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


@pytest.mark.asyncio
async def test_get_named_resource_uses_dispatch_metadata() -> None:
    dispatch = _entries_get_dispatch()
    mock_resource = MagicMock(spec=Message)
    mock_catalog = MagicMock()
    mock_catalog.get_entry.return_value = mock_resource
    mock_request = MagicMock()

    with (
        patch(
            "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client.dataplex_v1"
        ) as dataplex_v1,
        patch(
            "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client."
            "message_to_dict",
            return_value={"name": "projects/p/locations/us/entryGroups/g/entries/e"},
        ),
        patch(
            "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client.invoke_sync",
            side_effect=lambda fn, **_: fn(),
        ),
    ):
        dataplex_v1.CatalogServiceClient.return_value = mock_catalog
        dataplex_v1.BusinessGlossaryServiceClient.return_value = MagicMock()
        dataplex_v1.GetEntryRequest.return_value = mock_request
        client = SdkCatalogClient(MagicMock())

        resource = await client.get_named_resource(
            {"name": "projects/p/locations/us/entryGroups/g/entries/e"},
            dispatch=dispatch,
        )

    dataplex_v1.GetEntryRequest.assert_called_once_with(
        name="projects/p/locations/us/entryGroups/g/entries/e"
    )
    mock_catalog.get_entry.assert_called_once_with(request=mock_request)
    assert resource["name"] == "projects/p/locations/us/entryGroups/g/entries/e"


@dataclass
class _FakeListRequest:
    parent: str


@pytest.mark.asyncio
async def test_list_parent_resources_omits_order_by_when_unsupported() -> None:
    dispatch = _entries_list_dispatch()
    mock_pager = MagicMock()
    mock_pager.entries = []
    mock_pager.next_page_token = ""
    mock_catalog = MagicMock()
    mock_catalog.list_entries.return_value = mock_pager
    sdk_request = _FakeListRequest(parent="projects/p/locations/us/entryGroups/g")

    with (
        patch(
            "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client.dataplex_v1"
        ) as dataplex_v1,
        patch(
            "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client.invoke_sync",
            side_effect=lambda fn, **_: fn(),
        ),
    ):
        dataplex_v1.CatalogServiceClient.return_value = mock_catalog
        dataplex_v1.BusinessGlossaryServiceClient.return_value = MagicMock()
        dataplex_v1.ListEntriesRequest.return_value = sdk_request
        client = SdkCatalogClient(MagicMock())

        page = await client.list_parent_resources(
            {
                "parent": "projects/p/locations/us/entryGroups/g",
                "orderBy": "name",
            },
            dispatch=dispatch,
        )

    assert not hasattr(sdk_request, "order_by")
    mock_catalog.list_entries.assert_called_once_with(request=sdk_request)
    assert page["resources"] == []


@dataclass
class _FakeListGroupsRequest:
    parent: str
    order_by: str | None = None


@pytest.mark.asyncio
async def test_list_parent_resources_applies_order_by_when_supported() -> None:
    dispatch = _entry_groups_list_dispatch()
    mock_pager = MagicMock()
    mock_pager.entry_groups = []
    mock_pager.next_page_token = "next"
    mock_catalog = MagicMock()
    mock_catalog.list_entry_groups.return_value = mock_pager
    mock_request = _FakeListGroupsRequest(parent="projects/p/locations/us")

    with (
        patch(
            "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client.dataplex_v1"
        ) as dataplex_v1,
        patch(
            "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client.invoke_sync",
            side_effect=lambda fn, **_: fn(),
        ),
    ):
        dataplex_v1.CatalogServiceClient.return_value = mock_catalog
        dataplex_v1.BusinessGlossaryServiceClient.return_value = MagicMock()
        dataplex_v1.ListEntryGroupsRequest.return_value = mock_request
        client = SdkCatalogClient(MagicMock())

        page = await client.list_parent_resources(
            {
                "parent": "projects/p/locations/us",
                "orderBy": "name",
            },
            dispatch=dispatch,
        )

    assert mock_request.order_by == "name"
    assert page["nextPageToken"] == "next"


@pytest.mark.asyncio
async def test_resolve_entry_view_rejects_unknown_values() -> None:
    mock_catalog = MagicMock()

    with patch(
        "bq_inspector.knowledge_catalog.adapters.google_cloud.sdk_catalog_client.dataplex_v1"
    ) as dataplex_v1:
        dataplex_v1.CatalogServiceClient.return_value = mock_catalog
        dataplex_v1.BusinessGlossaryServiceClient.return_value = MagicMock()
        dataplex_v1.LookupEntryRequest = MagicMock()
        client = SdkCatalogClient(MagicMock())

        with pytest.raises(BqInspectFailure, match='view must be "BASIC"'):
            await client.lookup_entry(
                {
                    "name": "projects/p/locations/global",
                    "entry": "projects/p/locations/us/entryGroups/g/entries/e",
                    "view": "INVALID",
                }
            )
