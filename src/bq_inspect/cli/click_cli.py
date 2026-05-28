"""Click CLI application for bq-inspect."""

from __future__ import annotations

import json
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

import click

from bq_inspect.cli.click_decorators import (
    async_command,
    custom_help_option,
    operational_options,
    pass_inspection_options,
)
from bq_inspect.cli.help import resolve_help_text, strip_trailing_help_flags
from bq_inspect.cli.usage import (
    DATASETS_GET_USAGE,
    GLOBAL_USAGE,
    JOBS_GET_USAGE,
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
    TABLES_LIST_USAGE,
)
from bq_inspect.commands.command_shared import InspectionCommandOptions
from bq_inspect.commands.datasets.get import run_datasets_get
from bq_inspect.commands.jobs.list import run_jobs_list
from bq_inspect.commands.jobs.run_jobs_view import (
    run_jobs_get,
    run_jobs_impact,
    run_jobs_lineage,
    run_jobs_performance,
    run_jobs_query,
    run_jobs_summary,
)
from bq_inspect.commands.schema import run_schema_for_name
from bq_inspect.commands.tables.get import run_tables_get
from bq_inspect.commands.tables.list import run_tables_list
from bq_inspect.core.shared.errors import create_input_failure

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bq_inspect.cli.argv.operational_argv import OperationalArgv


def _read_tool_version() -> str:
    try:
        return version("bq-inspect")
    except PackageNotFoundError:
        return "0.0.0"


def operational_to_argv(operational: OperationalArgv) -> list[str]:
    """Convert parsed operational flags back to argv for existing command runners."""
    if operational["kind"] == "input-schema":
        return ["--input-schema"]
    if operational["kind"] == "output-schema":
        return ["--output-schema"]
    return ["--params", operational["params"]]


class BqInspectGroup(click.Group):
    """Click group that maps unknown commands to structured input failures."""

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        command = super().get_command(ctx, cmd_name)
        if command is None:
            raise create_input_failure(f"Unknown command: {cmd_name}")
        return command


def _partial_group_unknown_command(group_name: str) -> None:
    raise create_input_failure(f"Unknown command: {group_name}")


def _register_params_command(
    group: click.Group,
    name: str,
    usage: str,
    run_command: Callable[[list[str], InspectionCommandOptions], Awaitable[Any]],
) -> None:
    @group.command(name, add_help_option=False)
    @custom_help_option(usage)
    @operational_options
    @pass_inspection_options
    @async_command
    async def params_command(
        *,
        operational: OperationalArgv,
        command_options: InspectionCommandOptions,
    ) -> Any:
        return await run_command(operational_to_argv(operational), command_options)

    params_command.__name__ = name.replace(" ", "_")


@click.group(
    cls=BqInspectGroup,
    context_settings={"help_option_names": []},
    invoke_without_command=True,
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Read-only BigQuery job and metadata inspection."""
    ctx.ensure_object(dict)
    ctx.obj["options"] = InspectionCommandOptions(tool_version=_read_tool_version())

    if ctx.invoked_subcommand is None:
        sys.stdout.write(f"{GLOBAL_USAGE}\n")


@cli.group("jobs", invoke_without_command=True, add_help_option=False)
@click.pass_context
def jobs_group(ctx: click.Context) -> None:
    """Jobs inspection commands."""
    if ctx.invoked_subcommand is None:
        _partial_group_unknown_command("jobs")


_register_params_command(jobs_group, "summary", JOBS_SUMMARY_USAGE, run_jobs_summary)
_register_params_command(jobs_group, "query", JOBS_QUERY_USAGE, run_jobs_query)
_register_params_command(jobs_group, "performance", JOBS_PERFORMANCE_USAGE, run_jobs_performance)
_register_params_command(jobs_group, "lineage", JOBS_LINEAGE_USAGE, run_jobs_lineage)
_register_params_command(jobs_group, "impact", JOBS_IMPACT_USAGE, run_jobs_impact)
_register_params_command(jobs_group, "get", JOBS_GET_USAGE, run_jobs_get)
_register_params_command(jobs_group, "list", JOBS_LIST_USAGE, run_jobs_list)


@cli.group("datasets", invoke_without_command=True, add_help_option=False)
@click.pass_context
def datasets_group(ctx: click.Context) -> None:
    """Dataset metadata commands."""
    if ctx.invoked_subcommand is None:
        _partial_group_unknown_command("datasets")


_register_params_command(datasets_group, "get", DATASETS_GET_USAGE, run_datasets_get)


@cli.group("tables", invoke_without_command=True, add_help_option=False)
@click.pass_context
def tables_group(ctx: click.Context) -> None:
    """Table metadata commands."""
    if ctx.invoked_subcommand is None:
        _partial_group_unknown_command("tables")


_register_params_command(tables_group, "list", TABLES_LIST_USAGE, run_tables_list)
_register_params_command(tables_group, "get", TABLES_GET_USAGE, run_tables_get)


@cli.group("schema", invoke_without_command=True, add_help_option=False)
@custom_help_option(SCHEMA_USAGE)
@click.pass_context
def schema_group(ctx: click.Context) -> None:
    """Legacy schema commands."""
    if ctx.invoked_subcommand is None:
        _partial_group_unknown_command("schema")


def _register_schema_command(name: str, usage: str) -> None:
    @schema_group.command(name, add_help_option=False)
    @custom_help_option(usage)
    @click.option("--format", type=str, required=False)
    @async_command
    async def schema_command(*, format: str | None) -> Any:  # noqa: A002
        return await run_schema_for_name(name, format)

    schema_command.__name__ = f"schema_{name}"


_register_schema_command("input", SCHEMA_INPUT_USAGE)
_register_schema_command("output", SCHEMA_OUTPUT_USAGE)


def _write_json_result(result: Any) -> None:
    if result is not None:
        sys.stdout.write(f"{json.dumps(result, indent=2)}\n")


def _handle_trailing_help(raw_argv: list[str]) -> bool:
    argv, wants_help = strip_trailing_help_flags(raw_argv)
    if not wants_help:
        return False

    help_text = resolve_help_text(argv, wants_help)
    if help_text is None:
        return False

    sys.stdout.write(f"{help_text}\n")
    return True


def invoke(argv: list[str] | None = None) -> None:
    """Run the Click CLI and write JSON results to stdout."""
    raw_argv = list(sys.argv[1:] if argv is None else argv)

    if _handle_trailing_help(raw_argv):
        return

    result = cli.main(args=raw_argv, prog_name="bq-inspect", standalone_mode=False)
    _write_json_result(result)
