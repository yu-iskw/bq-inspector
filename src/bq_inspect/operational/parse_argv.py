"""Parse operational CLI flags (--params, --input-schema, --output-schema)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import click

from bq_inspect.core.shared.errors import create_input_failure
from bq_inspect.operational.click_errors import click_exception_to_failure
from bq_inspect.operational.flags import operational_flag_options
from bq_inspect.operational.resolve import resolve_operational_argv

if TYPE_CHECKING:
    from bq_inspect.operational.types import OperationalArgv

_OPERATIONAL_FLAG_OPTIONS = operational_flag_options()


def _parse_operational_callback(
    ctx: click.Context,
    params: str | None,
    input_schema: bool,
    output_schema: bool,
) -> OperationalArgv:
    del ctx
    return resolve_operational_argv(
        params=params,
        input_schema=input_schema,
        output_schema=output_schema,
    )


_OPERATIONAL_PARSER = click.Command(
    "operational",
    params=list(_OPERATIONAL_FLAG_OPTIONS),
    callback=_parse_operational_callback,
)

_OPERATIONAL_PARSER_CTX = click.Context(_OPERATIONAL_PARSER, allow_extra_args=False)
_OPERATIONAL_ARGV_PARSER = _OPERATIONAL_PARSER.make_parser(_OPERATIONAL_PARSER_CTX)


def parse_operational_argv(argv: list[str]) -> OperationalArgv:
    """Parse command argv for schema discovery or --params run mode."""
    try:
        opts, args, _order = _OPERATIONAL_ARGV_PARSER.parse_args(list(argv))
    except click.MissingParameter as error:
        if error.param is not None and error.param.name == "params":
            raise create_input_failure("expected one argument") from error
        raise click_exception_to_failure(error) from error
    except click.ClickException as error:
        raise click_exception_to_failure(error) from error

    if args:
        unknown_text = " ".join(args)
        raise create_input_failure(f"Unexpected positional argument(s): {unknown_text}")

    return resolve_operational_argv(
        params=opts.get("params"),
        input_schema=opts.get("input_schema") is True,
        output_schema=opts.get("output_schema") is True,
    )
