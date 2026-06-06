"""Tests for jobs get command execution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bq_inspector.commands.command_shared import InspectionCommandOptions
from bq_inspector.commands.jobs.run_jobs_view import run_jobs_get
from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.tests.test_support.fixture_job_client import FixtureJobClient

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def _jobs_get_params(body: dict[str, object]) -> list[str]:
    return ["--params", json.dumps(body)]


def _load_fixture(name: str = "successful-query-job.json") -> dict[str, object]:
    with (_FIXTURES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.mark.asyncio
async def test_run_jobs_get_parses_multiple_jobs_from_params_json() -> None:
    job = _load_fixture()
    client = FixtureJobClient(
        {
            "job_a": job,
            "job_b": {**job, "id": "job_b"},
        }
    )

    response = await run_jobs_get(
        _jobs_get_params(
            {
                "jobs": [
                    {"projectId": "analytics-prod", "jobId": "job_a"},
                    {"projectId": "analytics-prod", "jobId": "job_b"},
                ],
            }
        ),
        InspectionCommandOptions(client=client, tool_version="0.2.0"),
    )

    assert response["request"]["jobs"] == [
        {"projectId": "analytics-prod", "jobId": "job_a"},
        {"projectId": "analytics-prod", "jobId": "job_b"},
    ]


@pytest.mark.asyncio
async def test_run_jobs_get_returns_full_job_payload() -> None:
    job = _load_fixture()
    client = FixtureJobClient({"job_a": job})

    response = await run_jobs_get(
        _jobs_get_params(
            {
                "jobs": [{"projectId": "analytics-prod", "jobId": "job_a"}],
            }
        ),
        InspectionCommandOptions(client=client, tool_version="0.2.0"),
    )

    job_payload = response["jobs"][0]["job"]
    assert job_payload["id"] == "analytics-prod:US.job_123"
    assert job_payload["statistics"] is not None
    assert job_payload["configuration"] is not None
    assert response["request"]["view"] == "full"
    assert "selector" not in response["request"]


@pytest.mark.asyncio
async def test_run_jobs_get_requires_params() -> None:
    with pytest.raises(BqInspectFailure):
        await run_jobs_get(
            [],
            InspectionCommandOptions(client=FixtureJobClient({}), tool_version="0.2.0"),
        )


@pytest.mark.asyncio
async def test_run_jobs_get_rejects_unknown_operational_flags() -> None:
    with pytest.raises(BqInspectFailure):
        await run_jobs_get(
            ["--format", "ndjson", "--params", "{}"],
            InspectionCommandOptions(client=FixtureJobClient({}), tool_version="0.2.0"),
        )


@pytest.mark.asyncio
async def test_run_jobs_get_rejects_removed_selector_and_preset_params() -> None:
    client = InspectionCommandOptions(client=FixtureJobClient({}), tool_version="0.2.0")

    with pytest.raises(BqInspectFailure):
        await run_jobs_get(
            _jobs_get_params(
                {
                    "jobs": [{"projectId": "analytics-prod", "jobId": "job_a"}],
                    "selector": "id",
                }
            ),
            client,
        )

    with pytest.raises(BqInspectFailure):
        await run_jobs_get(
            _jobs_get_params(
                {
                    "jobs": [{"projectId": "analytics-prod", "jobId": "job_a"}],
                    "preset": "diagnostic",
                }
            ),
            client,
        )


@pytest.mark.asyncio
async def test_run_jobs_get_echoes_impersonation_fields_on_request_envelope() -> None:
    job = _load_fixture()
    client = FixtureJobClient({"job_a": job})

    response = await run_jobs_get(
        _jobs_get_params(
            {
                "jobs": [{"projectId": "analytics-prod", "jobId": "job_a"}],
                "impersonateServiceAccount": "target@analytics-prod.iam.gserviceaccount.com",
                "impersonateDelegates": ["delegate@analytics-prod.iam.gserviceaccount.com"],
            }
        ),
        InspectionCommandOptions(client=client, tool_version="0.2.0"),
    )

    assert response["request"]["impersonateServiceAccount"] == (
        "target@analytics-prod.iam.gserviceaccount.com"
    )
    assert response["request"]["impersonateDelegates"] == [
        "delegate@analytics-prod.iam.gserviceaccount.com"
    ]
