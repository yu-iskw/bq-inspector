"""Structured errors and exit codes for bq-inspect."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bq_inspect.core.shared.types import BqInspectError, BqInspectErrorCode

_EXIT_CODES: dict[BqInspectErrorCode, int] = {
    "BQINSPECT_INPUT_INVALID": 2,
    "BQINSPECT_PERMISSION_DENIED": 3,
    "BQINSPECT_JOB_NOT_FOUND": 4,
    "BQINSPECT_LOCATION_REQUIRED": 2,
    "BQINSPECT_API_RATE_LIMITED": 5,
    "BQINSPECT_API_UNAVAILABLE": 5,
    "BQINSPECT_INTERNAL": 1,
}

_DEFAULT_RETRIABLE_BY_CODE: dict[BqInspectErrorCode, bool] = {
    "BQINSPECT_INPUT_INVALID": False,
    "BQINSPECT_PERMISSION_DENIED": False,
    "BQINSPECT_JOB_NOT_FOUND": False,
    "BQINSPECT_LOCATION_REQUIRED": False,
    "BQINSPECT_API_RATE_LIMITED": True,
    "BQINSPECT_API_UNAVAILABLE": True,
    "BQINSPECT_INTERNAL": False,
}


class BqInspectFailure(Exception):  # noqa: N818
    """Exception carrying structured bq-inspect error details."""

    def __init__(self, details: BqInspectError) -> None:
        super().__init__(details["message"])
        self.details = details

    def to_json(self) -> BqInspectError:
        return self.details


def get_exit_code(error: BqInspectError) -> int:
    """Map a structured error code to a process exit code."""
    return _EXIT_CODES[error["code"]]


def create_bq_inspect_error(
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
        create_bq_inspect_error(
            code="BQINSPECT_INPUT_INVALID",
            message=message,
            hint=hint,
            source=source,
        )
    )
