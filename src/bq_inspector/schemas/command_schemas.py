"""Command ID to JSON Schema mapping."""

from __future__ import annotations

from typing import Any, Literal

from bq_inspector.schemas.input_schema import (
    DATASETS_GET_INPUT_SCHEMA,
    JOBS_GET_INPUT_SCHEMA,
    JOBS_IMPACT_INPUT_SCHEMA,
    JOBS_LINEAGE_INPUT_SCHEMA,
    JOBS_LIST_INPUT_SCHEMA,
    JOBS_PERFORMANCE_INPUT_SCHEMA,
    JOBS_QUERY_INPUT_SCHEMA,
    JOBS_SUMMARY_INPUT_SCHEMA,
    TABLES_GET_INPUT_SCHEMA,
    TABLES_LIST_INPUT_SCHEMA,
)
from bq_inspector.schemas.output_schema import (
    CATALOG_RESOURCE_OUTPUT_SCHEMA,
    JOBS_GET_OUTPUT_SCHEMA,
    JOBS_IMPACT_OUTPUT_SCHEMA,
    JOBS_LINEAGE_OUTPUT_SCHEMA,
    JOBS_LIST_OUTPUT_SCHEMA,
    JOBS_PERFORMANCE_OUTPUT_SCHEMA,
    JOBS_QUERY_OUTPUT_SCHEMA,
    JOBS_SUMMARY_OUTPUT_SCHEMA,
    TABLES_LIST_OUTPUT_SCHEMA,
)

CommandId = Literal[
    "datasets get",
    "jobs get",
    "jobs impact",
    "jobs lineage",
    "jobs list",
    "jobs performance",
    "jobs query",
    "jobs summary",
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

_COMMAND_SCHEMAS: dict[str, Any] = {
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
    "datasets get:output": CATALOG_RESOURCE_OUTPUT_SCHEMA,
    "tables list:input": TABLES_LIST_INPUT_SCHEMA,
    "tables list:output": TABLES_LIST_OUTPUT_SCHEMA,
    "tables get:input": TABLES_GET_INPUT_SCHEMA,
    "tables get:output": CATALOG_RESOURCE_OUTPUT_SCHEMA,
}


def get_command_schema(command: CommandId, kind: SchemaKind) -> Any:
    """Return the input or output JSON Schema for a command."""
    key = f"{command}:{kind}"
    schema = _COMMAND_SCHEMAS.get(key)
    if schema is None:
        raise ValueError(f"Unhandled schema key: {key}")
    return schema
