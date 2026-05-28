"""Datasets get command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspect.cli.argv.operational_argv import parse_operational_argv
from bq_inspect.cli.input.input_parsers import parse_datasets_get_input
from bq_inspect.cli.params.parse_params import resolve_params_value
from bq_inspect.commands.command_shared import create_sdk_inspection_client_from_input
from bq_inspect.core.datasets.get import get_dataset_metadata
from bq_inspect.schemas.command_schemas import get_command_schema

if TYPE_CHECKING:
    from bq_inspect.bigquery.port.inspection_client import BigQueryInspectionClient


class DatasetsGetCommandOptions:
    """Options for datasets get command execution."""

    def __init__(
        self,
        *,
        client: BigQueryInspectionClient | None = None,
        tool_version: str,
    ) -> None:
        self.client = client
        self.tool_version = tool_version


async def run_datasets_get(
    argv: list[str],
    command_options: DatasetsGetCommandOptions,
) -> Any:
    """Run datasets get with schema discovery or params execution."""
    argv_parsed = parse_operational_argv(argv)

    if argv_parsed["kind"] == "input-schema":
        return get_command_schema("datasets get", "input")

    if argv_parsed["kind"] == "output-schema":
        return get_command_schema("datasets get", "output")

    raw = resolve_params_value(argv_parsed["params"])
    input_data = parse_datasets_get_input(raw)

    return await _execute_datasets_get(input_data, command_options)


async def _execute_datasets_get(
    input_data: dict[str, Any],
    command_options: DatasetsGetCommandOptions,
) -> Any:
    client = command_options.client
    if client is None:
        client = await create_sdk_inspection_client_from_input(input_data)

    return await get_dataset_metadata(
        {"projectId": input_data["projectId"], "datasetId": input_data["datasetId"]},
        client=client,
        tool_version=command_options.tool_version,
    )
