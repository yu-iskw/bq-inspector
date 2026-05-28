"""Help text resolution for bq-inspect CLI."""

from __future__ import annotations

from bq_inspect.cli.usage import (
    DATASETS_GET_USAGE,
    GLOBAL_USAGE,
    JOBS_GET_USAGE,
    JOBS_IMPACT_USAGE,
    JOBS_LINEAGE_USAGE,
    JOBS_LIST_USAGE,
    JOBS_PERFORMANCE_USAGE,
    JOBS_QUERY_USAGE,
    JOBS_SUMMARY_USAGE,
    SCHEMA_INPUT_USAGE,
    SCHEMA_OUTPUT_USAGE,
    SCHEMA_USAGE,
    TABLES_GET_USAGE,
    TABLES_LIST_USAGE,
)


def _command_help_for_key(key: str) -> str | None:
    mapping: dict[str, str] = {
        "schema input": SCHEMA_INPUT_USAGE,
        "schema output": SCHEMA_OUTPUT_USAGE,
        "schema": SCHEMA_USAGE,
        "jobs summary": JOBS_SUMMARY_USAGE,
        "jobs query": JOBS_QUERY_USAGE,
        "jobs performance": JOBS_PERFORMANCE_USAGE,
        "jobs lineage": JOBS_LINEAGE_USAGE,
        "jobs impact": JOBS_IMPACT_USAGE,
        "jobs get": JOBS_GET_USAGE,
        "jobs list": JOBS_LIST_USAGE,
        "datasets get": DATASETS_GET_USAGE,
        "tables list": TABLES_LIST_USAGE,
        "tables get": TABLES_GET_USAGE,
    }
    return mapping.get(key)


def strip_trailing_help_flags(argv: list[str]) -> tuple[list[str], bool]:
    """Strip trailing --help / -h flags and return cleaned argv."""
    copy = list(argv)
    wants_help = False

    while copy and copy[-1] in ("--help", "-h"):
        wants_help = True
        copy.pop()

    return copy, wants_help


def resolve_help_text(argv: list[str], wants_help: bool) -> str | None:  # noqa: PLR0911
    """Return help text when the user asked for help, or None to continue dispatch."""
    if not wants_help:
        return None

    key = " ".join(argv)
    usage = _command_help_for_key(key)

    if usage is not None:
        return usage

    if argv:
        return f"{GLOBAL_USAGE}\n\nUnknown command: {key}"

    return GLOBAL_USAGE
