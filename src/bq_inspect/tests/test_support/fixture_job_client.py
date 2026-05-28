"""Fixture-based BigQuery client for unit tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bq_inspect.bigquery.types.list_jobs import ListJobsPage, ListJobsRequest
    from bq_inspect.bigquery.types.refs import DatasetRef, TableRef
    from bq_inspect.core.shared.types import JobRef


class FixtureBigQueryInput:
    """Configuration for FixtureBigQueryClient."""

    def __init__(
        self,
        *,
        jobs_by_id: dict[str, object] | None = None,
        list_jobs_page: ListJobsPage | None = None,
        datasets_by_key: dict[str, object] | None = None,
        tables_list_by_key: dict[str, list[object]] | None = None,
        tables_by_key: dict[str, object] | None = None,
    ) -> None:
        self.jobs_by_id = jobs_by_id
        self.list_jobs_page = list_jobs_page
        self.datasets_by_key = datasets_by_key
        self.tables_list_by_key = tables_list_by_key
        self.tables_by_key = tables_by_key


def _dataset_key(ref: DatasetRef) -> str:
    return f"{ref['projectId']}:{ref['datasetId']}"


def _table_key(ref: TableRef) -> str:
    return f"{ref['projectId']}:{ref['datasetId']}:{ref['tableId']}"


class FixtureBigQueryClient:
    """In-memory BigQuery client backed by fixture maps."""

    def __init__(self, input_data: FixtureBigQueryInput) -> None:
        self._input = input_data

    async def get_job(self, ref: JobRef) -> object:
        jobs = self._input.jobs_by_id
        if jobs is None:
            raise RuntimeError(f"Fixture job not found: {ref['jobId']}")
        job_id = ref["jobId"]
        job = jobs.get(job_id)
        if job is None:
            raise RuntimeError(f"Fixture job not found: {job_id}")
        return job

    async def list_jobs(self, request: ListJobsRequest) -> ListJobsPage:
        del request
        return self._input.list_jobs_page or {"jobs": []}

    async def get_dataset(self, ref: DatasetRef) -> object:
        key = _dataset_key(ref)
        datasets = self._input.datasets_by_key
        if datasets is None:
            raise RuntimeError(f"Fixture dataset not found: {key}")
        dataset = datasets.get(key)
        if dataset is None:
            raise RuntimeError(f"Fixture dataset not found: {key}")
        return dataset

    async def list_tables(self, ref: DatasetRef) -> list[object]:
        key = _dataset_key(ref)
        tables_list = self._input.tables_list_by_key
        if tables_list is None:
            raise RuntimeError(f"Fixture tables list not found: {key}")
        tables = tables_list.get(key)
        if tables is None:
            raise RuntimeError(f"Fixture tables list not found: {key}")
        return tables

    async def get_table(self, ref: TableRef) -> object:
        key = _table_key(ref)
        tables = self._input.tables_by_key
        if tables is None:
            raise RuntimeError(f"Fixture table not found: {key}")
        table = tables.get(key)
        if table is None:
            raise RuntimeError(f"Fixture table not found: {key}")
        return table


class FixtureJobClient:
    """Job-only fixture client wrapping FixtureBigQueryClient."""

    def __init__(self, jobs_by_id: dict[str, object]) -> None:
        self._inner = FixtureBigQueryClient(FixtureBigQueryInput(jobs_by_id=jobs_by_id))

    async def get_job(self, ref: JobRef) -> object:
        return await self._inner.get_job(ref)
