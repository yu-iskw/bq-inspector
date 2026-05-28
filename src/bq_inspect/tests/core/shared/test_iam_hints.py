"""Tests for IAM hint helpers."""

from __future__ import annotations

from bq_inspect.core.shared.iam_hints import iam_hint_for_api


def test_returns_jobs_hint() -> None:
    assert "resourceViewer" in (iam_hint_for_api("bigquery.jobs.get") or "")


def test_returns_metadata_hint_for_datasets_and_tables() -> None:
    assert "metadataViewer" in (iam_hint_for_api("bigquery.datasets.get") or "")
    assert "metadataViewer" in (iam_hint_for_api("bigquery.tables.list") or "")


def test_returns_none_for_unknown_apis() -> None:
    assert iam_hint_for_api("other.api") is None
