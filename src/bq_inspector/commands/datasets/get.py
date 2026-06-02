"""Datasets get command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.commands.command_shared import (
    InspectionCommandOptions,
    create_run_catalog_command,
    create_sdk_inspection_client_from_input,
)
from bq_inspector.core.datasets.get import get_dataset_metadata
from bq_inspector.input.input_parsers import parse_datasets_get_input

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import ParsedCatalogInput


async def _execute_datasets_get(
    input_data: ParsedCatalogInput,
    command_options: InspectionCommandOptions,
) -> Any:
    client = command_options.client
    if client is None:
        client = await create_sdk_inspection_client_from_input(input_data)

    return await get_dataset_metadata(
        {"projectId": input_data["projectId"], "datasetId": input_data["datasetId"]},
        client=client,
        tool_version=command_options.tool_version,
    )


datasets_get_command = create_run_catalog_command(
    "datasets get",
    parse_datasets_get_input,
    _execute_datasets_get,
)
run_datasets_get = datasets_get_command.run_argv
