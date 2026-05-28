"""Jobs list command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from bq_inspect.cli.argv.operational_argv import parse_operational_argv
from bq_inspect.cli.input.input_parsers import parse_jobs_list_input
from bq_inspect.cli.params.parse_params import resolve_params_value
from bq_inspect.commands.command_shared import (
    InspectionCommandOptions,
    create_sdk_inspection_client_from_input,
)
from bq_inspect.core.jobs.list import ListJobsOrchestrationInput, list_jobs
from bq_inspect.core.shared.impersonation_fields import ImpersonationFields
from bq_inspect.schemas.command_schemas import get_command_schema

if TYPE_CHECKING:
    from bq_inspect.cli.input.parsed_input_types import ParsedJobsListInput


async def run_jobs_list(
    argv: list[str],
    command_options: InspectionCommandOptions,
) -> Any:
    """Run jobs list with schema discovery or params execution."""
    argv_parsed = parse_operational_argv(argv)

    if argv_parsed["kind"] == "input-schema":
        return get_command_schema("jobs list", "input")

    if argv_parsed["kind"] == "output-schema":
        return get_command_schema("jobs list", "output")

    raw = resolve_params_value(argv_parsed["params"])
    input_data = parse_jobs_list_input(raw)

    return await _execute_jobs_list(input_data, command_options)


async def _execute_jobs_list(
    input_data: ParsedJobsListInput,
    command_options: InspectionCommandOptions,
) -> Any:
    client = command_options.client
    if client is None:
        client = await create_sdk_inspection_client_from_input(input_data)

    orchestration = ListJobsOrchestrationInput(
        client=client,
        tool_version=command_options.tool_version,
        list_request=input_data["listRequest"],
        filters=input_data["filters"],
        impersonation=_impersonation_from_parsed_input(input_data),
    )
    return await list_jobs(orchestration)


def _impersonation_from_parsed_input(input_data: ParsedJobsListInput) -> ImpersonationFields:
    impersonation = cast(ImpersonationFields, {})
    service_account = input_data.get("impersonateServiceAccount")
    if service_account is not None:
        impersonation["impersonateServiceAccount"] = service_account
    delegates = input_data.get("impersonateDelegates")
    if delegates is not None:
        impersonation["impersonateDelegates"] = delegates
    return impersonation
