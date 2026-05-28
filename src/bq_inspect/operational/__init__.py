"""Operational CLI contracts (types and flag resolution)."""

from bq_inspect.operational.resolve import resolve_operational_argv
from bq_inspect.operational.types import (
    InputSchemaArgv,
    OperationalArgv,
    OutputSchemaArgv,
    RunArgv,
)

__all__ = [
    "InputSchemaArgv",
    "OperationalArgv",
    "OutputSchemaArgv",
    "RunArgv",
    "resolve_operational_argv",
]
