"""Validate and map CLI params to typed command input."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspect.cli.input.map_input import (
    map_catalog_input,
    map_jobs_list_input,
    map_jobs_view_input,
)
from bq_inspect.schemas.validate_input import validate_input

if TYPE_CHECKING:
    from bq_inspect.cli.input.parsed_input_types import (
        ParsedCatalogInput,
        ParsedJobsListInput,
        ParsedJobsViewInput,
    )
    from bq_inspect.schemas.command_schemas import JobsViewCommandId


def parse_jobs_get_input(raw: Any) -> ParsedJobsViewInput:
    """Parse jobs get params."""
    return map_jobs_view_input(validate_input("jobs get", raw))


def parse_jobs_view_input_for_command(
    command_id: JobsViewCommandId,
    raw: Any,
) -> ParsedJobsViewInput:
    """Parse jobs view params for a specific view command."""
    return map_jobs_view_input(validate_input(command_id, raw))


def parse_jobs_list_input(raw: Any) -> ParsedJobsListInput:
    """Parse jobs list params."""
    return map_jobs_list_input(validate_input("jobs list", raw))


def parse_datasets_get_input(raw: Any) -> ParsedCatalogInput:
    """Parse datasets get params."""
    return map_catalog_input(validate_input("datasets get", raw))


def parse_tables_list_input(raw: Any) -> ParsedCatalogInput:
    """Parse tables list params."""
    return map_catalog_input(validate_input("tables list", raw))


def parse_tables_get_input(raw: Any) -> ParsedCatalogInput:
    """Parse tables get params."""
    return map_catalog_input(validate_input("tables get", raw))
