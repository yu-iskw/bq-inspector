"""BigQuery resource reference types."""

from __future__ import annotations

from typing import TypedDict


class DatasetRef(TypedDict):
    projectId: str
    datasetId: str


class TableRef(DatasetRef):
    tableId: str
