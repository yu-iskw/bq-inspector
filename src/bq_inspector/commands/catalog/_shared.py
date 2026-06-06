"""Shared helpers for Knowledge Catalog CLI commands."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

from bq_inspector.commands.command_shared import (
    InspectionCommandOptions,
    create_run_params_command,
    create_sdk_catalog_client_from_input,
)
from bq_inspector.core.knowledge_catalog.get_resource import get_catalog_resource
from bq_inspector.core.knowledge_catalog.list_resources import list_catalog_resources
from bq_inspector.core.knowledge_catalog.lookup_entry import lookup_catalog_entry
from bq_inspector.core.knowledge_catalog.search_entries import search_catalog_entries

if TYPE_CHECKING:
    from bq_inspector.commands.command_shared import ParamsCommandRunner
    from bq_inspector.input.parsed_input_types import (
        ParsedKnowledgeCatalogGetInput,
        ParsedKnowledgeCatalogListInput,
        ParsedKnowledgeCatalogLookupInput,
        ParsedKnowledgeCatalogSearchInput,
    )
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient
    from bq_inspector.schemas.command_schemas import CommandId


async def _resolve_catalog_client(
    input_data: ParsedKnowledgeCatalogSearchInput
    | ParsedKnowledgeCatalogLookupInput
    | ParsedKnowledgeCatalogGetInput
    | ParsedKnowledgeCatalogListInput,
    command_options: InspectionCommandOptions,
) -> CatalogInspectionClient:
    client = command_options.catalog_client
    if client is None:
        client = await create_sdk_catalog_client_from_input(input_data)
    return client


async def run_catalog_search_command(
    input_data: ParsedKnowledgeCatalogSearchInput,
    command_options: InspectionCommandOptions,
) -> dict[str, Any]:
    """Run catalog search with client resolution."""
    client = await _resolve_catalog_client(input_data, command_options)
    return await search_catalog_entries(
        input_data,
        client=client,
        tool_version=command_options.tool_version,
    )


async def run_catalog_lookup_command(
    input_data: ParsedKnowledgeCatalogLookupInput,
    command_options: InspectionCommandOptions,
) -> dict[str, Any]:
    """Run catalog entries lookup with client resolution."""
    client = await _resolve_catalog_client(input_data, command_options)
    return await lookup_catalog_entry(
        input_data,
        client=client,
        tool_version=command_options.tool_version,
    )


async def run_catalog_get_command(
    input_data: ParsedKnowledgeCatalogGetInput,
    command_options: InspectionCommandOptions,
    *,
    fetch: Callable[..., Any],
) -> dict[str, Any]:
    """Run a catalog get command with client resolution."""
    client = await _resolve_catalog_client(input_data, command_options)
    return await get_catalog_resource(
        input_data,
        client=client,
        tool_version=command_options.tool_version,
        fetch=fetch,
    )


async def run_catalog_list_command(
    input_data: ParsedKnowledgeCatalogListInput,
    command_options: InspectionCommandOptions,
    *,
    collection_key: str,
    fetch: Callable[..., Any],
) -> dict[str, Any]:
    """Run a catalog list command with client resolution."""
    client = await _resolve_catalog_client(input_data, command_options)
    return await list_catalog_resources(
        input_data,
        client=client,
        tool_version=command_options.tool_version,
        collection_key=collection_key,
        fetch=fetch,
    )


def create_catalog_search_command(
    command_id: CommandId,
    parse_fn: Callable[[object], ParsedKnowledgeCatalogSearchInput],
) -> ParamsCommandRunner:
    """Build a params command runner for catalog search."""
    return create_run_params_command(command_id, parse_fn, run_catalog_search_command)


def create_catalog_lookup_command(
    command_id: CommandId,
    parse_fn: Callable[[object], ParsedKnowledgeCatalogLookupInput],
) -> ParamsCommandRunner:
    """Build a params command runner for catalog entries lookup."""
    return create_run_params_command(command_id, parse_fn, run_catalog_lookup_command)


def create_catalog_get_command(
    command_id: CommandId,
    parse_fn: Callable[[object], ParsedKnowledgeCatalogGetInput],
    fetch: Callable[..., Any],
) -> ParamsCommandRunner:
    """Build a params command runner for a catalog get use case."""

    async def execute(
        input_data: ParsedKnowledgeCatalogGetInput,
        command_options: InspectionCommandOptions,
    ) -> dict[str, Any]:
        return await run_catalog_get_command(input_data, command_options, fetch=fetch)

    return create_run_params_command(command_id, parse_fn, execute)


def create_catalog_list_command(
    command_id: CommandId,
    parse_fn: Callable[[object], ParsedKnowledgeCatalogListInput],
    *,
    collection_key: str,
    fetch: Callable[..., Any],
) -> ParamsCommandRunner:
    """Build a params command runner for a catalog list use case."""

    async def execute(
        input_data: ParsedKnowledgeCatalogListInput,
        command_options: InspectionCommandOptions,
    ) -> dict[str, Any]:
        return await run_catalog_list_command(
            input_data,
            command_options,
            collection_key=collection_key,
            fetch=fetch,
        )

    return create_run_params_command(command_id, parse_fn, execute)
