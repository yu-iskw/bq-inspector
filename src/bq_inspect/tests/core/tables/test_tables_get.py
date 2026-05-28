"""Tests for get_table_metadata."""

from __future__ import annotations

import pytest

from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error
from bq_inspect.core.tables.get import get_table_metadata


@pytest.mark.asyncio
async def test_returns_table_metadata_on_success() -> None:
    class Client:
        async def get_table(self, ref: object) -> object:
            del ref
            return {"tableId": "t1", "type": "TABLE"}

    response = await get_table_metadata(
        {"projectId": "p", "datasetId": "d1", "tableId": "t1"},
        client=Client(),
        tool_version="0.1.0",
    )

    assert response["errors"] == []
    assert response["resource"] == {"tableId": "t1", "type": "TABLE"}
    assert response["request"] == {"projectId": "p", "datasetId": "d1", "tableId": "t1"}


@pytest.mark.asyncio
async def test_returns_errors_for_table_metadata_failures() -> None:
    class Client:
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
        client=Client(),
        tool_version="0.1.0",
    )

    assert "resource" not in response
    assert response["errors"][0]["code"] == "BQINSPECT_JOB_NOT_FOUND"
