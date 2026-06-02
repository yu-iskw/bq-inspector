"""Resolve operational CLI flags into schema discovery or run mode."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.core.shared.errors import create_input_failure

if TYPE_CHECKING:
    from bq_inspector.operational.types import OperationalArgv


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
