"""In-memory fake for Knowledge Catalog inspection tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bq_inspector.knowledge_catalog.resource_specs import (
        KnowledgeCatalogGetDispatch,
        KnowledgeCatalogListDispatch,
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


@dataclass
class FixtureCatalogInput:
    """Canned Knowledge Catalog responses keyed by request shape."""

    search_pages: dict[tuple[str, str], SearchEntriesPage] = field(default_factory=dict)
    lookup_by_entry: dict[str, dict[str, object]] = field(default_factory=dict)
    get_by_name: dict[str, dict[str, object]] = field(default_factory=dict)
    list_by_parent: dict[str, ListResourcesPage] = field(default_factory=dict)


class FixtureCatalogClient:
    """CatalogInspectionClient fake backed by canned responses."""

    def __init__(self, fixture: FixtureCatalogInput) -> None:
        self._fixture = fixture
        self.calls: list[tuple[str, Any]] = []

    async def get_named_resource(
        self,
        request: GetByNameRequest,
        *,
        dispatch: KnowledgeCatalogGetDispatch,
    ) -> dict[str, object]:
        self.calls.append((dispatch.sdk_method, request))
        return self._fixture.get_by_name.get(request["name"], {"name": request["name"]})

    async def list_parent_resources(
        self,
        request: ListByParentRequest,
        *,
        dispatch: KnowledgeCatalogListDispatch,
    ) -> ListResourcesPage:
        self.calls.append((dispatch.sdk_method, request))
        return self._fixture.list_by_parent.get(request["parent"], {"resources": []})

    async def search_entries(self, request: SearchEntriesRequest) -> SearchEntriesPage:
        self.calls.append(("search_entries", request))
        key = (request["name"], request["query"])
        return self._fixture.search_pages.get(
            key,
            {"entries": [], "totalSize": 0, "unreachable": []},
        )

    async def lookup_entry(self, request: LookupEntryRequest) -> dict[str, object]:
        self.calls.append(("lookup_entry", request))
        return self._fixture.lookup_by_entry.get(request["entry"], {"name": request["entry"]})
