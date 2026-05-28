"""BigQuery jobs.list request and page types."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class ListJobsRequest(TypedDict):
    projectId: str
    allUsers: NotRequired[bool]
    minCreationTime: NotRequired[int]
    maxCreationTime: NotRequired[int]
    pageToken: NotRequired[str]
    maxResults: NotRequired[int]
    state: NotRequired[str]
    parentJobId: NotRequired[str]


class ListJobsPage(TypedDict, total=False):
    jobs: list[object]
    nextPageToken: str
