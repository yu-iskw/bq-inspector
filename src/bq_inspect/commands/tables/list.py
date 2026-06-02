"""Tables list command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspect.input.input_parsers import parse_tables_list_input
from bq_inspect.commands.command_shared import (
    InspectionCommandOptions,
    create_run_catalog_command,
    create_sdk_inspection_client_from_input,
)
from bq_inspect.core.tables.list import list_tables_metadata

if TYPE_CHECKING:
    from bq_inspect.input.parsed_input_types import ParsedCatalogInput


async def _execute_tables_list(
    input_data: ParsedCatalogInput,
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


tables_list_command = create_run_catalog_command(
    "tables list",
    parse_tables_list_input,
    _execute_tables_list,
)
run_tables_list = tables_list_command.run_argv
