"""Tests for inspect_jobs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from bq_inspector.core.jobs.get import InspectJobOptions, inspect_jobs
from bq_inspector.core.shared.errors import BqInspectFailure, create_bq_inspector_error
from bq_inspector.tests.test_support.fixture_job_client import FixtureJobClient

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def _load_fixture(name: str = "successful-query-job.json") -> dict[str, object]:
    with (_FIXTURES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.mark.asyncio
async def test_produces_envelope_shape_for_single_job_summary_view() -> None:
    job = _load_fixture()
    client = FixtureJobClient({"job_123": job})

    def fixed_now() -> datetime:
        return datetime(2020, 1, 1, tzinfo=timezone.utc)

    response = await inspect_jobs(
        {"jobs": [{"projectId": "analytics-prod", "location": "US", "jobId": "job_123"}]},
        InspectJobOptions(client=client, tool_version="0.1.0", now=fixed_now),
    )

    assert response["schemaVersion"] == "bq-inspector.v1"
    assert response["tool"] == {"name": "bq-inspector", "version": "0.1.0", "readOnly": True}
    assert response["request"] == {
        "jobs": [{"projectId": "analytics-prod", "location": "US", "jobId": "job_123"}],
        "view": "summary",
    }
    assert len(response["jobs"]) == 1
    assert response["jobs"][0]["jobRef"] == {
        "projectId": "analytics-prod",
        "location": "US",
        "jobId": "job_123",
    }
    assert response["jobs"][0]["source"] == {
        "api": "bigquery.jobs.get",
        "fetchedAt": "2020-01-01T00:00:00.000Z",
    }
    assert response["jobs"][0]["errors"] == []
    assert response["errors"] == []

    job_payload = response["jobs"][0]["job"]
    assert isinstance(job_payload, dict)
    assert job_payload["id"] == "analytics-prod:US.job_123"
    assert job_payload["status"] is not None
    assert job_payload["statistics"] is not None
    assert "configuration" not in job_payload


@pytest.mark.asyncio
async def test_supports_multiple_job_ids() -> None:
    job_a = _load_fixture()
    job_b = {**job_a, "id": "job_b"}
    client = FixtureJobClient({"job_a": job_a, "job_b": job_b})

    response = await inspect_jobs(
        {
            "jobs": [
                {"projectId": "analytics-prod", "jobId": "job_a"},
                {"projectId": "analytics-prod", "jobId": "job_b"},
            ]
        },
        InspectJobOptions(
            client=client,
            tool_version="0.1.0",
            now=lambda: datetime(2020, 1, 1, tzinfo=timezone.utc),
        ),
    )

    assert len(response["jobs"]) == 2
    assert response["jobs"][0]["jobRef"]["jobId"] == "job_a"
    assert response["jobs"][1]["jobRef"]["jobId"] == "job_b"


@pytest.mark.asyncio
async def test_parallel_fetch_records_per_job_errors_without_aborting_siblings() -> None:
    job_a = _load_fixture()

    class MixedOutcomeClient:
        async def get_job(self, ref: dict[str, str]) -> object:
            if ref["jobId"] == "job_a":
                return job_a
            raise BqInspectFailure(
                create_bq_inspector_error(
                    code="BQINSPECTOR_JOB_NOT_FOUND",
                    message="Missing job.",
                    source={"api": "bigquery.jobs.get", "status": 404},
                )
            )

    response = await inspect_jobs(
        {
            "jobs": [
                {"projectId": "analytics-prod", "jobId": "job_a"},
                {"projectId": "analytics-prod", "jobId": "job_b"},
            ]
        },
        InspectJobOptions(
            client=MixedOutcomeClient(),
            tool_version="0.1.0",
            now=lambda: datetime(2020, 1, 1, tzinfo=timezone.utc),
        ),
    )

    assert len(response["jobs"]) == 2
    assert response["jobs"][0]["errors"] == []
    assert response["jobs"][0]["job"] is not None
    assert response["jobs"][1]["errors"][0]["code"] == "BQINSPECTOR_JOB_NOT_FOUND"
    assert len(response["errors"]) == 1


@pytest.mark.asyncio
async def test_returns_full_job_payload_when_view_is_full() -> None:
    job = _load_fixture()
    client = FixtureJobClient({"job_123": job})

    response = await inspect_jobs(
        {
            "jobs": [{"projectId": "analytics-prod", "jobId": "job_123"}],
            "view": "full",
        },
        InspectJobOptions(
            client=client,
            tool_version="0.1.0",
            now=lambda: datetime(2020, 1, 1, tzinfo=timezone.utc),
        ),
    )

    full_job = response["jobs"][0]["job"]
    assert isinstance(full_job, dict)
    assert full_job["configuration"] is not None
    assert full_job["user_email"] == "alice@example.com"
    assert response["request"]["view"] == "full"


@pytest.mark.asyncio
async def test_records_validation_errors_for_invalid_job_references() -> None:
    client = FixtureJobClient({})

    response = await inspect_jobs(
        {"jobs": [{"projectId": " ", "jobId": "job_123"}]},
        InspectJobOptions(
            client=client,
            tool_version="0.1.0",
            now=lambda: datetime(2020, 1, 1, tzinfo=timezone.utc),
        ),
    )

    assert response["jobs"][0]["errors"][0]["code"] == "BQINSPECTOR_INPUT_INVALID"
    assert len(response["errors"]) == 1


@pytest.mark.asyncio
async def test_uses_fallback_job_ref_with_location_when_validation_fails() -> None:
    client = FixtureJobClient({})

    response = await inspect_jobs(
        {"jobs": [{"projectId": " ", "location": " US ", "jobId": " job_123 "}]},
        InspectJobOptions(
            client=client,
            tool_version="0.1.0",
            now=lambda: datetime(2020, 1, 1, tzinfo=timezone.utc),
        ),
    )

    assert response["jobs"][0]["jobRef"] == {
        "projectId": "",
        "location": "US",
        "jobId": "job_123",
    }
    assert response["jobs"][0]["errors"][0]["code"] == "BQINSPECTOR_INPUT_INVALID"
    assert len(response["errors"]) == 1


@pytest.mark.asyncio
async def test_records_bq_inspector_failure_from_get_job() -> None:
    class DenyClient:
        async def get_job(self, ref: object) -> object:
            del ref
            raise BqInspectFailure(
                create_bq_inspector_error(
                    code="BQINSPECTOR_JOB_NOT_FOUND",
                    message="Missing.",
                    source={"api": "bigquery.jobs.get", "status": 404},
                )
            )

    response = await inspect_jobs(
        {"jobs": [{"projectId": "p", "jobId": "missing"}]},
        InspectJobOptions(
            client=DenyClient(),
            tool_version="0.1.0",
            now=lambda: datetime(2020, 1, 1, tzinfo=timezone.utc),
        ),
    )

    assert response["jobs"][0]["errors"][0]["code"] == "BQINSPECTOR_JOB_NOT_FOUND"


@pytest.mark.asyncio
async def test_maps_unexpected_get_job_errors_to_internal_errors() -> None:
    class NetworkClient:
        async def get_job(self, ref: object) -> object:
            del ref
            raise RuntimeError("network")

    response = await inspect_jobs(
        {"jobs": [{"projectId": "p", "jobId": "j1"}]},
        InspectJobOptions(
            client=NetworkClient(),
            tool_version="0.1.0",
            now=lambda: datetime(2020, 1, 1, tzinfo=timezone.utc),
        ),
    )

    assert response["jobs"][0]["errors"][0]["code"] == "BQINSPECTOR_INTERNAL"
    assert response["jobs"][0]["errors"][0]["message"] == "network"


@pytest.mark.asyncio
async def test_includes_impersonation_fields_in_request_echo() -> None:
    job = _load_fixture()
    client = FixtureJobClient({"job_123": job})

    response = await inspect_jobs(
        {
            "jobs": [{"projectId": "p", "jobId": "job_123"}],
            "impersonateServiceAccount": "sa@p.iam.gserviceaccount.com",
            "impersonateDelegates": ["d@p.iam.gserviceaccount.com"],
        },
        InspectJobOptions(
            client=client,
            tool_version="0.1.0",
            now=lambda: datetime(2020, 1, 1, tzinfo=timezone.utc),
        ),
    )

    assert response["request"]["impersonateServiceAccount"] == "sa@p.iam.gserviceaccount.com"
    assert response["request"]["impersonateDelegates"] == ["d@p.iam.gserviceaccount.com"]
