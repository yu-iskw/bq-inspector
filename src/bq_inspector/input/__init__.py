"""Validate and map CLI params JSON to typed command input."""

from bq_inspector.input.input_parsers import (
    parse_datasets_get_input,
    parse_jobs_get_input,
    parse_jobs_list_input,
    parse_jobs_view_input_for_command,
    parse_tables_get_input,
    parse_tables_list_input,
)

__all__ = [
    "parse_datasets_get_input",
    "parse_jobs_get_input",
    "parse_jobs_list_input",
    "parse_jobs_view_input_for_command",
    "parse_tables_get_input",
    "parse_tables_list_input",
]
