"""Structured errors and exit codes for bq-inspector."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import BqInspectError, BqInspectErrorCode

_EXIT_CODES: dict[BqInspectErrorCode, int] = {
    "BQINSPECTOR_INPUT_INVALID": 2,
    "BQINSPECTOR_PERMISSION_DENIED": 3,
    "BQINSPECTOR_JOB_NOT_FOUND": 4,
    "BQINSPECTOR_LOCATION_REQUIRED": 2,
    "BQINSPECTOR_API_RATE_LIMITED": 5,
    "BQINSPECTOR_API_UNAVAILABLE": 5,
    "BQINSPECTOR_INTERNAL": 1,
}

# BQINSPECTOR_JOB_NOT_FOUND: all HTTP 404 responses (jobs and catalog). Use source.api + hint.
_DEFAULT_RETRIABLE_BY_CODE: dict[BqInspectErrorCode, bool] = {
    "BQINSPECTOR_INPUT_INVALID": False,
    "BQINSPECTOR_PERMISSION_DENIED": False,
    "BQINSPECTOR_JOB_NOT_FOUND": False,
    "BQINSPECTOR_LOCATION_REQUIRED": False,
    "BQINSPECTOR_API_RATE_LIMITED": True,
    "BQINSPECTOR_API_UNAVAILABLE": True,
    "BQINSPECTOR_INTERNAL": False,
}


class BqInspectFailure(Exception):  # noqa: N818
    """Exception carrying structured bq-inspector error details."""

    def __init__(self, details: BqInspectError) -> None:
        super().__init__(details["message"])
        self.details = details

    def to_json(self) -> BqInspectError:
        return self.details


def get_exit_code(error: BqInspectError) -> int:
    """Map a structured error code to a process exit code."""
    return _EXIT_CODES[error["code"]]


def create_bq_inspector_error(
    *,
    code: BqInspectErrorCode,
    message: str,
    retriable: bool | None = None,
    hint: str | None = None,
    source: dict[str, Any] | None = None,
) -> BqInspectError:
    """Build a structured error with default retriable flag per code."""
    resolved_retriable = retriable if retriable is not None else _DEFAULT_RETRIABLE_BY_CODE[code]
    error: BqInspectError = {
        "code": code,
        "message": message,
        "retriable": resolved_retriable,
    }
    if hint is not None:
        error["hint"] = hint
    if source is not None:
        error["source"] = source  # type: ignore[typeddict-item]
    return error


def create_input_failure(
    message: str,
    *,
    hint: str | None = None,
    source: dict[str, Any] | None = None,
) -> BqInspectFailure:
    """Create a non-retriable input validation failure."""
    return BqInspectFailure(
        create_bq_inspector_error(
            code="BQINSPECTOR_INPUT_INVALID",
            message=message,
            hint=hint,
            source=source,
        )
    )
