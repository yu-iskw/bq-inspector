"""Jobs view commands (summary, query, performance, lineage, impact, get)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from bq_inspector.commands.command_shared import (
    InspectionCommandOptions,
    ParamsCommandRunner,
    create_run_params_command,
    create_sdk_inspection_client_from_input,
)
from bq_inspector.core.jobs.get import InspectJobOptions, inspect_jobs
from bq_inspector.core.shared.impersonation_fields import merge_impersonation_into
from bq_inspector.input.input_parsers import parse_jobs_view_input_for_command

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import InspectJobRequest, JobView
    from bq_inspector.input.parsed_input_types import ParsedJobsViewInput
    from bq_inspector.schemas.command_schemas import JobsViewCommandId


async def _execute_jobs_view(
    input_data: ParsedJobsViewInput,
    view: JobView,
    command_options: InspectionCommandOptions,
) -> Any:
    client = command_options.client
    if client is None:
        client = await create_sdk_inspection_client_from_input(input_data)

    request = cast(
        "InspectJobRequest",
        merge_impersonation_into(
            {
                "jobs": input_data["jobs"],
                "view": view,
            },
            input_data,
        ),
    )

    return await inspect_jobs(
        request,
        InspectJobOptions(client=client, tool_version=command_options.tool_version),
    )


def create_run_jobs_view_command(
    view: JobView,
    command_id: JobsViewCommandId,
) -> ParamsCommandRunner:
    """Build a jobs view command runner via the shared params command factory."""

    async def execute(
        input_data: ParsedJobsViewInput,
        command_options: InspectionCommandOptions,
    ) -> Any:
        return await _execute_jobs_view(input_data, view, command_options)

    def parse(raw: object) -> ParsedJobsViewInput:
        return parse_jobs_view_input_for_command(command_id, raw)

    return create_run_params_command(command_id, parse, execute)


jobs_get_command = create_run_jobs_view_command("full", "jobs get")
jobs_summary_command = create_run_jobs_view_command("summary", "jobs summary")
jobs_query_command = create_run_jobs_view_command("query", "jobs query")
jobs_performance_command = create_run_jobs_view_command("performance", "jobs performance")
jobs_lineage_command = create_run_jobs_view_command("lineage", "jobs lineage")
jobs_impact_command = create_run_jobs_view_command("impact", "jobs impact")

run_jobs_get = jobs_get_command.run_argv
run_jobs_summary = jobs_summary_command.run_argv
run_jobs_query = jobs_query_command.run_argv
run_jobs_performance = jobs_performance_command.run_argv
run_jobs_lineage = jobs_lineage_command.run_argv
run_jobs_impact = jobs_impact_command.run_argv
