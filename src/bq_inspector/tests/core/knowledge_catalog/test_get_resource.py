"""Core use-case tests for Knowledge Catalog get-by-name."""

from __future__ import annotations

import pytest

from bq_inspector.core.knowledge_catalog.get_resource import get_catalog_resource
from bq_inspector.knowledge_catalog.resource_specs import KNOWLEDGE_CATALOG_GET_RESOURCES
from bq_inspector.tests.test_support.fixture_catalog_client import (
    FixtureCatalogClient,
    FixtureCatalogInput,
)

_ENTRY_NAME = "projects/analytics-prod/locations/us/entryGroups/g/entries/example"


@pytest.mark.asyncio
async def test_get_catalog_resource_returns_fixture_payload() -> None:
    dispatch = next(
        spec.dispatch for spec in KNOWLEDGE_CATALOG_GET_RESOURCES if spec.subgroup == "entries"
    )
    client = FixtureCatalogClient(
        FixtureCatalogInput(
            get_by_name={
                _ENTRY_NAME: {
                    "name": _ENTRY_NAME,
                    "fullyQualifiedName": "bigquery:analytics-prod.sales.orders",
                }
            }
        )
    )

    response = await get_catalog_resource(
        {"name": _ENTRY_NAME},
        client=client,
        tool_version="0.1.0",
        dispatch=dispatch,
    )

    assert response["resource"]["fullyQualifiedName"] == "bigquery:analytics-prod.sales.orders"
    assert response["errors"] == []
    assert client.calls == [("get_entry", {"name": _ENTRY_NAME})]
