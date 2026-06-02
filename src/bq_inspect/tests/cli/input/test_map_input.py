"""Tests for CLI input mapping."""

from __future__ import annotations

from bq_inspect.core.jobs.list_request_fields import parse_iso_timestamp_to_millis
from bq_inspect.input.map_input import (
    map_catalog_input,
    map_jobs_list_input,
    map_jobs_view_input,
)


def test_map_jobs_view_input_normalizes_job_refs() -> None:
    result = map_jobs_view_input(
        {
            "jobs": [{"projectId": " p ", "jobId": "j", "location": "US"}],
        }
    )

    assert result == {
        "jobs": [{"projectId": "p", "jobId": "j", "location": "US"}],
    }


def test_map_jobs_view_input_maps_impersonation_fields() -> None:
    result = map_jobs_view_input(
        {
            "jobs": [{"projectId": "p", "jobId": "j"}],
            "impersonateServiceAccount": " sa@x.com ",
            "impersonateDelegates": [" d@x.com ", ""],
        }
    )

    assert result == {
        "jobs": [{"projectId": "p", "jobId": "j"}],
        "impersonateServiceAccount": "sa@x.com",
        "impersonateDelegates": ["d@x.com"],
    }


def test_map_jobs_view_input_drops_empty_impersonate_delegates() -> None:
    result = map_jobs_view_input(
        {
            "jobs": [{"projectId": "p", "jobId": "j"}],
            "impersonateDelegates": ["", "  "],
        }
    )

    assert result == {"jobs": [{"projectId": "p", "jobId": "j"}]}


def test_map_jobs_list_input_maps_optional_list_request_and_filter_fields() -> None:
    result = map_jobs_list_input(
        {
            "projectId": " p ",
            "maxCreationTime": "2026-05-18T00:00:00.000Z",
            "pageToken": " tok ",
            "maxResults": 10,
            "minBytesBilled": "1000",
            "state": " DONE ",
            "parentJobId": " parent ",
        }
    )

    assert result["listRequest"] == {
        "projectId": "p",
        "maxCreationTime": parse_iso_timestamp_to_millis("2026-05-18T00:00:00.000Z"),
        "pageToken": "tok",
        "maxResults": 10,
        "state": "DONE",
        "parentJobId": "parent",
    }
    assert result["filters"].min_bytes_billed == 1000


def test_map_catalog_input_trims_catalog_identifiers_and_optional_table_id() -> None:
    result = map_catalog_input({"projectId": " p ", "datasetId": " d ", "tableId": " t "})

    assert result == {
        "projectId": "p",
        "datasetId": "d",
        "tableId": "t",
    }
