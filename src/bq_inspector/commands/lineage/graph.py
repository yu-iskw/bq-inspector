"""Lineage graph command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.commands.command_shared import (
    InspectionCommandOptions,
    create_run_params_command,
    create_sdk_lineage_client_from_input,
)
from bq_inspector.core.lineage.search_graph import LineageGraphRequest, search_table_lineage_graph
from bq_inspector.input.input_parsers import parse_lineage_graph_input

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import ParsedLineageGraphInput


def _build_graph_request(input_data: ParsedLineageGraphInput) -> LineageGraphRequest:
    request: LineageGraphRequest = {
        "clientProjectId": input_data["clientProjectId"],
        "location": input_data["location"],
        "table": {
            "projectId": input_data["projectId"],
            "datasetId": input_data["datasetId"],
            "tableId": input_data["tableId"],
        },
        "direction": input_data["direction"],
    }
    if "maxDepth" in input_data:
        request["maxDepth"] = input_data["maxDepth"]
    if "maxResults" in input_data:
        request["maxResults"] = input_data["maxResults"]
    return request


async def _execute_lineage_graph(
    input_data: ParsedLineageGraphInput,
    command_options: InspectionCommandOptions,
) -> Any:
    client = command_options.lineage_client
    if client is None:
        client = await create_sdk_lineage_client_from_input(input_data)

    return await search_table_lineage_graph(
        _build_graph_request(input_data),
        client=client,
        tool_version=command_options.tool_version,
    )


lineage_graph_command = create_run_params_command(
    "lineage graph",
    parse_lineage_graph_input,
    _execute_lineage_graph,
)
run_lineage_graph = lineage_graph_command.run_argv
