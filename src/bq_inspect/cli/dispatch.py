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
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

from bq_inspect.cli.help import resolve_help_text, strip_trailing_help_flags
from bq_inspect.cli.usage import GLOBAL_USAGE
from bq_inspect.commands.command_shared import InspectionCommandOptions
from bq_inspect.commands.datasets.get import run_datasets_get
from bq_inspect.commands.jobs.list import run_jobs_list
from bq_inspect.commands.jobs.run_jobs_view import (
    run_jobs_get,
    run_jobs_impact,
    run_jobs_lineage,
    run_jobs_performance,
    run_jobs_query,
    run_jobs_summary,
)
from bq_inspect.commands.schema import run_schema_command
from bq_inspect.commands.tables.get import run_tables_get
from bq_inspect.commands.tables.list import run_tables_list
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


def _to_cli_error(error: Exception) -> BqInspectError:
    if isinstance(error, BqInspectFailure):
        return error.details

    message = error.args[0] if error.args and isinstance(error.args[0], str) else str(error)
    return create_bq_inspect_error(
        code="BQINSPECT_INTERNAL",
        message=message,
    )


@dataclass(frozen=True)
class _RouteSpec:
    path: tuple[str, ...]
    run: Callable[[list[str], InspectionCommandOptions], Awaitable[Any]]


def _matches_route(argv: list[str], spec: _RouteSpec) -> bool:
    if len(argv) < len(spec.path):
        return False
    return tuple(argv[: len(spec.path)]) == spec.path


def _command_routes() -> tuple[_RouteSpec, ...]:
    return (
        _RouteSpec(("jobs", "summary"), run_jobs_summary),
        _RouteSpec(("jobs", "query"), run_jobs_query),
        _RouteSpec(("jobs", "performance"), run_jobs_performance),
        _RouteSpec(("jobs", "lineage"), run_jobs_lineage),
        _RouteSpec(("jobs", "impact"), run_jobs_impact),
        _RouteSpec(("jobs", "get"), run_jobs_get),
        _RouteSpec(("jobs", "list"), run_jobs_list),
        _RouteSpec(("datasets", "get"), run_datasets_get),
        _RouteSpec(("tables", "list"), run_tables_list),
        _RouteSpec(("tables", "get"), run_tables_get),
        _RouteSpec(("schema",), lambda argv, _options: run_schema_command(argv)),
    )


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
    options = InspectionCommandOptions(tool_version=tool_version)
    matched = next((spec for spec in _command_routes() if _matches_route(argv, spec)), None)

    if matched is None:
        raise BqInspectFailure(
            create_bq_inspect_error(
                code="BQINSPECT_INPUT_INVALID",
                message="Unknown command: " + " ".join(argv),
            )
        )

    response = await matched.run(argv[len(matched.path) :], options)
    sys.stdout.write(f"{json.dumps(response, indent=2)}\n")


def main() -> None:
    """Run the bq-inspect CLI."""
    try:
        asyncio.run(_dispatch(sys.argv[1:]))
    except Exception as error:
        details = _to_cli_error(error)
        sys.stderr.write(f"{json.dumps(details, indent=2)}\n")
        raise SystemExit(get_exit_code(details)) from error
