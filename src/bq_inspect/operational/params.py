"""Resolve --params JSON or @file values."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bq_inspect.core.shared.errors import create_input_failure


def _read_params_file(file_path: str) -> str:
    if len(file_path) == 0:
        raise create_input_failure("Expected a file path after @.")

    resolved_path = Path(file_path)
    if not resolved_path.is_absolute():
        resolved_path = Path.cwd() / resolved_path

    try:
        return resolved_path.read_text(encoding="utf-8")
    except OSError as error:
        raise create_input_failure(
            f'Failed to read params file "{file_path}": {error}',
        ) from error


def _params_text_from_trimmed(trimmed: str) -> str:
    if trimmed.startswith("@"):
        return _read_params_file(trimmed[1:].strip())
    return trimmed


def resolve_params_value(raw: str) -> Any:
    """Parse inline JSON or read JSON from an @file path."""
    trimmed = raw.strip()

    if len(trimmed) == 0:
        raise create_input_failure("--params value must not be empty.")

    try:
        return json.loads(_params_text_from_trimmed(trimmed))
    except json.JSONDecodeError as error:
        raise create_input_failure("Params must be valid JSON.") from error
