"""Parsed CLI input types."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspect.core.shared.impersonation_fields import ImpersonationFields

if TYPE_CHECKING:
    from bq_inspect.bigquery.types.list_jobs import ListJobsRequest
    from bq_inspect.core.jobs.filter import JobFilters
    from bq_inspect.core.shared.types import JobRef


class ParsedJobsViewInput(ImpersonationFields, total=False):
    jobs: list[JobRef]


class ParsedJobsListInput(ImpersonationFields, total=False):
    listRequest: ListJobsRequest
    filters: JobFilters


class ParsedCatalogInput(ImpersonationFields, total=False):
    projectId: str
    datasetId: str
    tableId: str
