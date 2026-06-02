"""
Google Cloud SDK adapter for read-only BigQuery inspection.

- list_jobs: single-page fetch (CLI exposes pageToken).
- list_tables: default client paging (full dataset in one response).
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypeVar

from google.cloud import bigquery

from bq_inspector.bigquery.errors.google_api_errors import map_google_error_to_bq_inspector_failure
from bq_inspector.core.jobs.list_request_fields import list_request_to_sdk_kwargs
from bq_inspector.core.shared.api_error_hints import ApiErrorHintContext
from bq_inspector.core.shared.errors import BqInspectFailure

_T = TypeVar("_T")

if TYPE_CHECKING:
    from collections.abc import Callable

    from google.auth.credentials import Credentials
    from google.cloud.bigquery.client import Client

    from bq_inspector.bigquery.types.list_jobs import ListJobsPage, ListJobsRequest
    from bq_inspector.bigquery.types.refs import DatasetRef, TableRef
    from bq_inspector.core.shared.types import JobRef


async def _invoke_sync(
    fn: Callable[..., _T],
    *,
    api: str,
    context: ApiErrorHintContext | None = None,
) -> _T:
    try:
        return await asyncio.to_thread(fn)
    except BqInspectFailure:
        raise
    except Exception as error:
        raise map_google_error_to_bq_inspector_failure(error, api, context) from error


def _read_next_page_token(iterator: object) -> str | None:
    token = getattr(iterator, "next_page_token", None)
    if isinstance(token, str) and len(token) > 0:
        return token
    return None


def _resource_to_api_dict(resource: object) -> dict[str, object]:
    """Return the REST-shaped resource from a google-cloud-bigquery SDK object."""
    properties = getattr(resource, "_properties", None)
    if isinstance(properties, dict):
        return dict(properties)
    to_api_repr = getattr(resource, "to_api_repr", None)
    if callable(to_api_repr):
        result = to_api_repr()
        if isinstance(result, dict):
            return result
    raise TypeError("Expected BigQuery SDK resource or compatible mock")


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
        return await _invoke_sync(
            lambda: self._get_job_sync(ref),
            api="bigquery.jobs.get",
            context=ApiErrorHintContext(job_ref=ref),
        )

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
        return _resource_to_api_dict(job)

    async def list_jobs(self, request: ListJobsRequest) -> ListJobsPage:
        return await _invoke_sync(
            lambda: self._list_jobs_sync(request),
            api="bigquery.jobs.list",
        )

    def _list_jobs_sync(self, request: ListJobsRequest) -> ListJobsPage:
        bq = self._get_bigquery(request["projectId"])
        list_kwargs = list_request_to_sdk_kwargs(request)

        iterator = bq.list_jobs(**list_kwargs)
        page = next(iterator.pages, None)
        jobs: list[object] = (
            [_resource_to_api_dict(job) for job in page] if page is not None else []
        )
        next_page_token = _read_next_page_token(iterator)

        result: ListJobsPage = {"jobs": jobs}
        if next_page_token is not None:
            result["nextPageToken"] = next_page_token
        return result

    async def get_dataset(self, ref: DatasetRef) -> object:
        return await _invoke_sync(
            lambda: self._get_dataset_sync(ref),
            api="bigquery.datasets.get",
        )

    def _get_dataset_sync(self, ref: DatasetRef) -> object:
        bq = self._get_bigquery(ref["projectId"])
        project_id = ref["projectId"]
        dataset_id = ref["datasetId"]
        dataset = bq.get_dataset(f"{project_id}.{dataset_id}")
        return _resource_to_api_dict(dataset)

    async def list_tables(self, ref: DatasetRef) -> list[object]:
        return await _invoke_sync(
            lambda: self._list_tables_sync(ref),
            api="bigquery.tables.list",
        )

    def _list_tables_sync(self, ref: DatasetRef) -> list[object]:
        bq = self._get_bigquery(ref["projectId"])
        project_id = ref["projectId"]
        dataset_id = ref["datasetId"]
        tables = list(bq.list_tables(f"{project_id}.{dataset_id}"))
        return [_resource_to_api_dict(table) for table in tables]

    async def get_table(self, ref: TableRef) -> object:
        return await _invoke_sync(
            lambda: self._get_table_sync(ref),
            api="bigquery.tables.get",
        )

    def _get_table_sync(self, ref: TableRef) -> object:
        bq = self._get_bigquery(ref["projectId"])
        project_id = ref["projectId"]
        dataset_id = ref["datasetId"]
        table_id = ref["tableId"]
        table = bq.get_table(f"{project_id}.{dataset_id}.{table_id}")
        return _resource_to_api_dict(table)
