"""Tests for validate_input."""

from __future__ import annotations

import pytest

from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.schemas.validate_input import validate_input


def test_accepts_valid_jobs_get_params() -> None:
    obj = validate_input("jobs get", {"jobs": [{"projectId": "p", "jobId": "j"}]})
    assert len(obj["jobs"]) == 1


def test_rejects_non_object_params() -> None:
    with pytest.raises(BqInspectFailure):
        validate_input("jobs get", None)
    with pytest.raises(BqInspectFailure):
        validate_input("jobs get", [])


def test_rejects_empty_jobs_array() -> None:
    with pytest.raises(BqInspectFailure):
        validate_input("jobs get", {"jobs": []})


def test_rejects_unknown_properties() -> None:
    with pytest.raises(BqInspectFailure):
        validate_input(
            "jobs get",
            {
                "jobs": [{"projectId": "p", "jobId": "j"}],
                "projectId": "p",
            },
        )
    with pytest.raises(BqInspectFailure):
        validate_input(
            "jobs get",
            {
                "jobs": [{"projectId": "p", "jobId": "j"}],
                "redaction": "default",
            },
        )


def test_rejects_invalid_date_time_on_jobs_list() -> None:
    with pytest.raises(BqInspectFailure):
        validate_input(
            "jobs list",
            {
                "projectId": "p",
                "minCreationTime": "not-a-date",
            },
        )


def test_rejects_naive_date_time_without_timezone_on_jobs_list() -> None:
    with pytest.raises(BqInspectFailure):
        validate_input(
            "jobs list",
            {
                "projectId": "p",
                "minCreationTime": "2026-05-17T00:00:00",
            },
        )


def test_rejects_invalid_min_slot_ms_pattern() -> None:
    with pytest.raises(BqInspectFailure):
        validate_input(
            "jobs list",
            {
                "projectId": "p",
                "minSlotMs": "abc",
            },
        )


def test_includes_schema_errors_on_failure() -> None:
    with pytest.raises(BqInspectFailure) as exc_info:
        validate_input("jobs get", {"jobs": []})
    failure = exc_info.value
    schema_errors = failure.details.get("source", {}).get("schemaErrors", [])
    assert len(schema_errors) > 0


def test_requires_table_id_for_tables_get() -> None:
    with pytest.raises(BqInspectFailure):
        validate_input(
            "tables get",
            {
                "projectId": "p",
                "datasetId": "d",
            },
        )
