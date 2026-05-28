"""Tests for get_table_metadata."""

from __future__ import annotations

import pytest

from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error
from bq_inspect.core.tables.get import get_table_metadata
from bq_inspect.tests.test_support.fixture_job_client import (
    FixtureBigQueryClient,
    FixtureBigQueryInput,
)


@pytest.mark.asyncio
async def test_returns_table_metadata_on_success() -> None:
    client = FixtureBigQueryClient(
        FixtureBigQueryInput(
            tables_by_key={"p:d1:t1": {"tableId": "t1", "type": "TABLE"}},
        )
    )

    response = await get_table_metadata(
        {"projectId": "p", "datasetId": "d1", "tableId": "t1"},
        client=client,
        tool_version="0.1.0",
    )

    assert response["errors"] == []
    assert response["resource"] == {"tableId": "t1", "type": "TABLE"}
    assert response["request"] == {"projectId": "p", "datasetId": "d1", "tableId": "t1"}


@pytest.mark.asyncio
async def test_returns_errors_for_table_metadata_failures() -> None:
    class DenyClient:
        """Client that denies get_table requests."""

        async def get_job(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

        async def list_jobs(self, request: object) -> object:
            del request
            raise RuntimeError("not used")

        async def get_dataset(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

        async def list_tables(self, ref: object) -> list[object]:
            del ref
            raise RuntimeError("not used")

        async def get_table(self, ref: object) -> object:
            del ref
            raise BqInspectFailure(
                create_bq_inspect_error(
                    code="BQINSPECT_JOB_NOT_FOUND",
                    message="Missing.",
                    source={"api": "bigquery.tables.get", "status": 404},
                )
            )

    response = await get_table_metadata(
        {"projectId": "p", "datasetId": "d1", "tableId": "t1"},
        client=DenyClient(),
        tool_version="0.1.0",
    )

    assert "resource" not in response
    assert response["errors"][0]["code"] == "BQINSPECT_JOB_NOT_FOUND"
