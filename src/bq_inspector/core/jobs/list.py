"""List BigQuery jobs with post-list filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

from bq_inspector.core.jobs.filter import filter_job_summaries, filters_to_echo
from bq_inspector.core.jobs.list_request_fields import build_list_jobs_response_echo
from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure

if TYPE_CHECKING:
    from bq_inspector.bigquery.port.inspection_client import BigQueryInspectionClient
    from bq_inspector.bigquery.types.list_jobs import ListJobsRequest
    from bq_inspector.core.jobs.filter import JobFilters
    from bq_inspector.core.shared.impersonation_fields import ImpersonationFields
    from bq_inspector.core.shared.types import (
        BqInspectError,
        ListJobsPageBlock,
        ListJobsResponse,
    )


def _empty_impersonation_fields() -> ImpersonationFields:
    return cast("ImpersonationFields", {})


@dataclass
class ListJobsOrchestrationInput:
    """Input for list_jobs orchestration."""

    client: BigQueryInspectionClient
    tool_version: str
    list_request: ListJobsRequest
    filters: JobFilters
    impersonation: ImpersonationFields = field(default_factory=_empty_impersonation_fields)


async def list_jobs(input_data: ListJobsOrchestrationInput) -> ListJobsResponse:
    """List jobs and apply client-side filters."""
    envelope = build_tool_envelope(input_data.tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]
    request = build_list_jobs_response_echo(
        input_data.list_request,
        filters_to_echo(input_data.filters),
        input_data.impersonation,
    )

    try:
        page = await input_data.client.list_jobs(input_data.list_request)
        jobs = filter_job_summaries(page.get("jobs", []), input_data.filters)

        page_block: ListJobsPageBlock = {}
        next_page_token = page.get("nextPageToken")
        if next_page_token is not None and len(next_page_token) > 0:
            page_block["nextPageToken"] = next_page_token
    except BqInspectFailure as error:
        errors: list[BqInspectError] = [error.details]
        return {
            "schemaVersion": schema_version,
            "tool": tool,
            "request": request,
            "jobs": [],
            "page": {},
            "warnings": [],
            "errors": errors,
        }
    else:
        return {
            "schemaVersion": schema_version,
            "tool": tool,
            "request": request,
            "jobs": jobs,
            "page": page_block,
            "warnings": [],
            "errors": [],
        }
