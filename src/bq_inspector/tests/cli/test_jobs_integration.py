"""Integration tests for CLI commands with fixture client injection."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from bq_inspector.commands.command_shared import InspectionCommandOptions
from bq_inspector.commands.jobs.list import run_jobs_list
from bq_inspector.commands.jobs.run_jobs_view import (
    run_jobs_impact,
    run_jobs_lineage,
    run_jobs_summary,
)
from bq_inspector.core.jobs.get import InspectJobOptions, inspect_jobs
from bq_inspector.tests.test_support.fixture_job_client import (
    FixtureBigQueryClient,
    FixtureBigQueryInput,
    FixtureJobClient,
)

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _load_fixture(name: str = "successful-query-job.json") -> dict[str, object]:
    with (_FIXTURES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


_LINEAGE_JOB_PARAMS = json.dumps(
    {
        "jobs": [
            {
                "projectId": "analytics-prod",
                "location": "US",
                "jobId": "job_lineage_1",
            }
        ]
    }
)


@pytest.mark.asyncio
async def test_run_jobs_summary_with_fixture_client() -> None:
    job = _load_fixture()
    client = FixtureJobClient({"job_123": job})

    response = await run_jobs_summary(
        [
            "--params",
            json.dumps(
                {
                    "jobs": [
                        {
                            "projectId": "analytics-prod",
                            "location": "US",
                            "jobId": "job_123",
                        }
                    ]
                }
            ),
        ],
        InspectionCommandOptions(client=client, tool_version="0.1.0"),
    )

    assert response["schemaVersion"] == "bq-inspector.v1"
    assert response["tool"] == {"name": "bq-inspector", "version": "0.1.0", "readOnly": True}
    assert len(response["jobs"]) == 1
    assert response["jobs"][0]["jobRef"]["jobId"] == "job_123"
    assert response["errors"] == []


@pytest.mark.asyncio
async def test_run_jobs_list_with_fixture_client() -> None:
    job = _load_fixture()
    client = FixtureBigQueryClient(
        FixtureBigQueryInput(list_jobs_page={"jobs": [job], "nextPageToken": "next"})
    )

    response = await run_jobs_list(
        [
            "--params",
            json.dumps(
                {
                    "projectId": "analytics-prod",
                    "allUsers": True,
                    "minCreationTime": "2026-05-17T00:00:00Z",
                }
            ),
        ],
        InspectionCommandOptions(client=client, tool_version="0.1.0"),
    )

    assert response["schemaVersion"] == "bq-inspector.v1"
    assert len(response["jobs"]) == 1
    assert response["request"]["projectId"] == "analytics-prod"
    assert response["request"]["allUsers"] is True
    assert response["page"]["nextPageToken"] == "next"
    assert response["errors"] == []


@pytest.mark.asyncio
async def test_run_jobs_lineage_includes_referenced_tables() -> None:
    job = _load_fixture("query-job-with-lineage.json")
    client = FixtureJobClient({"job_lineage_1": job})

    response = await run_jobs_lineage(
        ["--params", _LINEAGE_JOB_PARAMS],
        InspectionCommandOptions(client=client, tool_version="0.1.0"),
    )

    query_stats = response["jobs"][0]["job"]["statistics"]["query"]
    tables = query_stats["referencedTables"]
    assert len(tables) == 1
    assert tables[0]["tableId"] == "users"
    assert "queryPlan" not in query_stats


@pytest.mark.asyncio
async def test_run_jobs_impact_includes_dml_stats() -> None:
    job = _load_fixture("query-job-with-lineage.json")
    client = FixtureJobClient({"job_lineage_1": job})

    response = await run_jobs_impact(
        ["--params", _LINEAGE_JOB_PARAMS],
        InspectionCommandOptions(client=client, tool_version="0.1.0"),
    )

    stats = response["jobs"][0]["job"]["statistics"]
    assert stats["query"]["dmlStats"] is not None
    assert stats["mlStatistics"] == {"modelId": "model_1"}
    assert "referencedTables" not in stats["query"]


@pytest.mark.asyncio
async def test_inspect_jobs_fixture_matches_command_path() -> None:
    """Sanity check that command wiring uses the same core path as direct inspect_jobs."""
    job = _load_fixture()
    client = FixtureJobClient({"job_123": job})

    def fixed_now() -> datetime:
        return datetime(2020, 1, 1, tzinfo=timezone.utc)

    direct = await inspect_jobs(
        {"jobs": [{"projectId": "analytics-prod", "location": "US", "jobId": "job_123"}]},
        InspectJobOptions(client=client, tool_version="0.1.0", now=fixed_now),
    )

    via_command = await run_jobs_summary(
        [
            "--params",
            json.dumps(
                {
                    "jobs": [
                        {
                            "projectId": "analytics-prod",
                            "location": "US",
                            "jobId": "job_123",
                        }
                    ]
                }
            ),
        ],
        InspectionCommandOptions(client=client, tool_version="0.1.0"),
    )

    assert via_command["schemaVersion"] == direct["schemaVersion"]
    assert via_command["jobs"][0]["jobRef"] == direct["jobs"][0]["jobRef"]
