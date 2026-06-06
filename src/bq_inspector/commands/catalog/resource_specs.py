"""Declarative Knowledge Catalog command and SDK resource specifications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from bq_inspector.cli.usage_build import ParamsBodyKind

CatalogServiceKind = Literal["catalog", "glossary"]


@dataclass(frozen=True)
class KnowledgeCatalogGetResourceSpec:
    """Get-by-name Knowledge Catalog CLI command and SDK metadata."""

    subgroup: str
    client_method: str
    example_file: str
    request_type_name: str
    service: CatalogServiceKind
    sdk_method: str
    api: str
    apply_entry_view: bool = False


@dataclass(frozen=True)
class KnowledgeCatalogListResourceSpec:
    """List-by-parent Knowledge Catalog CLI command and SDK metadata."""

    subgroup: str
    collection_key: str
    client_method: str
    example_file: str
    request_type_name: str
    service: CatalogServiceKind
    sdk_method: str
    api: str
    items_attr: str


CATALOG_GET_EXAMPLE = '{"name":"projects/analytics-prod/locations/us/entryTypes/example-type"}'
CATALOG_LIST_EXAMPLE = '{"parent":"projects/analytics-prod/locations/us","pageSize":100}'

KNOWLEDGE_CATALOG_GET_RESOURCES: tuple[KnowledgeCatalogGetResourceSpec, ...] = (
    KnowledgeCatalogGetResourceSpec(
        "entries",
        "get_entry",
        "./catalog-entries-get.json",
        "GetEntryRequest",
        "catalog",
        "get_entry",
        "dataplex.projects.locations.entryGroups.entries.get",
        apply_entry_view=True,
    ),
    KnowledgeCatalogGetResourceSpec(
        "entry-groups",
        "get_entry_group",
        "./catalog-entry-groups-get.json",
        "GetEntryGroupRequest",
        "catalog",
        "get_entry_group",
        "dataplex.projects.locations.entryGroups.get",
    ),
    KnowledgeCatalogGetResourceSpec(
        "entry-types",
        "get_entry_type",
        "./catalog-entry-types-get.json",
        "GetEntryTypeRequest",
        "catalog",
        "get_entry_type",
        "dataplex.projects.locations.entryTypes.get",
    ),
    KnowledgeCatalogGetResourceSpec(
        "aspect-types",
        "get_aspect_type",
        "./catalog-aspect-types-get.json",
        "GetAspectTypeRequest",
        "catalog",
        "get_aspect_type",
        "dataplex.projects.locations.aspectTypes.get",
    ),
    KnowledgeCatalogGetResourceSpec(
        "entry-links",
        "get_entry_link",
        "./catalog-entry-links-get.json",
        "GetEntryLinkRequest",
        "catalog",
        "get_entry_link",
        "dataplex.projects.locations.entryGroups.entryLinks.get",
    ),
    KnowledgeCatalogGetResourceSpec(
        "glossaries",
        "get_glossary",
        "./catalog-glossaries-get.json",
        "GetGlossaryRequest",
        "glossary",
        "get_glossary",
        "dataplex.projects.locations.glossaries.get",
    ),
    KnowledgeCatalogGetResourceSpec(
        "glossary-categories",
        "get_glossary_category",
        "./catalog-glossary-categories-get.json",
        "GetGlossaryCategoryRequest",
        "glossary",
        "get_glossary_category",
        "dataplex.projects.locations.glossaries.categories.get",
    ),
    KnowledgeCatalogGetResourceSpec(
        "glossary-terms",
        "get_glossary_term",
        "./catalog-glossary-terms-get.json",
        "GetGlossaryTermRequest",
        "glossary",
        "get_glossary_term",
        "dataplex.projects.locations.glossaries.terms.get",
    ),
)

KNOWLEDGE_CATALOG_LIST_RESOURCES: tuple[KnowledgeCatalogListResourceSpec, ...] = (
    KnowledgeCatalogListResourceSpec(
        "entries",
        "entries",
        "list_entries",
        "./catalog-entries-list.json",
        "ListEntriesRequest",
        "catalog",
        "list_entries",
        "dataplex.projects.locations.entryGroups.entries.list",
        "entries",
    ),
    KnowledgeCatalogListResourceSpec(
        "entry-groups",
        "entryGroups",
        "list_entry_groups",
        "./catalog-entry-groups-list.json",
        "ListEntryGroupsRequest",
        "catalog",
        "list_entry_groups",
        "dataplex.projects.locations.entryGroups.list",
        "entry_groups",
    ),
    KnowledgeCatalogListResourceSpec(
        "entry-types",
        "entryTypes",
        "list_entry_types",
        "./catalog-entry-types-list.json",
        "ListEntryTypesRequest",
        "catalog",
        "list_entry_types",
        "dataplex.projects.locations.entryTypes.list",
        "entry_types",
    ),
    KnowledgeCatalogListResourceSpec(
        "aspect-types",
        "aspectTypes",
        "list_aspect_types",
        "./catalog-aspect-types-list.json",
        "ListAspectTypesRequest",
        "catalog",
        "list_aspect_types",
        "dataplex.projects.locations.aspectTypes.list",
        "aspect_types",
    ),
    KnowledgeCatalogListResourceSpec(
        "glossaries",
        "glossaries",
        "list_glossaries",
        "./catalog-glossaries-list.json",
        "ListGlossariesRequest",
        "glossary",
        "list_glossaries",
        "dataplex.projects.locations.glossaries.list",
        "glossaries",
    ),
    KnowledgeCatalogListResourceSpec(
        "glossary-categories",
        "categories",
        "list_glossary_categories",
        "./catalog-glossary-categories-list.json",
        "ListGlossaryCategoriesRequest",
        "glossary",
        "list_glossary_categories",
        "dataplex.projects.locations.glossaries.categories.list",
        "categories",
    ),
    KnowledgeCatalogListResourceSpec(
        "glossary-terms",
        "terms",
        "list_glossary_terms",
        "./catalog-glossary-terms-list.json",
        "ListGlossaryTermsRequest",
        "glossary",
        "list_glossary_terms",
        "dataplex.projects.locations.glossaries.terms.list",
        "terms",
    ),
)


def knowledge_catalog_command_path(subgroup: str, verb: str) -> tuple[str, ...]:
    """Return the CLI path tuple for a nested Knowledge Catalog command."""
    return ("catalog", subgroup, verb)


def knowledge_catalog_command_id(subgroup: str, verb: str) -> str:
    """Return the canonical command id string."""
    return " ".join(knowledge_catalog_command_path(subgroup, verb))


def knowledge_catalog_export_name(subgroup: str, verb: str) -> str:
    """Return the module-level command runner export name."""
    slug = subgroup.replace("-", "_")
    return f"catalog_{slug}_{verb}_command"


def knowledge_catalog_body_kind(verb: str) -> ParamsBodyKind:
    """Return params body kind for a Knowledge Catalog verb."""
    if verb == "get":
        return ParamsBodyKind.CATALOG_GET
    if verb == "list":
        return ParamsBodyKind.CATALOG_LIST
    raise ValueError(f"Unsupported Knowledge Catalog verb: {verb}")
