"""Canonical registry of CLI commands, usage strings, and runners."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from bq_inspect.cli.usage_build import (
    ParamsBodyKind,
    ParamsCommandUsageMeta,
    build_datasets_group_usage,
    build_global_usage,
    build_jobs_group_usage,
    build_params_command_usage,
    build_schema_group_usage,
    build_schema_subcommand_usage,
    build_tables_group_usage,
)
from bq_inspect.commands.datasets.get import datasets_get_command
from bq_inspect.commands.jobs.list import run_jobs_list_command
from bq_inspect.commands.jobs.run_jobs_view import (
    jobs_get_command,
    jobs_impact_command,
    jobs_lineage_command,
    jobs_performance_command,
    jobs_query_command,
    jobs_summary_command,
)
from bq_inspect.commands.schema import run_schema_for_name
from bq_inspect.commands.tables.get import tables_get_command
from bq_inspect.commands.tables.list import tables_list_command

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any

    from bq_inspect.commands.command_shared import ParamsCommandRunner

GLOBAL_USAGE = build_global_usage()


@dataclass(frozen=True)
class GroupCommandSpec:
    """Top-level CLI group with help text and nested params commands."""

    name: str
    usage: str
    commands: tuple[ParamsCommandSpec, ...]


@dataclass(frozen=True)
class ParamsCommandSpec:
    """Params-based CLI command."""

    path: tuple[str, ...]
    usage: str
    runner: ParamsCommandRunner


@dataclass(frozen=True)
class SchemaCommandSpec:
    """Legacy schema subcommand."""

    name: str
    usage: str
    runner: Callable[[str], Awaitable[Any]]


def command_path_key(path: tuple[str, ...]) -> str:
    """Return the argv key for a command path."""
    return " ".join(path)


_PARAMS_USAGE_METAS: tuple[ParamsCommandUsageMeta, ...] = (
    ParamsCommandUsageMeta(
        ("jobs", "summary"),
        ParamsBodyKind.JOBS_VIEW,
        '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
        "./jobs-summary.json",
    ),
    ParamsCommandUsageMeta(
        ("jobs", "query"),
        ParamsBodyKind.JOBS_VIEW,
        '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
        "./jobs-query.json",
    ),
    ParamsCommandUsageMeta(
        ("jobs", "performance"),
        ParamsBodyKind.JOBS_VIEW,
        '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
        "./jobs-performance.json",
    ),
    ParamsCommandUsageMeta(
        ("jobs", "lineage"),
        ParamsBodyKind.JOBS_VIEW,
        '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
        "./jobs-lineage.json",
    ),
    ParamsCommandUsageMeta(
        ("jobs", "impact"),
        ParamsBodyKind.JOBS_VIEW,
        '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
        "./jobs-impact.json",
    ),
    ParamsCommandUsageMeta(
        ("jobs", "get"),
        ParamsBodyKind.JOBS_VIEW,
        '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
        "./jobs-get.json",
    ),
    ParamsCommandUsageMeta(
        ("jobs", "list"),
        ParamsBodyKind.JOBS_LIST,
        '{"projectId":"my-proj","allUsers":true,"maxResults":50}',
        "./jobs-list.json",
    ),
    ParamsCommandUsageMeta(
        ("datasets", "get"),
        ParamsBodyKind.DATASETS_GET,
        '{"projectId":"my-proj","datasetId":"analytics"}',
        "./datasets-get.json",
    ),
    ParamsCommandUsageMeta(
        ("tables", "list"),
        ParamsBodyKind.TABLES_LIST,
        '{"projectId":"my-proj","datasetId":"analytics"}',
        "./tables-list.json",
    ),
    ParamsCommandUsageMeta(
        ("tables", "get"),
        ParamsBodyKind.TABLES_GET,
        '{"projectId":"my-proj","datasetId":"analytics","tableId":"events"}',
        "./tables-get.json",
    ),
)

_RUNNERS_BY_PATH: dict[tuple[str, ...], ParamsCommandRunner] = {
    ("jobs", "summary"): jobs_summary_command,
    ("jobs", "query"): jobs_query_command,
    ("jobs", "performance"): jobs_performance_command,
    ("jobs", "lineage"): jobs_lineage_command,
    ("jobs", "impact"): jobs_impact_command,
    ("jobs", "get"): jobs_get_command,
    ("jobs", "list"): run_jobs_list_command,
    ("datasets", "get"): datasets_get_command,
    ("tables", "list"): tables_list_command,
    ("tables", "get"): tables_get_command,
}

PARAMS_COMMAND_SPECS: tuple[ParamsCommandSpec, ...] = tuple(
    ParamsCommandSpec(
        meta.path,
        build_params_command_usage(meta),
        _RUNNERS_BY_PATH[meta.path],
    )
    for meta in _PARAMS_USAGE_METAS
)

GROUP_COMMAND_SPECS: tuple[GroupCommandSpec, ...] = (
    GroupCommandSpec(
        "jobs",
        build_jobs_group_usage(),
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "jobs"),
    ),
    GroupCommandSpec(
        "datasets",
        build_datasets_group_usage(),
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "datasets"),
    ),
    GroupCommandSpec(
        "tables",
        build_tables_group_usage(),
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "tables"),
    ),
)

SCHEMA_GROUP_USAGE = build_schema_group_usage()

SCHEMA_COMMAND_SPECS: tuple[SchemaCommandSpec, ...] = (
    SchemaCommandSpec("input", build_schema_subcommand_usage("input"), run_schema_for_name),
    SchemaCommandSpec("output", build_schema_subcommand_usage("output"), run_schema_for_name),
)


def _build_help_lookup() -> dict[str, str]:
    lookup = {command_path_key(spec.path): spec.usage for spec in PARAMS_COMMAND_SPECS}
    for spec in SCHEMA_COMMAND_SPECS:
        lookup[command_path_key(("schema", spec.name))] = spec.usage
    lookup["schema"] = SCHEMA_GROUP_USAGE
    for group in GROUP_COMMAND_SPECS:
        lookup[group.name] = group.usage
    lookup[""] = GLOBAL_USAGE
    return lookup


_HELP_BY_KEY = _build_help_lookup()


def command_help_for_key(key: str) -> str | None:
    """Return usage text for a command path key."""
    return _HELP_BY_KEY.get(key)
