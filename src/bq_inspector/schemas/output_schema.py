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

_LINEAGE_REQUEST_PROPERTIES: dict[str, Any] = {
    "clientProjectId": {"type": "string", "minLength": 1},
    "location": {"type": "string", "minLength": 1},
    "projectId": {"type": "string", "minLength": 1},
    "datasetId": {"type": "string", "minLength": 1},
    "tableId": {"type": "string", "minLength": 1},
    "direction": {"type": "string", "enum": ["UPSTREAM", "DOWNSTREAM"]},
    "fullyQualifiedName": {"type": "string", "minLength": 1},
}

LINEAGE_LINKS_OUTPUT_SCHEMA: dict[str, Any] = {
    "title": "bq-inspector lineage links output",
    "type": "object",
    "required": ["schemaVersion", "tool", "request", "links", "page", "warnings", "errors"],
    "additionalProperties": False,
    "properties": {
        "schemaVersion": SCHEMA_VERSION_FIELD,
        "tool": TOOL_BLOCK,
        "request": {
            "type": "object",
            "required": [
                "clientProjectId",
                "location",
                "projectId",
                "datasetId",
                "tableId",
                "direction",
                "fullyQualifiedName",
            ],
            "additionalProperties": True,
            "properties": _LINEAGE_REQUEST_PROPERTIES,
        },
        "links": {"type": "array"},
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


def make_catalog_resource_output_schema(title: str) -> dict[str, Any]:
    """Build a Knowledge Catalog get/lookup output schema."""
    return {
        "title": title,
        "type": "object",
        "required": ["schemaVersion", "tool", "request", "resource", "warnings", "errors"],
        "additionalProperties": False,
        "properties": {
            "schemaVersion": SCHEMA_VERSION_FIELD,
            "tool": TOOL_BLOCK,
            "request": {"type": "object", "additionalProperties": True},
            "resource": True,
            "warnings": {"type": "array"},
            "errors": {"type": "array"},
        },
    }


def make_catalog_list_output_schema(title: str, collection_key: str) -> dict[str, Any]:
    """Build a Knowledge Catalog list output schema."""
    return {
        "title": title,
        "type": "object",
        "required": [
            "schemaVersion",
            "tool",
            "request",
            collection_key,
            "page",
            "warnings",
            "errors",
        ],
        "additionalProperties": False,
        "properties": {
            "schemaVersion": SCHEMA_VERSION_FIELD,
            "tool": TOOL_BLOCK,
            "request": {"type": "object", "additionalProperties": True},
            collection_key: {"type": "array"},
            "page": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nextPageToken": {"type": "string"},
                    "totalSize": {"type": "integer"},
                    "unreachable": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
            "warnings": {"type": "array"},
            "errors": {"type": "array"},
        },
    }


CATALOG_SEARCH_OUTPUT_SCHEMA: dict[str, Any] = {
    "title": "bq-inspector catalog search output",
    "type": "object",
    "required": ["schemaVersion", "tool", "request", "entries", "page", "warnings", "errors"],
    "additionalProperties": False,
    "properties": {
        "schemaVersion": SCHEMA_VERSION_FIELD,
        "tool": TOOL_BLOCK,
        "request": {"type": "object", "additionalProperties": True},
        "entries": {"type": "array"},
        "page": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "totalSize": {"type": "integer"},
                "nextPageToken": {"type": "string"},
                "unreachable": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
        "warnings": {"type": "array"},
        "errors": {"type": "array"},
    },
}

CATALOG_ENTRIES_LOOKUP_OUTPUT_SCHEMA = make_catalog_resource_output_schema(
    "bq-inspector catalog entries lookup output"
)
CATALOG_ENTRIES_GET_OUTPUT_SCHEMA = make_catalog_resource_output_schema(
    "bq-inspector catalog entries get output"
)
CATALOG_ENTRIES_LIST_OUTPUT_SCHEMA = make_catalog_list_output_schema(
    "bq-inspector catalog entries list output",
    "entries",
)
CATALOG_ENTRY_GROUPS_GET_OUTPUT_SCHEMA = make_catalog_resource_output_schema(
    "bq-inspector catalog entry-groups get output"
)
CATALOG_ENTRY_GROUPS_LIST_OUTPUT_SCHEMA = make_catalog_list_output_schema(
    "bq-inspector catalog entry-groups list output",
    "entryGroups",
)
CATALOG_ENTRY_TYPES_GET_OUTPUT_SCHEMA = make_catalog_resource_output_schema(
    "bq-inspector catalog entry-types get output"
)
CATALOG_ENTRY_TYPES_LIST_OUTPUT_SCHEMA = make_catalog_list_output_schema(
    "bq-inspector catalog entry-types list output",
    "entryTypes",
)
CATALOG_ASPECT_TYPES_GET_OUTPUT_SCHEMA = make_catalog_resource_output_schema(
    "bq-inspector catalog aspect-types get output"
)
CATALOG_ASPECT_TYPES_LIST_OUTPUT_SCHEMA = make_catalog_list_output_schema(
    "bq-inspector catalog aspect-types list output",
    "aspectTypes",
)
CATALOG_ENTRY_LINKS_GET_OUTPUT_SCHEMA = make_catalog_resource_output_schema(
    "bq-inspector catalog entry-links get output"
)
CATALOG_GLOSSARIES_GET_OUTPUT_SCHEMA = make_catalog_resource_output_schema(
    "bq-inspector catalog glossaries get output"
)
CATALOG_GLOSSARIES_LIST_OUTPUT_SCHEMA = make_catalog_list_output_schema(
    "bq-inspector catalog glossaries list output",
    "glossaries",
)
CATALOG_GLOSSARY_CATEGORIES_GET_OUTPUT_SCHEMA = make_catalog_resource_output_schema(
    "bq-inspector catalog glossary-categories get output"
)
CATALOG_GLOSSARY_CATEGORIES_LIST_OUTPUT_SCHEMA = make_catalog_list_output_schema(
    "bq-inspector catalog glossary-categories list output",
    "categories",
)
CATALOG_GLOSSARY_TERMS_GET_OUTPUT_SCHEMA = make_catalog_resource_output_schema(
    "bq-inspector catalog glossary-terms get output"
)
CATALOG_GLOSSARY_TERMS_LIST_OUTPUT_SCHEMA = make_catalog_list_output_schema(
    "bq-inspector catalog glossary-terms list output",
    "terms",
)

LINEAGE_GRAPH_OUTPUT_SCHEMA: dict[str, Any] = {
    "title": "bq-inspector lineage graph output",
    "type": "object",
    "required": [
        "schemaVersion",
        "tool",
        "request",
        "links",
        "unreachable",
        "warnings",
        "errors",
    ],
    "additionalProperties": False,
    "properties": {
        "schemaVersion": SCHEMA_VERSION_FIELD,
        "tool": TOOL_BLOCK,
        "request": {
            "type": "object",
            "required": [
                "clientProjectId",
                "location",
                "projectId",
                "datasetId",
                "tableId",
                "direction",
                "fullyQualifiedName",
            ],
            "additionalProperties": True,
            "properties": {
                **_LINEAGE_REQUEST_PROPERTIES,
                "maxDepth": {"type": "integer"},
                "maxResults": {"type": "integer"},
            },
        },
        "links": {"type": "array"},
        "unreachable": {
            "type": "array",
            "items": {"type": "string"},
        },
        "warnings": {"type": "array"},
        "errors": {"type": "array"},
    },
}
