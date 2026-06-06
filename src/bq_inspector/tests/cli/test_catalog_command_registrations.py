"""Tests for Knowledge Catalog CLI command registration coverage."""

from __future__ import annotations

import pytest

from bq_inspector.cli.command_registry import PARAMS_COMMAND_SPECS, command_path_key
from bq_inspector.commands.catalog.registry import build_knowledge_catalog_registrations
from bq_inspector.commands.catalog.resource_specs import (
    KNOWLEDGE_CATALOG_GET_RESOURCES,
    KNOWLEDGE_CATALOG_LIST_RESOURCES,
    knowledge_catalog_command_path,
)
from bq_inspector.schemas.command_schemas import get_command_schema


def _catalog_paths() -> tuple[tuple[str, ...], ...]:
    paths: list[tuple[str, ...]] = [
        ("catalog", "search"),
        ("catalog", "entries", "lookup"),
    ]
    paths.extend(
        knowledge_catalog_command_path(spec.subgroup, "get")
        for spec in KNOWLEDGE_CATALOG_GET_RESOURCES
    )
    paths.extend(
        knowledge_catalog_command_path(spec.subgroup, "list")
        for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES
    )
    return tuple(paths)


@pytest.mark.parametrize("path", _catalog_paths())
def test_knowledge_catalog_command_is_registered(path: tuple[str, ...]) -> None:
    registered = {spec.path for spec in PARAMS_COMMAND_SPECS}
    assert path in registered


@pytest.mark.parametrize("path", _catalog_paths())
def test_knowledge_catalog_command_has_input_schema(path: tuple[str, ...]) -> None:
    schema = get_command_schema(command_path_key(path), "input")
    assert isinstance(schema, dict)
    assert "properties" in schema


def test_knowledge_catalog_registration_count() -> None:
    expected_count = (
        2 + len(KNOWLEDGE_CATALOG_GET_RESOURCES) + len(KNOWLEDGE_CATALOG_LIST_RESOURCES)
    )
    assert len(build_knowledge_catalog_registrations()) == expected_count
