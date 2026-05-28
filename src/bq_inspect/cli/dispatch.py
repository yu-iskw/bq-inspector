# Copyright 2025 yu-iskw
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CLI dispatch and main entry for bq-inspect."""

from __future__ import annotations

import asyncio
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

from bq_inspect.cli.help import resolve_help_text, strip_trailing_help_flags
from bq_inspect.cli.usage import GLOBAL_USAGE
from bq_inspect.commands.datasets.get import DatasetsGetCommandOptions, run_datasets_get
from bq_inspect.commands.jobs.list import JobsListCommandOptions, run_jobs_list
from bq_inspect.commands.jobs.run_jobs_view import (
    JobsViewCommandOptions,
    run_jobs_get,
    run_jobs_impact,
    run_jobs_lineage,
    run_jobs_performance,
    run_jobs_query,
    run_jobs_summary,
)
from bq_inspect.commands.schema import run_schema_command
from bq_inspect.commands.tables.get import TablesGetCommandOptions, run_tables_get
from bq_inspect.commands.tables.list import TablesListCommandOptions, run_tables_list
from bq_inspect.core.shared.errors import (
    BqInspectFailure,
    create_bq_inspect_error,
    get_exit_code,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bq_inspect.core.shared.types import BqInspectError


def _read_tool_version() -> str:
    try:
        return version("bq-inspect")
    except PackageNotFoundError:
        return "0.0.0"


def _to_cli_error(error: BaseException) -> BqInspectError:
    if isinstance(error, BqInspectFailure):
        return error.details

    return create_bq_inspect_error(
        code="BQINSPECT_INTERNAL",
        message=str(error),
    )


_MIN_ROUTE_ARGS = 2


async def _dispatch(raw_argv: list[str]) -> None:
    argv, wants_help = strip_trailing_help_flags(raw_argv)

    if len(argv) == 0:
        sys.stdout.write(f"{GLOBAL_USAGE}\n")
        return

    help_text = resolve_help_text(argv, wants_help)

    if help_text is not None:
        sys.stdout.write(f"{help_text}\n")
        return

    tool_version = _read_tool_version()

    routes: list[tuple[Callable[[list[str]], bool], Callable[[list[str]], Awaitable[Any]]]] = [
        (
            lambda args: (
                len(args) >= _MIN_ROUTE_ARGS and args[0] == "jobs" and args[1] == "summary"
            ),
            lambda args: run_jobs_summary(
                args[2:],
                JobsViewCommandOptions(tool_version=tool_version),
            ),
        ),
        (
            lambda args: len(args) >= _MIN_ROUTE_ARGS and args[0] == "jobs" and args[1] == "query",
            lambda args: run_jobs_query(
                args[2:],
                JobsViewCommandOptions(tool_version=tool_version),
            ),
        ),
        (
            lambda args: (
                len(args) >= _MIN_ROUTE_ARGS and args[0] == "jobs" and args[1] == "performance"
            ),
            lambda args: run_jobs_performance(
                args[2:],
                JobsViewCommandOptions(tool_version=tool_version),
            ),
        ),
        (
            lambda args: (
                len(args) >= _MIN_ROUTE_ARGS and args[0] == "jobs" and args[1] == "lineage"
            ),
            lambda args: run_jobs_lineage(
                args[2:],
                JobsViewCommandOptions(tool_version=tool_version),
            ),
        ),
        (
            lambda args: len(args) >= _MIN_ROUTE_ARGS and args[0] == "jobs" and args[1] == "impact",
            lambda args: run_jobs_impact(
                args[2:],
                JobsViewCommandOptions(tool_version=tool_version),
            ),
        ),
        (
            lambda args: len(args) >= _MIN_ROUTE_ARGS and args[0] == "jobs" and args[1] == "get",
            lambda args: run_jobs_get(
                args[2:],
                JobsViewCommandOptions(tool_version=tool_version),
            ),
        ),
        (
            lambda args: len(args) >= _MIN_ROUTE_ARGS and args[0] == "jobs" and args[1] == "list",
            lambda args: run_jobs_list(
                args[2:],
                JobsListCommandOptions(tool_version=tool_version),
            ),
        ),
        (
            lambda args: (
                len(args) >= _MIN_ROUTE_ARGS and args[0] == "datasets" and args[1] == "get"
            ),
            lambda args: run_datasets_get(
                args[2:],
                DatasetsGetCommandOptions(tool_version=tool_version),
            ),
        ),
        (
            lambda args: len(args) >= _MIN_ROUTE_ARGS and args[0] == "tables" and args[1] == "list",
            lambda args: run_tables_list(
                args[2:],
                TablesListCommandOptions(tool_version=tool_version),
            ),
        ),
        (
            lambda args: len(args) >= _MIN_ROUTE_ARGS and args[0] == "tables" and args[1] == "get",
            lambda args: run_tables_get(
                args[2:],
                TablesGetCommandOptions(tool_version=tool_version),
            ),
        ),
        (
            lambda args: len(args) >= 1 and args[0] == "schema",
            lambda args: run_schema_command(args[1:]),
        ),
    ]

    route = next((entry for entry in routes if entry[0](argv)), None)

    if route is None:
        raise BqInspectFailure(
            create_bq_inspect_error(
                code="BQINSPECT_INPUT_INVALID",
                message=f"Unknown command: {' '.join(argv)}",
            )
        )

    response = await route[1](argv)
    sys.stdout.write(f"{json.dumps(response, indent=2)}\n")


def main() -> None:
    """Run the bq-inspect CLI."""
    try:
        asyncio.run(_dispatch(sys.argv[1:]))
    except BaseException as error:
        details = _to_cli_error(error)
        sys.stderr.write(f"{json.dumps(details, indent=2)}\n")
        raise SystemExit(get_exit_code(details)) from error
