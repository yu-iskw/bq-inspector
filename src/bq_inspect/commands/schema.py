"""Legacy schema subcommand."""

from __future__ import annotations

import argparse
from typing import Any

from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error
from bq_inspect.schemas.input_schema import JOBS_GET_INPUT_SCHEMA
from bq_inspect.schemas.output_schema import OUTPUT_SCHEMA


async def run_schema_command(argv: list[str]) -> Any:  # noqa: PLR0912
    """Run the legacy schema input/output subcommand."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("name", nargs="?")
    parser.add_argument("--format", type=str)
    args, unknown = parser.parse_known_args(argv)

    if unknown:
        unknown_text = " ".join(unknown)
        raise BqInspectFailure(
            create_bq_inspect_error(
                code="BQINSPECT_INPUT_INVALID",
                message=f"Unexpected argument(s): {unknown_text}",
            )
        )

    name = args.name

    if name not in ("input", "output"):
        raise BqInspectFailure(
            create_bq_inspect_error(
                code="BQINSPECT_INPUT_INVALID",
                message=f"Unknown schema command: {name!s}",
            )
        )

    format_value = args.format

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

    if name == "input":
        return JOBS_GET_INPUT_SCHEMA

    return OUTPUT_SCHEMA
