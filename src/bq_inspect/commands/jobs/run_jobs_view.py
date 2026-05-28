"""Jobs view commands (summary, query, performance, lineage, impact, get)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspect.cli.input.input_parsers import parse_jobs_view_input_for_command
from bq_inspect.commands.command_shared import (
    InspectionCommandOptions,
    create_run_params_command,
    create_sdk_inspection_client_from_input,
)
from bq_inspect.core.jobs.get import InspectJobOptions, inspect_jobs
from bq_inspect.core.shared.impersonation_fields import impersonation_request_fields

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bq_inspect.cli.input.parsed_input_types import ParsedJobsViewInput
    from bq_inspect.core.shared.types import InspectJobRequest, JobView
    from bq_inspect.schemas.command_schemas import JobsViewCommandId


async def _execute_jobs_view(
    input_data: ParsedJobsViewInput,
    view: JobView,
    command_options: InspectionCommandOptions,
) -> Any:
    client = command_options.client
    if client is None:
        client = await create_sdk_inspection_client_from_input(input_data)

    request: InspectJobRequest = {
        "jobs": input_data["jobs"],
        "view": view,
    }
    request.update(impersonation_request_fields(input_data))  # type: ignore[arg-type]

    return await inspect_jobs(
        request,
        InspectJobOptions(client=client, tool_version=command_options.tool_version),
    )


def create_run_jobs_view_command(
    view: JobView,
    command_id: JobsViewCommandId,
) -> Callable[[list[str], InspectionCommandOptions], Awaitable[Any]]:
    """Build a jobs view command runner via the shared params command factory."""

    async def execute(
        input_data: ParsedJobsViewInput,
        command_options: InspectionCommandOptions,
    ) -> Any:
        return await _execute_jobs_view(input_data, view, command_options)

    def parse(raw: object) -> ParsedJobsViewInput:
        return parse_jobs_view_input_for_command(command_id, raw)

    return create_run_params_command(command_id, parse, execute)


run_jobs_get = create_run_jobs_view_command("full", "jobs get")
run_jobs_summary = create_run_jobs_view_command("summary", "jobs summary")
run_jobs_query = create_run_jobs_view_command("query", "jobs query")
run_jobs_performance = create_run_jobs_view_command("performance", "jobs performance")
run_jobs_lineage = create_run_jobs_view_command("lineage", "jobs lineage")
run_jobs_impact = create_run_jobs_view_command("impact", "jobs impact")
