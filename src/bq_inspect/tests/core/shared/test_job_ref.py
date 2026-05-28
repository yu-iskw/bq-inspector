"""Tests for job reference normalization."""

from __future__ import annotations

import pytest

from bq_inspect.core.shared.errors import BqInspectFailure
from bq_inspect.core.shared.job_ref import normalize_job_ref


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
        "code": "BQINSPECT_INPUT_INVALID",
        "message": "Project ID is required.",
        "retriable": False,
    }


def test_rejects_blank_job_ids() -> None:
    with pytest.raises(BqInspectFailure) as exc_info:
        normalize_job_ref({"projectId": "analytics-prod", "jobId": " "})
    assert exc_info.value.details == {
        "code": "BQINSPECT_INPUT_INVALID",
        "message": "Job ID is required.",
        "retriable": False,
    }
