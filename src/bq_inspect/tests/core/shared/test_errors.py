"""Tests for shared error helpers."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from bq_inspect.core.shared.errors import (
    BqInspectFailure,
    create_bq_inspect_error,
    get_exit_code,
)

if TYPE_CHECKING:
    from bq_inspect.core.shared.types import BqInspectError, BqInspectErrorCode

_EXIT_CODE_CASES: list[tuple[BqInspectErrorCode, int]] = [
    ("BQINSPECT_INPUT_INVALID", 2),
    ("BQINSPECT_PERMISSION_DENIED", 3),
    ("BQINSPECT_JOB_NOT_FOUND", 4),
    ("BQINSPECT_LOCATION_REQUIRED", 2),
    ("BQINSPECT_API_RATE_LIMITED", 5),
    ("BQINSPECT_API_UNAVAILABLE", 5),
    ("BQINSPECT_INTERNAL", 1),
]


@pytest.mark.parametrize(("code", "exit_code"), _EXIT_CODE_CASES)
def test_get_exit_code(code: BqInspectErrorCode, exit_code: int) -> None:
    assert get_exit_code(_error_with_code(code)) == exit_code


def test_bq_inspect_failure_serializes_only_structured_error_details() -> None:
    failure = BqInspectFailure(
        create_bq_inspect_error(
            code="BQINSPECT_JOB_NOT_FOUND",
            message="Job was not found.",
            hint="Check the job ID and location.",
            source={"api": "bigquery.jobs.get", "status": 404},
        )
    )
    serialized = json.dumps(failure.to_json())
    assert json.loads(serialized) == {
        "code": "BQINSPECT_JOB_NOT_FOUND",
        "message": "Job was not found.",
        "hint": "Check the job ID and location.",
        "retriable": False,
        "source": {"api": "bigquery.jobs.get", "status": 404},
    }
    assert "stack" not in serialized


def test_create_non_retriable_input_validation_errors() -> None:
    assert create_bq_inspect_error(
        code="BQINSPECT_INPUT_INVALID",
        message="Project ID is required.",
    ) == {
        "code": "BQINSPECT_INPUT_INVALID",
        "message": "Project ID is required.",
        "retriable": False,
    }


def test_create_retriable_api_availability_errors_by_default() -> None:
    assert create_bq_inspect_error(
        code="BQINSPECT_API_UNAVAILABLE",
        message="BigQuery is unavailable.",
    ) == {
        "code": "BQINSPECT_API_UNAVAILABLE",
        "message": "BigQuery is unavailable.",
        "retriable": True,
    }


def _error_with_code(code: BqInspectErrorCode) -> BqInspectError:
    return {"code": code, "message": code, "retriable": False}
