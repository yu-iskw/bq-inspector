"""Map Google Cloud API exceptions to structured bq-inspector failures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from google.api_core.exceptions import GoogleAPICallError

from bq_inspector.core.shared.api_error_hints import ApiErrorHintContext, hint_for_api_error
from bq_inspector.core.shared.errors import BqInspectFailure, create_bq_inspector_error

if TYPE_CHECKING:
    from collections.abc import Callable

    from bq_inspector.core.shared.types import BqInspectErrorCode

_HTTP_STATUS_MIN = 100
_HTTP_STATUS_MAX = 600
_HTTP_STATUS_BAD_REQUEST = 400
_HTTP_STATUS_NOT_FOUND = 404
_HTTP_STATUS_TOO_MANY_REQUESTS = 429
_HTTP_STATUS_SERVER_ERROR = 500

_STATUS_CODE_RULES: tuple[tuple[Callable[[int], bool], BqInspectErrorCode], ...] = (
    (lambda status: status in (401, 403), "BQINSPECTOR_PERMISSION_DENIED"),
    (lambda status: status == _HTTP_STATUS_NOT_FOUND, "BQINSPECTOR_JOB_NOT_FOUND"),
    (lambda status: status == _HTTP_STATUS_TOO_MANY_REQUESTS, "BQINSPECTOR_API_RATE_LIMITED"),
    (lambda status: status >= _HTTP_STATUS_SERVER_ERROR, "BQINSPECTOR_API_UNAVAILABLE"),
    (
        lambda status: _HTTP_STATUS_BAD_REQUEST <= status < _HTTP_STATUS_SERVER_ERROR,
        "BQINSPECTOR_INPUT_INVALID",
    ),
)


@dataclass(frozen=True)
class GoogleApiErrorView:
    """Normalized HTTP status and message from a Google API failure."""

    status: int | None
    message: str

    @classmethod
    def from_error(cls, error: object) -> GoogleApiErrorView:
        """Build a view from a Google API or dict-shaped error."""
        return cls(status=_extract_http_status(error), message=_extract_message(error))


def parse_http_status(value: object) -> int | None:
    """Parse a numeric or string HTTP status in the valid range."""
    if isinstance(value, int):
        return value if _HTTP_STATUS_MIN <= value < _HTTP_STATUS_MAX else None
    if isinstance(value, str):
        return _parse_http_status_string(value)
    return None


def _parse_http_status_string(value: str) -> int | None:
    try:
        parsed = int(value, 10)
    except ValueError:
        return None
    return parsed if _HTTP_STATUS_MIN <= parsed < _HTTP_STATUS_MAX else None


def resolve_http_status(error: object) -> int | None:
    """Extract an HTTP status code from a Google API or dict-shaped error."""
    return GoogleApiErrorView.from_error(error).status


def extract_google_error_message(error: object) -> str:
    """Return the best available error message for a Google API failure."""
    return GoogleApiErrorView.from_error(error).message


def map_http_status_to_error_code(status: int) -> BqInspectErrorCode:
    """Map an HTTP status to a bq-inspector error code."""
    for matches, code in _STATUS_CODE_RULES:
        if matches(status):
            return code
    return "BQINSPECTOR_API_UNAVAILABLE"


def map_google_error_to_bq_inspector_failure(
    error: object,
    api: str = "bigquery.jobs.get",
    context: ApiErrorHintContext | None = None,
) -> BqInspectFailure:
    """Convert a Google API error into a structured BqInspectFailure."""
    view = GoogleApiErrorView.from_error(error)

    if view.status is None:
        return BqInspectFailure(
            create_bq_inspector_error(
                code="BQINSPECTOR_INTERNAL",
                message=view.message,
            )
        )

    code = map_http_status_to_error_code(view.status)
    hint = hint_for_api_error(code, api, context)

    error_details = create_bq_inspector_error(
        code=code,
        message=view.message,
        source={"api": api, "status": view.status},
    )
    if hint is not None:
        error_details["hint"] = hint

    return BqInspectFailure(error_details)


def _extract_http_status(error: object) -> int | None:
    if isinstance(error, GoogleAPICallError):
        return parse_http_status(error.code)

    if isinstance(error, dict):
        return _extract_http_status_from_mapping(error)

    return _extract_http_status_from_object(error)


def _extract_http_status_from_mapping(error: dict[str, object]) -> int | None:
    parsed_code = parse_http_status(error.get("code"))
    if parsed_code is not None:
        return parsed_code

    response = error.get("response")
    if isinstance(response, dict):
        return parse_http_status(response.get("status"))

    return None


def _extract_http_status_from_object(error: object) -> int | None:
    code = getattr(error, "code", None)
    if code is not None:
        parsed = parse_http_status(code)
        if parsed is not None:
            return parsed

    response = getattr(error, "response", None)
    if isinstance(response, dict):
        return parse_http_status(response.get("status"))

    return None


def _extract_message(error: object) -> str:
    message = _message_from_exception(error)
    if message is not None:
        return message

    message = _message_from_dict(error)
    if message is not None:
        return message

    message = _message_from_object_attr(error)
    return message if message is not None else "BigQuery request failed."


def _message_from_exception(error: object) -> str | None:
    if isinstance(error, BaseException):
        message = str(error).strip()
        if len(message) > 0:
            return message
    return None


def _message_from_dict(error: object) -> str | None:
    if isinstance(error, dict):
        dict_message = error.get("message")
        if isinstance(dict_message, str) and dict_message.strip():
            return dict_message
    return None


def _message_from_object_attr(error: object) -> str | None:
    object_message = getattr(error, "message", None)
    if isinstance(object_message, str) and object_message.strip():
        return object_message
    return None
