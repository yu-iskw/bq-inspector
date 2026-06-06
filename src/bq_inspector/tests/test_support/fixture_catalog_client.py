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
        self._fixture = fixture
        self.calls: list[tuple[str, Any]] = []

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

    async def get_entry(self, request: GetByNameRequest) -> dict[str, object]:
        self.calls.append(("get_entry", request))
        return self._fixture.get_by_name.get(request["name"], {"name": request["name"]})

    async def list_entries(self, request: ListByParentRequest) -> ListResourcesPage:
        self.calls.append(("list_entries", request))
        return self._fixture.list_by_parent.get(request["parent"], {"resources": []})

    async def get_entry_group(self, request: GetByNameRequest) -> dict[str, object]:
        self.calls.append(("get_entry_group", request))
        return self._fixture.get_by_name.get(request["name"], {"name": request["name"]})

    async def list_entry_groups(self, request: ListByParentRequest) -> ListResourcesPage:
        self.calls.append(("list_entry_groups", request))
        return self._fixture.list_by_parent.get(request["parent"], {"resources": []})

    async def get_entry_type(self, request: GetByNameRequest) -> dict[str, object]:
        self.calls.append(("get_entry_type", request))
        return self._fixture.get_by_name.get(request["name"], {"name": request["name"]})

    async def list_entry_types(self, request: ListByParentRequest) -> ListResourcesPage:
        self.calls.append(("list_entry_types", request))
        return self._fixture.list_by_parent.get(request["parent"], {"resources": []})

    async def get_aspect_type(self, request: GetByNameRequest) -> dict[str, object]:
        self.calls.append(("get_aspect_type", request))
        return self._fixture.get_by_name.get(request["name"], {"name": request["name"]})

    async def list_aspect_types(self, request: ListByParentRequest) -> ListResourcesPage:
        self.calls.append(("list_aspect_types", request))
        return self._fixture.list_by_parent.get(request["parent"], {"resources": []})

    async def get_entry_link(self, request: GetByNameRequest) -> dict[str, object]:
        self.calls.append(("get_entry_link", request))
        return self._fixture.get_by_name.get(request["name"], {"name": request["name"]})

    async def get_glossary(self, request: GetByNameRequest) -> dict[str, object]:
        self.calls.append(("get_glossary", request))
        return self._fixture.get_by_name.get(request["name"], {"name": request["name"]})

    async def list_glossaries(self, request: ListByParentRequest) -> ListResourcesPage:
        self.calls.append(("list_glossaries", request))
        return self._fixture.list_by_parent.get(request["parent"], {"resources": []})

    async def get_glossary_category(self, request: GetByNameRequest) -> dict[str, object]:
        self.calls.append(("get_glossary_category", request))
        return self._fixture.get_by_name.get(request["name"], {"name": request["name"]})

    async def list_glossary_categories(self, request: ListByParentRequest) -> ListResourcesPage:
        self.calls.append(("list_glossary_categories", request))
        return self._fixture.list_by_parent.get(request["parent"], {"resources": []})

    async def get_glossary_term(self, request: GetByNameRequest) -> dict[str, object]:
        self.calls.append(("get_glossary_term", request))
        return self._fixture.get_by_name.get(request["name"], {"name": request["name"]})

    async def list_glossary_terms(self, request: ListByParentRequest) -> ListResourcesPage:
        self.calls.append(("list_glossary_terms", request))
        return self._fixture.list_by_parent.get(request["parent"], {"resources": []})
