"""Command ID to JSON Schema mapping."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

from bq_inspector.schemas.input_schema import (
    CATALOG_ENTRIES_LOOKUP_INPUT_SCHEMA,
    CATALOG_SEARCH_INPUT_SCHEMA,
    DATASETS_GET_INPUT_SCHEMA,
    JOBS_GET_INPUT_SCHEMA,
    JOBS_IMPACT_INPUT_SCHEMA,
    JOBS_LINEAGE_INPUT_SCHEMA,
    JOBS_LIST_INPUT_SCHEMA,
    JOBS_PERFORMANCE_INPUT_SCHEMA,
    JOBS_QUERY_INPUT_SCHEMA,
    JOBS_SUMMARY_INPUT_SCHEMA,
    LINEAGE_GRAPH_INPUT_SCHEMA,
    LINEAGE_LINKS_INPUT_SCHEMA,
    TABLES_GET_INPUT_SCHEMA,
    TABLES_LIST_INPUT_SCHEMA,
)
from bq_inspector.schemas.output_schema import (
    CATALOG_ENTRIES_LOOKUP_OUTPUT_SCHEMA,
    CATALOG_SEARCH_OUTPUT_SCHEMA,
    DATASET_TABLE_RESOURCE_OUTPUT_SCHEMA,
    JOBS_GET_OUTPUT_SCHEMA,
    JOBS_IMPACT_OUTPUT_SCHEMA,
    JOBS_LINEAGE_OUTPUT_SCHEMA,
    JOBS_LIST_OUTPUT_SCHEMA,
    JOBS_PERFORMANCE_OUTPUT_SCHEMA,
    JOBS_QUERY_OUTPUT_SCHEMA,
    JOBS_SUMMARY_OUTPUT_SCHEMA,
    LINEAGE_GRAPH_OUTPUT_SCHEMA,
    LINEAGE_LINKS_OUTPUT_SCHEMA,
    TABLES_LIST_OUTPUT_SCHEMA,
)

CommandId = Literal[
    "catalog aspect-types get",
    "catalog aspect-types list",
    "catalog entries get",
    "catalog entries list",
    "catalog entries lookup",
    "catalog entry-groups get",
    "catalog entry-groups list",
    "catalog entry-links get",
    "catalog entry-types get",
    "catalog entry-types list",
    "catalog glossaries get",
    "catalog glossaries list",
    "catalog glossary-categories get",
    "catalog glossary-categories list",
    "catalog glossary-terms get",
    "catalog glossary-terms list",
    "catalog search",
    "datasets get",
    "jobs get",
    "jobs impact",
    "jobs lineage",
    "jobs list",
    "jobs performance",
    "jobs query",
    "jobs summary",
    "lineage graph",
    "lineage links",
    "tables get",
    "tables list",
]

JobsViewCommandId = Literal[
    "jobs get",
    "jobs impact",
    "jobs lineage",
    "jobs performance",
    "jobs query",
    "jobs summary",
]

SchemaKind = Literal["input", "output"]

_BASE_COMMAND_SCHEMAS: dict[str, Any] = {
    "jobs get:input": JOBS_GET_INPUT_SCHEMA,
    "jobs get:output": JOBS_GET_OUTPUT_SCHEMA,
    "jobs summary:input": JOBS_SUMMARY_INPUT_SCHEMA,
    "jobs summary:output": JOBS_SUMMARY_OUTPUT_SCHEMA,
    "jobs query:input": JOBS_QUERY_INPUT_SCHEMA,
    "jobs query:output": JOBS_QUERY_OUTPUT_SCHEMA,
    "jobs performance:input": JOBS_PERFORMANCE_INPUT_SCHEMA,
    "jobs performance:output": JOBS_PERFORMANCE_OUTPUT_SCHEMA,
    "jobs lineage:input": JOBS_LINEAGE_INPUT_SCHEMA,
    "jobs lineage:output": JOBS_LINEAGE_OUTPUT_SCHEMA,
    "jobs impact:input": JOBS_IMPACT_INPUT_SCHEMA,
    "jobs impact:output": JOBS_IMPACT_OUTPUT_SCHEMA,
    "jobs list:input": JOBS_LIST_INPUT_SCHEMA,
    "jobs list:output": JOBS_LIST_OUTPUT_SCHEMA,
    "datasets get:input": DATASETS_GET_INPUT_SCHEMA,
    "datasets get:output": DATASET_TABLE_RESOURCE_OUTPUT_SCHEMA,
    "tables list:input": TABLES_LIST_INPUT_SCHEMA,
    "tables list:output": TABLES_LIST_OUTPUT_SCHEMA,
    "tables get:input": TABLES_GET_INPUT_SCHEMA,
    "tables get:output": DATASET_TABLE_RESOURCE_OUTPUT_SCHEMA,
    "lineage links:input": LINEAGE_LINKS_INPUT_SCHEMA,
    "lineage links:output": LINEAGE_LINKS_OUTPUT_SCHEMA,
    "lineage graph:input": LINEAGE_GRAPH_INPUT_SCHEMA,
    "lineage graph:output": LINEAGE_GRAPH_OUTPUT_SCHEMA,
    "catalog search:input": CATALOG_SEARCH_INPUT_SCHEMA,
    "catalog search:output": CATALOG_SEARCH_OUTPUT_SCHEMA,
    "catalog entries lookup:input": CATALOG_ENTRIES_LOOKUP_INPUT_SCHEMA,
    "catalog entries lookup:output": CATALOG_ENTRIES_LOOKUP_OUTPUT_SCHEMA,
}


@lru_cache(maxsize=1)
def _command_schemas() -> dict[str, Any]:
    from bq_inspector.schemas.knowledge_catalog_schemas import (  # noqa: PLC0415
        build_knowledge_catalog_command_schemas,
    )

    return {
        **_BASE_COMMAND_SCHEMAS,
        **build_knowledge_catalog_command_schemas(),
    }


def get_command_schema(command: CommandId, kind: SchemaKind) -> Any:
    """Return the input or output JSON Schema for a command."""
    key = f"{command}:{kind}"
    schema = _command_schemas().get(key)
    if schema is None:
        raise ValueError(f"Unhandled schema key: {key}")
    return schema
