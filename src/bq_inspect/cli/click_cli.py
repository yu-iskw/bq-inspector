"""Click CLI application for bq-inspect."""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

import click

from bq_inspect.cli.click_decorators import (
    async_command,
    custom_help_option,
    operational_options,
    pass_inspection_options,
)
from bq_inspect.cli.command_registry import (
    GROUP_COMMAND_SPECS,
    SCHEMA_COMMAND_SPECS,
    SCHEMA_GROUP_USAGE,
    GroupCommandSpec,
    SchemaCommandSpec,
)
from bq_inspect.cli.help import resolve_help_text, strip_trailing_help_flags, write_help_text
from bq_inspect.cli.usage import GLOBAL_USAGE
from bq_inspect.commands.command_shared import InspectionCommandOptions, ParamsCommandRunner
from bq_inspect.commands.schema import run_schema_for_name
from bq_inspect.core.shared.errors import create_input_failure

if TYPE_CHECKING:
    from bq_inspect.operational.types import OperationalArgv


@lru_cache(maxsize=1)
def _read_tool_version() -> str:
    try:
        return version("bq-inspect")
    except PackageNotFoundError:
        return "0.0.0"


class BqInspectGroup(click.Group):
    """Click group that maps unknown commands to structured input failures."""

    def __init__(self, *args: Any, group_path: tuple[str, ...] = (), **kwargs: Any) -> None:
        self._group_path = group_path
        super().__init__(*args, **kwargs)

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        command = super().get_command(ctx, cmd_name)
        if command is None:
            raise create_input_failure(self._unknown_command_message(cmd_name))
        return command

    def _unknown_command_message(self, cmd_name: str) -> str:
        if self._group_path:
            return f"Unknown command: {' '.join((*self._group_path, cmd_name))}"
        return f"Unknown command: {cmd_name}"


def _register_params_command(
    group: click.Group,
    name: str,
    usage: str,
    runner: ParamsCommandRunner,
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
        return await runner.run_operational(operational, command_options)

    params_command.__name__ = name.replace(" ", "_")


def _build_params_group(spec: GroupCommandSpec) -> click.Group:
    @click.group(
        spec.name,
        cls=BqInspectGroup,
        group_path=(spec.name,),
        invoke_without_command=True,
        add_help_option=False,
    )
    @custom_help_option(spec.usage)
    @click.pass_context
    def group(ctx: click.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise create_input_failure(f"Unknown command: {spec.name}")

    for command_spec in spec.commands:
        _register_params_command(
            group,
            command_spec.path[-1],
            command_spec.usage,
            command_spec.runner,
        )

    group.__doc__ = spec.name
    return group


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
        write_help_text(GLOBAL_USAGE)


for group_spec in GROUP_COMMAND_SPECS:
    cli.add_command(_build_params_group(group_spec))


@cli.group(
    "schema",
    cls=BqInspectGroup,
    group_path=("schema",),
    invoke_without_command=True,
    add_help_option=False,
)
@custom_help_option(SCHEMA_GROUP_USAGE)
@click.pass_context
def schema_group(ctx: click.Context) -> None:
    """Legacy schema commands."""
    if ctx.invoked_subcommand is None:
        raise create_input_failure("Unknown command: schema")


def _register_schema_command(spec: SchemaCommandSpec) -> None:
    @schema_group.command(spec.name, add_help_option=False)
    @custom_help_option(spec.usage)
    @click.option(
        "--format",
        "schema_format",
        type=click.Choice(["json-schema"], case_sensitive=False),
        required=True,
    )
    @async_command
    async def schema_command(*, schema_format: str) -> Any:
        return await run_schema_for_name(spec.name, schema_format)

    schema_command.__name__ = f"schema_{spec.name}"


for schema_spec in SCHEMA_COMMAND_SPECS:
    _register_schema_command(schema_spec)


def _write_json_result(result: Any) -> None:
    if result is not None:
        sys.stdout.write(f"{json.dumps(result, indent=2)}\n")


def invoke(argv: list[str] | None = None) -> None:
    """Run the Click CLI and write JSON results to stdout."""
    raw_argv = list(sys.argv[1:] if argv is None else argv)

    argv, wants_help = strip_trailing_help_flags(raw_argv)
    if wants_help:
        write_help_text(resolve_help_text(argv, wants_help))
        return

    result = cli.main(args=raw_argv, prog_name="bq-inspect", standalone_mode=False)
    _write_json_result(result)
