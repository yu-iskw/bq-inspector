"""Port for read-only Knowledge Catalog inspection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from bq_inspector.knowledge_catalog.resource_specs import (
        KnowledgeCatalogGetResourceSpec,
        KnowledgeCatalogListResourceSpec,
    )
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

    async def get_named_resource(
        self,
        request: GetByNameRequest,
        *,
        spec: KnowledgeCatalogGetResourceSpec,
    ) -> dict[str, object]:
        """Retrieve a catalog resource by canonical name."""
        raise NotImplementedError

    async def list_parent_resources(
        self,
        request: ListByParentRequest,
        *,
        spec: KnowledgeCatalogListResourceSpec,
    ) -> ListResourcesPage:
        """List catalog resources under a parent."""
        raise NotImplementedError
