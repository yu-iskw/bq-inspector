"""Shared Click decorators for bq-inspect commands."""

from __future__ import annotations

import asyncio
import functools
import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

import click

from bq_inspect.cli.argv.operational_argv import (
    OPERATIONAL_FLAG_DECORATORS,
    resolve_operational_argv,
)

if TYPE_CHECKING:
    from bq_inspect.commands.command_shared import InspectionCommandOptions

F = TypeVar("F", bound=Callable[..., Any])


def custom_help_option(usage: str) -> Callable[[F], F]:
    """Attach a custom plain-text help handler that writes usage strings."""

    def decorator(command: F) -> F:
        def show_help(ctx: click.Context, param: click.Parameter, value: bool) -> None:
            del param
            if not value or ctx.resilient_parsing:
                return
            sys.stdout.write(f"{usage}\n")
            ctx.exit(0)

        return click.option(
            "-h",
            "--help",
            is_flag=True,
            expose_value=False,
            is_eager=True,
            callback=show_help,
            help="Show this message and exit.",
        )(command)

    return decorator


def operational_options(command: F) -> F:
    """Attach --params, --input-schema, and --output-schema to a command."""
    wrapped = command
    for decorator in reversed(OPERATIONAL_FLAG_DECORATORS):
        wrapped = decorator(wrapped)

    @functools.wraps(command)
    def wrapper(
        *args: Any,
        params: str | None,
        input_schema: bool,
        output_schema: bool,
        **kwargs: Any,
    ) -> Any:
        operational = resolve_operational_argv(
            params=params,
            input_schema=input_schema,
            output_schema=output_schema,
        )
        return wrapped(*args, operational=operational, **kwargs)

    return wrapper  # type: ignore[return-value]


def async_command(command: F) -> F:
    """Run an async Click command via asyncio.run."""

    @functools.wraps(command)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        async def invoke() -> Any:
            return await command(*args, **kwargs)

        return asyncio.run(invoke())

    return wrapper  # type: ignore[return-value]


def pass_inspection_options(command: F) -> F:
    """Inject InspectionCommandOptions from the root Click context."""

    @click.pass_context
    @functools.wraps(command)
    def wrapper(ctx: click.Context, *args: Any, **kwargs: Any) -> Any:
        options: InspectionCommandOptions = ctx.obj["options"]
        return command(*args, command_options=options, **kwargs)

    return wrapper  # type: ignore[return-value]
