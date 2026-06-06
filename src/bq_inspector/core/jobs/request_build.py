"""Canonical BigQuery jobs inspection request builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.core.shared.impersonation_fields import merge_impersonation_into

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import InspectJobRequest, JobView
    from bq_inspector.input.parsed_input_types import ParsedJobsViewInput


def build_inspect_job_request(
    input_data: ParsedJobsViewInput,
    view: JobView,
) -> InspectJobRequest:
    """Build a typed inspect-jobs request from parsed CLI input."""
    return merge_impersonation_into(
        {
            "jobs": input_data["jobs"],
            "view": view,
        },
        input_data,
    )  # type: ignore[return-value]


def build_inspect_job_request_echo(
    request: InspectJobRequest,
    view: JobView,
) -> dict[str, object]:
    """Build the request echo block for an inspect-jobs response."""
    return merge_impersonation_into(
        {
            "jobs": request["jobs"],
            "view": view,
        },
        request,
    )
