"""Legacy schema subcommand."""

from __future__ import annotations

from typing import Any

from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error
from bq_inspect.schemas.input_schema import JOBS_GET_INPUT_SCHEMA
from bq_inspect.schemas.output_schema import OUTPUT_SCHEMA


def _validate_schema_name(name: str | None) -> str:
    if name not in ("input", "output"):
        raise BqInspectFailure(
            create_bq_inspect_error(
                code="BQINSPECT_INPUT_INVALID",
                message=f"Unknown schema command: {name!s}",
            )
        )
    return name


def _validate_schema_format(format_value: str | None) -> None:
    if format_value != "json-schema":
        if format_value is None:
            message = "Missing --format json-schema"
        else:
            message = f"Unsupported --format value: {format_value}"
        raise BqInspectFailure(
            create_bq_inspect_error(
                code="BQINSPECT_INPUT_INVALID",
                message=message,
            )
        )


async def run_schema_for_name(name: str | None, format_value: str | None) -> Any:
    """Run the legacy schema input/output subcommand."""
    validated_name = _validate_schema_name(name)
    _validate_schema_format(format_value)

    if validated_name == "input":
        return JOBS_GET_INPUT_SCHEMA

    return OUTPUT_SCHEMA


async def run_schema_command(argv: list[str]) -> Any:
    """Run the legacy schema input/output subcommand from argv."""
    name: str | None = None
    format_value: str | None = None
    index = 0

    while index < len(argv):
        arg = argv[index]
        if arg == "--format":
            if index + 1 >= len(argv):
                raise BqInspectFailure(
                    create_bq_inspect_error(
                        code="BQINSPECT_INPUT_INVALID",
                        message="Missing --format json-schema",
                    )
                )
            format_value = argv[index + 1]
            index += 2
            continue

        if arg.startswith("-"):
            unknown_text = " ".join(argv[index:])
            raise BqInspectFailure(
                create_bq_inspect_error(
                    code="BQINSPECT_INPUT_INVALID",
                    message=f"Unexpected argument(s): {unknown_text}",
                )
            )

        if name is not None:
            unknown_text = " ".join(argv[index:])
            raise BqInspectFailure(
                create_bq_inspect_error(
                    code="BQINSPECT_INPUT_INVALID",
                    message=f"Unexpected argument(s): {unknown_text}",
                )
            )

        name = arg
        index += 1

    return await run_schema_for_name(name, format_value)
