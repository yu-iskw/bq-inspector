"""Inspect one or more BigQuery jobs."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import TYPE_CHECKING, cast

from bq_inspect.core.jobs.project_job import project_job
from bq_inspect.core.shared.envelope import build_tool_envelope
from bq_inspect.core.shared.errors import BqInspectFailure, create_bq_inspect_error
from bq_inspect.core.shared.impersonation_fields import merge_impersonation_into
from bq_inspect.core.shared.job_ref import normalize_job_ref

if TYPE_CHECKING:
    from collections.abc import Callable

    from bq_inspect.bigquery.port.inspection_client import BigQueryJobClient
    from bq_inspect.core.shared.types import (
        BqInspectError,
        BqInspectWarning,
        InspectedJob,
        InspectJobRequest,
        InspectJobResponse,
        InspectJobResponseRequest,
        JobRef,
        JobView,
    )

_JOBS_GET_API = "bigquery.jobs.get"


class InspectJobOptions:
    """Options for inspect_jobs orchestration."""

    def __init__(
        self,
        *,
        client: BigQueryJobClient,
        tool_version: str,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.client = client
        self.tool_version = tool_version
        self.now = now or (lambda: datetime.now(timezone.utc))


def _build_request_echo(
    request: InspectJobRequest,
    view: JobView,
) -> InspectJobResponseRequest:
    return cast(
        "InspectJobResponseRequest",
        merge_impersonation_into(
            {
                "jobs": request["jobs"],
                "view": view,
            },
            request,
        ),
    )


async def inspect_jobs(
    request: InspectJobRequest,
    options: InspectJobOptions,
) -> InspectJobResponse:
    """Fetch and project jobs according to the requested view."""
    view: JobView = request.get("view", "summary")
    inspected_jobs = await asyncio.gather(
        *[
            _inspect_one_job(
                input_ref=input_ref,
                client=options.client,
                now=options.now,
                view=view,
            )
            for input_ref in request["jobs"]
        ]
    )

    global_warnings = [warning for job in inspected_jobs for warning in job.get("warnings", [])]

    errors: list[BqInspectError] = [
        error for job in inspected_jobs for error in job.get("errors", [])
    ]

    envelope = build_tool_envelope(options.tool_version)

    return {
        "schemaVersion": envelope["schemaVersion"],
        "tool": envelope["tool"],
        "request": _build_request_echo(request, view),
        "jobs": inspected_jobs,
        "warnings": global_warnings,
        "errors": errors,
    }


async def _inspect_one_job(
    *,
    input_ref: JobRef,
    client: BigQueryJobClient,
    now: Callable[[], datetime],
    view: JobView,
) -> InspectedJob:
    warnings: list[BqInspectWarning] = []
    errors: list[BqInspectError] = []
    fetched_at = (
        now().astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    )

    try:
        job_ref = normalize_job_ref(input_ref)
    except BqInspectFailure as error:
        return _build_failed_inspection(
            error=error,
            job_ref=_fallback_job_ref(input_ref),
            fetched_at=fetched_at,
            warnings=warnings,
            errors=errors,
            fallback_message="Unexpected job reference failure.",
        )

    try:
        job = await client.get_job(job_ref)
    except Exception as error:  # noqa: BLE001
        return _build_failed_inspection(
            error=error,
            job_ref=job_ref,
            fetched_at=fetched_at,
            warnings=warnings,
            errors=errors,
            fallback_message="Unexpected BigQuery client failure.",
        )

    projected_job = project_job(job, view)

    return {
        "jobRef": job_ref,
        "source": {
            "api": _JOBS_GET_API,
            "fetchedAt": fetched_at,
        },
        "job": projected_job,
        "warnings": warnings,
        "errors": errors,
    }


def _build_failed_inspection(  # noqa: PLR0913
    *,
    error: BaseException,
    job_ref: JobRef,
    fetched_at: str,
    warnings: list[BqInspectWarning],
    errors: list[BqInspectError],
    fallback_message: str,
) -> InspectedJob:
    if isinstance(error, BqInspectFailure):
        errors.append(error.details)
    else:
        message = error.args[0] if isinstance(error, Exception) and error.args else fallback_message
        resolved_message = message if isinstance(message, str) else fallback_message
        errors.append(
            create_bq_inspect_error(
                code="BQINSPECT_INTERNAL",
                message=resolved_message,
            )
        )

    return {
        "jobRef": job_ref,
        "source": {
            "api": _JOBS_GET_API,
            "fetchedAt": fetched_at,
        },
        "warnings": warnings,
        "errors": errors,
    }


def _fallback_job_ref(job: JobRef) -> JobRef:
    project_id = job["projectId"].strip()
    job_id = job["jobId"].strip()
    location = job.get("location")
    trimmed_location = location.strip() if location is not None else None

    if trimmed_location is None or len(trimmed_location) == 0:
        return {"projectId": project_id, "jobId": job_id}
    return {"projectId": project_id, "location": trimmed_location, "jobId": job_id}
