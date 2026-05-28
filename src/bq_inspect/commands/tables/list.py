"""Tables list command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspect.cli.argv.operational_argv import parse_operational_argv
from bq_inspect.cli.input.input_parsers import parse_tables_list_input
from bq_inspect.cli.params.parse_params import resolve_params_value
from bq_inspect.commands.command_shared import create_sdk_inspection_client_from_input
from bq_inspect.core.tables.list import list_tables_metadata
from bq_inspect.schemas.command_schemas import get_command_schema

if TYPE_CHECKING:
    from bq_inspect.bigquery.port.inspection_client import BigQueryInspectionClient
    from bq_inspect.cli.input.parsed_input_types import ParsedCatalogInput


class TablesListCommandOptions:
    """Options for tables list command execution."""

    def __init__(
        self,
        *,
        client: BigQueryInspectionClient | None = None,
        tool_version: str,
    ) -> None:
        self.client = client
        self.tool_version = tool_version


async def run_tables_list(
    argv: list[str],
    command_options: TablesListCommandOptions,
) -> Any:
    """Run tables list with schema discovery or params execution."""
    argv_parsed = parse_operational_argv(argv)

    if argv_parsed["kind"] == "input-schema":
        return get_command_schema("tables list", "input")

    if argv_parsed["kind"] == "output-schema":
        return get_command_schema("tables list", "output")

    raw = resolve_params_value(argv_parsed["params"])
    input_data = parse_tables_list_input(raw)

    return await _execute_tables_list(input_data, command_options)


async def _execute_tables_list(
    input_data: ParsedCatalogInput,
    command_options: TablesListCommandOptions,
) -> Any:
    client = command_options.client
    if client is None:
        client = await create_sdk_inspection_client_from_input(input_data)

    return await list_tables_metadata(
        {"projectId": input_data["projectId"], "datasetId": input_data["datasetId"]},
        client=client,
        tool_version=command_options.tool_version,
    )
