"""Jobs list command."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.commands.command_shared import (
    InspectionCommandOptions,
    create_run_params_command,
    create_sdk_inspection_client_from_input,
)
from bq_inspector.core.jobs.list import ListJobsOrchestrationInput, list_jobs
from bq_inspector.core.shared.impersonation_fields import select_impersonation_fields
from bq_inspector.input.input_parsers import parse_jobs_list_input

if TYPE_CHECKING:
    from bq_inspector.input.parsed_input_types import ParsedJobsListInput


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
        impersonation=select_impersonation_fields(input_data),
    )
    return await list_jobs(orchestration)


run_jobs_list_command = create_run_params_command(
    "jobs list", parse_jobs_list_input, _execute_jobs_list
)
run_jobs_list = run_jobs_list_command.run_argv
