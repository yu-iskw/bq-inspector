"""Integration tests for lineage CLI commands with fixture client injection."""

from __future__ import annotations

import json

import pytest

from bq_inspector.commands.command_shared import InspectionCommandOptions
from bq_inspector.commands.lineage.links import run_lineage_links
from bq_inspector.schemas.command_schemas import get_command_schema
from bq_inspector.tests.test_support.fixture_lineage_client import (
    FixtureLineageClient,
    FixtureLineageInput,
)

_FQN = "bigquery:data-proj.analytics.events"


@pytest.mark.asyncio
async def test_lineage_links_input_schema() -> None:
    schema = get_command_schema("lineage links", "input")
    assert schema["required"] == ["location", "projectId", "datasetId", "tableId", "direction"]


@pytest.mark.asyncio
async def test_run_lineage_links_with_fixture_client() -> None:
    client = FixtureLineageClient(
        FixtureLineageInput(
            links_by_fqn_direction={
                (_FQN, "UPSTREAM"): [
                    {
                        "source": {"fullyQualifiedName": "bigquery:data-proj.raw.events"},
                        "target": {"fullyQualifiedName": _FQN},
                    }
                ]
            }
        )
    )

    response = await run_lineage_links(
        [
            "--params",
            json.dumps(
                {
                    "clientProjectId": "billing-proj",
                    "location": "us",
                    "projectId": "data-proj",
                    "datasetId": "analytics",
                    "tableId": "events",
                    "direction": "UPSTREAM",
                }
            ),
        ],
        InspectionCommandOptions(lineage_client=client, tool_version="0.1.0"),
    )

    assert response["schemaVersion"] == "bq-inspector.v1"
    assert len(response["links"]) == 1
    assert response["errors"] == []
