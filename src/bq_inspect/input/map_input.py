"""Map validated JSON params to domain input types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspect.core.jobs.filter import JobFilters
from bq_inspect.core.jobs.list_request_fields import list_request_from_validated_params
from bq_inspect.core.shared.job_ref import normalize_job_ref
from bq_inspect.core.shared.normalize import normalize_delegate_list, normalize_optional_trimmed

if TYPE_CHECKING:
    from bq_inspect.core.shared.impersonation_fields import ImpersonationFields
    from bq_inspect.core.shared.types import JobRef
    from bq_inspect.input.parsed_input_types import (
        ParsedCatalogInput,
        ParsedJobsListInput,
        ParsedJobsViewInput,
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
