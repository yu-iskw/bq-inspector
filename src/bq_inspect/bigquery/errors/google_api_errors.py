"""Map Google Cloud API exceptions to structured bq-inspect failures."""

from __future__ import annotations

from typing import TYPE_CHECKING

from google.api_core.exceptions import GoogleAPICallError

from bq_inspect.core.shared.api_error_hints import ApiErrorHintContext, hint_for_api_error
from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error

if TYPE_CHECKING:
    from bq_inspect.core.shared.types import BqInspectErrorCode

_HTTP_STATUS_MIN = 100
_HTTP_STATUS_MAX = 600
_HTTP_STATUS_NOT_FOUND = 404
_HTTP_STATUS_TOO_MANY_REQUESTS = 429
_HTTP_STATUS_SERVER_ERROR = 500


def resolve_http_status(error: object) -> int | None:  # noqa: PLR0911, PLR0912
    """Extract an HTTP status code from a Google API or dict-shaped error."""
    if isinstance(error, GoogleAPICallError):
        return parse_http_status(error.code)

    if not isinstance(error, dict):
        code = getattr(error, "code", None)
        if code is not None:
            parsed = parse_http_status(code)
            if parsed is not None:
                return parsed
        response = getattr(error, "response", None)
        if isinstance(response, dict):
            return parse_http_status(response.get("status"))
        return None

    parsed_code = parse_http_status(error.get("code"))
    if parsed_code is not None:
        return parsed_code

    response = error.get("response")
    if isinstance(response, dict):
        return parse_http_status(response.get("status"))

    return None


def parse_http_status(value: object) -> int | None:  # noqa: PLR0911
    """Parse a numeric or string HTTP status in the valid range."""
    if isinstance(value, int) and _HTTP_STATUS_MIN <= value < _HTTP_STATUS_MAX:
        return value

    if isinstance(value, str):
        try:
            parsed = int(value, 10)
        except ValueError:
            return None
        if _HTTP_STATUS_MIN <= parsed < _HTTP_STATUS_MAX:
            return parsed

    return None


def extract_google_error_message(error: object) -> str:  # noqa: PLR0911, PLR0912
    """Return the best available error message for a Google API failure."""
    if isinstance(error, BaseException):
        message = str(error).strip()
        if len(message) > 0:
            return message

    if isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str) and message.strip():
            return message

    if hasattr(error, "message"):
        message = getattr(error, "message", None)
        if isinstance(message, str) and message.strip():
            return message

    return "BigQuery request failed."


def map_http_status_to_error_code(status: int) -> BqInspectErrorCode:  # noqa: PLR0911
    """Map an HTTP status to a bq-inspect error code."""
    if status in (401, 403):
        return "BQINSPECT_PERMISSION_DENIED"

    if status == _HTTP_STATUS_NOT_FOUND:
        return "BQINSPECT_JOB_NOT_FOUND"

    if status == _HTTP_STATUS_TOO_MANY_REQUESTS:
        return "BQINSPECT_API_RATE_LIMITED"

    if status >= _HTTP_STATUS_SERVER_ERROR:
        return "BQINSPECT_API_UNAVAILABLE"

    return "BQINSPECT_API_UNAVAILABLE"


def map_google_error_to_bq_inspect_failure(
    error: object,
    api: str = "bigquery.jobs.get",
    context: ApiErrorHintContext | None = None,
) -> BqInspectFailure:
    """Convert a Google API error into a structured BqInspectFailure."""
    status = resolve_http_status(error)
    message = extract_google_error_message(error)

    if status is None:
        return BqInspectFailure(
            create_bq_inspect_error(
                code="BQINSPECT_INTERNAL",
                message=message,
            )
        )

    code = map_http_status_to_error_code(status)
    hint = hint_for_api_error(code, api, context)

    error_details = create_bq_inspect_error(
        code=code,
        message=message,
        source={"api": api, "status": status},
    )
    if hint is not None:
        error_details["hint"] = hint

    return BqInspectFailure(error_details)
