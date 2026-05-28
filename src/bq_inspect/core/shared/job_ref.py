"""Job reference normalization."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspect.core.shared.errors import create_input_failure

if TYPE_CHECKING:
    from bq_inspect.core.shared.types import JobRef


def normalize_job_ref(input_ref: JobRef) -> JobRef:
    """Validate and trim job reference fields."""
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
