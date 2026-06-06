"""Drift and alignment tests for Knowledge Catalog resource specifications."""

from __future__ import annotations

import inspect

from bq_inspector.commands.catalog.commands import build_knowledge_catalog_command_runners
from bq_inspector.commands.catalog.resource_specs import (
    KNOWLEDGE_CATALOG_GET_RESOURCES,
    KNOWLEDGE_CATALOG_LIST_RESOURCES,
    knowledge_catalog_export_name,
)
from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient


def _unique_values(values: tuple[str, ...]) -> set[str]:
    return set(values)


def test_get_resource_client_methods_are_unique() -> None:
    methods = tuple(spec.client_method for spec in KNOWLEDGE_CATALOG_GET_RESOURCES)
    assert len(methods) == len(_unique_values(methods))


def test_list_resource_client_methods_are_unique() -> None:
    methods = tuple(spec.client_method for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES)
    assert len(methods) == len(_unique_values(methods))


def test_get_resource_subgroups_are_unique() -> None:
    subgroups = tuple(spec.subgroup for spec in KNOWLEDGE_CATALOG_GET_RESOURCES)
    assert len(subgroups) == len(_unique_values(subgroups))


def test_list_resource_subgroups_are_unique() -> None:
    subgroups = tuple(spec.subgroup for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES)
    assert len(subgroups) == len(_unique_values(subgroups))


def test_client_method_matches_sdk_method() -> None:
    for spec in KNOWLEDGE_CATALOG_GET_RESOURCES:
        assert spec.client_method == spec.sdk_method
    for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES:
        assert spec.client_method == spec.sdk_method


def test_list_subgroups_are_subset_of_get_subgroups() -> None:
    get_subgroups = {spec.subgroup for spec in KNOWLEDGE_CATALOG_GET_RESOURCES}
    list_subgroups = {spec.subgroup for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES}
    assert list_subgroups <= get_subgroups


def test_entry_links_has_get_without_list() -> None:
    get_subgroups = {spec.subgroup for spec in KNOWLEDGE_CATALOG_GET_RESOURCES}
    list_subgroups = {spec.subgroup for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES}
    assert "entry-links" in get_subgroups
    assert "entry-links" not in list_subgroups


def test_command_runners_align_with_resource_specs() -> None:
    runners = build_knowledge_catalog_command_runners()
    expected_keys = {
        knowledge_catalog_export_name(spec.subgroup, "get")
        for spec in KNOWLEDGE_CATALOG_GET_RESOURCES
    } | {
        knowledge_catalog_export_name(spec.subgroup, "list")
        for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES
    }
    assert set(runners) == expected_keys
    assert len(runners) == len(KNOWLEDGE_CATALOG_GET_RESOURCES) + len(
        KNOWLEDGE_CATALOG_LIST_RESOURCES
    )


def test_get_resources_cover_catalog_inspection_client_methods() -> None:
    """Every CatalogInspectionClient get/list method is declared in resource specs."""
    protocol_methods = {
        name
        for name, member in inspect.getmembers(CatalogInspectionClient)
        if not name.startswith("_")
        and callable(member)
        and name not in {"search_entries", "lookup_entry"}
    }
    spec_methods = {spec.client_method for spec in KNOWLEDGE_CATALOG_GET_RESOURCES} | {
        spec.client_method for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES
    }
    assert protocol_methods == spec_methods
