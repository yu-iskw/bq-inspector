"""Declarative Knowledge Catalog command and SDK resource specifications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

from bq_inspector.cli.usage_build import ParamsBodyKind
from bq_inspector.schemas.command_schemas import CommandId  # noqa: TC001

CatalogServiceKind = Literal["catalog", "glossary"]


@dataclass(frozen=True)
class KnowledgeCatalogGetCommandSpec:
    """Get-by-name Knowledge Catalog command."""

    subgroup: str
    client_method: str
    example_file: str


@dataclass(frozen=True)
class KnowledgeCatalogListCommandSpec:
    """List-by-parent Knowledge Catalog command."""

    subgroup: str
    collection_key: str
    client_method: str
    example_file: str


@dataclass(frozen=True)
class KnowledgeCatalogGetSdkSpec:
    """SDK metadata for a get-by-name catalog resource."""

    client_method: str
    request_type_name: str
    service: CatalogServiceKind
    sdk_method: str
    api: str
    apply_entry_view: bool = False


@dataclass(frozen=True)
class KnowledgeCatalogListSdkSpec:
    """SDK metadata for a list-by-parent catalog resource."""

    client_method: str
    request_type_name: str
    service: CatalogServiceKind
    sdk_method: str
    api: str
    items_attr: str


CATALOG_GET_EXAMPLE = '{"name":"projects/analytics-prod/locations/us/entryTypes/example-type"}'
CATALOG_LIST_EXAMPLE = '{"parent":"projects/analytics-prod/locations/us","pageSize":100}'

KNOWLEDGE_CATALOG_GET_COMMANDS: tuple[KnowledgeCatalogGetCommandSpec, ...] = (
    KnowledgeCatalogGetCommandSpec("entries", "get_entry", "./catalog-entries-get.json"),
    KnowledgeCatalogGetCommandSpec(
        "entry-groups", "get_entry_group", "./catalog-entry-groups-get.json"
    ),
    KnowledgeCatalogGetCommandSpec(
        "entry-types", "get_entry_type", "./catalog-entry-types-get.json"
    ),
    KnowledgeCatalogGetCommandSpec(
        "aspect-types", "get_aspect_type", "./catalog-aspect-types-get.json"
    ),
    KnowledgeCatalogGetCommandSpec(
        "entry-links", "get_entry_link", "./catalog-entry-links-get.json"
    ),
    KnowledgeCatalogGetCommandSpec("glossaries", "get_glossary", "./catalog-glossaries-get.json"),
    KnowledgeCatalogGetCommandSpec(
        "glossary-categories",
        "get_glossary_category",
        "./catalog-glossary-categories-get.json",
    ),
    KnowledgeCatalogGetCommandSpec(
        "glossary-terms",
        "get_glossary_term",
        "./catalog-glossary-terms-get.json",
    ),
)

KNOWLEDGE_CATALOG_LIST_COMMANDS: tuple[KnowledgeCatalogListCommandSpec, ...] = (
    KnowledgeCatalogListCommandSpec(
        "entries", "entries", "list_entries", "./catalog-entries-list.json"
    ),
    KnowledgeCatalogListCommandSpec(
        "entry-groups",
        "entryGroups",
        "list_entry_groups",
        "./catalog-entry-groups-list.json",
    ),
    KnowledgeCatalogListCommandSpec(
        "entry-types",
        "entryTypes",
        "list_entry_types",
        "./catalog-entry-types-list.json",
    ),
    KnowledgeCatalogListCommandSpec(
        "aspect-types",
        "aspectTypes",
        "list_aspect_types",
        "./catalog-aspect-types-list.json",
    ),
    KnowledgeCatalogListCommandSpec(
        "glossaries",
        "glossaries",
        "list_glossaries",
        "./catalog-glossaries-list.json",
    ),
    KnowledgeCatalogListCommandSpec(
        "glossary-categories",
        "categories",
        "list_glossary_categories",
        "./catalog-glossary-categories-list.json",
    ),
    KnowledgeCatalogListCommandSpec(
        "glossary-terms",
        "terms",
        "list_glossary_terms",
        "./catalog-glossary-terms-list.json",
    ),
)

KNOWLEDGE_CATALOG_GET_SDK_SPECS: tuple[KnowledgeCatalogGetSdkSpec, ...] = (
    KnowledgeCatalogGetSdkSpec(
        "get_entry",
        "GetEntryRequest",
        "catalog",
        "get_entry",
        "dataplex.projects.locations.entryGroups.entries.get",
        apply_entry_view=True,
    ),
    KnowledgeCatalogGetSdkSpec(
        "get_entry_group",
        "GetEntryGroupRequest",
        "catalog",
        "get_entry_group",
        "dataplex.projects.locations.entryGroups.get",
    ),
    KnowledgeCatalogGetSdkSpec(
        "get_entry_type",
        "GetEntryTypeRequest",
        "catalog",
        "get_entry_type",
        "dataplex.projects.locations.entryTypes.get",
    ),
    KnowledgeCatalogGetSdkSpec(
        "get_aspect_type",
        "GetAspectTypeRequest",
        "catalog",
        "get_aspect_type",
        "dataplex.projects.locations.aspectTypes.get",
    ),
    KnowledgeCatalogGetSdkSpec(
        "get_entry_link",
        "GetEntryLinkRequest",
        "catalog",
        "get_entry_link",
        "dataplex.projects.locations.entryGroups.entryLinks.get",
    ),
    KnowledgeCatalogGetSdkSpec(
        "get_glossary",
        "GetGlossaryRequest",
        "glossary",
        "get_glossary",
        "dataplex.projects.locations.glossaries.get",
    ),
    KnowledgeCatalogGetSdkSpec(
        "get_glossary_category",
        "GetGlossaryCategoryRequest",
        "glossary",
        "get_glossary_category",
        "dataplex.projects.locations.glossaries.categories.get",
    ),
    KnowledgeCatalogGetSdkSpec(
        "get_glossary_term",
        "GetGlossaryTermRequest",
        "glossary",
        "get_glossary_term",
        "dataplex.projects.locations.glossaries.terms.get",
    ),
)

KNOWLEDGE_CATALOG_LIST_SDK_SPECS: tuple[KnowledgeCatalogListSdkSpec, ...] = (
    KnowledgeCatalogListSdkSpec(
        "list_entries",
        "ListEntriesRequest",
        "catalog",
        "list_entries",
        "dataplex.projects.locations.entryGroups.entries.list",
        "entries",
    ),
    KnowledgeCatalogListSdkSpec(
        "list_entry_groups",
        "ListEntryGroupsRequest",
        "catalog",
        "list_entry_groups",
        "dataplex.projects.locations.entryGroups.list",
        "entry_groups",
    ),
    KnowledgeCatalogListSdkSpec(
        "list_entry_types",
        "ListEntryTypesRequest",
        "catalog",
        "list_entry_types",
        "dataplex.projects.locations.entryTypes.list",
        "entry_types",
    ),
    KnowledgeCatalogListSdkSpec(
        "list_aspect_types",
        "ListAspectTypesRequest",
        "catalog",
        "list_aspect_types",
        "dataplex.projects.locations.aspectTypes.list",
        "aspect_types",
    ),
    KnowledgeCatalogListSdkSpec(
        "list_glossaries",
        "ListGlossariesRequest",
        "glossary",
        "list_glossaries",
        "dataplex.projects.locations.glossaries.list",
        "glossaries",
    ),
    KnowledgeCatalogListSdkSpec(
        "list_glossary_categories",
        "ListGlossaryCategoriesRequest",
        "glossary",
        "list_glossary_categories",
        "dataplex.projects.locations.glossaries.categories.list",
        "categories",
    ),
    KnowledgeCatalogListSdkSpec(
        "list_glossary_terms",
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


def knowledge_catalog_command_id(subgroup: str, verb: str) -> CommandId:
    """Return the canonical command id string."""
    return cast("CommandId", " ".join(knowledge_catalog_command_path(subgroup, verb)))


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
