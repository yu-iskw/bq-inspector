"""Shared Click decorators for bq-inspect commands."""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

import click

from bq_inspect.operational.resolve import resolve_operational_argv

if TYPE_CHECKING:
    from bq_inspect.commands.command_shared import InspectionCommandOptions
    from bq_inspect.operational.types import OperationalArgv

F = TypeVar("F", bound=Callable[..., Any])


def operational_options(command: F) -> F:
    """Attach --params, --input-schema, and --output-schema to a command."""

    def _attach_flag_options(wrapped: F) -> F:
        from bq_inspect.operational.flags import operational_flag_decorators

        result = wrapped
        for decorator in reversed(operational_flag_decorators()):
            result = decorator(result)
        return result

    @functools.wraps(command)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        operational: OperationalArgv = resolve_operational_argv(
            params=kwargs.pop("params", None),
            input_schema=kwargs.pop("input_schema", False) is True,
            output_schema=kwargs.pop("output_schema", False) is True,
        )
        return command(*args, operational=operational, **kwargs)

    return _attach_flag_options(wrapper)  # type: ignore[return-value]


def async_command(command: F) -> F:
    """Run an async Click command via asyncio.run."""

    @functools.wraps(command)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        async def run_async() -> Any:
            return await command(*args, **kwargs)

        return asyncio.run(run_async())

    return wrapper  # type: ignore[return-value]


def pass_inspection_options(command: F) -> F:
    """Inject InspectionCommandOptions from the root Click context."""

    @click.pass_context
    @functools.wraps(command)
    def wrapper(ctx: click.Context, *args: Any, **kwargs: Any) -> Any:
        options: InspectionCommandOptions = ctx.obj["options"]
        return command(*args, command_options=options, **kwargs)

    return wrapper  # type: ignore[return-value]
