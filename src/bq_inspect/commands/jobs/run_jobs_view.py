"""Jobs view commands (summary, query, performance, lineage, impact, get)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspect.cli.argv.operational_argv import parse_operational_argv
from bq_inspect.cli.input.input_parsers import parse_jobs_view_input_for_command
from bq_inspect.cli.params.parse_params import resolve_params_value
from bq_inspect.commands.command_shared import create_sdk_inspection_client_from_input
from bq_inspect.core.jobs.get import InspectJobOptions, inspect_jobs
from bq_inspect.core.shared.impersonation_fields import impersonation_request_fields
from bq_inspect.schemas.command_schemas import JobsViewCommandId, get_command_schema

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bq_inspect.bigquery.port.inspection_client import BigQueryJobClient
    from bq_inspect.cli.input.parsed_input_types import ParsedJobsViewInput
    from bq_inspect.core.shared.types import InspectJobRequest, JobView


class JobsViewCommandOptions:
    """Options for jobs view command execution."""

    def __init__(
        self,
        *,
        client: BigQueryJobClient | None = None,
        tool_version: str,
    ) -> None:
        self.client = client
        self.tool_version = tool_version


async def _execute_jobs_view(
    input_data: ParsedJobsViewInput,
    view: JobView,
    command_options: JobsViewCommandOptions,
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


def _create_run_jobs_view(
    view: JobView,
    command_id: JobsViewCommandId,
) -> Callable[[list[str], JobsViewCommandOptions], Awaitable[Any]]:
    async def run_jobs_view(
        argv: list[str],
        command_options: JobsViewCommandOptions,
    ) -> Any:
        argv_parsed = parse_operational_argv(argv)

        if argv_parsed["kind"] == "input-schema":
            return get_command_schema(command_id, "input")

        if argv_parsed["kind"] == "output-schema":
            return get_command_schema(command_id, "output")

        raw = resolve_params_value(argv_parsed["params"])
        input_data = parse_jobs_view_input_for_command(command_id, raw)

        return await _execute_jobs_view(input_data, view, command_options)

    return run_jobs_view


run_jobs_get = _create_run_jobs_view("full", "jobs get")
run_jobs_summary = _create_run_jobs_view("summary", "jobs summary")
run_jobs_query = _create_run_jobs_view("query", "jobs query")
run_jobs_performance = _create_run_jobs_view("performance", "jobs performance")
run_jobs_lineage = _create_run_jobs_view("lineage", "jobs lineage")
run_jobs_impact = _create_run_jobs_view("impact", "jobs impact")
