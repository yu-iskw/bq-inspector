"""Legacy schema subcommand."""

from __future__ import annotations

from typing import Any

from bq_inspect.core.shared.errors import create_input_failure
from bq_inspect.schemas.input_schema import JOBS_GET_INPUT_SCHEMA
from bq_inspect.schemas.output_schema import OUTPUT_SCHEMA


def _validate_schema_name(name: str) -> str:
    if name not in ("input", "output"):
        raise create_input_failure(f"Unknown schema command: {name!s}")
    return name


def _validate_schema_format(format_value: str) -> None:
    if format_value != "json-schema":
        if format_value is None:
            message = "Missing --format json-schema"
        else:
            message = f"Unsupported --format value: {format_value}"
        raise create_input_failure(message)


async def run_schema_for_name(name: str, format_value: str) -> Any:
    """Run the legacy schema input/output subcommand."""
    validated_name = _validate_schema_name(name)
    _validate_schema_format(format_value)

    if validated_name == "input":
        return JOBS_GET_INPUT_SCHEMA

    return OUTPUT_SCHEMA
