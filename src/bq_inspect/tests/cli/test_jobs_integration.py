"""Integration tests for CLI commands with fixture client injection."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from bq_inspect.commands.command_shared import InspectionCommandOptions
from bq_inspect.commands.jobs.list import run_jobs_list
from bq_inspect.commands.jobs.run_jobs_view import run_jobs_summary
from bq_inspect.core.jobs.get import InspectJobOptions, inspect_jobs
from bq_inspect.tests.test_support.fixture_job_client import (
    FixtureBigQueryClient,
    FixtureBigQueryInput,
    FixtureJobClient,
)

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _load_fixture(name: str = "successful-query-job.json") -> dict[str, object]:
    with (_FIXTURES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


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

    assert response["schemaVersion"] == "bq-inspect.v1"
    assert response["tool"] == {"name": "bq-inspect", "version": "0.1.0", "readOnly": True}
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

    assert response["schemaVersion"] == "bq-inspect.v1"
    assert len(response["jobs"]) == 1
    assert response["request"]["projectId"] == "analytics-prod"
    assert response["request"]["allUsers"] is True
    assert response["page"]["nextPageToken"] == "next"
    assert response["errors"] == []


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
