"""Canonical mapping for BigQuery jobs.list request fields."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

from bq_inspect.core.shared.impersonation_fields import impersonation_request_fields

if TYPE_CHECKING:
    from bq_inspect.bigquery.types.list_jobs import ListJobsRequest
    from bq_inspect.core.shared.impersonation_fields import ImpersonationFields
    from bq_inspect.core.shared.types import JobListFiltersEcho, ListJobsResponseRequest


def parse_iso_timestamp_to_millis(value: str) -> int:
    """Parse an ISO-8601 timestamp string to epoch milliseconds."""
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return int(parsed.timestamp() * 1000)


def millis_to_datetime(millis: int) -> datetime:
    """Convert epoch milliseconds to a timezone-aware datetime."""
    return datetime.fromtimestamp(millis / 1000.0, tz=UTC)


def apply_list_request_optionals_to_mapping(  # noqa: PLR0912
    target: dict[str, Any],
    source: ListJobsRequest,
) -> None:
    """Copy optional ListJobsRequest fields onto target when present."""
    if source.get("allUsers") is True:
        target["allUsers"] = True

    min_creation_time = source.get("minCreationTime")
    if min_creation_time is not None:
        target["minCreationTime"] = min_creation_time

    max_creation_time = source.get("maxCreationTime")
    if max_creation_time is not None:
        target["maxCreationTime"] = max_creation_time

    page_token = source.get("pageToken")
    if page_token is not None and len(page_token) > 0:
        target["pageToken"] = page_token

    max_results = source.get("maxResults")
    if max_results is not None:
        target["maxResults"] = max_results

    state = source.get("state")
    if state is not None and len(state) > 0:
        target["state"] = state

    parent_job_id = source.get("parentJobId")
    if parent_job_id is not None and len(parent_job_id) > 0:
        target["parentJobId"] = parent_job_id


def list_request_from_validated_params(obj: dict[str, Any]) -> ListJobsRequest:  # noqa: PLR0912
    """Build ListJobsRequest from validated jobs list params (excludes post-list filters)."""
    list_request: ListJobsRequest = {
        "projectId": str(obj["projectId"]).strip(),
    }

    if obj.get("allUsers") is True:
        list_request["allUsers"] = True

    min_creation_time = obj.get("minCreationTime")
    if isinstance(min_creation_time, str):
        list_request["minCreationTime"] = parse_iso_timestamp_to_millis(min_creation_time)

    max_creation_time = obj.get("maxCreationTime")
    if isinstance(max_creation_time, str):
        list_request["maxCreationTime"] = parse_iso_timestamp_to_millis(max_creation_time)

    page_token = obj.get("pageToken")
    if isinstance(page_token, str) and len(page_token.strip()) > 0:
        list_request["pageToken"] = page_token.strip()

    max_results = obj.get("maxResults")
    if isinstance(max_results, int):
        list_request["maxResults"] = max_results

    state = obj.get("state")
    if isinstance(state, str) and len(state.strip()) > 0:
        list_request["state"] = state.strip()

    parent_job_id = obj.get("parentJobId")
    if isinstance(parent_job_id, str) and len(parent_job_id.strip()) > 0:
        list_request["parentJobId"] = parent_job_id.strip()

    return list_request


def list_request_to_sdk_kwargs(request: ListJobsRequest) -> dict[str, Any]:  # noqa: PLR0912
    """Map a ListJobsRequest to google-cloud-bigquery list_jobs keyword arguments."""
    list_kwargs: dict[str, Any] = {"project": request["projectId"]}

    if request.get("allUsers") is True:
        list_kwargs["all_users"] = True

    min_creation_time = request.get("minCreationTime")
    if min_creation_time is not None:
        list_kwargs["min_creation_time"] = millis_to_datetime(min_creation_time)

    max_creation_time = request.get("maxCreationTime")
    if max_creation_time is not None:
        list_kwargs["max_creation_time"] = millis_to_datetime(max_creation_time)

    page_token = request.get("pageToken")
    if page_token is not None and len(page_token) > 0:
        list_kwargs["page_token"] = page_token

    max_results = request.get("maxResults")
    if max_results is not None:
        list_kwargs["max_results"] = max_results

    state = request.get("state")
    if state is not None and len(state) > 0:
        list_kwargs["state_filter"] = state.lower()

    parent_job_id = request.get("parentJobId")
    if parent_job_id is not None and len(parent_job_id) > 0:
        list_kwargs["parent_job"] = parent_job_id

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
