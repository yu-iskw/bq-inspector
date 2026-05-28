"""Parse operational CLI flags (--params, --input-schema, --output-schema)."""

from __future__ import annotations

from typing import Literal, TypedDict

import click

from bq_inspect.core.shared.errors import BqInspectFailure, create_input_failure


class InputSchemaArgv(TypedDict):
    kind: Literal["input-schema"]


class OutputSchemaArgv(TypedDict):
    kind: Literal["output-schema"]


class RunArgv(TypedDict):
    kind: Literal["run"]
    params: str


OperationalArgv = InputSchemaArgv | OutputSchemaArgv | RunArgv


def resolve_operational_argv(
    *,
    params: str | None,
    input_schema: bool,
    output_schema: bool,
    extra_args: tuple[str, ...] = (),
) -> OperationalArgv:
    """Resolve operational flags into schema discovery or run mode."""
    if extra_args:
        unknown_text = " ".join(extra_args)
        raise create_input_failure(f"Unexpected positional argument(s): {unknown_text}")

    wants_input = input_schema is True
    wants_output = output_schema is True

    if wants_input and wants_output:
        raise create_input_failure("Use either --input-schema or --output-schema, not both.")

    if wants_input:
        return {"kind": "input-schema"}

    if wants_output:
        return {"kind": "output-schema"}

    if params is None or len(params.strip()) == 0:
        raise create_input_failure(
            "--params is required (JSON object or @path to a JSON file).",
            hint="Use --input-schema to print the expected params shape.",
        )

    return {"kind": "run", "params": params}


def _click_exception_to_failure(error: click.ClickException) -> BqInspectFailure:
    message = error.format_message()
    if "requires an argument" in message and "--params" in message:
        return create_input_failure("expected one argument")
    return create_input_failure(message)


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
    params=[
        click.Option(["--params"], type=str, default=None),
        click.Option(["--input-schema"], is_flag=True, default=False),
        click.Option(["--output-schema"], is_flag=True, default=False),
    ],
    callback=_parse_operational_callback,
)


def parse_operational_argv(argv: list[str]) -> OperationalArgv:  # noqa: PLR0912
    """Parse command argv for schema discovery or --params run mode."""
    if argv == ["--params"]:
        raise create_input_failure("expected one argument")

    for index, arg in enumerate(argv):
        if arg == "--params" and (index + 1 >= len(argv) or argv[index + 1].startswith("-")):
            raise create_input_failure("expected one argument")

    ctx = click.Context(_OPERATIONAL_PARSER, allow_extra_args=False)
    parser = _OPERATIONAL_PARSER.make_parser(ctx)

    try:
        opts, args, _order = parser.parse_args(list(argv))
    except click.MissingParameter as error:
        if error.param is not None and error.param.name == "params":
            raise create_input_failure("expected one argument") from error
        raise _click_exception_to_failure(error) from error
    except click.ClickException as error:
        raise _click_exception_to_failure(error) from error

    if args:
        unknown_text = " ".join(args)
        raise create_input_failure(f"Unexpected positional argument(s): {unknown_text}")

    params_value = opts.get("params")
    input_schema = opts.get("input_schema") is True
    output_schema = opts.get("output_schema") is True

    return resolve_operational_argv(
        params=params_value,
        input_schema=input_schema,
        output_schema=output_schema,
    )


def operational_argv_from_click(
    *,
    params: str | None,
    input_schema: bool,
    output_schema: bool,
) -> OperationalArgv:
    """Resolve operational flags collected by Click command options."""
    return resolve_operational_argv(
        params=params,
        input_schema=input_schema,
        output_schema=output_schema,
    )
