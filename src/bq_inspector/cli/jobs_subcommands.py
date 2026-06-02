"""Job subcommand names and help descriptions (single source)."""

from __future__ import annotations

JOBS_SUBCOMMANDS: tuple[tuple[str, str], ...] = (
    ("summary", "Job status, timing, bytes/slots (default inspection)"),
    ("query", "SQL, configuration, and light lineage stats"),
    ("performance", "Query plan, timeline, performanceInsights, script/session stats"),
    ("lineage", "Referenced tables, routines, datasets, destinations"),
    ("impact", "DML stats, load/export/ML/search/spark side-effect stats"),
    ("get", "Full BigQuery Job JSON"),
    ("list", "List jobs (optional client-side filters in params)"),
)

JOB_SUBCOMMAND_NAMES: frozenset[str] = frozenset(name for name, _ in JOBS_SUBCOMMANDS)
