"""Shared helpers for asset-lineage CLI commands."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from bq_inspector.commands.command_shared import (
    InspectionCommandOptions,
    create_run_params_command,
    create_sdk_lineage_client_from_input,
)
from bq_inspector.core.asset_lineage.requests import (
    LineageGraphRequest,
    LineageLinksRequest,
    TableLineageRequest,
)
from bq_inspector.core.shared.types import LineageGraphResponse, LineageLinksResponse
from bq_inspector.input.parsed_input_types import ParsedLineageInput

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bq_inspector.bigquery.types.refs import TableRef
    from bq_inspector.commands.command_shared import ParamsCommandRunner
    from bq_inspector.schemas.command_schemas import CommandId

_InputT = TypeVar("_InputT", bound=ParsedLineageInput)
_RequestT = TypeVar("_RequestT", LineageLinksRequest, LineageGraphRequest)
_ResponseT = TypeVar("_ResponseT", LineageLinksResponse, LineageGraphResponse)


def table_ref_from_parsed(input_data: ParsedLineageInput) -> TableRef:
    """Build a table ref from parsed lineage params."""
    return {
        "projectId": input_data["projectId"],
        "datasetId": input_data["datasetId"],
        "tableId": input_data["tableId"],
    }


def base_lineage_request(input_data: ParsedLineageInput) -> TableLineageRequest:
    """Map parsed input to shared table-lineage request fields."""
    return {
        "clientProjectId": input_data["clientProjectId"],
        "location": input_data["location"],
        "table": table_ref_from_parsed(input_data),
        "direction": input_data["direction"],
    }


async def run_asset_lineage_command(
    input_data: _InputT,
    command_options: InspectionCommandOptions,
    *,
    build_request: Callable[[_InputT], _RequestT],
    search_fn: Callable[..., Awaitable[_ResponseT]],
) -> _ResponseT:
    """Resolve a lineage client and run a table-lineage use case."""
    client = command_options.lineage_client
    if client is None:
        client = await create_sdk_lineage_client_from_input(input_data)

    return await search_fn(
        build_request(input_data),
        client=client,
        tool_version=command_options.tool_version,
    )


def create_asset_lineage_params_command(
    command_id: CommandId,
    parse_fn: Callable[[object], _InputT],
    build_request: Callable[[_InputT], _RequestT],
    search_fn: Callable[..., Awaitable[_ResponseT]],
) -> ParamsCommandRunner:
    """Build a params command runner for asset-lineage search use cases."""

    async def execute(
        input_data: _InputT,
        command_options: InspectionCommandOptions,
    ) -> _ResponseT:
        return await run_asset_lineage_command(
            input_data,
            command_options,
            build_request=build_request,
            search_fn=search_fn,
        )

    return create_run_params_command(command_id, parse_fn, execute)
