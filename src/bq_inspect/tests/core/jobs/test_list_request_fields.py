"""Tests for jobs.list request field mapping helpers."""

from datetime import UTC, datetime

from bq_inspect.core.jobs.list_request_fields import parse_iso_timestamp_to_millis


def test_parse_iso_timestamp_to_millis_treats_naive_values_as_utc() -> None:
    naive = "2026-05-17T00:00:00"
    with_offset = "2026-05-17T00:00:00+00:00"
    with_z = "2026-05-17T00:00:00Z"

    assert parse_iso_timestamp_to_millis(naive) == parse_iso_timestamp_to_millis(with_offset)
    assert parse_iso_timestamp_to_millis(naive) == parse_iso_timestamp_to_millis(with_z)
    assert parse_iso_timestamp_to_millis(naive) == int(
        datetime(2026, 5, 17, tzinfo=UTC).timestamp() * 1000
    )
