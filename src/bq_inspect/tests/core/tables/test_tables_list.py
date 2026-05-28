"""Tests for list_tables_metadata."""

from __future__ import annotations

import pytest

from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error
from bq_inspect.core.tables.list import list_tables_metadata


@pytest.mark.asyncio
async def test_returns_tables_list() -> None:
    class Client:
        async def list_tables(self, ref: object) -> list[object]:
            del ref
            return [{"tableId": "t1"}]

    response = await list_tables_metadata(
        {"projectId": "p", "datasetId": "d1"},
        client=Client(),
        tool_version="0.1.0",
    )

    assert len(response["tables"]) == 1


@pytest.mark.asyncio
async def test_returns_errors_for_list_tables_failures() -> None:
    class Client:
        async def list_tables(self, ref: object) -> list[object]:
            del ref
            raise BqInspectFailure(
                create_bq_inspect_error(
                    code="BQINSPECT_PERMISSION_DENIED",
                    message="Denied.",
                    source={"api": "bigquery.tables.list", "status": 403},
                )
            )

    response = await list_tables_metadata(
        {"projectId": "p", "datasetId": "d1"},
        client=Client(),
        tool_version="0.1.0",
    )

    assert response["tables"] == []
    assert response["errors"][0]["code"] == "BQINSPECT_PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_rethrows_non_bq_inspect_failure_errors() -> None:
    class Client:
        async def list_tables(self, ref: object) -> list[object]:
            del ref
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await list_tables_metadata(
            {"projectId": "p", "datasetId": "d1"},
            client=Client(),
            tool_version="0.1.0",
        )
