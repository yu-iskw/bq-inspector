"""Parsed CLI input types."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import NotRequired

from bq_inspector.core.shared.impersonation_fields import ImpersonationFields

if TYPE_CHECKING:
    from bq_inspector.bigquery.types.list_jobs import ListJobsRequest
    from bq_inspector.core.jobs.filter import JobFilters
    from bq_inspector.core.shared.types import JobRef
    from bq_inspector.datalineage.types.requests import LineageDirection


class ParsedJobsViewInput(ImpersonationFields):
    jobs: list[JobRef]


class ParsedJobsListInput(ImpersonationFields):
    listRequest: ListJobsRequest
    filters: JobFilters


class ParsedCatalogInput(ImpersonationFields):
    projectId: str
    datasetId: str
    tableId: NotRequired[str]


class ParsedLineageInput(ImpersonationFields):
    clientProjectId: str
    location: str
    projectId: str
    datasetId: str
    tableId: str
    direction: LineageDirection
    pageSize: NotRequired[int]
    pageToken: NotRequired[str]


class ParsedLineageGraphInput(ParsedLineageInput):
    maxDepth: NotRequired[int]
    maxResults: NotRequired[int]
