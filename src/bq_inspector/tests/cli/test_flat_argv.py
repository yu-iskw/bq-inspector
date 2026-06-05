"""Tests for flat argv normalization and help policy."""

from __future__ import annotations

from bq_inspector.cli.flat_argv import flat_help_command_key, normalize_flat_job_argv


def test_prepends_jobs_for_job_subcommand() -> None:
    assert normalize_flat_job_argv(["performance", "--params", "{}"]) == [
        "jobs",
        "performance",
        "--params",
        "{}",
    ]


def test_leaves_nested_jobs_path_unchanged() -> None:
    assert normalize_flat_job_argv(["jobs", "summary"]) == ["jobs", "summary"]


def test_leaves_non_job_commands_unchanged() -> None:
    assert normalize_flat_job_argv(["datasets", "get"]) == ["datasets", "get"]


def test_leaves_lineage_group_subcommands_unchanged() -> None:
    assert normalize_flat_job_argv(["lineage", "links", "--input-schema"]) == [
        "lineage",
        "links",
        "--input-schema",
    ]
    assert normalize_flat_job_argv(["lineage", "graph", "--params", "{}"]) == [
        "lineage",
        "graph",
        "--params",
        "{}",
    ]


def test_flat_lineage_still_maps_to_jobs_lineage() -> None:
    assert normalize_flat_job_argv(["lineage", "--input-schema"]) == [
        "jobs",
        "lineage",
        "--input-schema",
    ]


def test_flat_help_lineage_resolves_to_group_not_jobs_lineage() -> None:
    assert flat_help_command_key(["lineage"]) is None
    assert flat_help_command_key(["lineage", "links"]) is None
