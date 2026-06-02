"""Tests for API error hint helpers."""

from __future__ import annotations

from bq_inspector.core.shared.api_error_hints import ApiErrorHintContext, hint_for_api_error


def test_returns_iam_hint_for_permission_denied_on_jobs_apis() -> None:
    hint = hint_for_api_error("BQINSPECTOR_PERMISSION_DENIED", "bigquery.jobs.get")
    assert hint is not None
    assert "resourceViewer" in hint


def test_appends_location_guidance_without_location_on_job_ref() -> None:
    hint = hint_for_api_error(
        "BQINSPECTOR_PERMISSION_DENIED",
        "bigquery.jobs.get",
        ApiErrorHintContext(job_ref={"projectId": "p", "jobId": "j"}),
    )
    assert hint is not None
    assert "resourceViewer" in hint
    assert "Add location on each job ref" in hint


def test_appends_location_guidance_for_job_not_found_without_location() -> None:
    hint = hint_for_api_error(
        "BQINSPECTOR_JOB_NOT_FOUND",
        "bigquery.jobs.get",
        ApiErrorHintContext(job_ref={"projectId": "p", "jobId": "j"}),
    )
    assert hint is not None
    assert "Add location on each job ref" in hint


def test_appends_job_ref_verification_when_permission_denied_with_location() -> None:
    hint = hint_for_api_error(
        "BQINSPECTOR_PERMISSION_DENIED",
        "bigquery.jobs.get",
        ApiErrorHintContext(job_ref={"projectId": "p", "jobId": "j", "location": "US"}),
    )
    assert hint is not None
    assert "resourceViewer" in hint
    assert "Confirm projectId and jobId from jobs.list" in hint
    assert "Add location on each job ref" not in hint


def test_returns_catalog_hint_for_dataset_not_found() -> None:
    hint = hint_for_api_error("BQINSPECTOR_JOB_NOT_FOUND", "bigquery.datasets.get")
    assert hint is not None
    assert "datasetId" in hint
    assert "source.api" in hint


def test_returns_none_for_non_permission_errors_without_job_context() -> None:
    assert hint_for_api_error("BQINSPECTOR_API_RATE_LIMITED", "bigquery.jobs.get") is None
