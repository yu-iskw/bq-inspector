"""Contextual hints for BigQuery API errors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspect.core.shared.iam_hints import iam_hint_for_api

if TYPE_CHECKING:
    from bq_inspect.core.shared.types import BqInspectErrorCode, JobRef

_MISSING_JOB_LOCATION_HINT = (
    "Add location on each job ref (use the same region as in jobs.list output). "
    "Without location, jobs.get often returns 403 Access Denied instead of a clear "
    "not-found error."
)

_JOBS_GET_PERMISSION_DENIED_WITH_LOCATION_HINT = (
    "Confirm projectId and jobId from jobs.list output. BigQuery may return Access "
    "Denied for a non-existent or inaccessible job even when location is set, not only "
    "for IAM gaps."
)


class ApiErrorHintContext:
    """Optional context for API error hint generation."""

    def __init__(self, *, job_ref: JobRef | None = None) -> None:
        self.job_ref = job_ref


def _is_job_location_missing(job_ref: JobRef | None) -> bool:
    if job_ref is None:
        return True
    location = job_ref.get("location")
    if location is None:
        return True
    trimmed = location.strip()
    return len(trimmed) == 0


def hint_for_api_error(
    code: BqInspectErrorCode,
    api: str,
    context: ApiErrorHintContext | None = None,
) -> str | None:
    """Return a combined hint string for an API error, or None."""
    parts: list[str] = []
    iam_hint = iam_hint_for_api(api) if code == "BQINSPECT_PERMISSION_DENIED" else None

    if iam_hint is not None:
        parts.append(iam_hint)

    job_ref = context.job_ref if context is not None else None

    if (
        api == "bigquery.jobs.get"
        and _is_job_location_missing(job_ref)
        and code in ("BQINSPECT_PERMISSION_DENIED", "BQINSPECT_JOB_NOT_FOUND")
    ):
        parts.append(_MISSING_JOB_LOCATION_HINT)

    if (
        api == "bigquery.jobs.get"
        and code == "BQINSPECT_PERMISSION_DENIED"
        and not _is_job_location_missing(job_ref)
    ):
        parts.append(_JOBS_GET_PERMISSION_DENIED_WITH_LOCATION_HINT)

    if len(parts) == 0:
        return None

    return " ".join(parts)
