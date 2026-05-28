"""Shared types for bq-inspect responses and requests."""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

BqInspectSchemaVersion = Literal["bq-inspect.v1"]

JobView = Literal["full", "impact", "lineage", "performance", "query", "summary"]

BqInspectErrorCode = Literal[
    "BQINSPECT_API_RATE_LIMITED",
    "BQINSPECT_API_UNAVAILABLE",
    "BQINSPECT_INPUT_INVALID",
    "BQINSPECT_INTERNAL",
    "BQINSPECT_JOB_NOT_FOUND",
    "BQINSPECT_LOCATION_REQUIRED",
    "BQINSPECT_PERMISSION_DENIED",
]


class JobRef(TypedDict):
    projectId: str
    jobId: str
    location: NotRequired[str]


class SchemaError(TypedDict):
    path: str
    message: str


class BqInspectErrorSource(TypedDict, total=False):
    api: str
    status: int
    schemaErrors: list[SchemaError]


class BqInspectError(TypedDict):
    code: BqInspectErrorCode
    message: str
    retriable: bool
    hint: NotRequired[str]
    source: NotRequired[BqInspectErrorSource]


class BqInspectWarning(TypedDict, total=False):
    code: str
    message: str
    path: str


class ToolBlock(TypedDict):
    name: Literal["bq-inspect"]
    version: str
    readOnly: Literal[True]


class InspectJobRequest(TypedDict):
    jobs: list[JobRef]
    view: NotRequired[JobView]
    schemaVersion: NotRequired[BqInspectSchemaVersion]
    impersonateServiceAccount: NotRequired[str]
    impersonateDelegates: NotRequired[list[str]]


class JobSource(TypedDict):
    api: Literal["bigquery.jobs.get"]
    fetchedAt: str


class InspectedJob(TypedDict, total=False):
    jobRef: JobRef
    source: JobSource
    job: object
    warnings: list[BqInspectWarning]
    errors: list[BqInspectError]


class InspectJobResponseRequest(TypedDict):
    jobs: list[JobRef]
    view: JobView
    impersonateServiceAccount: NotRequired[str]
    impersonateDelegates: NotRequired[list[str]]


class InspectJobResponse(TypedDict):
    schemaVersion: BqInspectSchemaVersion
    tool: ToolBlock
    request: InspectJobResponseRequest
    jobs: list[InspectedJob]
    warnings: list[BqInspectWarning]
    errors: list[BqInspectError]


class JobListFiltersEcho(TypedDict, total=False):
    minSlotMs: str
    minBytesBilled: str
    labels: dict[str, str]


class ListJobsResponseRequest(TypedDict):
    projectId: str
    filters: JobListFiltersEcho
    allUsers: NotRequired[bool]
    minCreationTime: NotRequired[int]
    maxCreationTime: NotRequired[int]
    pageToken: NotRequired[str]
    maxResults: NotRequired[int]
    state: NotRequired[str]
    parentJobId: NotRequired[str]
    impersonateServiceAccount: NotRequired[str]
    impersonateDelegates: NotRequired[list[str]]


class ListJobsPageBlock(TypedDict, total=False):
    nextPageToken: str


class ToolEnvelope(TypedDict):
    schemaVersion: BqInspectSchemaVersion
    tool: ToolBlock


class ListJobsResponse(TypedDict):
    schemaVersion: BqInspectSchemaVersion
    tool: ToolBlock
    request: ListJobsResponseRequest
    jobs: list[object]
    page: ListJobsPageBlock
    warnings: list[BqInspectWarning]
    errors: list[BqInspectError]


class CatalogResourceResponse(TypedDict):
    schemaVersion: BqInspectSchemaVersion
    tool: ToolBlock
    request: dict[str, str]
    warnings: list[BqInspectWarning]
    errors: list[BqInspectError]
    resource: NotRequired[object]


class TablesListResponse(TypedDict):
    schemaVersion: BqInspectSchemaVersion
    tool: ToolBlock
    request: dict[str, str]
    tables: list[object]
    warnings: list[BqInspectWarning]
    errors: list[BqInspectError]
