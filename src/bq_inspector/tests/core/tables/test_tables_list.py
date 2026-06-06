"""Tests for list_tables_metadata."""

from __future__ import annotations

import pytest

from bq_inspector.core.shared.errors import BqInspectFailure, create_bq_inspector_error
from bq_inspector.core.tables.list import list_tables_metadata
from bq_inspector.tests.test_support.fixture_job_client import (
    FixtureBigQueryClient,
    FixtureBigQueryInput,
)


@pytest.mark.asyncio
async def test_returns_tables_list() -> None:
    client = FixtureBigQueryClient(
        FixtureBigQueryInput(
            tables_list_by_key={"p:d1": [{"tableId": "t1"}]},
        )
    )

    response = await list_tables_metadata(
        {"projectId": "p", "datasetId": "d1"},
        client=client,
        tool_version="0.2.0",
    )

    assert len(response["tables"]) == 1


@pytest.mark.asyncio
async def test_returns_errors_for_list_tables_failures() -> None:
    class DenyClient:
        """Client that denies list_tables requests."""

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
            raise BqInspectFailure(
                create_bq_inspector_error(
                    code="BQINSPECTOR_PERMISSION_DENIED",
                    message="Denied.",
                    source={"api": "bigquery.tables.list", "status": 403},
                )
            )

        async def get_table(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

    response = await list_tables_metadata(
        {"projectId": "p", "datasetId": "d1"},
        client=DenyClient(),
        tool_version="0.2.0",
    )

    assert response["tables"] == []
    assert response["errors"][0]["code"] == "BQINSPECTOR_PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_rethrows_non_bq_inspector_failure_errors() -> None:
    class BoomClient:
        """Client that raises unexpected errors from list_tables."""

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
            raise RuntimeError("boom")

        async def get_table(self, ref: object) -> object:
            del ref
            raise RuntimeError("not used")

    with pytest.raises(RuntimeError, match="boom"):
        await list_tables_metadata(
            {"projectId": "p", "datasetId": "d1"},
            client=BoomClient(),
            tool_version="0.2.0",
        )
