"""Tables get command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.commands.command_shared import (
    InspectionCommandOptions,
    create_run_catalog_command,
    create_sdk_inspection_client_from_input,
)
from bq_inspector.core.shared.errors import create_input_failure
from bq_inspector.core.tables.get import get_table_metadata
from bq_inspector.input.input_parsers import parse_tables_get_input

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import ParsedCatalogInput


async def _execute_tables_get(
    input_data: ParsedCatalogInput,
    command_options: InspectionCommandOptions,
) -> Any:
    table_id = input_data.get("tableId")
    if table_id is None:
        raise create_input_failure("tableId is required.")

    client = command_options.client
    if client is None:
        client = await create_sdk_inspection_client_from_input(input_data)

    return await get_table_metadata(
        {
            "projectId": input_data["projectId"],
            "datasetId": input_data["datasetId"],
            "tableId": table_id,
        },
        client=client,
        tool_version=command_options.tool_version,
    )


tables_get_command = create_run_catalog_command(
    "tables get",
    parse_tables_get_input,
    _execute_tables_get,
)
run_tables_get = tables_get_command.run_argv
