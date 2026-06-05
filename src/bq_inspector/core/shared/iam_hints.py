"""IAM hint strings for API permission errors."""

from __future__ import annotations

_IAM_HINT_PREFIXES: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("bigquery.jobs.",),
        "Grant roles/bigquery.resourceViewer or a custom role with jobs.get/jobs.list.",
    ),
    (
        ("bigquery.datasets.", "bigquery.tables."),
        (
            "Grant roles/bigquery.metadataViewer on the dataset/project or a "
            "custom metadata-only role."
        ),
    ),
    (
        ("datalineage.",),
        (
            "Grant roles/datalineage.viewer on clientProjectId and ensure the "
            "Data Lineage API is enabled in that project."
        ),
    ),
)


def iam_hint_for_api(api: str) -> str | None:
    """Return an IAM hint for known BigQuery APIs, or None."""
    for prefixes, hint in _IAM_HINT_PREFIXES:
        if api.startswith(prefixes):
            return hint
    return None
