"""Integration tests for catalog CLI commands with fixture client injection."""

from __future__ import annotations

import json

import pytest

from bq_inspect.commands.command_shared import InspectionCommandOptions
from bq_inspect.commands.datasets.get import run_datasets_get
from bq_inspect.commands.tables.get import run_tables_get
from bq_inspect.commands.tables.list import run_tables_list
from bq_inspect.tests.test_support.fixture_job_client import (
    FixtureBigQueryClient,
    FixtureBigQueryInput,
)


@pytest.mark.asyncio
async def test_run_datasets_get_with_fixture_client() -> None:
    client = FixtureBigQueryClient(
        FixtureBigQueryInput(
            datasets_by_key={
                "analytics-prod:analytics": {"datasetReference": {"datasetId": "analytics"}}
            }
        )
    )

    response = await run_datasets_get(
        [
            "--params",
            json.dumps({"projectId": "analytics-prod", "datasetId": "analytics"}),
        ],
        InspectionCommandOptions(client=client, tool_version="0.1.0"),
    )

    assert response["schemaVersion"] == "bq-inspect.v1"
    assert response["resource"]["datasetReference"]["datasetId"] == "analytics"
    assert response["errors"] == []


@pytest.mark.asyncio
async def test_run_tables_list_with_fixture_client() -> None:
    client = FixtureBigQueryClient(
        FixtureBigQueryInput(
            tables_list_by_key={
                "analytics-prod:analytics": [{"tableReference": {"tableId": "events"}}],
            }
        )
    )

    response = await run_tables_list(
        [
            "--params",
            json.dumps({"projectId": "analytics-prod", "datasetId": "analytics"}),
        ],
        InspectionCommandOptions(client=client, tool_version="0.1.0"),
    )

    assert response["schemaVersion"] == "bq-inspect.v1"
    assert len(response["tables"]) == 1
    assert response["tables"][0]["tableReference"]["tableId"] == "events"
    assert response["errors"] == []


@pytest.mark.asyncio
async def test_run_tables_get_with_fixture_client() -> None:
    client = FixtureBigQueryClient(
        FixtureBigQueryInput(
            tables_by_key={
                "analytics-prod:analytics:events": {"tableReference": {"tableId": "events"}},
            }
        )
    )

    response = await run_tables_get(
        [
            "--params",
            json.dumps(
                {
                    "projectId": "analytics-prod",
                    "datasetId": "analytics",
                    "tableId": "events",
                }
            ),
        ],
        InspectionCommandOptions(client=client, tool_version="0.1.0"),
    )

    assert response["schemaVersion"] == "bq-inspect.v1"
    assert response["resource"]["tableReference"]["tableId"] == "events"
    assert response["errors"] == []
