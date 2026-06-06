"""Google Cloud SDK adapter for read-only Knowledge Catalog inspection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from google.cloud import dataplex_v1

from bq_inspector.commands.catalog.resource_specs import (
    KNOWLEDGE_CATALOG_GET_RESOURCES,
    KNOWLEDGE_CATALOG_LIST_RESOURCES,
    KnowledgeCatalogGetResourceSpec,
    KnowledgeCatalogListResourceSpec,
)
from bq_inspector.core.shared.invoke_sync import invoke_sync
from bq_inspector.core.shared.pagination import read_next_page_token
from bq_inspector.core.shared.protobuf_dict import message_to_dict

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


def _catalog_dict(message: object) -> dict[str, object]:
    return message_to_dict(message, preserving_proto_field_name=False)


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
        "resources": [_catalog_dict(item) for item in items],
    }
    if token := read_next_page_token(pager):
        page["nextPageToken"] = token
    return page


class SdkCatalogClient:
    """Read-only Knowledge Catalog client backed by google-cloud-dataplex."""

    def __init__(self, auth_client: Credentials) -> None:
        self._catalog = dataplex_v1.CatalogServiceClient(credentials=auth_client)
        self._glossary = dataplex_v1.BusinessGlossaryServiceClient(credentials=auth_client)

    @property
    def catalog_service(self) -> dataplex_v1.CatalogServiceClient:
        return self._catalog

    @property
    def glossary_service(self) -> dataplex_v1.BusinessGlossaryServiceClient:
        return self._glossary

    def service_for_kind(self, service: str) -> object:
        if service == "catalog":
            return self.catalog_service
        return self.glossary_service

    async def get_named_resource(  # noqa: PLR0913
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
        return _catalog_dict(resource)

    async def list_parent_resources(  # noqa: PLR0913
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
                {"entry": _catalog_dict(result.dataplex_entry)}
                for result in pager.results  # type: ignore[attr-defined]
            ],
            "totalSize": pager.total_size,  # type: ignore[attr-defined]
            "unreachable": list(pager.unreachable),  # type: ignore[attr-defined]
        }
        if token := read_next_page_token(pager):
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
        return _catalog_dict(entry)

    @staticmethod
    def make_get_method(spec: KnowledgeCatalogGetResourceSpec) -> Any:
        async def method(self: SdkCatalogClient, request: GetByNameRequest) -> dict[str, object]:
            return await self.get_named_resource(
                request,
                request_cls=getattr(dataplex_v1, spec.request_type_name),
                service=self.service_for_kind(spec.service),
                method_name=spec.sdk_method,
                api=spec.api,
                apply_entry_view=spec.apply_entry_view,
            )

        method.__name__ = spec.client_method
        return method

    @staticmethod
    def make_list_method(spec: KnowledgeCatalogListResourceSpec) -> Any:
        async def method(self: SdkCatalogClient, request: ListByParentRequest) -> ListResourcesPage:
            return await self.list_parent_resources(
                request,
                request_cls=getattr(dataplex_v1, spec.request_type_name),
                service=self.service_for_kind(spec.service),
                method_name=spec.sdk_method,
                api=spec.api,
                items_attr=spec.items_attr,
            )

        method.__name__ = spec.client_method
        return method


for _get_spec in KNOWLEDGE_CATALOG_GET_RESOURCES:
    setattr(SdkCatalogClient, _get_spec.client_method, SdkCatalogClient.make_get_method(_get_spec))

for _list_spec in KNOWLEDGE_CATALOG_LIST_RESOURCES:
    setattr(
        SdkCatalogClient,
        _list_spec.client_method,
        SdkCatalogClient.make_list_method(_list_spec),
    )
