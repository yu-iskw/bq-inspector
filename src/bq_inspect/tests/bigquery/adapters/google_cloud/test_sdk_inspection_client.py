"""Tests for the Google Cloud SDK inspection client adapter."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import NotFound

from bq_inspect.bigquery.adapters.google_cloud.sdk_inspection_client import SdkBigQueryClient
from bq_inspect.core.shared.errors import BqInspectFailure


@pytest.fixture
def auth_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_bigquery_client() -> MagicMock:
    client = MagicMock()
    client.get_job = MagicMock()
    client.list_jobs = MagicMock()
    client.get_dataset = MagicMock()
    client.list_tables = MagicMock()
    client.get_table = MagicMock()
    return client


@pytest.fixture
def sdk_client(auth_client: MagicMock, mock_bigquery_client: MagicMock) -> SdkBigQueryClient:
    with patch(
        "bq_inspect.bigquery.adapters.google_cloud.sdk_inspection_client.bigquery.Client",
        return_value=mock_bigquery_client,
    ):
        yield SdkBigQueryClient(auth_client)


@pytest.mark.asyncio
async def test_get_job_returns_metadata_with_location(
    sdk_client: SdkBigQueryClient,
    mock_bigquery_client: MagicMock,
) -> None:
    job = MagicMock()
    job.to_api_repr.return_value = {"id": "job-1"}
    mock_bigquery_client.get_job.return_value = job

    result = await sdk_client.get_job({"projectId": "p", "jobId": "j", "location": "US"})

    assert result == {"id": "job-1"}
    mock_bigquery_client.get_job.assert_called_once_with("j", project="p", location="US")


@pytest.mark.asyncio
async def test_get_job_omits_location_when_blank(
    sdk_client: SdkBigQueryClient,
    mock_bigquery_client: MagicMock,
) -> None:
    job = MagicMock()
    job.to_api_repr.return_value = {"id": "job-1"}
    mock_bigquery_client.get_job.return_value = job

    await sdk_client.get_job({"projectId": "p", "jobId": "j", "location": "  "})

    mock_bigquery_client.get_job.assert_called_once_with("j", project="p")


@pytest.mark.asyncio
async def test_get_job_maps_api_errors_to_bq_inspect_failure(
    sdk_client: SdkBigQueryClient,
    mock_bigquery_client: MagicMock,
) -> None:
    mock_bigquery_client.get_job.side_effect = NotFound("Missing.")

    with pytest.raises(BqInspectFailure) as exc_info:
        await sdk_client.get_job({"projectId": "p", "jobId": "j"})

    assert exc_info.value.details["code"] == "BQINSPECT_JOB_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_jobs_returns_jobs_and_next_page_token(
    sdk_client: SdkBigQueryClient,
    mock_bigquery_client: MagicMock,
) -> None:
    listed_job = MagicMock()
    listed_job.to_api_repr.return_value = {"id": "listed"}
    page = MagicMock()
    page.__iter__ = MagicMock(return_value=iter([listed_job]))
    iterator = MagicMock()
    iterator.pages = iter([page])
    iterator.next_page_token = "next"
    mock_bigquery_client.list_jobs.return_value = iterator

    result = await sdk_client.list_jobs(
        {
            "projectId": "p",
            "allUsers": True,
            "minCreationTime": 1,
            "maxCreationTime": 2,
            "pageToken": "tok",
            "maxResults": 5,
            "state": "DONE",
            "parentJobId": "parent_1",
        }
    )

    assert result == {"jobs": [{"id": "listed"}], "nextPageToken": "next"}
    call_kwargs = mock_bigquery_client.list_jobs.call_args.kwargs
    assert call_kwargs["project"] == "p"
    assert call_kwargs["all_users"] is True
    assert call_kwargs["page_token"] == "tok"
    assert call_kwargs["max_results"] == 5
    assert call_kwargs["state_filter"] == "done"
    assert call_kwargs["parent_job"] == "parent_1"


@pytest.mark.asyncio
async def test_get_dataset_returns_metadata(
    sdk_client: SdkBigQueryClient,
    mock_bigquery_client: MagicMock,
) -> None:
    dataset = MagicMock()
    dataset.to_api_repr.return_value = {"datasetId": "d"}
    mock_bigquery_client.get_dataset.return_value = dataset

    result = await sdk_client.get_dataset({"projectId": "p", "datasetId": "d"})

    assert result == {"datasetId": "d"}


@pytest.mark.asyncio
async def test_list_tables_returns_table_metadata(
    sdk_client: SdkBigQueryClient,
    mock_bigquery_client: MagicMock,
) -> None:
    table = MagicMock()
    table.to_api_repr.return_value = {"tableId": "t"}
    mock_bigquery_client.list_tables.return_value = iter([table])

    result = await sdk_client.list_tables({"projectId": "p", "datasetId": "d"})

    assert result == [{"tableId": "t"}]
    mock_bigquery_client.list_tables.assert_called_once_with("d", project="p")


@pytest.mark.asyncio
async def test_get_table_returns_metadata(
    sdk_client: SdkBigQueryClient,
    mock_bigquery_client: MagicMock,
) -> None:
    table = MagicMock()
    table.to_api_repr.return_value = {"tableId": "t"}
    mock_bigquery_client.get_table.return_value = table

    result = await sdk_client.get_table(
        {"projectId": "p", "datasetId": "d", "tableId": "t"},
    )

    assert result == {"tableId": "t"}


@pytest.mark.asyncio
async def test_reuses_bigquery_client_per_project(auth_client: MagicMock) -> None:
    mock_client = MagicMock()
    job = MagicMock()
    job.to_api_repr.return_value = {"id": "job-1"}
    mock_client.get_job.return_value = job

    with patch(
        "bq_inspect.bigquery.adapters.google_cloud.sdk_inspection_client.bigquery.Client",
        return_value=mock_client,
    ) as client_ctor:
        client = SdkBigQueryClient(auth_client)
        await client.get_job({"projectId": "p", "jobId": "a"})
        await client.get_job({"projectId": "p", "jobId": "b"})

    client_ctor.assert_called_once()
