"""Tests for job reference normalization."""

from __future__ import annotations

import pytest

from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.core.shared.job_ref import normalize_job_ref


def test_trims_project_location_and_job_id() -> None:
    assert normalize_job_ref(
        {"projectId": " analytics-prod ", "location": " US ", "jobId": " job_123 "}
    ) == {"projectId": "analytics-prod", "location": "US", "jobId": "job_123"}


def test_omits_blank_locations_after_trimming() -> None:
    assert normalize_job_ref(
        {"projectId": "analytics-prod", "location": " ", "jobId": "job_123"}
    ) == {"projectId": "analytics-prod", "jobId": "job_123"}


def test_rejects_blank_project_ids() -> None:
    with pytest.raises(BqInspectFailure) as exc_info:
        normalize_job_ref({"projectId": " ", "jobId": "job_123"})
    assert exc_info.value.details == {
        "code": "BQINSPECTOR_INPUT_INVALID",
        "message": "Project ID is required.",
        "retriable": False,
    }


def test_rejects_blank_job_ids() -> None:
    with pytest.raises(BqInspectFailure) as exc_info:
        normalize_job_ref({"projectId": "analytics-prod", "jobId": " "})
    assert exc_info.value.details == {
        "code": "BQINSPECTOR_INPUT_INVALID",
        "message": "Job ID is required.",
        "retriable": False,
    }


def test_parses_composite_job_id_from_job_id_field() -> None:
    assert normalize_job_ref(
        {
            "projectId": "ubie-yu-sandbox",
            "jobId": "ubie-yu-sandbox:US.bquxjob_e77feda_19e85d5e021",
        }
    ) == {
        "projectId": "ubie-yu-sandbox",
        "location": "US",
        "jobId": "bquxjob_e77feda_19e85d5e021",
    }


def test_composite_job_id_rejects_mismatched_project_id() -> None:
    with pytest.raises(BqInspectFailure) as exc_info:
        normalize_job_ref(
            {
                "projectId": "other-project",
                "jobId": "ubie-yu-sandbox:US.bquxjob_e77feda_19e85d5e021",
            }
        )
    assert exc_info.value.details["code"] == "BQINSPECTOR_INPUT_INVALID"
    assert "project in jobId" in exc_info.value.details["message"]


def test_composite_job_id_rejects_conflicting_location() -> None:
    with pytest.raises(BqInspectFailure) as exc_info:
        normalize_job_ref(
            {
                "projectId": "p",
                "jobId": "p:US.job1",
                "location": "EU",
            }
        )
    assert exc_info.value.details["code"] == "BQINSPECTOR_INPUT_INVALID"
    assert "location must match" in exc_info.value.details["message"]


def test_plain_job_id_unchanged() -> None:
    assert normalize_job_ref(
        {"projectId": "analytics-prod", "jobId": "bquxjob_abc", "location": "US"}
    ) == {"projectId": "analytics-prod", "location": "US", "jobId": "bquxjob_abc"}
