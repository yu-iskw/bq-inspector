"""Shared command helpers for building BigQuery clients."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspect.bigquery.adapters.google_cloud.sdk_inspection_client import SdkBigQueryClient
from bq_inspect.bigquery.auth.create_auth_client import AuthClientOptions, create_auth_client
from bq_inspect.cli.argv.operational_argv import parse_operational_argv
from bq_inspect.cli.params.parse_params import resolve_params_value
from bq_inspect.schemas.command_schemas import CommandId, get_command_schema

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bq_inspect.bigquery.port.inspection_client import BigQueryInspectionClient
    from bq_inspect.core.shared.impersonation_fields import ImpersonationFields


class InspectionCommandOptions:
    """Shared options for command execution with optional client injection."""

    def __init__(
        self,
        *,
        client: BigQueryInspectionClient | None = None,
        tool_version: str,
    ) -> None:
        self.client = client
        self.tool_version = tool_version


JobsViewCommandOptions = InspectionCommandOptions
JobsListCommandOptions = InspectionCommandOptions
DatasetsGetCommandOptions = InspectionCommandOptions
TablesListCommandOptions = InspectionCommandOptions
TablesGetCommandOptions = InspectionCommandOptions


async def create_sdk_inspection_client_from_input(
    input_data: ImpersonationFields,
) -> SdkBigQueryClient:
    """Create an SDK-backed inspection client from impersonation params."""
    options: AuthClientOptions = {}
    service_account = input_data.get("impersonateServiceAccount")
    if service_account is not None:
        options["impersonateServiceAccount"] = service_account
    delegates = input_data.get("impersonateDelegates")
    if delegates is not None:
        options["impersonateDelegates"] = delegates
    auth_client = await create_auth_client(options)
    return SdkBigQueryClient(auth_client)


def create_run_catalog_command(
    command_id: CommandId,
    parse_fn: Callable[[Any], ImpersonationFields],
    execute_fn: Callable[[Any, InspectionCommandOptions], Awaitable[Any]],
) -> Callable[[list[str], InspectionCommandOptions], Awaitable[Any]]:
    """Build a catalog command runner with shared schema and params handling."""

    async def run_catalog_command(
        argv: list[str],
        command_options: InspectionCommandOptions,
    ) -> Any:
        argv_parsed = parse_operational_argv(argv)

        if argv_parsed["kind"] == "input-schema":
            return get_command_schema(command_id, "input")

        if argv_parsed["kind"] == "output-schema":
            return get_command_schema(command_id, "output")

        raw = resolve_params_value(argv_parsed["params"])
        input_data = parse_fn(raw)
        return await execute_fn(input_data, command_options)

    return run_catalog_command
