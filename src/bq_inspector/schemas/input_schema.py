"""Input JSON schemas for bq-inspector commands."""

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
                "jobId": {
                    "type": "string",
                    "minLength": 1,
                    "description": (
                        "Job id, or full BigQuery job resource id "
                        "(project:location.jobId, e.g. my-proj:US.bquxjob_abc)."
                    ),
                },
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


JOBS_GET_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspector jobs get input")
JOBS_SUMMARY_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspector jobs summary input")
JOBS_QUERY_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspector jobs query input")
JOBS_PERFORMANCE_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspector jobs performance input")
JOBS_LINEAGE_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspector jobs lineage input")
JOBS_IMPACT_INPUT_SCHEMA = _make_jobs_view_input_schema("bq-inspector jobs impact input")

JOBS_LIST_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspector jobs list input",
    "type": "object",
    "required": ["projectId"],
    "additionalProperties": False,
    "properties": {
        "projectId": {"type": "string", "minLength": 1},
        "minCreationTime": {
            "type": "string",
            "format": "date-time",
            "description": (
                "Forwarded to jobs.list minCreationTime (API). Must include a timezone "
                "(Z or numeric offset, for example 2026-05-17T00:00:00Z)."
            ),
        },
        "maxCreationTime": {
            "type": "string",
            "format": "date-time",
            "description": (
                "Forwarded to jobs.list maxCreationTime (API). Must include a timezone "
                "(Z or numeric offset, for example 2026-05-18T00:00:00Z)."
            ),
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
    "title": "bq-inspector datasets get input",
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
    "title": "bq-inspector tables list input",
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
    "title": "bq-inspector tables get input",
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

_LINEAGE_BASE_PROPERTIES: dict[str, Any] = {
    "clientProjectId": {
        "type": "string",
        "minLength": 1,
        "description": (
            "Project used as the Data Lineage API parent for billing and quota. "
            "Defaults to projectId when omitted."
        ),
    },
    "location": {
        "type": "string",
        "minLength": 1,
        "description": (
            "Data Lineage API location (for example us, eu, or global). "
            "This is not the BigQuery dataset location."
        ),
    },
    "projectId": {"type": "string", "minLength": 1},
    "datasetId": {"type": "string", "minLength": 1},
    "tableId": {"type": "string", "minLength": 1},
    "direction": {
        "type": "string",
        "enum": ["UPSTREAM", "DOWNSTREAM"],
        "description": (
            "UPSTREAM finds immediate sources; DOWNSTREAM finds immediate destinations."
        ),
    },
    "impersonateServiceAccount": {"type": "string", "minLength": 1},
    "impersonateDelegates": {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
    },
}

LINEAGE_LINKS_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspector lineage links input",
    "type": "object",
    "required": ["location", "projectId", "datasetId", "tableId", "direction"],
    "additionalProperties": False,
    "properties": {
        **_LINEAGE_BASE_PROPERTIES,
        "pageSize": {"type": "integer", "minimum": 1, "maximum": 100},
        "pageToken": {"type": "string", "minLength": 1},
    },
}

LINEAGE_GRAPH_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspector lineage graph input",
    "type": "object",
    "required": ["location", "projectId", "datasetId", "tableId", "direction"],
    "additionalProperties": False,
    "properties": {
        **_LINEAGE_BASE_PROPERTIES,
        "maxDepth": {"type": "integer", "minimum": 1, "maximum": 100},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": 10000},
    },
}

_IMPERSONATION_PROPERTIES: dict[str, Any] = {
    "impersonateServiceAccount": {"type": "string", "minLength": 1},
    "impersonateDelegates": {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
    },
}

CATALOG_SEARCH_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspector catalog search input",
    "type": "object",
    "required": ["projectId", "query"],
    "additionalProperties": False,
    "properties": {
        "projectId": {
            "type": "string",
            "minLength": 1,
            "description": (
                "Project used for the Dataplex search request path, billing, quota, "
                "and dataplex.projects.search permission check."
            ),
        },
        "location": {
            "type": "string",
            "const": "global",
            "default": "global",
            "description": "Knowledge Catalog search location. P0 supports global search.",
        },
        "query": {
            "type": "string",
            "minLength": 1,
            "description": "Opaque Knowledge Catalog search query.",
        },
        "scope": {
            "type": "string",
            "minLength": 1,
            "description": "Optional search scope such as a project or organization resource.",
        },
        "semanticSearch": {
            "type": "boolean",
            "default": False,
            "description": "Enable natural-language semantic search explicitly.",
        },
        "orderBy": {
            "type": "string",
            "enum": ["relevance", "last_modified_timestamp", "last_modified_timestamp asc"],
        },
        "pageSize": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 50},
        "pageToken": {"type": "string", "minLength": 1},
        **_IMPERSONATION_PROPERTIES,
    },
}

_CATALOG_ENTRY_VIEW_PROPERTIES: dict[str, Any] = {
    "view": {
        "type": "string",
        "enum": ["BASIC", "FULL", "CUSTOM", "ALL"],
    },
    "aspectTypes": {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
    },
    "paths": {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
    },
}

CATALOG_ENTRIES_LOOKUP_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspector catalog entries lookup input",
    "type": "object",
    "required": ["projectId", "location", "entry"],
    "additionalProperties": False,
    "properties": {
        "projectId": {"type": "string", "minLength": 1},
        "location": {"type": "string", "minLength": 1},
        "entry": {"type": "string", "minLength": 1},
        **_CATALOG_ENTRY_VIEW_PROPERTIES,
        **_IMPERSONATION_PROPERTIES,
    },
}

CATALOG_GET_BY_NAME_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspector catalog get by name input",
    "type": "object",
    "required": ["name"],
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string", "minLength": 1},
        **_CATALOG_ENTRY_VIEW_PROPERTIES,
        **_IMPERSONATION_PROPERTIES,
    },
}

CATALOG_LIST_BY_PARENT_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT_2020_12,
    "title": "bq-inspector catalog list by parent input",
    "type": "object",
    "required": ["parent"],
    "additionalProperties": False,
    "properties": {
        "parent": {"type": "string", "minLength": 1},
        "pageSize": {"type": "integer", "minimum": 1},
        "pageToken": {"type": "string", "minLength": 1},
        "filter": {"type": "string", "minLength": 1},
        "orderBy": {"type": "string", "minLength": 1},
        **_IMPERSONATION_PROPERTIES,
    },
}
