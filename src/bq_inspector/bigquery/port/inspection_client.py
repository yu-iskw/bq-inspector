"""BigQuery inspection client protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from bq_inspector.bigquery.types.list_jobs import ListJobsPage, ListJobsRequest
    from bq_inspector.bigquery.types.refs import DatasetRef, TableRef
    from bq_inspector.core.shared.types import JobRef


class BigQueryInspectionClient(Protocol):
    """Port for read-only BigQuery metadata and job inspection."""

    async def get_job(self, ref: JobRef) -> object:
        """Fetch a single job by reference."""
        raise NotImplementedError

    async def list_jobs(self, request: ListJobsRequest) -> ListJobsPage:
        """List jobs for a project."""
        raise NotImplementedError

    async def get_dataset(self, ref: DatasetRef) -> object:
        """Fetch dataset metadata."""
        raise NotImplementedError

    async def list_tables(self, ref: DatasetRef) -> list[object]:
        """List tables in a dataset."""
        raise NotImplementedError

    async def get_table(self, ref: TableRef) -> object:
        """Fetch table metadata."""
        raise NotImplementedError


class BigQueryJobClient(Protocol):
    """Subset of BigQueryInspectionClient for job get operations."""

    async def get_job(self, ref: JobRef) -> object:
        """Fetch a single job by reference."""
        raise NotImplementedError
