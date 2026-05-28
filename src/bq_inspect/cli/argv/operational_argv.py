"""Parse operational CLI flags (--params, --input-schema, --output-schema)."""

from __future__ import annotations

from typing import Literal, TypedDict

import click

from bq_inspect.core.shared.errors import BqInspectFailure, create_input_failure

OPERATIONAL_FLAG_DECORATORS = (
    click.option("--params", type=str, default=None),
    click.option("--input-schema", is_flag=True, default=False),
    click.option("--output-schema", is_flag=True, default=False),
)

OPERATIONAL_FLAG_OPTIONS: tuple[click.Option, ...] = (
    click.Option(["--params"], type=str, default=None),
    click.Option(["--input-schema"], is_flag=True, default=False),
    click.Option(["--output-schema"], is_flag=True, default=False),
)


class InputSchemaArgv(TypedDict):
    kind: Literal["input-schema"]


class OutputSchemaArgv(TypedDict):
    kind: Literal["output-schema"]


class RunArgv(TypedDict):
    kind: Literal["run"]
    params: str


OperationalArgv = InputSchemaArgv | OutputSchemaArgv | RunArgv


def normalize_click_exception_message(error: click.ClickException) -> str:
    """Map Click CLI errors to stable bq-inspect input messages."""
    message = error.format_message()
    if "requires an argument" in message and "--params" in message:
        return "expected one argument"
    return message


def click_exception_to_failure(error: click.ClickException) -> BqInspectFailure:
    """Convert a Click exception into a structured input failure."""
    return create_input_failure(normalize_click_exception_message(error))


def resolve_operational_argv(
    *,
    params: str | None,
    input_schema: bool,
    output_schema: bool,
) -> OperationalArgv:
    """Resolve operational flags into schema discovery or run mode."""
    if input_schema and output_schema:
        raise create_input_failure("Use either --input-schema or --output-schema, not both.")

    if input_schema:
        return {"kind": "input-schema"}

    if output_schema:
        return {"kind": "output-schema"}

    if params is None or len(params.strip()) == 0:
        raise create_input_failure(
            "--params is required (JSON object or @path to a JSON file).",
            hint="Use --input-schema to print the expected params shape.",
        )

    return {"kind": "run", "params": params}


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
    params=list(OPERATIONAL_FLAG_OPTIONS),
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
