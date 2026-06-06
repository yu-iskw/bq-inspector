"""Shared helpers for Knowledge Catalog CLI commands."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.commands.command_shared import (
    InspectionCommandOptions,
    create_run_params_command,
    create_sdk_catalog_client_from_input,
)
from bq_inspector.core.knowledge_catalog.get_resource import get_catalog_resource
from bq_inspector.core.knowledge_catalog.list_resources import list_catalog_resources
from bq_inspector.core.knowledge_catalog.lookup_entry import lookup_catalog_entry
from bq_inspector.core.knowledge_catalog.search_entries import search_catalog_entries
from bq_inspector.input.parsed_input_types import (
    ParsedKnowledgeCatalogGetInput,
    ParsedKnowledgeCatalogListInput,
    ParsedKnowledgeCatalogLookupInput,
    ParsedKnowledgeCatalogSearchInput,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bq_inspector.commands.command_shared import ParamsCommandRunner
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient
    from bq_inspector.knowledge_catalog.resource_specs import (
        KnowledgeCatalogGetDispatch,
        KnowledgeCatalogListDispatch,
    )
    from bq_inspector.schemas.command_schemas import CommandId

_CatalogInput = (
    ParsedKnowledgeCatalogSearchInput
    | ParsedKnowledgeCatalogLookupInput
    | ParsedKnowledgeCatalogGetInput
    | ParsedKnowledgeCatalogListInput
)


async def _resolve_catalog_client(
    input_data: _CatalogInput,
    command_options: InspectionCommandOptions,
) -> CatalogInspectionClient:
    client = command_options.catalog_client
    if client is None:
        client = await create_sdk_catalog_client_from_input(input_data)
    return client


async def run_catalog_command(
    input_data: _CatalogInput,
    command_options: InspectionCommandOptions,
    *,
    use_case: Callable[..., Awaitable[dict[str, Any]]],
    **kwargs: object,
) -> dict[str, Any]:
    """Resolve a catalog client and run a Knowledge Catalog use case."""
    client = await _resolve_catalog_client(input_data, command_options)
    return await use_case(
        input_data,
        client=client,
        tool_version=command_options.tool_version,
        **kwargs,
    )


def create_catalog_search_command(
    command_id: CommandId,
    parse_fn: Callable[[object], ParsedKnowledgeCatalogSearchInput],
) -> ParamsCommandRunner:
    """Build a params command runner for catalog search."""

    async def execute(
        input_data: ParsedKnowledgeCatalogSearchInput,
        command_options: InspectionCommandOptions,
    ) -> dict[str, Any]:
        return await run_catalog_command(
            input_data,
            command_options,
            use_case=search_catalog_entries,
        )

    return create_run_params_command(command_id, parse_fn, execute)


def create_catalog_lookup_command(
    command_id: CommandId,
    parse_fn: Callable[[object], ParsedKnowledgeCatalogLookupInput],
) -> ParamsCommandRunner:
    """Build a params command runner for catalog entries lookup."""

    async def execute(
        input_data: ParsedKnowledgeCatalogLookupInput,
        command_options: InspectionCommandOptions,
    ) -> dict[str, Any]:
        return await run_catalog_command(
            input_data,
            command_options,
            use_case=lookup_catalog_entry,
        )

    return create_run_params_command(command_id, parse_fn, execute)


def create_catalog_get_command(
    command_id: CommandId,
    parse_fn: Callable[[object], ParsedKnowledgeCatalogGetInput],
    *,
    dispatch: KnowledgeCatalogGetDispatch,
) -> ParamsCommandRunner:
    """Build a params command runner for a catalog get use case."""

    async def execute(
        input_data: ParsedKnowledgeCatalogGetInput,
        command_options: InspectionCommandOptions,
    ) -> dict[str, Any]:
        return await run_catalog_command(
            input_data,
            command_options,
            use_case=get_catalog_resource,
            dispatch=dispatch,
        )

    return create_run_params_command(command_id, parse_fn, execute)


def create_catalog_list_command(
    command_id: CommandId,
    parse_fn: Callable[[object], ParsedKnowledgeCatalogListInput],
    *,
    collection_key: str,
    dispatch: KnowledgeCatalogListDispatch,
) -> ParamsCommandRunner:
    """Build a params command runner for a catalog list use case."""

    async def execute(
        input_data: ParsedKnowledgeCatalogListInput,
        command_options: InspectionCommandOptions,
    ) -> dict[str, Any]:
        return await run_catalog_command(
            input_data,
            command_options,
            use_case=list_catalog_resources,
            collection_key=collection_key,
            dispatch=dispatch,
        )

    return create_run_params_command(command_id, parse_fn, execute)
