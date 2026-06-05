"""Lineage links command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.commands.command_shared import (
    InspectionCommandOptions,
    create_run_params_command,
    create_sdk_lineage_client_from_input,
)
from bq_inspector.core.lineage.search_links import LineageLinksRequest, search_table_links
from bq_inspector.input.input_parsers import parse_lineage_links_input

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import ParsedLineageInput


def _build_links_request(input_data: ParsedLineageInput) -> LineageLinksRequest:
    request: LineageLinksRequest = {
        "clientProjectId": input_data["clientProjectId"],
        "location": input_data["location"],
        "table": {
            "projectId": input_data["projectId"],
            "datasetId": input_data["datasetId"],
            "tableId": input_data["tableId"],
        },
        "direction": input_data["direction"],
    }
    if "pageSize" in input_data:
        request["pageSize"] = input_data["pageSize"]
    if "pageToken" in input_data:
        request["pageToken"] = input_data["pageToken"]
    return request


async def _execute_lineage_links(
    input_data: ParsedLineageInput,
    command_options: InspectionCommandOptions,
) -> Any:
    client = command_options.lineage_client
    if client is None:
        client = await create_sdk_lineage_client_from_input(input_data)

    return await search_table_links(
        _build_links_request(input_data),
        client=client,
        tool_version=command_options.tool_version,
    )


lineage_links_command = create_run_params_command(
    "lineage links",
    parse_lineage_links_input,
    _execute_lineage_links,
)
run_lineage_links = lineage_links_command.run_argv
