"""Google Cloud SDK adapter for read-only Knowledge Catalog inspection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from google.cloud import dataplex_v1
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

from bq_inspector.core.shared.invoke_sync import invoke_sync

if TYPE_CHECKING:
    from google.auth.credentials import Credentials

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

_ENTRY_VIEW_MAP: dict[str, dataplex_v1.EntryView] = {
    "BASIC": dataplex_v1.EntryView.BASIC,
    "FULL": dataplex_v1.EntryView.FULL,
    "CUSTOM": dataplex_v1.EntryView.CUSTOM,
    "ALL": dataplex_v1.EntryView.ALL,
}


def _message_to_dict(message: object) -> dict[str, object]:
    protobuf = getattr(message, "_pb", message)
    if not isinstance(protobuf, Message):
        raise TypeError("Expected protobuf message convertible to dict")
    result = MessageToDict(protobuf, preserving_proto_field_name=False)
    if isinstance(result, dict):
        return result
    raise TypeError("Expected protobuf message convertible to dict")


def _read_next_page_token(pager: object) -> str | None:
    token = getattr(pager, "next_page_token", None)
    if isinstance(token, str) and len(token) > 0:
        return token
    return None


def _resolve_entry_view(view: str | None) -> dataplex_v1.EntryView | None:
    if view is None:
        return None
    return _ENTRY_VIEW_MAP.get(view)


def _apply_search_options(sdk_request: object, request: SearchEntriesRequest) -> None:
    page_size = request.get("pageSize")
    if page_size is not None:
        sdk_request.page_size = page_size  # type: ignore[attr-defined]

    page_token = request.get("pageToken")
    if page_token is not None:
        sdk_request.page_token = page_token  # type: ignore[attr-defined]

    scope = request.get("scope")
    if scope is not None:
        sdk_request.scope = scope  # type: ignore[attr-defined]

    order_by = request.get("orderBy")
    if order_by is not None:
        sdk_request.order_by = order_by  # type: ignore[attr-defined]

    semantic_search = request.get("semanticSearch")
    if semantic_search is not None:
        sdk_request.semantic_search = semantic_search  # type: ignore[attr-defined]


def _apply_entry_view_fields(
    sdk_request: object,
    request: GetByNameRequest | LookupEntryRequest,
) -> None:
    view = _resolve_entry_view(request.get("view"))
    if view is not None:
        sdk_request.view = view  # type: ignore[attr-defined]

    aspect_types = request.get("aspectTypes")
    if aspect_types is not None:
        sdk_request.aspect_types.extend(aspect_types)  # type: ignore[attr-defined]

    paths = request.get("paths")
    if paths is not None:
        sdk_request.paths.extend(paths)  # type: ignore[attr-defined]


def _apply_list_pagination(sdk_request: object, request: ListByParentRequest) -> None:
    page_size = request.get("pageSize")
    if page_size is not None:
        sdk_request.page_size = page_size  # type: ignore[attr-defined]

    page_token = request.get("pageToken")
    if page_token is not None:
        sdk_request.page_token = page_token  # type: ignore[attr-defined]

    filter_value = request.get("filter")
    if filter_value is not None:
        sdk_request.filter = filter_value  # type: ignore[attr-defined]

    order_by = request.get("orderBy")
    if order_by is not None:
        sdk_request.order_by = order_by  # type: ignore[attr-defined]


def _list_page_from_pager(
    pager: object,
    *,
    items_attr: str,
) -> ListResourcesPage:
    items = getattr(pager, items_attr, [])
    page: ListResourcesPage = {
        "resources": [_message_to_dict(item) for item in items],
    }
    if token := _read_next_page_token(pager):
        page["nextPageToken"] = token
    return page


class SdkCatalogClient:
    """Read-only Knowledge Catalog client backed by google-cloud-dataplex."""

    def __init__(self, auth_client: Credentials) -> None:
        self._catalog = dataplex_v1.CatalogServiceClient(credentials=auth_client)
        self._glossary = dataplex_v1.BusinessGlossaryServiceClient(credentials=auth_client)

    async def _get_resource(  # noqa: PLR0913
        self,
        request: GetByNameRequest,
        *,
        request_cls: type[Any],
        service: object,
        method_name: str,
        api: str,
        apply_entry_view: bool = False,
    ) -> dict[str, object]:
        sdk_request = request_cls(name=request["name"])
        if apply_entry_view:
            _apply_entry_view_fields(sdk_request, request)

        method = getattr(service, method_name)

        def _call() -> object:
            return method(request=sdk_request)

        resource = await invoke_sync(_call, api=api)
        return _message_to_dict(resource)

    async def _list_resources(  # noqa: PLR0913
        self,
        request: ListByParentRequest,
        *,
        request_cls: type[Any],
        service: object,
        method_name: str,
        api: str,
        items_attr: str,
    ) -> ListResourcesPage:
        sdk_request = request_cls(parent=request["parent"])
        _apply_list_pagination(sdk_request, request)
        method = getattr(service, method_name)

        def _call() -> object:
            return method(request=sdk_request)

        pager = await invoke_sync(_call, api=api)
        return _list_page_from_pager(pager, items_attr=items_attr)

    async def search_entries(self, request: SearchEntriesRequest) -> SearchEntriesPage:
        sdk_request = dataplex_v1.SearchEntriesRequest(
            name=request["name"],
            query=request["query"],
        )
        _apply_search_options(sdk_request, request)

        def _call() -> object:
            return self._catalog.search_entries(request=sdk_request)

        pager = await invoke_sync(_call, api="dataplex.projects.locations.searchEntries")
        page: SearchEntriesPage = {
            "entries": [
                {"entry": _message_to_dict(result.dataplex_entry)}
                for result in pager.results  # type: ignore[attr-defined]
            ],
            "totalSize": pager.total_size,  # type: ignore[attr-defined]
            "unreachable": list(pager.unreachable),  # type: ignore[attr-defined]
        }
        if token := _read_next_page_token(pager):
            page["nextPageToken"] = token
        return page

    async def lookup_entry(self, request: LookupEntryRequest) -> dict[str, object]:
        sdk_request = dataplex_v1.LookupEntryRequest(
            name=request["name"],
            entry=request["entry"],
        )
        _apply_entry_view_fields(sdk_request, request)

        def _call() -> object:
            return self._catalog.lookup_entry(request=sdk_request)

        entry = await invoke_sync(_call, api="dataplex.projects.locations.lookupEntry")
        return _message_to_dict(entry)

    async def get_entry(self, request: GetByNameRequest) -> dict[str, object]:
        return await self._get_resource(
            request,
            request_cls=dataplex_v1.GetEntryRequest,
            service=self._catalog,
            method_name="get_entry",
            api="dataplex.projects.locations.entryGroups.entries.get",
            apply_entry_view=True,
        )

    async def list_entries(self, request: ListByParentRequest) -> ListResourcesPage:
        return await self._list_resources(
            request,
            request_cls=dataplex_v1.ListEntriesRequest,
            service=self._catalog,
            method_name="list_entries",
            api="dataplex.projects.locations.entryGroups.entries.list",
            items_attr="entries",
        )

    async def get_entry_group(self, request: GetByNameRequest) -> dict[str, object]:
        return await self._get_resource(
            request,
            request_cls=dataplex_v1.GetEntryGroupRequest,
            service=self._catalog,
            method_name="get_entry_group",
            api="dataplex.projects.locations.entryGroups.get",
        )

    async def list_entry_groups(self, request: ListByParentRequest) -> ListResourcesPage:
        return await self._list_resources(
            request,
            request_cls=dataplex_v1.ListEntryGroupsRequest,
            service=self._catalog,
            method_name="list_entry_groups",
            api="dataplex.projects.locations.entryGroups.list",
            items_attr="entry_groups",
        )

    async def get_entry_type(self, request: GetByNameRequest) -> dict[str, object]:
        return await self._get_resource(
            request,
            request_cls=dataplex_v1.GetEntryTypeRequest,
            service=self._catalog,
            method_name="get_entry_type",
            api="dataplex.projects.locations.entryTypes.get",
        )

    async def list_entry_types(self, request: ListByParentRequest) -> ListResourcesPage:
        return await self._list_resources(
            request,
            request_cls=dataplex_v1.ListEntryTypesRequest,
            service=self._catalog,
            method_name="list_entry_types",
            api="dataplex.projects.locations.entryTypes.list",
            items_attr="entry_types",
        )

    async def get_aspect_type(self, request: GetByNameRequest) -> dict[str, object]:
        return await self._get_resource(
            request,
            request_cls=dataplex_v1.GetAspectTypeRequest,
            service=self._catalog,
            method_name="get_aspect_type",
            api="dataplex.projects.locations.aspectTypes.get",
        )

    async def list_aspect_types(self, request: ListByParentRequest) -> ListResourcesPage:
        return await self._list_resources(
            request,
            request_cls=dataplex_v1.ListAspectTypesRequest,
            service=self._catalog,
            method_name="list_aspect_types",
            api="dataplex.projects.locations.aspectTypes.list",
            items_attr="aspect_types",
        )

    async def get_entry_link(self, request: GetByNameRequest) -> dict[str, object]:
        return await self._get_resource(
            request,
            request_cls=dataplex_v1.GetEntryLinkRequest,
            service=self._catalog,
            method_name="get_entry_link",
            api="dataplex.projects.locations.entryGroups.entryLinks.get",
        )

    async def get_glossary(self, request: GetByNameRequest) -> dict[str, object]:
        return await self._get_resource(
            request,
            request_cls=dataplex_v1.GetGlossaryRequest,
            service=self._glossary,
            method_name="get_glossary",
            api="dataplex.projects.locations.glossaries.get",
        )

    async def list_glossaries(self, request: ListByParentRequest) -> ListResourcesPage:
        return await self._list_resources(
            request,
            request_cls=dataplex_v1.ListGlossariesRequest,
            service=self._glossary,
            method_name="list_glossaries",
            api="dataplex.projects.locations.glossaries.list",
            items_attr="glossaries",
        )

    async def get_glossary_category(self, request: GetByNameRequest) -> dict[str, object]:
        return await self._get_resource(
            request,
            request_cls=dataplex_v1.GetGlossaryCategoryRequest,
            service=self._glossary,
            method_name="get_glossary_category",
            api="dataplex.projects.locations.glossaries.categories.get",
        )

    async def list_glossary_categories(self, request: ListByParentRequest) -> ListResourcesPage:
        return await self._list_resources(
            request,
            request_cls=dataplex_v1.ListGlossaryCategoriesRequest,
            service=self._glossary,
            method_name="list_glossary_categories",
            api="dataplex.projects.locations.glossaries.categories.list",
            items_attr="categories",
        )

    async def get_glossary_term(self, request: GetByNameRequest) -> dict[str, object]:
        return await self._get_resource(
            request,
            request_cls=dataplex_v1.GetGlossaryTermRequest,
            service=self._glossary,
            method_name="get_glossary_term",
            api="dataplex.projects.locations.glossaries.terms.get",
        )

    async def list_glossary_terms(self, request: ListByParentRequest) -> ListResourcesPage:
        return await self._list_resources(
            request,
            request_cls=dataplex_v1.ListGlossaryTermsRequest,
            service=self._glossary,
            method_name="list_glossary_terms",
            api="dataplex.projects.locations.glossaries.terms.list",
            items_attr="terms",
        )
