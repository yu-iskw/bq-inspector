"""Validate and map CLI params to typed command input."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.input.map_input import (
    map_catalog_input,
    map_jobs_list_input,
    map_jobs_view_input,
    map_lineage_graph_input,
    map_lineage_input,
)
from bq_inspector.input.map_knowledge_catalog_input import (
    map_knowledge_catalog_get_input,
    map_knowledge_catalog_list_input,
    map_knowledge_catalog_lookup_input,
    map_knowledge_catalog_search_input,
)
from bq_inspector.schemas.command_schemas import CommandId, JobsViewCommandId
from bq_inspector.schemas.validate_input import validate_input

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import (
        ParsedCatalogInput,
        ParsedJobsListInput,
        ParsedJobsViewInput,
        ParsedKnowledgeCatalogGetInput,
        ParsedKnowledgeCatalogListInput,
        ParsedKnowledgeCatalogLookupInput,
        ParsedKnowledgeCatalogSearchInput,
        ParsedLineageGraphInput,
        ParsedLineageInput,
    )

CatalogCommandId = CommandId


def _parse_catalog_input(command_id: CatalogCommandId, raw: Any) -> ParsedCatalogInput:
    return map_catalog_input(validate_input(command_id, raw))


def _parse_jobs_view_input(command_id: JobsViewCommandId, raw: Any) -> ParsedJobsViewInput:
    return map_jobs_view_input(validate_input(command_id, raw))


def parse_jobs_get_input(raw: Any) -> ParsedJobsViewInput:
    """Parse jobs get params."""
    return _parse_jobs_view_input("jobs get", raw)


def parse_jobs_view_input_for_command(
    command_id: JobsViewCommandId,
    raw: Any,
) -> ParsedJobsViewInput:
    """Parse jobs view params for a specific view command."""
    return _parse_jobs_view_input(command_id, raw)


def parse_jobs_list_input(raw: Any) -> ParsedJobsListInput:
    """Parse jobs list params."""
    return map_jobs_list_input(validate_input("jobs list", raw))


def parse_datasets_get_input(raw: Any) -> ParsedCatalogInput:
    """Parse datasets get params."""
    return _parse_catalog_input("datasets get", raw)


def parse_tables_list_input(raw: Any) -> ParsedCatalogInput:
    """Parse tables list params."""
    return _parse_catalog_input("tables list", raw)


def parse_tables_get_input(raw: Any) -> ParsedCatalogInput:
    """Parse tables get params."""
    return _parse_catalog_input("tables get", raw)


def parse_lineage_links_input(raw: Any) -> ParsedLineageInput:
    """Parse lineage links params."""
    return map_lineage_input(validate_input("lineage links", raw))


def parse_lineage_graph_input(raw: Any) -> ParsedLineageGraphInput:
    """Parse lineage graph params."""
    return map_lineage_graph_input(validate_input("lineage graph", raw))


def _parse_knowledge_catalog_search(raw: Any) -> ParsedKnowledgeCatalogSearchInput:
    return map_knowledge_catalog_search_input(validate_input("catalog search", raw))


def _parse_knowledge_catalog_lookup(raw: Any) -> ParsedKnowledgeCatalogLookupInput:
    return map_knowledge_catalog_lookup_input(validate_input("catalog entries lookup", raw))


def _parse_knowledge_catalog_get(
    command_id: CommandId,
    raw: Any,
) -> ParsedKnowledgeCatalogGetInput:
    return map_knowledge_catalog_get_input(validate_input(command_id, raw))


def _parse_knowledge_catalog_list(
    command_id: CommandId,
    raw: Any,
) -> ParsedKnowledgeCatalogListInput:
    return map_knowledge_catalog_list_input(validate_input(command_id, raw))


def parse_catalog_search_input(raw: Any) -> ParsedKnowledgeCatalogSearchInput:
    """Parse catalog search params."""
    return _parse_knowledge_catalog_search(raw)


def parse_catalog_entries_lookup_input(raw: Any) -> ParsedKnowledgeCatalogLookupInput:
    """Parse catalog entries lookup params."""
    return _parse_knowledge_catalog_lookup(raw)


def parse_catalog_entries_get_input(raw: Any) -> ParsedKnowledgeCatalogGetInput:
    """Parse catalog entries get params."""
    return _parse_knowledge_catalog_get("catalog entries get", raw)


def parse_catalog_entries_list_input(raw: Any) -> ParsedKnowledgeCatalogListInput:
    """Parse catalog entries list params."""
    return _parse_knowledge_catalog_list("catalog entries list", raw)


def parse_catalog_entry_groups_get_input(raw: Any) -> ParsedKnowledgeCatalogGetInput:
    """Parse catalog entry-groups get params."""
    return _parse_knowledge_catalog_get("catalog entry-groups get", raw)


def parse_catalog_entry_groups_list_input(raw: Any) -> ParsedKnowledgeCatalogListInput:
    """Parse catalog entry-groups list params."""
    return _parse_knowledge_catalog_list("catalog entry-groups list", raw)


def parse_catalog_entry_types_get_input(raw: Any) -> ParsedKnowledgeCatalogGetInput:
    """Parse catalog entry-types get params."""
    return _parse_knowledge_catalog_get("catalog entry-types get", raw)


def parse_catalog_entry_types_list_input(raw: Any) -> ParsedKnowledgeCatalogListInput:
    """Parse catalog entry-types list params."""
    return _parse_knowledge_catalog_list("catalog entry-types list", raw)


def parse_catalog_aspect_types_get_input(raw: Any) -> ParsedKnowledgeCatalogGetInput:
    """Parse catalog aspect-types get params."""
    return _parse_knowledge_catalog_get("catalog aspect-types get", raw)


def parse_catalog_aspect_types_list_input(raw: Any) -> ParsedKnowledgeCatalogListInput:
    """Parse catalog aspect-types list params."""
    return _parse_knowledge_catalog_list("catalog aspect-types list", raw)


def parse_catalog_entry_links_get_input(raw: Any) -> ParsedKnowledgeCatalogGetInput:
    """Parse catalog entry-links get params."""
    return _parse_knowledge_catalog_get("catalog entry-links get", raw)


def parse_catalog_glossaries_get_input(raw: Any) -> ParsedKnowledgeCatalogGetInput:
    """Parse catalog glossaries get params."""
    return _parse_knowledge_catalog_get("catalog glossaries get", raw)


def parse_catalog_glossaries_list_input(raw: Any) -> ParsedKnowledgeCatalogListInput:
    """Parse catalog glossaries list params."""
    return _parse_knowledge_catalog_list("catalog glossaries list", raw)


def parse_catalog_glossary_categories_get_input(raw: Any) -> ParsedKnowledgeCatalogGetInput:
    """Parse catalog glossary-categories get params."""
    return _parse_knowledge_catalog_get("catalog glossary-categories get", raw)


def parse_catalog_glossary_categories_list_input(raw: Any) -> ParsedKnowledgeCatalogListInput:
    """Parse catalog glossary-categories list params."""
    return _parse_knowledge_catalog_list("catalog glossary-categories list", raw)


def parse_catalog_glossary_terms_get_input(raw: Any) -> ParsedKnowledgeCatalogGetInput:
    """Parse catalog glossary-terms get params."""
    return _parse_knowledge_catalog_get("catalog glossary-terms get", raw)


def parse_catalog_glossary_terms_list_input(raw: Any) -> ParsedKnowledgeCatalogListInput:
    """Parse catalog glossary-terms list params."""
    return _parse_knowledge_catalog_list("catalog glossary-terms list", raw)
