"""Knowledge Catalog command JSON schemas derived from resource specs."""

from __future__ import annotations

from typing import Any

from bq_inspector.commands.catalog.resource_specs import (
    KNOWLEDGE_CATALOG_GET_RESOURCES,
    KNOWLEDGE_CATALOG_LIST_RESOURCES,
)
from bq_inspector.schemas.input_schema import (
    _IMPERSONATION_PROPERTIES,
    CATALOG_GET_BY_NAME_INPUT_SCHEMA,
    CATALOG_LIST_BY_PARENT_INPUT_SCHEMA,
    JSON_SCHEMA_DRAFT_2020_12,
)
from bq_inspector.schemas.output_schema import (
    make_catalog_list_output_schema,
    make_catalog_resource_output_schema,
)


def make_knowledge_catalog_get_input_schema(
    subgroup: str,
    *,
    include_entry_view: bool,
) -> dict[str, Any]:
    """Build a get-by-name Knowledge Catalog input schema."""
    title = f"bq-inspector catalog {subgroup} get input"
    if include_entry_view:
        return {
            **CATALOG_GET_BY_NAME_INPUT_SCHEMA,
            "title": title,
        }
    return {
        **{key: value for key, value in CATALOG_GET_BY_NAME_INPUT_SCHEMA.items() if key != "title"},
        "$schema": JSON_SCHEMA_DRAFT_2020_12,
        "title": title,
        "type": "object",
        "required": ["name"],
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string", "minLength": 1},
            **_IMPERSONATION_PROPERTIES,
        },
    }


def make_knowledge_catalog_list_input_schema(subgroup: str) -> dict[str, Any]:
    """Build a list-by-parent Knowledge Catalog input schema."""
    return {
        **CATALOG_LIST_BY_PARENT_INPUT_SCHEMA,
        "title": f"bq-inspector catalog {subgroup} list input",
    }


def build_knowledge_catalog_command_schemas() -> dict[str, Any]:
    """Return input and output JSON schemas for Knowledge Catalog get/list commands."""
    schemas: dict[str, Any] = {}
    for spec in KNOWLEDGE_CATALOG_GET_RESOURCES:
        command_id = f"catalog {spec.subgroup} get"
        schemas[f"{command_id}:input"] = make_knowledge_catalog_get_input_schema(
            spec.subgroup,
            include_entry_view=spec.apply_entry_view,
        )
        schemas[f"{command_id}:output"] = make_catalog_resource_output_schema(
            f"bq-inspector catalog {spec.subgroup} get output"
        )
    for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES:
        command_id = f"catalog {spec.subgroup} list"
        schemas[f"{command_id}:input"] = make_knowledge_catalog_list_input_schema(spec.subgroup)
        schemas[f"{command_id}:output"] = make_catalog_list_output_schema(
            f"bq-inspector catalog {spec.subgroup} list output",
            spec.collection_key,
        )
    return schemas
