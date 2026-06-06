"""Tables list command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.commands.command_shared import (
    InspectionCommandOptions,
    create_run_params_command,
    create_sdk_inspection_client_from_input,
)
from bq_inspector.core.tables.list import list_tables_metadata
from bq_inspector.input.input_parsers import parse_tables_list_input

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import ParsedDatasetTableInput


async def _execute_tables_list(
    input_data: ParsedDatasetTableInput,
    command_options: InspectionCommandOptions,
) -> Any:
    client = command_options.client
    if client is None:
        client = await create_sdk_inspection_client_from_input(input_data)

    return await list_tables_metadata(
        {"projectId": input_data["projectId"], "datasetId": input_data["datasetId"]},
        client=client,
        tool_version=command_options.tool_version,
    )


tables_list_command = create_run_params_command(
    "tables list",
    parse_tables_list_input,
    _execute_tables_list,
)
run_tables_list = tables_list_command.run_argv
