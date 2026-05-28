"""Tests for post-list job filtering."""

from __future__ import annotations

from bq_inspect.core.jobs.filter import JobFilters, filter_job_summaries


def test_filters_by_minimum_slot_ms_using_query_total_slot_ms() -> None:
    base_job = {
        "status": {"state": "DONE"},
        "statistics": {
            "query": {
                "totalSlotMs": "5000",
                "totalBytesBilled": "100",
            },
        },
        "labels": {"team": "data-platform", "dbt_invocation_id": "abc"},
    }
    jobs = [
        base_job,
        {
            **base_job,
            "statistics": {"query": {"totalSlotMs": "10", "totalBytesBilled": "100"}},
        },
    ]
    filtered = filter_job_summaries(jobs, JobFilters(min_slot_ms=1000))
    assert len(filtered) == 1
    assert filtered[0] == base_job


def test_falls_back_to_statistics_total_slot_ms() -> None:
    job = {
        "status": {"state": "DONE"},
        "statistics": {"totalSlotMs": "8000", "query": {"totalBytesBilled": "1"}},
    }
    filtered = filter_job_summaries([job], JobFilters(min_slot_ms=7000))
    assert filtered == [job]


def test_filters_by_labels() -> None:
    base_job = {
        "status": {"state": "DONE"},
        "statistics": {
            "query": {
                "totalSlotMs": "5000",
                "totalBytesBilled": "100",
            },
        },
        "labels": {"team": "data-platform", "dbt_invocation_id": "abc"},
    }
    jobs = [base_job, {**base_job, "labels": {"team": "other"}}]
    filtered = filter_job_summaries(jobs, JobFilters(labels={"team": "data-platform"}))
    assert len(filtered) == 1


def test_filters_by_minimum_bytes_billed() -> None:
    base_job = {
        "status": {"state": "DONE"},
        "statistics": {
            "query": {
                "totalSlotMs": "5000",
                "totalBytesBilled": "100",
            },
        },
        "labels": {"team": "data-platform", "dbt_invocation_id": "abc"},
    }
    jobs = [
        base_job,
        {
            **base_job,
            "statistics": {"query": {"totalSlotMs": "5000", "totalBytesBilled": "1"}},
        },
    ]
    filtered = filter_job_summaries(jobs, JobFilters(min_bytes_billed=50))
    assert len(filtered) == 1
    assert filtered[0] == base_job


def test_excludes_jobs_with_invalid_numeric_statistics() -> None:
    job = {
        "status": {"state": "DONE"},
        "statistics": {"query": {"totalSlotMs": "not-a-number", "totalBytesBilled": "100"}},
    }
    assert filter_job_summaries([job], JobFilters(min_slot_ms=1)) == []


def test_ignores_empty_label_filters() -> None:
    base_job = {
        "status": {"state": "DONE"},
        "statistics": {
            "query": {
                "totalSlotMs": "5000",
                "totalBytesBilled": "100",
            },
        },
        "labels": {"team": "data-platform", "dbt_invocation_id": "abc"},
    }
    assert filter_job_summaries([base_job], JobFilters(labels={})) == [base_job]
