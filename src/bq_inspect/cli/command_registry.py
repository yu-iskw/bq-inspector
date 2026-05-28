"""Canonical registry of CLI commands, usage strings, and runners."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from bq_inspect.cli.usage import (
    DATASETS_GET_USAGE,
    DATASETS_GROUP_USAGE,
    JOBS_GET_USAGE,
    JOBS_GROUP_USAGE,
    JOBS_IMPACT_USAGE,
    JOBS_LINEAGE_USAGE,
    JOBS_LIST_USAGE,
    JOBS_PERFORMANCE_USAGE,
    JOBS_QUERY_USAGE,
    JOBS_SUMMARY_USAGE,
    SCHEMA_INPUT_USAGE,
    SCHEMA_OUTPUT_USAGE,
    SCHEMA_USAGE,
    TABLES_GET_USAGE,
    TABLES_GROUP_USAGE,
    TABLES_LIST_USAGE,
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
from bq_inspect.commands.tables.get import tables_get_command
from bq_inspect.commands.tables.list import tables_list_command

if TYPE_CHECKING:
    from bq_inspect.commands.command_shared import ParamsCommandRunner


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


def command_path_key(path: tuple[str, ...]) -> str:
    """Return the argv key for a command path."""
    return " ".join(path)


PARAMS_COMMAND_SPECS: tuple[ParamsCommandSpec, ...] = (
    ParamsCommandSpec(("jobs", "summary"), JOBS_SUMMARY_USAGE, jobs_summary_command),
    ParamsCommandSpec(("jobs", "query"), JOBS_QUERY_USAGE, jobs_query_command),
    ParamsCommandSpec(("jobs", "performance"), JOBS_PERFORMANCE_USAGE, jobs_performance_command),
    ParamsCommandSpec(("jobs", "lineage"), JOBS_LINEAGE_USAGE, jobs_lineage_command),
    ParamsCommandSpec(("jobs", "impact"), JOBS_IMPACT_USAGE, jobs_impact_command),
    ParamsCommandSpec(("jobs", "get"), JOBS_GET_USAGE, jobs_get_command),
    ParamsCommandSpec(("jobs", "list"), JOBS_LIST_USAGE, run_jobs_list_command),
    ParamsCommandSpec(("datasets", "get"), DATASETS_GET_USAGE, datasets_get_command),
    ParamsCommandSpec(("tables", "list"), TABLES_LIST_USAGE, tables_list_command),
    ParamsCommandSpec(("tables", "get"), TABLES_GET_USAGE, tables_get_command),
)

GROUP_COMMAND_SPECS: tuple[GroupCommandSpec, ...] = (
    GroupCommandSpec(
        "jobs",
        JOBS_GROUP_USAGE,
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "jobs"),
    ),
    GroupCommandSpec(
        "datasets",
        DATASETS_GROUP_USAGE,
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "datasets"),
    ),
    GroupCommandSpec(
        "tables",
        TABLES_GROUP_USAGE,
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "tables"),
    ),
)

SCHEMA_COMMAND_SPECS: tuple[SchemaCommandSpec, ...] = (
    SchemaCommandSpec("input", SCHEMA_INPUT_USAGE),
    SchemaCommandSpec("output", SCHEMA_OUTPUT_USAGE),
)

SCHEMA_GROUP_USAGE = SCHEMA_USAGE


def _build_help_lookup() -> dict[str, str]:
    lookup = {command_path_key(spec.path): spec.usage for spec in PARAMS_COMMAND_SPECS}
    for spec in SCHEMA_COMMAND_SPECS:
        lookup[command_path_key(("schema", spec.name))] = spec.usage
    lookup["schema"] = SCHEMA_GROUP_USAGE
    for group in GROUP_COMMAND_SPECS:
        lookup[group.name] = group.usage
    return lookup


_HELP_BY_KEY = _build_help_lookup()


def command_help_for_key(key: str) -> str | None:
    """Return usage text for a command path key."""
    return _HELP_BY_KEY.get(key)
