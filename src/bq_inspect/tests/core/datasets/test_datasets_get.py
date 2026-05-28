"""Tests for get_dataset_metadata."""

from __future__ import annotations

import pytest

from bq_inspect.core.datasets.get import get_dataset_metadata
from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error
from bq_inspect.tests.test_support.fixture_job_client import (
    FixtureBigQueryClient,
    FixtureBigQueryInput,
)


@pytest.mark.asyncio
async def test_returns_dataset_metadata() -> None:
    client = FixtureBigQueryClient(
        FixtureBigQueryInput(
            datasets_by_key={"p:d1": {"datasetId": "d1", "friendlyName": "D"}},
        )
    )

    response = await get_dataset_metadata(
        {"projectId": "p", "datasetId": "d1"},
        client=client,
        tool_version="0.1.0",
    )

    assert response["errors"] == []
    assert response["resource"] == {"datasetId": "d1", "friendlyName": "D"}


@pytest.mark.asyncio
async def test_returns_errors_for_dataset_metadata_failures() -> None:
    class DenyClient:
        """Client that denies get_dataset requests."""

        async def get_job(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

        async def list_jobs(self, request: object) -> object:
            del request
            raise RuntimeError("not used")

        async def get_dataset(self, ref: object) -> object:
            del ref
            raise BqInspectFailure(
                create_bq_inspect_error(
                    code="BQINSPECT_PERMISSION_DENIED",
                    message="Denied.",
                    source={"api": "bigquery.datasets.get", "status": 403},
                )
            )

        async def list_tables(self, ref: object) -> list[object]:
            del ref
            raise RuntimeError("not used")

        async def get_table(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

    response = await get_dataset_metadata(
        {"projectId": "p", "datasetId": "d1"},
        client=DenyClient(),
        tool_version="0.1.0",
    )

    assert "resource" not in response
    assert response["errors"][0]["code"] == "BQINSPECT_PERMISSION_DENIED"
