"""Tests for Google API error mapping."""

from __future__ import annotations

import pytest

from bq_inspect.bigquery.errors.google_api_errors import (
    extract_google_error_message,
    map_google_error_to_bq_inspect_failure,
    map_http_status_to_error_code,
    resolve_http_status,
)
from bq_inspect.core.shared.api_error_hints import ApiErrorHintContext
from bq_inspect.core.shared.errors import BqInspectFailure


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (401, "BQINSPECT_PERMISSION_DENIED"),
        (403, "BQINSPECT_PERMISSION_DENIED"),
        (404, "BQINSPECT_JOB_NOT_FOUND"),
        (429, "BQINSPECT_API_RATE_LIMITED"),
        (500, "BQINSPECT_API_UNAVAILABLE"),
        (400, "BQINSPECT_INPUT_INVALID"),
        (418, "BQINSPECT_INPUT_INVALID"),
    ],
)
def test_map_http_status_to_error_code(status: int, code: str) -> None:
    assert map_http_status_to_error_code(status) == code


def test_resolve_http_status_reads_numeric_code() -> None:
    assert resolve_http_status({"code": 404}) == 404


def test_resolve_http_status_reads_nested_response_status() -> None:
    assert resolve_http_status({"response": {"status": 403}}) == 403


def test_resolve_http_status_parses_stringified_codes() -> None:
    assert resolve_http_status({"code": "429"}) == 429


def test_resolve_http_status_returns_none_for_non_http_codes() -> None:
    assert resolve_http_status({"code": "ENOTFOUND"}) is None
    assert resolve_http_status(None) is None


def test_extract_google_error_message_prefers_exception_message() -> None:
    assert extract_google_error_message(ValueError("boom")) == "boom"


def test_extract_google_error_message_falls_back_for_non_errors() -> None:
    assert extract_google_error_message("x") == "BigQuery request failed."


def test_extract_google_error_message_reads_plain_object_message() -> None:
    assert extract_google_error_message({"message": "from object"}) == "from object"


def test_map_google_error_to_bq_inspect_failure_maps_http_errors() -> None:
    failure = map_google_error_to_bq_inspect_failure(
        {"code": 404, "message": "Missing job."},
        "bigquery.jobs.get",
    )

    assert isinstance(failure, BqInspectFailure)
    assert failure.details["code"] == "BQINSPECT_JOB_NOT_FOUND"
    assert failure.details["source"] == {"api": "bigquery.jobs.get", "status": 404}


def test_map_google_error_to_bq_inspect_failure_adds_iam_hints_for_catalog_apis() -> None:
    failure = map_google_error_to_bq_inspect_failure(
        {"code": 403, "message": "Denied."},
        "bigquery.tables.get",
    )

    assert failure.details["code"] == "BQINSPECT_PERMISSION_DENIED"
    assert failure.details.get("hint") is not None
    assert "metadataViewer" in failure.details["hint"]
    assert failure.details["source"] == {"api": "bigquery.tables.get", "status": 403}


def test_map_google_error_to_bq_inspect_failure_adds_location_guidance_for_jobs_get_403() -> None:
    failure = map_google_error_to_bq_inspect_failure(
        {"code": 403, "message": "Access Denied."},
        "bigquery.jobs.get",
        context=ApiErrorHintContext(job_ref={"projectId": "p", "jobId": "j"}),
    )

    assert failure.details.get("hint") is not None
    assert "Add location on each job ref" in failure.details["hint"]


def test_map_google_error_to_bq_inspect_failure_adds_location_guidance_for_jobs_get_404() -> None:
    failure = map_google_error_to_bq_inspect_failure(
        {"code": 404, "message": "Not found: Job"},
        "bigquery.jobs.get",
        context=ApiErrorHintContext(job_ref={"projectId": "p", "jobId": "j"}),
    )

    assert failure.details["code"] == "BQINSPECT_JOB_NOT_FOUND"
    assert failure.details.get("hint") is not None
    assert "Add location on each job ref" in failure.details["hint"]


def test_map_google_error_to_bq_inspect_failure_maps_client_errors_as_non_retriable() -> None:
    failure = map_google_error_to_bq_inspect_failure(
        {"code": 400, "message": "Invalid state filter."},
        "bigquery.jobs.list",
    )

    assert failure.details["code"] == "BQINSPECT_INPUT_INVALID"
    assert failure.details["retriable"] is False
    assert failure.details["source"] == {"api": "bigquery.jobs.list", "status": 400}


def test_map_google_error_to_bq_inspect_failure_maps_missing_status_to_internal() -> None:
    failure = map_google_error_to_bq_inspect_failure(RuntimeError("network"))

    assert failure.details["code"] == "BQINSPECT_INTERNAL"
