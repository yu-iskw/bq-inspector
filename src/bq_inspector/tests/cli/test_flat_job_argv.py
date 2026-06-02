"""Tests for flat job subcommand argv normalization."""

from __future__ import annotations

from bq_inspector.cli.click_cli import _normalize_flat_job_argv


def test_prepends_jobs_for_job_subcommand() -> None:
    assert _normalize_flat_job_argv(["performance", "--params", "{}"]) == [
        "jobs",
        "performance",
        "--params",
        "{}",
    ]


def test_leaves_nested_jobs_path_unchanged() -> None:
    assert _normalize_flat_job_argv(["jobs", "summary"]) == ["jobs", "summary"]


def test_leaves_non_job_commands_unchanged() -> None:
    assert _normalize_flat_job_argv(["datasets", "get"]) == ["datasets", "get"]
