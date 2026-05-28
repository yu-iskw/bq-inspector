"""Tests for CLI help resolution."""

import pytest

from bq_inspect.cli.help import resolve_help_text, strip_trailing_help_flags
from bq_inspect.cli.usage import GLOBAL_USAGE, JOBS_GET_USAGE


def test_strip_trailing_help_flags() -> None:
    assert strip_trailing_help_flags(["jobs", "get", "--help"]) == (
        ["jobs", "get"],
        True,
    )
    assert strip_trailing_help_flags(["jobs", "get", "-h"]) == (
        ["jobs", "get"],
        True,
    )
    assert strip_trailing_help_flags(["--help"]) == ([], True)


def test_strip_trailing_help_flags_leaves_argv_unchanged() -> None:
    assert strip_trailing_help_flags(["jobs", "get", "--project", "p"]) == (
        ["jobs", "get", "--project", "p"],
        False,
    )


def test_resolve_help_text_requires_help_flag() -> None:
    with pytest.raises(ValueError, match="wants_help"):
        resolve_help_text(["jobs", "get"], False)


def test_resolve_help_text_global_usage_for_bare_help() -> None:
    text = resolve_help_text([], True)
    assert text == GLOBAL_USAGE
    assert "jobs get" in text


def test_resolve_help_text_jobs_get_usage() -> None:
    text = resolve_help_text(["jobs", "get"], True)
    assert text == JOBS_GET_USAGE
    assert "--params" in text
    assert "--input-schema" in text
    assert "--output-schema" in text
    assert "--selector-schema" not in text
    assert "--project" not in text


def test_resolve_help_text_jobs_list_usage() -> None:
    text = resolve_help_text(["jobs", "list"], True)
    assert text is not None
    assert "--params" in text
    assert "minCreationTime" in text
    assert "allUsers" in text
    assert "--min-creation-time" not in text


def test_resolve_help_text_catalog_commands() -> None:
    datasets_get = resolve_help_text(["datasets", "get"], True)
    assert datasets_get is not None
    assert "datasetId" in datasets_get
    tables_list = resolve_help_text(["tables", "list"], True)
    assert tables_list is not None
    assert "tables list" in tables_list
    tables_get = resolve_help_text(["tables", "get"], True)
    assert tables_get is not None
    assert "tableId" in tables_get
    assert "--table" not in tables_get


def test_resolve_help_text_schema_variants() -> None:
    schema = resolve_help_text(["schema"], True)
    assert schema is not None
    assert "json-schema" in schema
    schema_input = resolve_help_text(["schema", "input"], True)
    assert schema_input is not None
    assert "schema input" in schema_input
    schema_output = resolve_help_text(["schema", "output"], True)
    assert schema_output is not None
    assert "schema output" in schema_output


def test_resolve_help_text_jobs_group_usage() -> None:
    text = resolve_help_text(["jobs"], True)
    assert text is not None
    assert "summary" in text
    assert "Subcommands:" in text


def test_resolve_help_text_unknown_command() -> None:
    text = resolve_help_text(["foo", "bar"], True)
    assert text is not None
    assert GLOBAL_USAGE in text
    assert "Unknown command: foo bar" in text
