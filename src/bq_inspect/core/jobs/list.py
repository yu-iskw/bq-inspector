"""List BigQuery jobs with post-list filtering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspect.core.jobs.filter import JobFilters, filter_job_summaries, filters_to_echo
from bq_inspect.core.shared.envelope import build_tool_envelope
from bq_inspect.core.shared.errors import BqInspectFailure
from bq_inspect.core.shared.impersonation_fields import (
    ImpersonationFields,
    impersonation_request_fields,
)

if TYPE_CHECKING:
    from bq_inspect.bigquery.port.inspection_client import BigQueryInspectionClient
    from bq_inspect.bigquery.types.list_jobs import ListJobsRequest
    from bq_inspect.core.shared.types import (
        BqInspectError,
        ListJobsPageBlock,
        ListJobsResponse,
        ListJobsResponseRequest,
    )


class ListJobsOrchestrationInput:
    """Input for list_jobs orchestration."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        client: BigQueryInspectionClient,
        tool_version: str,
        list_request: ListJobsRequest,
        filters: JobFilters,
        impersonate_service_account: str | None = None,
        impersonate_delegates: list[str] | None = None,
    ) -> None:
        self.client = client
        self.tool_version = tool_version
        self.list_request = list_request
        self.filters = filters
        self.impersonate_service_account = impersonate_service_account
        self.impersonate_delegates = impersonate_delegates

    def as_impersonation_fields(self) -> ImpersonationFields:
        fields: ImpersonationFields = {}
        if self.impersonate_service_account is not None:
            fields["impersonateServiceAccount"] = self.impersonate_service_account
        if self.impersonate_delegates is not None:
            fields["impersonateDelegates"] = self.impersonate_delegates
        return fields


def _build_list_jobs_request_echo(  # noqa: PLR0912
    list_request: ListJobsRequest,
    filters: JobFilters,
    impersonation: ImpersonationFields,
) -> ListJobsResponseRequest:
    request: ListJobsResponseRequest = {
        "projectId": list_request["projectId"],
        "filters": filters_to_echo(filters),
    }

    if list_request.get("allUsers") is True:
        request["allUsers"] = True
    min_creation_time = list_request.get("minCreationTime")
    if min_creation_time is not None:
        request["minCreationTime"] = min_creation_time

    max_creation_time = list_request.get("maxCreationTime")
    if max_creation_time is not None:
        request["maxCreationTime"] = max_creation_time

    page_token = list_request.get("pageToken")
    if page_token is not None and len(page_token) > 0:
        request["pageToken"] = page_token

    max_results = list_request.get("maxResults")
    if max_results is not None:
        request["maxResults"] = max_results

    state = list_request.get("state")
    if state is not None and len(state) > 0:
        request["state"] = state

    parent_job_id = list_request.get("parentJobId")
    if parent_job_id is not None and len(parent_job_id) > 0:
        request["parentJobId"] = parent_job_id

    request.update(impersonation_request_fields(impersonation))  # type: ignore[arg-type]
    return request


async def list_jobs(input_data: ListJobsOrchestrationInput) -> ListJobsResponse:
    """List jobs and apply client-side filters."""
    envelope = build_tool_envelope(input_data.tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]
    request = _build_list_jobs_request_echo(
        input_data.list_request,
        input_data.filters,
        input_data.as_impersonation_fields(),
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
