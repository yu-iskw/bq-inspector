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
from bq_inspector.schemas.command_schemas import CommandId, JobsViewCommandId
from bq_inspector.schemas.validate_input import validate_input

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import (
        ParsedCatalogInput,
        ParsedJobsListInput,
        ParsedJobsViewInput,
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
