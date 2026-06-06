"""Knowledge Catalog CLI command registrations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.commands.catalog._shared import (
    create_catalog_get_command,
    create_catalog_list_command,
    create_catalog_lookup_command,
    create_catalog_search_command,
)
from bq_inspector.commands.catalog.resource_specs import (
    KNOWLEDGE_CATALOG_GET_COMMANDS,
    KNOWLEDGE_CATALOG_LIST_COMMANDS,
    knowledge_catalog_command_id,
    knowledge_catalog_export_name,
)
from bq_inspector.input.input_parsers import (
    parse_knowledge_catalog_get_input,
    parse_knowledge_catalog_list_input,
    parse_knowledge_catalog_lookup_input,
    parse_knowledge_catalog_search_input,
)

if TYPE_CHECKING:
    from bq_inspector.commands.command_shared import ParamsCommandRunner
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient
    from bq_inspector.knowledge_catalog.types.requests import GetByNameRequest, ListByParentRequest


def _client_get_fetch(client_method: str) -> Any:
    async def fetch(
        client: CatalogInspectionClient,
        request: GetByNameRequest,
    ) -> dict[str, object]:
        method = getattr(client, client_method)
        return await method(request)

    return fetch


def _client_list_fetch(client_method: str) -> Any:
    async def fetch(
        client: CatalogInspectionClient,
        request: ListByParentRequest,
    ) -> dict[str, object]:
        method = getattr(client, client_method)
        return await method(request)

    return fetch


def _build_get_command(spec: Any) -> ParamsCommandRunner:
    command_id = knowledge_catalog_command_id(spec.subgroup, "get")

    def parse(raw: object) -> Any:
        return parse_knowledge_catalog_get_input(command_id, raw)

    return create_catalog_get_command(
        command_id,
        parse,
        fetch=_client_get_fetch(spec.client_method),
    )


def _build_list_command(spec: Any) -> ParamsCommandRunner:
    command_id = knowledge_catalog_command_id(spec.subgroup, "list")

    def parse(raw: object) -> Any:
        return parse_knowledge_catalog_list_input(command_id, raw)

    return create_catalog_list_command(
        command_id,
        parse,
        collection_key=spec.collection_key,
        fetch=_client_list_fetch(spec.client_method),
    )


catalog_search_command = create_catalog_search_command(
    "catalog search",
    parse_knowledge_catalog_search_input,
)

catalog_entries_lookup_command = create_catalog_lookup_command(
    "catalog entries lookup",
    parse_knowledge_catalog_lookup_input,
)

_COMMAND_EXPORTS: dict[str, ParamsCommandRunner] = {
    "catalog_search_command": catalog_search_command,
    "catalog_entries_lookup_command": catalog_entries_lookup_command,
}

for _get_spec in KNOWLEDGE_CATALOG_GET_COMMANDS:
    _COMMAND_EXPORTS[knowledge_catalog_export_name(_get_spec.subgroup, "get")] = _build_get_command(
        _get_spec
    )

for _list_spec in KNOWLEDGE_CATALOG_LIST_COMMANDS:
    _COMMAND_EXPORTS[knowledge_catalog_export_name(_list_spec.subgroup, "list")] = (
        _build_list_command(_list_spec)
    )

globals().update(_COMMAND_EXPORTS)
