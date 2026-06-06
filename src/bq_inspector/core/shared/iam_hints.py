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
            "Grant roles/datalineage.viewer on each project that stores the lineage "
            "links/events (datalineage.events.get); links live with their Lineage "
            "Events and may be in a different project than the table. "
            "clientProjectId is used for billing/quota only—enable the Data Lineage "
            "API there when it differs from the link-owning project(s)."
        ),
    ),
    (
        ("dataplex.",),
        (
            "Grant roles/dataplex.catalogViewer on the search request project for "
            "dataplex.projects.search. BigQuery-backed search results also depend on "
            "source-system metadata permissions such as roles/bigquery.metadataViewer."
        ),
    ),
)


def iam_hint_for_api(api: str) -> str | None:
    """Return an IAM hint for known BigQuery APIs, or None."""
    for prefixes, hint in _IAM_HINT_PREFIXES:
        if api.startswith(prefixes):
            return hint
    return None
