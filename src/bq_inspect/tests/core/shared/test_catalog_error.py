"""Tests for catalog error envelope."""

from __future__ import annotations

import pytest

from bq_inspect.core.shared.catalog_error import catalog_error_envelope
from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error


def test_maps_bq_inspect_failure_to_errors_array() -> None:
    tool = {"name": "bq-inspect", "version": "0.1.0", "readOnly": True}
    failure = BqInspectFailure(
        create_bq_inspect_error(
            code="BQINSPECT_PERMISSION_DENIED",
            message="Denied.",
            source={"api": "bigquery.datasets.get", "status": 403},
        )
    )
    envelope = catalog_error_envelope(
        "bq-inspect.v1",
        tool,
        {"projectId": "p", "datasetId": "d1"},
        failure,
    )
    assert len(envelope["errors"]) == 1
    assert envelope["errors"][0]["code"] == "BQINSPECT_PERMISSION_DENIED"
    assert envelope["request"] == {"projectId": "p", "datasetId": "d1"}
    assert "resource" not in envelope


def test_includes_table_id_in_request_when_provided() -> None:
    tool = {"name": "bq-inspect", "version": "0.1.0", "readOnly": True}
    failure = BqInspectFailure(
        create_bq_inspect_error(
            code="BQINSPECT_JOB_NOT_FOUND",
            message="Missing.",
            source={"api": "bigquery.tables.get", "status": 404},
        )
    )
    envelope = catalog_error_envelope(
        "bq-inspect.v1",
        tool,
        {"projectId": "p", "datasetId": "d1", "tableId": "t1"},
        failure,
    )
    assert envelope["request"] == {"projectId": "p", "datasetId": "d1", "tableId": "t1"}


def test_rethrows_non_bq_inspect_failure_errors() -> None:
    tool = {"name": "bq-inspect", "version": "0.1.0", "readOnly": True}
    with pytest.raises(RuntimeError, match="boom"):
        catalog_error_envelope(
            "bq-inspect.v1",
            tool,
            {"projectId": "p", "datasetId": "d1"},
            RuntimeError("boom"),
        )
