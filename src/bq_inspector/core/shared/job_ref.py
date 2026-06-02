"""Job reference normalization."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.core.shared.errors import create_input_failure

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import JobRef


def _try_parse_composite_job_id(value: str) -> JobRef | None:
    """Parse project:location.jobId if value looks like a full BigQuery job id."""
    trimmed = value.strip()
    if ":" not in trimmed or "." not in trimmed.split(":", 1)[1]:
        return None
    project_id, rest = trimmed.split(":", 1)
    location, job_id = rest.split(".", 1)
    if not project_id.strip() or not location.strip() or not job_id.strip():
        return None
    return {
        "projectId": project_id.strip(),
        "location": location.strip(),
        "jobId": job_id.strip(),
    }


def _validate_composite_job_ref(input_ref: JobRef, composite: JobRef) -> None:
    explicit_project = str(input_ref["projectId"]).strip()
    if explicit_project and explicit_project != composite["projectId"]:
        raise create_input_failure(
            "jobId is a composite job id; projectId must match the project in jobId."
        )
    explicit_location = input_ref.get("location")
    trimmed_location = explicit_location.strip() if isinstance(explicit_location, str) else None
    composite_location = composite.get("location")
    if (
        trimmed_location
        and isinstance(composite_location, str)
        and trimmed_location != composite_location
    ):
        raise create_input_failure(
            "jobId is a composite job id; location must match the location in jobId."
        )


def normalize_job_ref(input_ref: JobRef) -> JobRef:
    """Validate and trim job reference fields."""
    composite = _try_parse_composite_job_id(str(input_ref["jobId"]))
    if composite is not None:
        _validate_composite_job_ref(input_ref, composite)
        return composite

    project_id = input_ref["projectId"].strip()
    job_id = input_ref["jobId"].strip()
    location = input_ref.get("location")
    trimmed_location = location.strip() if location is not None else None

    if len(project_id) == 0:
        raise create_input_failure("Project ID is required.")

    if len(job_id) == 0:
        raise create_input_failure("Job ID is required.")

    if trimmed_location is None or len(trimmed_location) == 0:
        return {"projectId": project_id, "jobId": job_id}
    return {"projectId": project_id, "location": trimmed_location, "jobId": job_id}
