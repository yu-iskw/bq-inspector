"""Project BigQuery job payloads to view-specific subsets."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bq_inspector.core.jobs.bigquery_job_types import is_big_query_job

if TYPE_CHECKING:
    from collections.abc import Callable

    from bq_inspector.core.shared.types import JobView

QUERY_LINEAGE_KEYS = (
    "referencedTables",
    "referencedViews",
    "referencedRoutines",
    "referencedRowAccessPolicies",
    "referencedDatasets",
    "referencedPropertyGraphs",
    "destinationTable",
    "ddlTargetTable",
    "ddlAffectedRowAccessPolicy",
    "statementType",
)

QUERY_IMPACT_KEYS = ("dmlStats", "statementType")

STATISTICS_IMPACT_TOP_KEYS = (
    "load",
    "extract",
    "copy",
    "mlStatistics",
    "exportDataStatistics",
    "externalServiceCost",
    "biEngineStatistics",
    "loadQueryStatistics",
    "searchStatistics",
    "vectorSearchStatistics",
    "sparkStatistics",
    "materializedViewStatistics",
    "metadataCacheStatistics",
)

QUERY_QUERY_VIEW_KEYS = (
    *QUERY_LINEAGE_KEYS,
    "totalBytesProcessed",
    "totalBytesBilled",
    "totalSlotMs",
)

# BigQuery JobStatistics2: SQL text lives in statistics.query.query (not statistics.query itself).
QUERY_STATISTICS_SQL_KEY = "query"


def _omit_keys(source: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    output = dict(source)
    for key in keys:
        output.pop(key, None)
    return output


def _trim_statistics_query(
    statistics: dict[str, Any],
    query_keys_to_omit: tuple[str, ...],
) -> dict[str, Any]:
    query = statistics.get("query")
    if query is None or not isinstance(query, dict):
        return dict(statistics)
    return {**statistics, "query": _omit_keys(query, query_keys_to_omit)}


def _omit_query_sql_from_statistics(statistics: dict[str, Any]) -> dict[str, Any]:
    """Keep statistics.query (plan, timeline, insights); drop only the SQL text field."""
    return _trim_statistics_query(statistics, (QUERY_STATISTICS_SQL_KEY,))


def _pick_defined(record: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key in keys:
        if key in record:
            output[key] = record[key]
    return output


def _has_keys(record: dict[str, Any]) -> bool:
    return len(record) > 0


def _pick_query_subset(
    statistics: dict[str, Any] | None,
    keys: tuple[str, ...],
) -> dict[str, Any] | None:
    if statistics is None:
        return None
    query = statistics.get("query")
    if query is None or not isinstance(query, dict):
        return None
    picked = _pick_defined(query, keys)
    return {"query": picked} if _has_keys(picked) else None


def _pick_statistics_top_level(
    statistics: dict[str, Any] | None,
    keys: tuple[str, ...],
) -> dict[str, Any] | None:
    if statistics is None:
        return None
    picked = _pick_defined(statistics, keys)
    return picked if _has_keys(picked) else None


def _merge_statistics_parts(
    query_part: dict[str, Any] | None,
    top_part: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if query_part is None and top_part is None:
        return None
    merged: dict[str, Any] = {}
    if query_part is not None:
        merged.update(query_part)
    if top_part is not None:
        merged.update(top_part)
    return merged


def _project_summary(job: dict[str, Any]) -> dict[str, Any]:
    output = _pick_defined(job, ("id", "jobReference", "kind", "status"))
    statistics = job.get("statistics")
    if isinstance(statistics, dict):
        output["statistics"] = _trim_statistics_query(statistics, ("queryPlan", "timeline"))
    return output


def _project_query(job: dict[str, Any]) -> dict[str, Any]:
    output = _pick_defined(job, ("jobReference", "configuration", "labels"))
    statistics = job.get("statistics")
    stats = _pick_query_subset(
        statistics if isinstance(statistics, dict) else None, QUERY_QUERY_VIEW_KEYS
    )
    if stats is not None:
        output["statistics"] = stats
    return output


def _project_performance(job: dict[str, Any]) -> dict[str, Any]:
    output = _pick_defined(
        job,
        ("jobReference", "status", "sessionInfo", "reservationEdition"),
    )
    statistics = job.get("statistics")
    if isinstance(statistics, dict):
        output["statistics"] = _omit_query_sql_from_statistics(statistics)
    return output


def _project_lineage(job: dict[str, Any]) -> dict[str, Any]:
    output = _pick_defined(job, ("jobReference", "status"))
    statistics = job.get("statistics")
    stats = _pick_query_subset(
        statistics if isinstance(statistics, dict) else None, QUERY_LINEAGE_KEYS
    )
    if stats is not None:
        output["statistics"] = stats
    return output


def _project_impact(job: dict[str, Any]) -> dict[str, Any]:
    output = _pick_defined(job, ("jobReference", "status"))
    statistics = job.get("statistics")
    stats_dict = statistics if isinstance(statistics, dict) else None
    statistics_out = _merge_statistics_parts(
        _pick_query_subset(stats_dict, QUERY_IMPACT_KEYS),
        _pick_statistics_top_level(stats_dict, STATISTICS_IMPACT_TOP_KEYS),
    )
    if statistics_out is not None:
        output["statistics"] = statistics_out
    return output


_JOB_PROJECTORS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "summary": _project_summary,
    "query": _project_query,
    "performance": _project_performance,
    "lineage": _project_lineage,
    "impact": _project_impact,
}


def project_job(job: object, view: JobView) -> object:
    """Return a view-specific projection of a BigQuery job payload."""
    if view == "full" or not is_big_query_job(job):
        return job

    projector = _JOB_PROJECTORS.get(view)
    return projector(job) if projector is not None else job
