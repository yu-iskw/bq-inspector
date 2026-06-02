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

import json
import sys
from typing import TYPE_CHECKING

import click

from bq_inspect.cli.click_cli import invoke
from bq_inspect.core.shared.errors import (
    BqInspectFailure,
    create_bq_inspect_error,
    get_exit_code,
)
from bq_inspect.operational.click_errors import normalize_click_exception_message

if TYPE_CHECKING:
    from bq_inspect.core.shared.types import BqInspectError


def _to_cli_error(error: Exception) -> BqInspectError:
    if isinstance(error, BqInspectFailure):
        return error.details

    if isinstance(error, click.ClickException):
        return create_bq_inspect_error(
            code="BQINSPECT_INPUT_INVALID",
            message=normalize_click_exception_message(error),
        )

    message = error.args[0] if error.args and isinstance(error.args[0], str) else str(error)
    return create_bq_inspect_error(
        code="BQINSPECT_INTERNAL",
        message=message,
    )


def main() -> None:
    """Run the bq-inspect CLI."""
    try:
        invoke()
    except Exception as error:
        details = _to_cli_error(error)
        sys.stderr.write(f"{json.dumps(details, indent=2)}\n")
        raise SystemExit(get_exit_code(details)) from error
