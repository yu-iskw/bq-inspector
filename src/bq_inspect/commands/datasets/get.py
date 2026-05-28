"""Datasets get command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspect.cli.input.input_parsers import parse_datasets_get_input
from bq_inspect.commands.command_shared import (
    InspectionCommandOptions,
    create_run_catalog_command,
    create_sdk_inspection_client_from_input,
)
from bq_inspect.core.datasets.get import get_dataset_metadata

if TYPE_CHECKING:
    from bq_inspect.cli.input.parsed_input_types import ParsedCatalogInput


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


run_datasets_get = create_run_catalog_command(
    "datasets get",
    parse_datasets_get_input,
    _execute_datasets_get,
)
