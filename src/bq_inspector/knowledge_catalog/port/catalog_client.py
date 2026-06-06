"""Port for read-only Knowledge Catalog inspection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from bq_inspector.knowledge_catalog.types.requests import (
        GetByNameRequest,
        ListByParentRequest,
        LookupEntryRequest,
        SearchEntriesRequest,
    )
    from bq_inspector.knowledge_catalog.types.responses import (
        ListResourcesPage,
        SearchEntriesPage,
    )


class CatalogInspectionClient(Protocol):
    """Port for read-only Knowledge Catalog (Dataplex) inspection."""

    async def search_entries(self, request: SearchEntriesRequest) -> SearchEntriesPage:
        """Search catalog entries."""
        raise NotImplementedError

    async def lookup_entry(self, request: LookupEntryRequest) -> dict[str, object]:
        """Resolve an entry by canonical name."""
        raise NotImplementedError

    async def get_entry(self, request: GetByNameRequest) -> dict[str, object]:
        """Retrieve an entry by canonical resource name."""
        raise NotImplementedError

    async def list_entries(self, request: ListByParentRequest) -> ListResourcesPage:
        """List entries under an entry group."""
        raise NotImplementedError

    async def get_entry_group(self, request: GetByNameRequest) -> dict[str, object]:
        """Retrieve an entry group."""
        raise NotImplementedError

    async def list_entry_groups(self, request: ListByParentRequest) -> ListResourcesPage:
        """List entry groups."""
        raise NotImplementedError

    async def get_entry_type(self, request: GetByNameRequest) -> dict[str, object]:
        """Retrieve an entry type."""
        raise NotImplementedError

    async def list_entry_types(self, request: ListByParentRequest) -> ListResourcesPage:
        """List entry types."""
        raise NotImplementedError

    async def get_aspect_type(self, request: GetByNameRequest) -> dict[str, object]:
        """Retrieve an aspect type."""
        raise NotImplementedError

    async def list_aspect_types(self, request: ListByParentRequest) -> ListResourcesPage:
        """List aspect types."""
        raise NotImplementedError

    async def get_entry_link(self, request: GetByNameRequest) -> dict[str, object]:
        """Retrieve an entry link."""
        raise NotImplementedError

    async def get_glossary(self, request: GetByNameRequest) -> dict[str, object]:
        """Retrieve a glossary."""
        raise NotImplementedError

    async def list_glossaries(self, request: ListByParentRequest) -> ListResourcesPage:
        """List glossaries."""
        raise NotImplementedError

    async def get_glossary_category(self, request: GetByNameRequest) -> dict[str, object]:
        """Retrieve a glossary category."""
        raise NotImplementedError

    async def list_glossary_categories(self, request: ListByParentRequest) -> ListResourcesPage:
        """List glossary categories."""
        raise NotImplementedError

    async def get_glossary_term(self, request: GetByNameRequest) -> dict[str, object]:
        """Retrieve a glossary term."""
        raise NotImplementedError

    async def list_glossary_terms(self, request: ListByParentRequest) -> ListResourcesPage:
        """List glossary terms."""
        raise NotImplementedError
