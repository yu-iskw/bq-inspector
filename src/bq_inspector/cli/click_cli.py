"""Click CLI application for bq-inspector."""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

import click

from bq_inspector.cli.click_decorators import (
    async_command,
    operational_options,
    pass_inspection_options,
)
from bq_inspector.cli.command_registry import (
    GLOBAL_USAGE,
    GROUP_COMMAND_SPECS,
    GroupCommandSpec,
    ParamsCommandSpec,
)
from bq_inspector.cli.flat_argv import flat_unknown_command_hint, normalize_flat_argv
from bq_inspector.cli.help import resolve_help_text, strip_trailing_help_flags, write_help_text
from bq_inspector.commands.command_shared import InspectionCommandOptions, ParamsCommandRunner
from bq_inspector.core.shared.errors import create_input_failure

if TYPE_CHECKING:
    from bq_inspector.operational.types import OperationalArgv


@lru_cache(maxsize=1)
def _read_tool_version() -> str:
    try:
        return version("bq-inspector")
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
        if not self._group_path:
            hint = flat_unknown_command_hint(cmd_name)
            if hint is not None:
                return f"Unknown command: {cmd_name}. Did you mean: {hint}?"
        if self._group_path:
            return f"Unknown command: {' '.join((*self._group_path, cmd_name))}"
        return f"Unknown command: {cmd_name}"


def _register_params_command(
    group: click.Group,
    name: str,
    runner: ParamsCommandRunner,
) -> None:
    @group.command(name, add_help_option=False)
    @operational_options
    @pass_inspection_options
    @async_command
    async def params_command(
        *,
        operational: OperationalArgv,
        command_options: InspectionCommandOptions,
    ) -> Any:
        return await runner.run_operational(operational, command_options)

    params_command.__name__ = name.replace(" ", "_")  # pyright: ignore[reportAttributeAccessIssue]


def _build_nested_subgroup(
    name: str,
    *,
    parent_path: tuple[str, ...],
    commands: tuple[ParamsCommandSpec, ...],
) -> click.Group:
    @click.group(
        name,
        cls=BqInspectGroup,
        group_path=(*parent_path, name),
        invoke_without_command=True,
        add_help_option=False,
    )
    @click.pass_context
    def subgroup(ctx: click.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise create_input_failure(f"Unknown command: {' '.join((*parent_path, name))}")

    for command_spec in commands:
        _register_params_command(subgroup, command_spec.path[-1], command_spec.runner)

    subgroup.__doc__ = name
    return subgroup


def _build_params_group(spec: GroupCommandSpec) -> click.Group:
    @click.group(
        spec.name,
        cls=BqInspectGroup,
        group_path=(spec.name,),
        invoke_without_command=True,
        add_help_option=False,
    )
    @click.pass_context
    def group(ctx: click.Context) -> None:
        if ctx.invoked_subcommand is None:
            raise create_input_failure(f"Unknown command: {spec.name}")

    # Catalog (and future groups) nest resources as group -> subgroup -> verb (depth 3).
    top_level_command_depth = 2
    direct_commands = [
        command for command in spec.commands if len(command.path) == top_level_command_depth
    ]
    nested_commands = [
        command for command in spec.commands if len(command.path) > top_level_command_depth
    ]

    for command_spec in direct_commands:
        _register_params_command(group, command_spec.path[-1], command_spec.runner)

    subgroup_names = sorted({command.path[1] for command in nested_commands})
    for subgroup_name in subgroup_names:
        subgroup_specs = tuple(
            command for command in nested_commands if command.path[1] == subgroup_name
        )
        group.add_command(
            _build_nested_subgroup(
                subgroup_name,
                parent_path=(spec.name,),
                commands=subgroup_specs,
            )
        )

    group.__doc__ = spec.name
    return group


@click.group(
    cls=BqInspectGroup,
    context_settings={"help_option_names": []},
    invoke_without_command=True,
    add_help_option=False,
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


def _write_json_result(result: Any) -> None:
    if result is not None:
        sys.stdout.write(f"{json.dumps(result, indent=2)}\n")


def invoke(argv: list[str] | None = None) -> None:
    """Run the Click CLI and write JSON results to stdout."""
    raw_argv = list(sys.argv[1:] if argv is None else argv)

    argv_without_help, wants_help = strip_trailing_help_flags(raw_argv)
    if wants_help:
        write_help_text(resolve_help_text(argv_without_help, wants_help=True))
        return

    normalized_argv = normalize_flat_argv(raw_argv)
    result = cli.main(args=normalized_argv, prog_name="bq-inspector", standalone_mode=False)
    _write_json_result(result)
