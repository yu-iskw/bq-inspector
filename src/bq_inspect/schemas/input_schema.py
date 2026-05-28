"""Input JSON schemas for bq-inspect commands."""

from __future__ import annotations

from typing import Any

JSON_SCHEMA_DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"

JOBS_VIEW_INPUT_PROPERTIES: dict[str, Any] = {
    "jobs": {
        "type": "array",
        "minItems": 1,
        "items": {
            "type": "object",
            "required": ["projectId", "jobId"],
            "additionalProperties": False,
            "properties": {
                "projectId": {"type": "string", "minLength": 1},
                "location": {
                    "type": "string",
                    "minLength": 1,
                    "description": (
                        "BigQuery location for the job (for example US, EU, or "
                        "asia-northeast1). Required in practice for regional jobs; copy "
                        "from jobs.list jobReference.location. Omitting location often "
                        "yields 403 on jobs.get."
                    ),
                },
                "jobId": {"type": "string", "minLength": 1},
            },
        },
    },
    "impersonateServiceAccount": {"type": "string", "minLength": 1},
    "impersonateDelegates": {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
    },
}


def _make_jobs_view_input_schema(title: str) -> dict[str, Any]:
    return {
        "$schema": JSON_SCHEMA_DRAFT_2020_12,
        "title": title,
        "type": "object",
        "required": ["jobs"],
        "additionalProperties": False,
        "properties": JOBS_VIEW_INPUT_PROPERTIES,
    }


JOBS_GET_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspect jobs get input")
JOBS_SUMMARY_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspect jobs summary input")
JOBS_QUERY_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspect jobs query input")
JOBS_PERFORMANCE_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspect jobs performance input")
JOBS_LINEAGE_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspect jobs lineage input")
JOBS_IMPACT_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspect jobs impact input")

JOBS_LIST_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspect jobs list input",
    "type": "object",
    "required": ["projectId"],
    "additionalProperties": False,
    "properties": {
        "projectId": {"type": "string", "minLength": 1},
        "minCreationTime": {
            "type": "string",
            "format": "date-time",
            "description": "Forwarded to jobs.list minCreationTime (API).",
        },
        "maxCreationTime": {
            "type": "string",
            "format": "date-time",
            "description": "Forwarded to jobs.list maxCreationTime (API).",
        },
        "pageToken": {
            "type": "string",
            "minLength": 1,
            "description": "Forwarded to jobs.list pageToken (API).",
        },
        "maxResults": {
            "type": "integer",
            "minimum": 1,
            "description": "Forwarded to jobs.list maxResults (API).",
        },
        "allUsers": {
            "type": "boolean",
            "description": (
                "Forwarded to jobs.list allUsers (API). When true, list jobs from all "
                "users in the project. In shared sandboxes, omitting this often returns "
                "an empty list even when jobs exist."
            ),
        },
        "state": {
            "type": "string",
            "minLength": 1,
            "description": "Forwarded to jobs.list stateFilter (API): DONE, PENDING, or RUNNING.",
        },
        "parentJobId": {
            "type": "string",
            "minLength": 1,
            "description": "Forwarded to jobs.list parentJobId (API): list child jobs of this parent.",
        },
        "minSlotMs": {
            "type": "string",
            "pattern": "^[0-9]+$",
            "description": (
                "Post-list filter: minimum totalSlotMs on the current page only; "
                "paginate with pageToken if needed."
            ),
        },
        "minBytesBilled": {
            "type": "string",
            "pattern": "^[0-9]+$",
            "description": (
                "Post-list filter: minimum totalBytesBilled on the current page only; "
                "paginate with pageToken if needed."
            ),
        },
        "labels": {
            "type": "object",
            "additionalProperties": {"type": "string"},
            "description": (
                "Post-list filter: job labels must match on the current page only; "
                "paginate with pageToken if needed."
            ),
        },
        "impersonateServiceAccount": {"type": "string", "minLength": 1},
        "impersonateDelegates": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
    },
}

DATASETS_GET_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspect datasets get input",
    "type": "object",
    "required": ["projectId", "datasetId"],
    "additionalProperties": False,
    "properties": {
        "projectId": {"type": "string", "minLength": 1},
        "datasetId": {"type": "string", "minLength": 1},
        "impersonateServiceAccount": {"type": "string", "minLength": 1},
        "impersonateDelegates": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
    },
}

TABLES_LIST_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspect tables list input",
    "type": "object",
    "required": ["projectId", "datasetId"],
    "additionalProperties": False,
    "properties": {
        "projectId": {"type": "string", "minLength": 1},
        "datasetId": {"type": "string", "minLength": 1},
        "impersonateServiceAccount": {"type": "string", "minLength": 1},
        "impersonateDelegates": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
    },
}

TABLES_GET_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspect tables get input",
    "type": "object",
    "required": ["projectId", "datasetId", "tableId"],
    "additionalProperties": False,
    "properties": {
        "projectId": {"type": "string", "minLength": 1},
        "datasetId": {"type": "string", "minLength": 1},
        "tableId": {"type": "string", "minLength": 1},
        "impersonateServiceAccount": {"type": "string", "minLength": 1},
        "impersonateDelegates": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
    },
}
