"""In-memory fake for Knowledge Catalog inspection tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

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
        from bq_inspector.commands.catalog.resource_specs import (  # noqa: PLC0415
            KNOWLEDGE_CATALOG_GET_COMMANDS,
            KNOWLEDGE_CATALOG_LIST_COMMANDS,
        )

        self._fixture = fixture
        self.calls: list[tuple[str, Any]] = []

        for spec in KNOWLEDGE_CATALOG_GET_COMMANDS:
            setattr(self, spec.client_method, self._make_get_handler(spec.client_method))

        for spec in KNOWLEDGE_CATALOG_LIST_COMMANDS:
            setattr(self, spec.client_method, self._make_list_handler(spec.client_method))

    def _make_get_handler(self, method_name: str) -> Any:
        async def handler(request: GetByNameRequest) -> dict[str, object]:
            self.calls.append((method_name, request))
            return self._fixture.get_by_name.get(request["name"], {"name": request["name"]})

        return handler

    def _make_list_handler(self, method_name: str) -> Any:
        async def handler(request: ListByParentRequest) -> ListResourcesPage:
            self.calls.append((method_name, request))
            return self._fixture.list_by_parent.get(request["parent"], {"resources": []})

        return handler

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
