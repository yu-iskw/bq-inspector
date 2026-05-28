"""Canonical mapping for BigQuery jobs.list request fields."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Literal, cast

from bq_inspect.core.shared.impersonation_fields import impersonation_request_fields

if TYPE_CHECKING:
    from collections.abc import Callable

    from bq_inspect.bigquery.types.list_jobs import ListJobsRequest
    from bq_inspect.core.shared.impersonation_fields import ImpersonationFields
    from bq_inspect.core.shared.types import JobListFiltersEcho, ListJobsResponseRequest


def parse_iso_timestamp_to_millis(value: str) -> int:
    """Parse an ISO-8601 timestamp string to epoch milliseconds."""
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def millis_to_datetime(millis: int) -> datetime:
    """Convert epoch milliseconds to a timezone-aware datetime."""
    return datetime.fromtimestamp(millis / 1000.0, tz=timezone.utc)


def _millis_to_datetime_value(value: object) -> datetime:
    if not isinstance(value, int):
        raise TypeError("expected int milliseconds")
    return millis_to_datetime(value)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


@dataclass(frozen=True)
class _ListRequestOptionalField:
    """Optional ListJobsRequest field copied when include(value) is true."""

    key: str
    include: Callable[[object], bool]
    transform: Callable[[object], object]


_LIST_REQUEST_OPTIONAL_FIELDS: tuple[_ListRequestOptionalField, ...] = (
    _ListRequestOptionalField("allUsers", lambda value: value is True, lambda value: value),
    _ListRequestOptionalField(
        "minCreationTime",
        lambda value: value is not None,
        lambda value: value,
    ),
    _ListRequestOptionalField(
        "maxCreationTime",
        lambda value: value is not None,
        lambda value: value,
    ),
    _ListRequestOptionalField("pageToken", _non_empty_string, lambda value: value),
    _ListRequestOptionalField(
        "maxResults",
        lambda value: value is not None,
        lambda value: value,
    ),
    _ListRequestOptionalField("state", _non_empty_string, lambda value: value),
    _ListRequestOptionalField("parentJobId", _non_empty_string, lambda value: value),
)


@dataclass(frozen=True)
class _SdkOptionalField:
    """Optional ListJobsRequest field mapped to google-cloud-bigquery kwargs."""

    source_key: str
    target_key: str
    include: Callable[[object], bool]
    transform: Callable[[object], object]


_SDK_OPTIONAL_FIELDS: tuple[_SdkOptionalField, ...] = (
    _SdkOptionalField("allUsers", "all_users", lambda value: value is True, lambda value: value),
    _SdkOptionalField(
        "minCreationTime",
        "min_creation_time",
        lambda value: value is not None,
        _millis_to_datetime_value,
    ),
    _SdkOptionalField(
        "maxCreationTime",
        "max_creation_time",
        lambda value: value is not None,
        _millis_to_datetime_value,
    ),
    _SdkOptionalField("pageToken", "page_token", _non_empty_string, lambda value: value),
    _SdkOptionalField(
        "maxResults",
        "max_results",
        lambda value: value is not None,
        lambda value: value,
    ),
    _SdkOptionalField(
        "state",
        "state_filter",
        _non_empty_string,
        lambda value: str(value).lower(),
    ),
    _SdkOptionalField("parentJobId", "parent_job", _non_empty_string, lambda value: value),
)


def _apply_optional_fields(
    target: dict[str, Any],
    source: ListJobsRequest,
    fields: tuple[_ListRequestOptionalField, ...],
) -> None:
    for field in fields:
        value = source.get(field.key)
        if field.include(value):
            target[field.key] = field.transform(value)


def apply_list_request_optionals_to_mapping(
    target: dict[str, Any],
    source: ListJobsRequest,
) -> None:
    """Copy optional ListJobsRequest fields onto target when present."""
    _apply_optional_fields(target, source, _LIST_REQUEST_OPTIONAL_FIELDS)


def _optional_trimmed_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    trimmed = value.strip()
    return trimmed if len(trimmed) > 0 else None


def _apply_timestamp_param(
    target: ListJobsRequest,
    obj: dict[str, Any],
    key: Literal["minCreationTime", "maxCreationTime"],
) -> None:
    raw = obj.get(key)
    if isinstance(raw, str):
        target[key] = parse_iso_timestamp_to_millis(raw)


def _apply_string_param(
    target: ListJobsRequest,
    obj: dict[str, Any],
    key: Literal["pageToken", "state", "parentJobId"],
) -> None:
    trimmed = _optional_trimmed_string(obj.get(key))
    if trimmed is not None:
        target[key] = trimmed


def list_request_from_validated_params(obj: dict[str, Any]) -> ListJobsRequest:
    """Build ListJobsRequest from validated jobs list params (excludes post-list filters)."""
    list_request: ListJobsRequest = {
        "projectId": str(obj["projectId"]).strip(),
    }

    if obj.get("allUsers") is True:
        list_request["allUsers"] = True

    _apply_timestamp_param(list_request, obj, "minCreationTime")
    _apply_timestamp_param(list_request, obj, "maxCreationTime")
    _apply_string_param(list_request, obj, "pageToken")

    max_results = obj.get("maxResults")
    if isinstance(max_results, int):
        list_request["maxResults"] = max_results

    _apply_string_param(list_request, obj, "state")
    _apply_string_param(list_request, obj, "parentJobId")

    return list_request


def list_request_to_sdk_kwargs(request: ListJobsRequest) -> dict[str, Any]:
    """Map a ListJobsRequest to google-cloud-bigquery list_jobs keyword arguments."""
    list_kwargs: dict[str, Any] = {"project": request["projectId"]}

    for field in _SDK_OPTIONAL_FIELDS:
        value = request.get(field.source_key)
        if field.include(value):
            list_kwargs[field.target_key] = field.transform(value)

    return list_kwargs


def build_list_jobs_response_echo(
    list_request: ListJobsRequest,
    filters: JobListFiltersEcho,
    impersonation: ImpersonationFields,
) -> ListJobsResponseRequest:
    """Build the jobs list response request echo block."""
    request: ListJobsResponseRequest = {
        "projectId": list_request["projectId"],
        "filters": filters,
    }
    apply_list_request_optionals_to_mapping(cast("dict[str, Any]", request), list_request)
    request.update(impersonation_request_fields(impersonation))  # type: ignore[arg-type]
    return request
