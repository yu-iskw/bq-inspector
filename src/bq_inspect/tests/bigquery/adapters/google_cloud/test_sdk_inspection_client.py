"""Tests for the Google Cloud SDK inspection client adapter."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import BadRequest, NotFound

from bq_inspect.bigquery.adapters.google_cloud.sdk_inspection_client import SdkBigQueryClient
from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error


@pytest.fixture
def mock_auth_client_fx() -> MagicMock:
    return MagicMock()


@pytest.fixture
def bq_client_mock_fx() -> MagicMock:
    client = MagicMock()
    client.get_job = MagicMock()
    client.list_jobs = MagicMock()
    client.get_dataset = MagicMock()
    client.list_tables = MagicMock()
    client.get_table = MagicMock()
    return client


@pytest.fixture
def sdk_client_fx(
    mock_auth_client_fx: MagicMock,
    bq_client_mock_fx: MagicMock,
) -> SdkBigQueryClient:
    with patch(
        "bq_inspect.bigquery.adapters.google_cloud.sdk_inspection_client.bigquery.Client",
        return_value=bq_client_mock_fx,
    ):
        yield SdkBigQueryClient(mock_auth_client_fx)


@pytest.mark.asyncio
async def test_get_job_returns_metadata_with_location(
    sdk_client_fx: SdkBigQueryClient,
    bq_client_mock_fx: MagicMock,
) -> None:
    job = MagicMock()
    job.to_api_repr.return_value = {"id": "job-1"}
    bq_client_mock_fx.get_job.return_value = job

    result = await sdk_client_fx.get_job({"projectId": "p", "jobId": "j", "location": "US"})

    assert result == {"id": "job-1"}
    bq_client_mock_fx.get_job.assert_called_once_with("j", project="p", location="US")


@pytest.mark.asyncio
async def test_get_job_omits_location_when_blank(
    sdk_client_fx: SdkBigQueryClient,
    bq_client_mock_fx: MagicMock,
) -> None:
    job = MagicMock()
    job.to_api_repr.return_value = {"id": "job-1"}
    bq_client_mock_fx.get_job.return_value = job

    await sdk_client_fx.get_job({"projectId": "p", "jobId": "j", "location": "  "})

    bq_client_mock_fx.get_job.assert_called_once_with("j", project="p")


@pytest.mark.asyncio
async def test_get_job_maps_api_errors_to_bq_inspect_failure(
    sdk_client_fx: SdkBigQueryClient,
    bq_client_mock_fx: MagicMock,
) -> None:
    bq_client_mock_fx.get_job.side_effect = NotFound("Missing.")

    with pytest.raises(BqInspectFailure) as exc_info:
        await sdk_client_fx.get_job({"projectId": "p", "jobId": "j"})

    assert exc_info.value.details["code"] == "BQINSPECT_JOB_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_jobs_returns_jobs_and_next_page_token(
    sdk_client_fx: SdkBigQueryClient,
    bq_client_mock_fx: MagicMock,
) -> None:
    listed_job = MagicMock()
    listed_job.to_api_repr.return_value = {"id": "listed"}
    page = MagicMock()
    page.__iter__ = MagicMock(return_value=iter([listed_job]))
    iterator = MagicMock()
    iterator.pages = iter([page])
    iterator.next_page_token = "next"
    bq_client_mock_fx.list_jobs.return_value = iterator

    result = await sdk_client_fx.list_jobs(
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
    call_kwargs = bq_client_mock_fx.list_jobs.call_args.kwargs
    assert call_kwargs["project"] == "p"
    assert call_kwargs["all_users"] is True
    assert call_kwargs["page_token"] == "tok"
    assert call_kwargs["max_results"] == 5
    assert call_kwargs["state_filter"] == "done"
    assert call_kwargs["parent_job"] == "parent_1"


@pytest.mark.asyncio
async def test_list_jobs_returns_empty_page_when_iterator_has_no_pages(
    sdk_client_fx: SdkBigQueryClient,
    bq_client_mock_fx: MagicMock,
) -> None:
    iterator = MagicMock()
    iterator.pages = iter([])
    iterator.next_page_token = None
    bq_client_mock_fx.list_jobs.return_value = iterator

    result = await sdk_client_fx.list_jobs({"projectId": "p"})

    assert result == {"jobs": []}


@pytest.mark.asyncio
async def test_list_jobs_maps_bad_request_to_input_invalid(
    sdk_client_fx: SdkBigQueryClient,
    bq_client_mock_fx: MagicMock,
) -> None:
    bq_client_mock_fx.list_jobs.side_effect = BadRequest("Invalid state filter.")

    with pytest.raises(BqInspectFailure) as exc_info:
        await sdk_client_fx.list_jobs({"projectId": "p", "state": "INVALID"})

    assert exc_info.value.details["code"] == "BQINSPECT_INPUT_INVALID"
    assert exc_info.value.details["retriable"] is False


@pytest.mark.asyncio
async def test_invoke_sync_preserves_bq_inspect_failure(
    sdk_client_fx: SdkBigQueryClient,
    bq_client_mock_fx: MagicMock,
) -> None:
    structured = BqInspectFailure(
        create_bq_inspect_error(
            code="BQINSPECT_JOB_NOT_FOUND",
            message="Missing.",
            source={"api": "bigquery.jobs.get", "status": 404},
        )
    )
    bq_client_mock_fx.get_job.side_effect = structured

    with pytest.raises(BqInspectFailure) as exc_info:
        await sdk_client_fx.get_job({"projectId": "p", "jobId": "j"})

    assert exc_info.value.details["code"] == "BQINSPECT_JOB_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_dataset_returns_metadata(
    sdk_client_fx: SdkBigQueryClient,
    bq_client_mock_fx: MagicMock,
) -> None:
    dataset = MagicMock()
    dataset.to_api_repr.return_value = {"datasetId": "d"}
    bq_client_mock_fx.get_dataset.return_value = dataset

    result = await sdk_client_fx.get_dataset({"projectId": "p", "datasetId": "d"})

    assert result == {"datasetId": "d"}


@pytest.mark.asyncio
async def test_list_tables_returns_table_metadata(
    sdk_client_fx: SdkBigQueryClient,
    bq_client_mock_fx: MagicMock,
) -> None:
    table = MagicMock()
    table.to_api_repr.return_value = {"tableId": "t"}
    bq_client_mock_fx.list_tables.return_value = iter([table])

    result = await sdk_client_fx.list_tables({"projectId": "p", "datasetId": "d"})

    assert result == [{"tableId": "t"}]
    bq_client_mock_fx.list_tables.assert_called_once_with("p.d")


@pytest.mark.asyncio
async def test_get_table_returns_metadata(
    sdk_client_fx: SdkBigQueryClient,
    bq_client_mock_fx: MagicMock,
) -> None:
    table = MagicMock()
    table.to_api_repr.return_value = {"tableId": "t"}
    bq_client_mock_fx.get_table.return_value = table

    result = await sdk_client_fx.get_table(
        {"projectId": "p", "datasetId": "d", "tableId": "t"},
    )

    assert result == {"tableId": "t"}


@pytest.mark.asyncio
async def test_reuses_bigquery_client_per_project(mock_auth_client_fx: MagicMock) -> None:
    mock_client = MagicMock()
    job = MagicMock()
    job.to_api_repr.return_value = {"id": "job-1"}
    mock_client.get_job.return_value = job

    with patch(
        "bq_inspect.bigquery.adapters.google_cloud.sdk_inspection_client.bigquery.Client",
        return_value=mock_client,
    ) as client_ctor:
        client = SdkBigQueryClient(mock_auth_client_fx)
        await client.get_job({"projectId": "p", "jobId": "a"})
        await client.get_job({"projectId": "p", "jobId": "b"})

    client_ctor.assert_called_once()
