"""Map validated JSON params to domain input types."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from bq_inspect.core.jobs.filter import JobFilters
from bq_inspect.core.shared.job_ref import normalize_job_ref
from bq_inspect.core.shared.normalize import normalize_delegate_list, normalize_optional_trimmed

if TYPE_CHECKING:
    from bq_inspect.bigquery.types.list_jobs import ListJobsRequest
    from bq_inspect.cli.input.parsed_input_types import (
        ParsedCatalogInput,
        ParsedJobsListInput,
        ParsedJobsViewInput,
    )
    from bq_inspect.core.shared.impersonation_fields import ImpersonationFields
    from bq_inspect.core.shared.types import JobRef


def _parse_impersonation_fields(obj: dict[str, Any]) -> ImpersonationFields:
    fields: ImpersonationFields = {}

    raw_service_account = obj.get("impersonateServiceAccount")
    if isinstance(raw_service_account, str):
        service_account = normalize_optional_trimmed(raw_service_account)
        if service_account is not None:
            fields["impersonateServiceAccount"] = service_account

    raw_delegates = obj.get("impersonateDelegates")
    if raw_delegates is not None:
        delegates = normalize_delegate_list(raw_delegates)
        if len(delegates) > 0:
            fields["impersonateDelegates"] = delegates

    return fields


def _map_jobs_array(raw: Any) -> list[JobRef]:
    if not isinstance(raw, list):
        return []
    return [normalize_job_ref(job) for job in raw]


def map_jobs_view_input(obj: dict[str, Any]) -> ParsedJobsViewInput:
    """Map jobs view command params to domain input."""
    impersonation = _parse_impersonation_fields(obj)
    return {"jobs": _map_jobs_array(obj.get("jobs")), **impersonation}


def _parse_iso_timestamp(value: str) -> int:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    return int(datetime.fromisoformat(candidate).timestamp() * 1000)


def map_jobs_list_input(obj: dict[str, Any]) -> ParsedJobsListInput:  # noqa: C901, PLR0912
    """Map jobs list command params to domain input."""
    list_request: ListJobsRequest = {
        "projectId": str(obj["projectId"]).strip(),
    }

    if obj.get("allUsers") is True:
        list_request["allUsers"] = True

    min_creation_time = obj.get("minCreationTime")
    if isinstance(min_creation_time, str):
        list_request["minCreationTime"] = _parse_iso_timestamp(min_creation_time)

    max_creation_time = obj.get("maxCreationTime")
    if isinstance(max_creation_time, str):
        list_request["maxCreationTime"] = _parse_iso_timestamp(max_creation_time)

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

    labels: dict[str, str] | None = None
    raw_labels = obj.get("labels")
    if isinstance(raw_labels, dict) and len(raw_labels) > 0:
        labels = {str(key): str(value) for key, value in raw_labels.items()}

    filters = JobFilters()
    min_slot_ms = obj.get("minSlotMs")
    if isinstance(min_slot_ms, str):
        filters.min_slot_ms = int(min_slot_ms)

    min_bytes_billed = obj.get("minBytesBilled")
    if isinstance(min_bytes_billed, str):
        filters.min_bytes_billed = int(min_bytes_billed)

    if labels is not None:
        filters.labels = labels

    result: ParsedJobsListInput = {
        "listRequest": list_request,
        "filters": filters,
        **(_parse_impersonation_fields(obj)),
    }
    return result


def map_catalog_input(obj: dict[str, Any]) -> ParsedCatalogInput:
    """Map catalog command params to domain input."""
    result: ParsedCatalogInput = {
        "projectId": str(obj["projectId"]).strip(),
        "datasetId": str(obj["datasetId"]).strip(),
        **(_parse_impersonation_fields(obj)),
    }

    table_id = obj.get("tableId")
    if isinstance(table_id, str):
        result["tableId"] = table_id.strip()

    return result
