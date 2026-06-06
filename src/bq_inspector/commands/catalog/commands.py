"""Knowledge Catalog CLI command registrations."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from bq_inspector.commands.catalog._shared import (
    create_catalog_get_command,
    create_catalog_list_command,
    create_catalog_lookup_command,
    create_catalog_search_command,
)
from bq_inspector.input.input_parsers import (
    parse_knowledge_catalog_get_input,
    parse_knowledge_catalog_list_input,
    parse_knowledge_catalog_lookup_input,
    parse_knowledge_catalog_search_input,
)
from bq_inspector.knowledge_catalog.resource_specs import (
    KNOWLEDGE_CATALOG_GET_RESOURCES,
    KNOWLEDGE_CATALOG_LIST_RESOURCES,
    KnowledgeCatalogGetCommandSpec,
    KnowledgeCatalogListCommandSpec,
    knowledge_catalog_command_id,
    knowledge_catalog_export_name,
)

if TYPE_CHECKING:
    from bq_inspector.commands.command_shared import ParamsCommandRunner
    from bq_inspector.input.parsed_input_types import (
        ParsedKnowledgeCatalogGetInput,
        ParsedKnowledgeCatalogListInput,
    )
    from bq_inspector.schemas.command_schemas import CommandId


def _build_get_command(spec: KnowledgeCatalogGetCommandSpec) -> ParamsCommandRunner:
    command_id = cast(
        "CommandId",
        knowledge_catalog_command_id(spec.subgroup, "get"),
    )

    def parse(raw: object) -> ParsedKnowledgeCatalogGetInput:
        return parse_knowledge_catalog_get_input(command_id, raw)

    return create_catalog_get_command(
        command_id,
        parse,
        dispatch=spec.dispatch,
    )


def _build_list_command(spec: KnowledgeCatalogListCommandSpec) -> ParamsCommandRunner:
    command_id = cast(
        "CommandId",
        knowledge_catalog_command_id(spec.subgroup, "list"),
    )

    def parse(raw: object) -> ParsedKnowledgeCatalogListInput:
        return parse_knowledge_catalog_list_input(command_id, raw)

    return create_catalog_list_command(
        command_id,
        parse,
        collection_key=spec.collection_key,
        dispatch=spec.dispatch,
    )


catalog_search_command = create_catalog_search_command(
    "catalog search",
    parse_knowledge_catalog_search_input,
)

catalog_entries_lookup_command = create_catalog_lookup_command(
    "catalog entries lookup",
    parse_knowledge_catalog_lookup_input,
)


def build_knowledge_catalog_command_runners() -> dict[str, ParamsCommandRunner]:
    """Build get/list command runners keyed by export name."""
    runners: dict[str, ParamsCommandRunner] = {}

    for get_spec in KNOWLEDGE_CATALOG_GET_RESOURCES:
        runners[knowledge_catalog_export_name(get_spec.subgroup, "get")] = _build_get_command(
            get_spec
        )

    for list_spec in KNOWLEDGE_CATALOG_LIST_RESOURCES:
        runners[knowledge_catalog_export_name(list_spec.subgroup, "list")] = _build_list_command(
            list_spec
        )

    return runners
