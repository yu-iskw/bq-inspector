"""Validate command input params against JSON Schema."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from jsonschema import Draft202012Validator, FormatChecker

from bq_inspector.core.shared.errors import create_input_failure
from bq_inspector.schemas.command_schemas import CommandId, get_command_schema

if TYPE_CHECKING:
    from jsonschema.exceptions import ValidationError

_format_checker = FormatChecker()


def _has_explicit_timezone(value: str) -> bool:
    if value.endswith("Z"):
        return True
    tail = value[10:]
    return "+" in tail or "-" in tail


@_format_checker.checks("date-time")
def _check_date_time(instance: object) -> bool:
    if not isinstance(instance, str) or not _has_explicit_timezone(instance):
        return False
    candidate = instance[:-1] + "+00:00" if instance.endswith("Z") else instance
    try:
        datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return True


_validator_cache: dict[CommandId, Draft202012Validator] = {}


def _get_validator(command_id: CommandId) -> Draft202012Validator:
    cached = _validator_cache.get(command_id)
    if cached is not None:
        return cached

    schema = get_command_schema(command_id, "input")
    validator = Draft202012Validator(schema, format_checker=_format_checker)
    _validator_cache[command_id] = validator
    return validator


def _format_schema_errors(errors: list[ValidationError]) -> list[dict[str, str]]:
    formatted: list[dict[str, str]] = []
    for error in errors[:5]:
        path = "/" + "/".join(str(part) for part in error.path) if error.path else "/"
        formatted.append({"path": path, "message": error.message})
    return formatted


def validate_input(command_id: CommandId, data: Any) -> dict[str, Any]:
    """Validate params against the command input schema; return the parsed object."""
    if not isinstance(data, dict):
        raise create_input_failure("params must be a JSON object.")

    validator = _get_validator(command_id)
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        raise create_input_failure(
            "params do not match the input schema.",
            hint=f"Run bq-inspector {command_id} --input-schema.",
            source={"schemaErrors": _format_schema_errors(errors)},
        )

    return data
