"""Tests for get_dataset_metadata."""

from __future__ import annotations

import pytest

from bq_inspect.core.datasets.get import get_dataset_metadata
from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error


@pytest.mark.asyncio
async def test_returns_dataset_metadata() -> None:
    class Client:
        async def get_dataset(self, ref: object) -> object:
            del ref
            return {"datasetId": "d1", "friendlyName": "D"}

    response = await get_dataset_metadata(
        {"projectId": "p", "datasetId": "d1"},
        client=Client(),
        tool_version="0.1.0",
    )

    assert response["errors"] == []
    assert response["resource"] == {"datasetId": "d1", "friendlyName": "D"}


@pytest.mark.asyncio
async def test_returns_errors_for_dataset_metadata_failures() -> None:
    class Client:
        async def get_dataset(self, ref: object) -> object:
            del ref
            raise BqInspectFailure(
                create_bq_inspect_error(
                    code="BQINSPECT_PERMISSION_DENIED",
                    message="Denied.",
                    source={"api": "bigquery.datasets.get", "status": 403},
                )
            )

    response = await get_dataset_metadata(
        {"projectId": "p", "datasetId": "d1"},
        client=Client(),
        tool_version="0.1.0",
    )

    assert "resource" not in response
    assert response["errors"][0]["code"] == "BQINSPECT_PERMISSION_DENIED"
