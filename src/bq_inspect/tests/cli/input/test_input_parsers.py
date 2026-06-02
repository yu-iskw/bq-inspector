"""Tests for CLI input parsers."""

from __future__ import annotations

import pytest

from bq_inspect.input.input_parsers import (
    parse_datasets_get_input,
    parse_jobs_get_input,
    parse_jobs_list_input,
    parse_tables_get_input,
    parse_tables_list_input,
)
from bq_inspect.core.jobs.list_request_fields import parse_iso_timestamp_to_millis
from bq_inspect.core.shared.errors import BqInspectFailure


def test_parse_jobs_get_input_parses_jobs_with_optional_location() -> None:
    result = parse_jobs_get_input(
        {
            "jobs": [{"projectId": "p", "jobId": "a", "location": "US"}],
        }
    )

    assert result["jobs"] == [{"projectId": "p", "jobId": "a", "location": "US"}]


def test_parse_jobs_get_input_rejects_removed_redaction_field() -> None:
    with pytest.raises(BqInspectFailure):
        parse_jobs_get_input(
            {
                "jobs": [{"projectId": "p", "jobId": "a"}],
                "redaction": "strict",
            }
        )


def test_parse_jobs_get_input_rejects_removed_selector_and_preset_fields() -> None:
    with pytest.raises(BqInspectFailure):
        parse_jobs_get_input(
            {
                "jobs": [{"projectId": "p", "jobId": "a"}],
                "selector": "id",
            }
        )

    with pytest.raises(BqInspectFailure):
        parse_jobs_get_input(
            {
                "jobs": [{"projectId": "p", "jobId": "a"}],
                "preset": "diagnostic",
            }
        )


def test_parse_jobs_get_input_rejects_unknown_keys() -> None:
    with pytest.raises(BqInspectFailure):
        parse_jobs_get_input(
            {
                "jobs": [{"projectId": "p", "jobId": "a"}],
                "projectId": "p",
            }
        )


def test_parse_jobs_list_input_parses_api_list_request_and_post_list_filters() -> None:
    result = parse_jobs_list_input(
        {
            "projectId": "p",
            "allUsers": True,
            "minCreationTime": "2026-05-17T00:00:00.000Z",
            "state": "DONE",
            "parentJobId": "parent_1",
            "minSlotMs": "60000",
            "labels": {"env": "prod"},
        }
    )

    assert result["listRequest"] == {
        "projectId": "p",
        "allUsers": True,
        "minCreationTime": parse_iso_timestamp_to_millis("2026-05-17T00:00:00.000Z"),
        "state": "DONE",
        "parentJobId": "parent_1",
    }
    assert result["filters"].min_slot_ms == 60_000
    assert result["filters"].labels == {"env": "prod"}


def test_parse_jobs_list_input_rejects_location() -> None:
    with pytest.raises(BqInspectFailure):
        parse_jobs_list_input(
            {
                "projectId": "p",
                "location": "EU",
            }
        )


def test_parse_datasets_get_input_parses_catalog_identifiers() -> None:
    assert parse_datasets_get_input({"projectId": "p", "datasetId": "d"}) == {
        "projectId": "p",
        "datasetId": "d",
    }


def test_parse_tables_list_input_matches_datasets_get_shape() -> None:
    assert parse_tables_list_input({"projectId": "p", "datasetId": "d"}) == {
        "projectId": "p",
        "datasetId": "d",
    }


def test_parse_tables_get_input_requires_table_id() -> None:
    assert parse_tables_get_input({"projectId": "p", "datasetId": "d", "tableId": "t"}) == {
        "projectId": "p",
        "datasetId": "d",
        "tableId": "t",
    }

    with pytest.raises(BqInspectFailure):
        parse_tables_get_input({"projectId": "p", "datasetId": "d"})
