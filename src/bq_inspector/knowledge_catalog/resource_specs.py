"""Declarative Knowledge Catalog command and SDK resource specifications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CatalogServiceKind = Literal["catalog", "glossary"]


@dataclass(frozen=True)
class KnowledgeCatalogGetDispatch:
    """SDK dispatch metadata for get-by-name catalog resources."""

    request_type_name: str
    service: CatalogServiceKind
    sdk_method: str
    api: str
    apply_entry_view: bool = False


@dataclass(frozen=True)
class KnowledgeCatalogListDispatch:
    """SDK dispatch metadata for list-by-parent catalog resources."""

    request_type_name: str
    service: CatalogServiceKind
    sdk_method: str
    api: str
    items_attr: str
    supports_order_by: bool = True


@dataclass(frozen=True)
class KnowledgeCatalogGetCommandSpec:
    """CLI registration metadata for a catalog get command."""

    subgroup: str
    example_file: str
    dispatch: KnowledgeCatalogGetDispatch

    @property
    def apply_entry_view(self) -> bool:
        return self.dispatch.apply_entry_view


@dataclass(frozen=True)
class KnowledgeCatalogListCommandSpec:
    """CLI registration metadata for a catalog list command."""

    subgroup: str
    collection_key: str
    example_file: str
    dispatch: KnowledgeCatalogListDispatch

    @property
    def supports_order_by(self) -> bool:
        return self.dispatch.supports_order_by


CATALOG_GET_EXAMPLE = '{"name":"projects/analytics-prod/locations/us/entryTypes/example-type"}'
CATALOG_LIST_EXAMPLE = '{"parent":"projects/analytics-prod/locations/us","pageSize":100}'

KNOWLEDGE_CATALOG_GET_RESOURCES: tuple[KnowledgeCatalogGetCommandSpec, ...] = (
    KnowledgeCatalogGetCommandSpec(
        "entries",
        "./catalog-entries-get.json",
        KnowledgeCatalogGetDispatch(
            "GetEntryRequest",
            "catalog",
            "get_entry",
            "dataplex.projects.locations.entryGroups.entries.get",
            apply_entry_view=True,
        ),
    ),
    KnowledgeCatalogGetCommandSpec(
        "entry-groups",
        "./catalog-entry-groups-get.json",
        KnowledgeCatalogGetDispatch(
            "GetEntryGroupRequest",
            "catalog",
            "get_entry_group",
            "dataplex.projects.locations.entryGroups.get",
        ),
    ),
    KnowledgeCatalogGetCommandSpec(
        "entry-types",
        "./catalog-entry-types-get.json",
        KnowledgeCatalogGetDispatch(
            "GetEntryTypeRequest",
            "catalog",
            "get_entry_type",
            "dataplex.projects.locations.entryTypes.get",
        ),
    ),
    KnowledgeCatalogGetCommandSpec(
        "aspect-types",
        "./catalog-aspect-types-get.json",
        KnowledgeCatalogGetDispatch(
            "GetAspectTypeRequest",
            "catalog",
            "get_aspect_type",
            "dataplex.projects.locations.aspectTypes.get",
        ),
    ),
    KnowledgeCatalogGetCommandSpec(
        "entry-links",
        "./catalog-entry-links-get.json",
        KnowledgeCatalogGetDispatch(
            "GetEntryLinkRequest",
            "catalog",
            "get_entry_link",
            "dataplex.projects.locations.entryGroups.entryLinks.get",
        ),
    ),
    KnowledgeCatalogGetCommandSpec(
        "glossaries",
        "./catalog-glossaries-get.json",
        KnowledgeCatalogGetDispatch(
            "GetGlossaryRequest",
            "glossary",
            "get_glossary",
            "dataplex.projects.locations.glossaries.get",
        ),
    ),
    KnowledgeCatalogGetCommandSpec(
        "glossary-categories",
        "./catalog-glossary-categories-get.json",
        KnowledgeCatalogGetDispatch(
            "GetGlossaryCategoryRequest",
            "glossary",
            "get_glossary_category",
            "dataplex.projects.locations.glossaries.categories.get",
        ),
    ),
    KnowledgeCatalogGetCommandSpec(
        "glossary-terms",
        "./catalog-glossary-terms-get.json",
        KnowledgeCatalogGetDispatch(
            "GetGlossaryTermRequest",
            "glossary",
            "get_glossary_term",
            "dataplex.projects.locations.glossaries.terms.get",
        ),
    ),
)

KNOWLEDGE_CATALOG_LIST_RESOURCES: tuple[KnowledgeCatalogListCommandSpec, ...] = (
    KnowledgeCatalogListCommandSpec(
        "entries",
        "entries",
        "./catalog-entries-list.json",
        KnowledgeCatalogListDispatch(
            "ListEntriesRequest",
            "catalog",
            "list_entries",
            "dataplex.projects.locations.entryGroups.entries.list",
            "entries",
            supports_order_by=False,
        ),
    ),
    KnowledgeCatalogListCommandSpec(
        "entry-groups",
        "entryGroups",
        "./catalog-entry-groups-list.json",
        KnowledgeCatalogListDispatch(
            "ListEntryGroupsRequest",
            "catalog",
            "list_entry_groups",
            "dataplex.projects.locations.entryGroups.list",
            "entry_groups",
        ),
    ),
    KnowledgeCatalogListCommandSpec(
        "entry-types",
        "entryTypes",
        "./catalog-entry-types-list.json",
        KnowledgeCatalogListDispatch(
            "ListEntryTypesRequest",
            "catalog",
            "list_entry_types",
            "dataplex.projects.locations.entryTypes.list",
            "entry_types",
        ),
    ),
    KnowledgeCatalogListCommandSpec(
        "aspect-types",
        "aspectTypes",
        "./catalog-aspect-types-list.json",
        KnowledgeCatalogListDispatch(
            "ListAspectTypesRequest",
            "catalog",
            "list_aspect_types",
            "dataplex.projects.locations.aspectTypes.list",
            "aspect_types",
        ),
    ),
    KnowledgeCatalogListCommandSpec(
        "glossaries",
        "glossaries",
        "./catalog-glossaries-list.json",
        KnowledgeCatalogListDispatch(
            "ListGlossariesRequest",
            "glossary",
            "list_glossaries",
            "dataplex.projects.locations.glossaries.list",
            "glossaries",
        ),
    ),
    KnowledgeCatalogListCommandSpec(
        "glossary-categories",
        "categories",
        "./catalog-glossary-categories-list.json",
        KnowledgeCatalogListDispatch(
            "ListGlossaryCategoriesRequest",
            "glossary",
            "list_glossary_categories",
            "dataplex.projects.locations.glossaries.categories.list",
            "categories",
        ),
    ),
    KnowledgeCatalogListCommandSpec(
        "glossary-terms",
        "terms",
        "./catalog-glossary-terms-list.json",
        KnowledgeCatalogListDispatch(
            "ListGlossaryTermsRequest",
            "glossary",
            "list_glossary_terms",
            "dataplex.projects.locations.glossaries.terms.list",
            "terms",
        ),
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
