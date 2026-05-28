"""Parse operational CLI flags (--params, --input-schema, --output-schema)."""

from __future__ import annotations

import argparse
from typing import Literal, NoReturn, TypedDict

from bq_inspect.core.shared.errors import create_input_failure


class InputSchemaArgv(TypedDict):
    kind: Literal["input-schema"]


class OutputSchemaArgv(TypedDict):
    kind: Literal["output-schema"]


class RunArgv(TypedDict):
    kind: Literal["run"]
    params: str


OperationalArgv = InputSchemaArgv | OutputSchemaArgv | RunArgv


class _QuietArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that raises structured input failures instead of printing usage."""

    def error(self, message: str) -> NoReturn:
        raise create_input_failure(message)

    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        if message:
            raise create_input_failure(message)
        raise SystemExit(status)


def parse_operational_argv(argv: list[str]) -> OperationalArgv:
    """Parse command argv for schema discovery or --params run mode."""
    parser = _QuietArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--params", type=str)
    parser.add_argument("--input-schema", action="store_true")
    parser.add_argument("--output-schema", action="store_true")

    args, unknown = parser.parse_known_args(argv)

    if unknown:
        unknown_text = " ".join(unknown)
        raise create_input_failure(f"Unexpected positional argument(s): {unknown_text}")

    wants_input = args.input_schema is True
    wants_output = args.output_schema is True

    if wants_input and wants_output:
        raise create_input_failure("Use either --input-schema or --output-schema, not both.")

    if wants_input:
        return {"kind": "input-schema"}

    if wants_output:
        return {"kind": "output-schema"}

    params = args.params

    if params is None or len(params.strip()) == 0:
        raise create_input_failure(
            "--params is required (JSON object or @path to a JSON file).",
            hint="Use --input-schema to print the expected params shape.",
        )

    return {"kind": "run", "params": params}
