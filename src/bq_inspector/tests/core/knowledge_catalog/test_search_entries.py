"""Core use-case tests for Knowledge Catalog search."""

from __future__ import annotations

import pytest

from bq_inspector.core.knowledge_catalog.search_entries import search_catalog_entries
from bq_inspector.tests.test_support.fixture_catalog_client import (
    FixtureCatalogClient,
    FixtureCatalogInput,
)


@pytest.mark.asyncio
async def test_search_catalog_entries_empty_results_succeed() -> None:
    client = FixtureCatalogClient(FixtureCatalogInput())

    response = await search_catalog_entries(
        {
            "projectId": "agent-tools-prod",
            "location": "global",
            "query": "no matches",
            "semanticSearch": False,
            "pageSize": 50,
        },
        client=client,
        tool_version="0.1.0",
    )

    assert response["entries"] == []
    assert response["errors"] == []
    assert response["warnings"] == []


@pytest.mark.asyncio
async def test_search_catalog_entries_request_echo() -> None:
    client = FixtureCatalogClient(FixtureCatalogInput())

    response = await search_catalog_entries(
        {
            "projectId": "agent-tools-prod",
            "location": "global",
            "query": "test",
            "scope": "projects/analytics-prod",
            "semanticSearch": True,
            "pageSize": 25,
        },
        client=client,
        tool_version="0.1.0",
    )

    assert response["request"]["projectId"] == "agent-tools-prod"
    assert response["request"]["query"] == "test"
    assert response["request"]["scope"] == "projects/analytics-prod"
    assert response["request"]["semanticSearch"] is True
    assert response["request"]["pageSize"] == 25
