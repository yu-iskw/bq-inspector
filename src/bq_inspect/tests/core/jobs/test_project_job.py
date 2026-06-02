"""Tests for job projection."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from bq_inspect.core.jobs.project_job import project_job

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def _load_fixture(name: str = "successful-query-job.json") -> dict[str, object]:
    with (_FIXTURES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def test_summary_omits_configuration_and_strips_query_plan() -> None:
    fixture = _load_fixture()
    fixture_stats = fixture["statistics"]
    assert isinstance(fixture_stats, dict)
    fixture_query = fixture_stats["query"]
    assert isinstance(fixture_query, dict)
    job = {
        **fixture,
        "statistics": {
            **fixture_stats,
            "query": {
                **fixture_query,
                "queryPlan": [{"name": "stage"}],
                "timeline": [{"elapsedMs": "1"}],
            },
        },
    }

    projected = project_job(job, "summary")
    assert isinstance(projected, dict)
    assert "configuration" not in projected
    assert "user_email" not in projected
    assert projected["id"] == "analytics-prod:US.job_123"
    assert projected["status"] is not None

    statistics = projected["statistics"]
    assert isinstance(statistics, dict)
    query_stats = statistics["query"]
    assert isinstance(query_stats, dict)
    assert query_stats["totalBytesProcessed"] == "12345"
    assert "queryPlan" not in query_stats
    assert "timeline" not in query_stats


def test_query_keeps_sql_configuration_and_lineage_statistics() -> None:
    projected = project_job(_load_fixture("query-job-with-lineage.json"), "query")
    assert isinstance(projected, dict)
    configuration = projected["configuration"]
    assert isinstance(configuration, dict)
    query = configuration["query"]
    assert isinstance(query, dict)
    assert "SELECT" in str(query["query"])

    statistics = projected["statistics"]
    assert isinstance(statistics, dict)
    query_stats = statistics["query"]
    assert isinstance(query_stats, dict)
    referenced_tables = query_stats["referencedTables"]
    assert isinstance(referenced_tables, list)
    assert len(referenced_tables) == 1
    assert "queryPlan" not in query_stats
    assert "dmlStats" not in query_stats
    assert query_stats["totalSlotMs"] == "100"


def test_performance_keeps_query_plan_and_omits_configuration_sql() -> None:
    fixture = _load_fixture()
    fixture_stats = fixture["statistics"]
    assert isinstance(fixture_stats, dict)
    fixture_query = fixture_stats["query"]
    assert isinstance(fixture_query, dict)
    job = {
        **fixture,
        "statistics": {
            **fixture_stats,
            "query": {
                **fixture_query,
                "query": "SELECT 1",
                "queryPlan": [{"name": "stage"}],
                "timeline": [{"elapsedMs": "1"}],
                "performanceInsights": [{"insight": "unused_columns"}],
            },
        },
    }

    projected = project_job(job, "performance")
    assert isinstance(projected, dict)
    assert "configuration" not in projected
    statistics = projected["statistics"]
    assert isinstance(statistics, dict)
    assert "query" in statistics
    query_stats = statistics["query"]
    assert isinstance(query_stats, dict)
    assert query_stats["queryPlan"] == [{"name": "stage"}]
    assert query_stats["timeline"] == [{"elapsedMs": "1"}]
    assert query_stats["performanceInsights"] == [{"insight": "unused_columns"}]
    assert query_stats["totalBytesProcessed"] == "12345"
    assert "query" not in query_stats


def test_performance_keeps_query_statistics_from_lineage_fixture() -> None:
    projected = project_job(_load_fixture("query-job-with-lineage.json"), "performance")
    assert isinstance(projected, dict)
    statistics = projected["statistics"]
    assert isinstance(statistics, dict)
    query_stats = statistics["query"]
    assert isinstance(query_stats, dict)
    assert query_stats["queryPlan"] == [{"name": "stage-0"}]
    assert query_stats["timeline"] == [{"elapsedMs": "100"}]
    assert query_stats["performanceInsights"] == [{"insight": "unused_columns"}]
    assert "query" not in query_stats


def test_lineage_keeps_referenced_tables_and_drops_query_plan() -> None:
    projected = project_job(_load_fixture("query-job-with-lineage.json"), "lineage")
    assert isinstance(projected, dict)
    assert "configuration" not in projected
    statistics = projected["statistics"]
    assert isinstance(statistics, dict)
    query_stats = statistics["query"]
    assert isinstance(query_stats, dict)
    referenced_tables = query_stats["referencedTables"]
    assert isinstance(referenced_tables, list)
    assert len(referenced_tables) == 1
    assert "queryPlan" not in query_stats
    assert "dmlStats" not in query_stats


def test_impact_keeps_dml_stats_and_job_type_statistics() -> None:
    projected = project_job(_load_fixture("query-job-with-lineage.json"), "impact")
    assert isinstance(projected, dict)
    stats = projected["statistics"]
    assert isinstance(stats, dict)
    query_stats = stats["query"]
    assert isinstance(query_stats, dict)
    assert query_stats["dmlStats"] is not None
    assert "referencedTables" not in query_stats
    assert stats["mlStatistics"] == {"modelId": "model_1"}
    assert "queryPlan" not in stats


def test_full_returns_job_unchanged() -> None:
    job = _load_fixture()
    snapshot = copy.deepcopy(job)
    assert project_job(job, "full") == snapshot


def test_does_not_mutate_input() -> None:
    input_job = {"configuration": {"query": {"query": "SELECT 'secret'"}}}
    snapshot = copy.deepcopy(input_job)
    project_job(input_job, "summary")
    assert input_job == snapshot
