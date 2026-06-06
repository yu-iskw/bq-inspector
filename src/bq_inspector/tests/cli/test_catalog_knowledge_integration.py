"""Integration tests for Knowledge Catalog CLI commands with fixture client injection."""

from __future__ import annotations

import json

import pytest

from bq_inspector.commands.catalog.commands import (
    build_knowledge_catalog_command_runners,
    catalog_search_command,
)
from bq_inspector.commands.command_shared import InspectionCommandOptions
from bq_inspector.schemas.command_schemas import get_command_schema
from bq_inspector.tests.test_support.fixture_catalog_client import (
    FixtureCatalogClient,
    FixtureCatalogInput,
)

_ENTRY_NAME = (
    "projects/analytics-prod/locations/us-central1/entryGroups/@bigquery/entries/example-entry"
)


@pytest.mark.asyncio
async def test_catalog_search_input_schema() -> None:
    schema = get_command_schema("catalog search", "input")
    assert schema["required"] == ["projectId", "query"]


@pytest.mark.asyncio
async def test_catalog_search_output_schema() -> None:
    schema = get_command_schema("catalog search", "output")
    assert "entries" in schema["properties"]


@pytest.mark.asyncio
async def test_run_catalog_search_with_fixture_client() -> None:
    client = FixtureCatalogClient(
        FixtureCatalogInput(
            search_pages={
                (
                    "projects/agent-tools-prod/locations/global",
                    "customer orders",
                ): {
                    "entries": [
                        {
                            "entry": {
                                "name": _ENTRY_NAME,
                                "fullyQualifiedName": "bigquery:analytics-prod.sales.orders",
                            }
                        }
                    ],
                    "totalSize": 1,
                    "unreachable": ["us-west1"],
                }
            }
        )
    )

    response = await catalog_search_command.run_argv(
        [
            "--params",
            json.dumps(
                {
                    "projectId": "agent-tools-prod",
                    "query": "customer orders",
                    "scope": "projects/analytics-prod",
                    "pageSize": 50,
                }
            ),
        ],
        InspectionCommandOptions(catalog_client=client, tool_version="0.2.0"),
    )

    assert response["schemaVersion"] == "bq-inspector.v1"
    assert len(response["entries"]) == 1
    assert response["page"]["unreachable"] == ["us-west1"]
    assert len(response["warnings"]) == 1
    assert response["warnings"][0]["code"] == "BQINSPECTOR_PARTIAL_RESULTS"
    assert response["errors"] == []


@pytest.mark.asyncio
async def test_catalog_entries_lookup_input_schema() -> None:
    schema = get_command_schema("catalog entries lookup", "input")
    assert schema["required"] == ["projectId", "location", "entry"]


@pytest.mark.asyncio
async def test_run_catalog_entries_get_with_fixture_client() -> None:
    runners = build_knowledge_catalog_command_runners()
    entries_get = runners["catalog_entries_get_command"]
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

    response = await entries_get.run_argv(
        ["--params", json.dumps({"name": _ENTRY_NAME})],
        InspectionCommandOptions(catalog_client=client, tool_version="0.2.0"),
    )

    assert response["resource"]["fullyQualifiedName"] == "bigquery:analytics-prod.sales.orders"
    assert response["errors"] == []
    assert client.calls[0][0] == "get_entry"


@pytest.mark.asyncio
async def test_catalog_entry_links_get_has_no_list_command() -> None:
    schema = get_command_schema("catalog entry-links get", "input")
    assert schema["required"] == ["name"]
    with pytest.raises(ValueError, match="Unhandled schema key"):
        get_command_schema("catalog entry-links list", "input")  # type: ignore[arg-type]
