"""Tests for list_jobs orchestration."""

from __future__ import annotations

import pytest

from bq_inspect.core.jobs.filter import JobFilters
from bq_inspect.core.jobs.list import ListJobsOrchestrationInput, list_jobs
from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error
from bq_inspect.tests.test_support.fixture_job_client import (
    FixtureBigQueryClient,
    FixtureBigQueryInput,
)


@pytest.mark.asyncio
async def test_returns_filtered_jobs_and_next_page_token() -> None:
    client = FixtureBigQueryClient(
        FixtureBigQueryInput(
            list_jobs_page={
                "jobs": [
                    {"status": {"state": "DONE"}, "statistics": {"query": {"totalSlotMs": "5000"}}},
                    {"status": {"state": "DONE"}, "statistics": {"query": {"totalSlotMs": "10"}}},
                ],
                "nextPageToken": "next",
            }
        )
    )

    response = await list_jobs(
        ListJobsOrchestrationInput(
            client=client,
            tool_version="0.1.0",
            list_request={"projectId": "p"},
            filters=JobFilters(min_slot_ms=1000),
        )
    )

    assert response["errors"] == []
    assert len(response["jobs"]) == 1
    assert response["page"]["nextPageToken"] == "next"
    assert response["request"]["projectId"] == "p"
    assert response["request"]["filters"]["minSlotMs"] == "1000"


@pytest.mark.asyncio
async def test_captures_bigquery_failures_in_errors_envelope() -> None:
    class DenyClient:
        """Client that denies list_jobs requests."""

        async def get_job(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

        async def list_jobs(self, request: object) -> object:
            del request
            raise BqInspectFailure(
                create_bq_inspect_error(
                    code="BQINSPECT_PERMISSION_DENIED",
                    message="Denied.",
                    source={"api": "bigquery.jobs.list", "status": 403},
                )
            )

        async def get_dataset(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

        async def list_tables(self, ref: object) -> list[object]:
            del ref
            raise RuntimeError("not used")

        async def get_table(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

    response = await list_jobs(
        ListJobsOrchestrationInput(
            client=DenyClient(),
            tool_version="0.1.0",
            list_request={"projectId": "p"},
            filters=JobFilters(),
        )
    )

    assert response["jobs"] == []
    assert len(response["errors"]) == 1
    assert response["errors"][0]["code"] == "BQINSPECT_PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_rethrows_non_bq_inspect_failure_errors() -> None:
    class BoomClient:
        """Client that raises unexpected errors from list_jobs."""

        async def get_job(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

        async def list_jobs(self, request: object) -> object:
            del request
            raise RuntimeError("boom")

        async def get_dataset(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

        async def list_tables(self, ref: object) -> list[object]:
            del ref
            raise RuntimeError("not used")

        async def get_table(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

    with pytest.raises(RuntimeError, match="boom"):
        await list_jobs(
            ListJobsOrchestrationInput(
                client=BoomClient(),
                tool_version="0.1.0",
                list_request={"projectId": "p"},
                filters=JobFilters(),
            )
        )


@pytest.mark.asyncio
async def test_echoes_list_request_options_and_impersonation() -> None:
    client = FixtureBigQueryClient(FixtureBigQueryInput(list_jobs_page={"jobs": []}))

    response = await list_jobs(
        ListJobsOrchestrationInput(
            client=client,
            tool_version="0.1.0",
            list_request={
                "projectId": "p",
                "allUsers": True,
                "minCreationTime": 1,
                "maxCreationTime": 2,
                "pageToken": "tok",
                "maxResults": 10,
                "state": "DONE",
                "parentJobId": "parent_1",
            },
            filters=JobFilters(labels={"team": "data"}),
            impersonate_service_account="sa@p.iam.gserviceaccount.com",
            impersonate_delegates=["d@p.iam.gserviceaccount.com"],
        )
    )

    assert response["request"]["projectId"] == "p"
    assert response["request"]["allUsers"] is True
    assert response["request"]["minCreationTime"] == 1
    assert response["request"]["maxCreationTime"] == 2
    assert response["request"]["pageToken"] == "tok"
    assert response["request"]["maxResults"] == 10
    assert response["request"]["state"] == "DONE"
    assert response["request"]["parentJobId"] == "parent_1"
    assert response["request"]["impersonateServiceAccount"] == "sa@p.iam.gserviceaccount.com"
    assert response["request"]["impersonateDelegates"] == ["d@p.iam.gserviceaccount.com"]
    assert response["request"]["filters"] == {"labels": {"team": "data"}}
