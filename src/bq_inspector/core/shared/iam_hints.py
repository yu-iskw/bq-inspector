"""IAM hint strings for API permission errors."""

from __future__ import annotations


def iam_hint_for_api(api: str) -> str | None:
    """Return an IAM hint for known BigQuery APIs, or None."""
    if api.startswith("bigquery.jobs."):
        return "Grant roles/bigquery.resourceViewer or a custom role with jobs.get/jobs.list."

    if api.startswith(("bigquery.datasets.", "bigquery.tables.")):
        return (
            "Grant roles/bigquery.metadataViewer on the dataset/project or a "
            "custom metadata-only role."
        )

    return None
