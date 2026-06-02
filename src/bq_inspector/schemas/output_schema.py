"""Output JSON schemas for bq-inspector commands."""

from __future__ import annotations

from typing import Any, Literal

TOOL_BLOCK: dict[str, Any] = {
    "type": "object",
    "required": ["name", "version", "readOnly"],
    "additionalProperties": False,
    "properties": {
        "name": {"const": "bq-inspector"},
        "version": {"type": "string", "minLength": 1},
        "readOnly": {"const": True},
    },
}

SCHEMA_VERSION_FIELD: dict[str, Any] = {"const": "bq-inspector.v1"}

JobViewConst = Literal["full", "impact", "lineage", "performance", "query", "summary"]


def _make_jobs_view_output_schema(view: JobViewConst, title: str) -> dict[str, Any]:
    return {
        "title": title,
        "type": "object",
        "required": ["schemaVersion", "tool", "request", "jobs", "warnings", "errors"],
        "additionalProperties": False,
        "properties": {
            "schemaVersion": SCHEMA_VERSION_FIELD,
            "tool": TOOL_BLOCK,
            "request": {
                "type": "object",
                "required": ["jobs", "view"],
                "additionalProperties": False,
                "properties": {
                    "jobs": {"type": "array"},
                    "view": {"const": view},
                    "impersonateServiceAccount": {"type": "string", "minLength": 1},
                    "impersonateDelegates": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                    },
                },
            },
            "jobs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["jobRef", "source", "warnings", "errors"],
                    "additionalProperties": False,
                    "properties": {
                        "jobRef": {"type": "object"},
                        "source": {
                            "type": "object",
                            "required": ["api", "fetchedAt"],
                            "additionalProperties": False,
                            "properties": {
                                "api": {"const": "bigquery.jobs.get"},
                                "fetchedAt": {"type": "string", "minLength": 1},
                            },
                        },
                        "job": True,
                        "warnings": {"type": "array"},
                        "errors": {"type": "array"},
                    },
                },
            },
            "warnings": {"type": "array"},
            "errors": {"type": "array"},
        },
    }


JOBS_GET_OUTPUT_SCHEMA = _make_jobs_view_output_schema("full", "bq-inspector jobs get output")
JOBS_SUMMARY_OUTPUT_SCHEMA = _make_jobs_view_output_schema(
    "summary", "bq-inspector jobs summary output"
)
JOBS_QUERY_OUTPUT_SCHEMA = _make_jobs_view_output_schema("query", "bq-inspector jobs query output")
JOBS_PERFORMANCE_OUTPUT_SCHEMA = _make_jobs_view_output_schema(
    "performance", "bq-inspector jobs performance output"
)
JOBS_LINEAGE_OUTPUT_SCHEMA = _make_jobs_view_output_schema(
    "lineage", "bq-inspector jobs lineage output"
)
JOBS_IMPACT_OUTPUT_SCHEMA = _make_jobs_view_output_schema(
    "impact", "bq-inspector jobs impact output"
)

JOBS_LIST_OUTPUT_SCHEMA: dict[str, Any] = {
    "title": "bq-inspector jobs list output",
    "type": "object",
    "required": ["schemaVersion", "tool", "request", "jobs", "page", "warnings", "errors"],
    "additionalProperties": False,
    "properties": {
        "schemaVersion": SCHEMA_VERSION_FIELD,
        "tool": TOOL_BLOCK,
        "request": {
            "type": "object",
            "required": ["projectId", "filters"],
            "additionalProperties": True,
            "properties": {
                "projectId": {"type": "string", "minLength": 1},
                "allUsers": {"type": "boolean"},
                "minCreationTime": {"type": "number"},
                "maxCreationTime": {"type": "number"},
                "pageToken": {"type": "string"},
                "maxResults": {"type": "number"},
                "state": {"type": "string", "minLength": 1},
                "parentJobId": {"type": "string", "minLength": 1},
                "filters": {"type": "object"},
                "impersonateServiceAccount": {"type": "string", "minLength": 1},
                "impersonateDelegates": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                },
            },
        },
        "jobs": {"type": "array"},
        "page": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "nextPageToken": {"type": "string"},
            },
        },
        "warnings": {"type": "array"},
        "errors": {"type": "array"},
    },
}

CATALOG_RESOURCE_OUTPUT_SCHEMA: dict[str, Any] = {
    "title": "bq-inspector catalog resource output",
    "type": "object",
    "required": ["schemaVersion", "tool", "request", "warnings", "errors"],
    "additionalProperties": False,
    "properties": {
        "schemaVersion": SCHEMA_VERSION_FIELD,
        "tool": TOOL_BLOCK,
        "request": {
            "type": "object",
            "required": ["projectId", "datasetId"],
            "additionalProperties": True,
            "properties": {
                "projectId": {"type": "string", "minLength": 1},
                "datasetId": {"type": "string", "minLength": 1},
                "tableId": {"type": "string", "minLength": 1},
            },
        },
        "resource": True,
        "warnings": {"type": "array"},
        "errors": {"type": "array"},
    },
}

TABLES_LIST_OUTPUT_SCHEMA: dict[str, Any] = {
    "title": "bq-inspector tables list output",
    "type": "object",
    "required": ["schemaVersion", "tool", "request", "tables", "warnings", "errors"],
    "additionalProperties": False,
    "properties": {
        "schemaVersion": SCHEMA_VERSION_FIELD,
        "tool": TOOL_BLOCK,
        "request": {
            "type": "object",
            "required": ["projectId", "datasetId"],
            "additionalProperties": False,
            "properties": {
                "projectId": {"type": "string", "minLength": 1},
                "datasetId": {"type": "string", "minLength": 1},
            },
        },
        "tables": {"type": "array"},
        "warnings": {"type": "array"},
        "errors": {"type": "array"},
    },
}

OUTPUT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "bq-inspector command output (union)",
    "oneOf": [
        JOBS_GET_OUTPUT_SCHEMA,
        JOBS_SUMMARY_OUTPUT_SCHEMA,
        JOBS_QUERY_OUTPUT_SCHEMA,
        JOBS_PERFORMANCE_OUTPUT_SCHEMA,
        JOBS_LINEAGE_OUTPUT_SCHEMA,
        JOBS_IMPACT_OUTPUT_SCHEMA,
        JOBS_LIST_OUTPUT_SCHEMA,
        CATALOG_RESOURCE_OUTPUT_SCHEMA,
        TABLES_LIST_OUTPUT_SCHEMA,
    ],
}
