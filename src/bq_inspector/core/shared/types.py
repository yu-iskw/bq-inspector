"""Shared types for bq-inspector responses and requests."""

from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import NotRequired

BqInspectSchemaVersion = Literal["bq-inspector.v1"]

JobView = Literal["full", "impact", "lineage", "performance", "query", "summary"]

BqInspectErrorCode = Literal[
    "BQINSPECTOR_API_RATE_LIMITED",
    "BQINSPECTOR_API_UNAVAILABLE",
    "BQINSPECTOR_INPUT_INVALID",
    "BQINSPECTOR_INTERNAL",
    "BQINSPECTOR_JOB_NOT_FOUND",
    "BQINSPECTOR_LOCATION_REQUIRED",
    "BQINSPECTOR_PERMISSION_DENIED",
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
    name: Literal["bq-inspector"]
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


class LineageRequestEcho(TypedDict, total=False):
    """Echo of asset-lineage command params in API responses."""

    clientProjectId: str
    location: str
    projectId: str
    datasetId: str
    tableId: str
    direction: str
    fullyQualifiedName: str
    pageSize: int
    pageToken: str
    maxDepth: int
    maxResults: int


class LineageLinksPageBlock(TypedDict, total=False):
    nextPageToken: str


class LineageLinkDict(TypedDict, total=False):
    """REST-shaped Data Lineage link entry."""

    source: dict[str, object]
    target: dict[str, object]
    depth: int


class LineageLinksResponse(TypedDict):
    schemaVersion: BqInspectSchemaVersion
    tool: ToolBlock
    request: LineageRequestEcho
    links: list[dict[str, object]]
    page: LineageLinksPageBlock
    warnings: list[BqInspectWarning]
    errors: list[BqInspectError]


class LineageGraphResponse(TypedDict):
    schemaVersion: BqInspectSchemaVersion
    tool: ToolBlock
    request: LineageRequestEcho
    links: list[dict[str, object]]
    unreachable: list[str]
    warnings: list[BqInspectWarning]
    errors: list[BqInspectError]
