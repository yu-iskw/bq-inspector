"""Operational CLI contracts (types, flag parsing, and params resolution)."""

from bq_inspector.operational.click_errors import (
    click_exception_to_failure,
    normalize_click_exception_message,
)
from bq_inspector.operational.params import resolve_params_value
from bq_inspector.operational.parse_argv import parse_operational_argv
from bq_inspector.operational.resolve import resolve_operational_argv
from bq_inspector.operational.types import (
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
    "click_exception_to_failure",
    "normalize_click_exception_message",
    "parse_operational_argv",
    "resolve_operational_argv",
    "resolve_params_value",
]
