"""
Google Cloud SDK adapter for read-only BigQuery inspection.

- list_jobs: single-page fetch (CLI exposes pageToken).
- list_tables: default client paging (full dataset in one response).
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from google.cloud import bigquery

from bq_inspect.bigquery.errors.google_api_errors import map_google_error_to_bq_inspect_failure
from bq_inspect.core.shared.api_error_hints import ApiErrorHintContext

if TYPE_CHECKING:
    from google.auth.credentials import Credentials
    from google.cloud.bigquery.client import Client

    from bq_inspect.bigquery.types.list_jobs import ListJobsPage, ListJobsRequest
    from bq_inspect.bigquery.types.refs import DatasetRef, TableRef
    from bq_inspect.core.shared.types import JobRef


def _millis_to_datetime(millis: int) -> datetime:
    return datetime.fromtimestamp(millis / 1000.0, tz=UTC)


def _read_next_page_token(iterator: object) -> str | None:
    token = getattr(iterator, "next_page_token", None)
    if isinstance(token, str) and len(token) > 0:
        return token
    return None


class SdkBigQueryClient:
    """BigQuery inspection client backed by google-cloud-bigquery."""

    def __init__(self, auth_client: Credentials) -> None:
        self._auth_client = auth_client
        self._bq_by_project: dict[str, Client] = {}

    def _get_bigquery(self, project_id: str) -> Client:
        client = self._bq_by_project.get(project_id)
        if client is None:
            client = bigquery.Client(project=project_id, credentials=self._auth_client)
            self._bq_by_project[project_id] = client
        return client

    async def get_job(self, ref: JobRef) -> object:
        try:
            return await asyncio.to_thread(self._get_job_sync, ref)
        except Exception as error:
            raise map_google_error_to_bq_inspect_failure(
                error,
                "bigquery.jobs.get",
                ApiErrorHintContext(job_ref=ref),
            ) from error

    def _get_job_sync(self, ref: JobRef) -> object:
        bq = self._get_bigquery(ref["projectId"])
        location = ref.get("location")
        trimmed_location = location.strip() if isinstance(location, str) else None
        if trimmed_location is None or len(trimmed_location) == 0:
            job = bq.get_job(ref["jobId"], project=ref["projectId"])
        else:
            job = bq.get_job(
                ref["jobId"],
                project=ref["projectId"],
                location=trimmed_location,
            )
        return job.to_api_repr()

    async def list_jobs(self, request: ListJobsRequest) -> ListJobsPage:
        try:
            return await asyncio.to_thread(self._list_jobs_sync, request)
        except Exception as error:
            raise map_google_error_to_bq_inspect_failure(error, "bigquery.jobs.list") from error

    def _list_jobs_sync(self, request: ListJobsRequest) -> ListJobsPage:  # noqa: PLR0912
        bq = self._get_bigquery(request["projectId"])
        list_kwargs: dict[str, Any] = {"project": request["projectId"]}

        if request.get("allUsers") is True:
            list_kwargs["all_users"] = True

        min_creation_time = request.get("minCreationTime")
        if min_creation_time is not None:
            list_kwargs["min_creation_time"] = _millis_to_datetime(min_creation_time)

        max_creation_time = request.get("maxCreationTime")
        if max_creation_time is not None:
            list_kwargs["max_creation_time"] = _millis_to_datetime(max_creation_time)

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

        iterator = bq.list_jobs(**list_kwargs)
        page = next(iterator.pages)
        jobs = [job.to_api_repr() for job in page]
        next_page_token = _read_next_page_token(iterator)

        result: ListJobsPage = {"jobs": jobs}
        if next_page_token is not None:
            result["nextPageToken"] = next_page_token
        return result

    async def get_dataset(self, ref: DatasetRef) -> object:
        try:
            return await asyncio.to_thread(self._get_dataset_sync, ref)
        except Exception as error:
            raise map_google_error_to_bq_inspect_failure(
                error,
                "bigquery.datasets.get",
            ) from error

    def _get_dataset_sync(self, ref: DatasetRef) -> object:
        bq = self._get_bigquery(ref["projectId"])
        project_id = ref["projectId"]
        dataset_id = ref["datasetId"]
        dataset = bq.get_dataset(f"{project_id}.{dataset_id}")
        return dataset.to_api_repr()

    async def list_tables(self, ref: DatasetRef) -> list[object]:
        try:
            return await asyncio.to_thread(self._list_tables_sync, ref)
        except Exception as error:
            raise map_google_error_to_bq_inspect_failure(error, "bigquery.tables.list") from error

    def _list_tables_sync(self, ref: DatasetRef) -> list[object]:
        bq = self._get_bigquery(ref["projectId"])
        project_id = ref["projectId"]
        dataset_id = ref["datasetId"]
        tables = list(bq.list_tables(f"{project_id}.{dataset_id}"))
        return [table.to_api_repr() for table in tables]

    async def get_table(self, ref: TableRef) -> object:
        try:
            return await asyncio.to_thread(self._get_table_sync, ref)
        except Exception as error:
            raise map_google_error_to_bq_inspect_failure(error, "bigquery.tables.get") from error

    def _get_table_sync(self, ref: TableRef) -> object:
        bq = self._get_bigquery(ref["projectId"])
        project_id = ref["projectId"]
        dataset_id = ref["datasetId"]
        table_id = ref["tableId"]
        table = bq.get_table(f"{project_id}.{dataset_id}.{table_id}")
        return table.to_api_repr()
