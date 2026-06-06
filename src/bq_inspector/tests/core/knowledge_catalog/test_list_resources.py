"""Core use-case tests for Knowledge Catalog list-by-parent."""

from __future__ import annotations

import pytest

from bq_inspector.core.knowledge_catalog.list_resources import list_catalog_resources
from bq_inspector.knowledge_catalog.resource_specs import KNOWLEDGE_CATALOG_LIST_RESOURCES
from bq_inspector.tests.test_support.fixture_catalog_client import (
    FixtureCatalogClient,
    FixtureCatalogInput,
)

_PARENT = "projects/analytics-prod/locations/us/entryGroups/g"


@pytest.mark.asyncio
async def test_list_catalog_resources_returns_fixture_page() -> None:
    spec = next(
        spec for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES if spec.subgroup == "entries"
    )
    client = FixtureCatalogClient(
        FixtureCatalogInput(
            list_by_parent={
                _PARENT: {
                    "resources": [{"name": f"{_PARENT}/entries/a"}],
                    "nextPageToken": "token-1",
                }
            }
        )
    )

    response = await list_catalog_resources(
        {"parent": _PARENT, "pageSize": 50},
        client=client,
        tool_version="0.1.0",
        collection_key=spec.collection_key,
        dispatch=spec.dispatch,
    )

    assert response["entries"] == [{"name": f"{_PARENT}/entries/a"}]
    assert response["page"]["nextPageToken"] == "token-1"
    assert response["errors"] == []
    assert client.calls == [("list_entries", {"parent": _PARENT, "pageSize": 50})]
