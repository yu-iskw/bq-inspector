"""Map validated JSON params to domain input types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.jobs.filter import JobFilters
from bq_inspector.core.jobs.list_request_fields import list_request_from_validated_params
from bq_inspector.core.shared.job_ref import normalize_job_ref
from bq_inspector.core.shared.normalize import normalize_delegate_list, normalize_optional_trimmed

if TYPE_CHECKING:
    from bq_inspector.core.shared.impersonation_fields import ImpersonationFields
    from bq_inspector.core.shared.types import JobRef
    from bq_inspector.datalineage.types.requests import LineageDirection
    from bq_inspector.input.parsed_input_types import (
        ParsedCatalogInput,
        ParsedJobsListInput,
        ParsedJobsViewInput,
        ParsedLineageGraphInput,
        ParsedLineageInput,
    )


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


def map_jobs_list_input(obj: dict[str, Any]) -> ParsedJobsListInput:
    """Map jobs list command params to domain input."""
    list_request = list_request_from_validated_params(obj)

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


def _resolve_client_project_id(obj: dict[str, Any]) -> str:
    raw_client_project_id = obj.get("clientProjectId")
    if isinstance(raw_client_project_id, str):
        client_project_id = normalize_optional_trimmed(raw_client_project_id)
        if client_project_id is not None:
            return client_project_id
    return str(obj["projectId"]).strip()


def _parse_lineage_direction(raw: object) -> LineageDirection:
    direction = str(raw).strip()
    if direction == "UPSTREAM":
        return "UPSTREAM"
    return "DOWNSTREAM"


def map_lineage_input(obj: dict[str, Any]) -> ParsedLineageInput:
    """Map lineage command params to domain input."""
    result: ParsedLineageInput = {
        "clientProjectId": _resolve_client_project_id(obj),
        "location": str(obj["location"]).strip(),
        "projectId": str(obj["projectId"]).strip(),
        "datasetId": str(obj["datasetId"]).strip(),
        "tableId": str(obj["tableId"]).strip(),
        "direction": _parse_lineage_direction(obj["direction"]),
        **(_parse_impersonation_fields(obj)),
    }

    page_size = obj.get("pageSize")
    if isinstance(page_size, int):
        result["pageSize"] = page_size

    page_token = obj.get("pageToken")
    if isinstance(page_token, str):
        trimmed = page_token.strip()
        if len(trimmed) > 0:
            result["pageToken"] = trimmed

    return result


def map_lineage_graph_input(obj: dict[str, Any]) -> ParsedLineageGraphInput:
    """Map lineage graph command params to domain input."""
    result: ParsedLineageGraphInput = {**map_lineage_input(obj)}

    max_depth = obj.get("maxDepth")
    if isinstance(max_depth, int):
        result["maxDepth"] = max_depth

    max_results = obj.get("maxResults")
    if isinstance(max_results, int):
        result["maxResults"] = max_results

    return result
