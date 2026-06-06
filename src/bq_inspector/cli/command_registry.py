"""Canonical registry of CLI commands, usage strings, and runners."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from bq_inspector.cli.usage_build import (
    ParamsBodyKind,
    ParamsCommandUsageMeta,
    build_catalog_group_usage,
    build_datasets_group_usage,
    build_global_usage,
    build_jobs_group_usage,
    build_lineage_group_usage,
    build_params_command_usage,
    build_tables_group_usage,
)
from bq_inspector.commands.catalog.commands import (
    catalog_aspect_types_get_command,
    catalog_aspect_types_list_command,
    catalog_entries_get_command,
    catalog_entries_list_command,
    catalog_entries_lookup_command,
    catalog_entry_groups_get_command,
    catalog_entry_groups_list_command,
    catalog_entry_links_get_command,
    catalog_entry_types_get_command,
    catalog_entry_types_list_command,
    catalog_glossaries_get_command,
    catalog_glossaries_list_command,
    catalog_glossary_categories_get_command,
    catalog_glossary_categories_list_command,
    catalog_glossary_terms_get_command,
    catalog_glossary_terms_list_command,
    catalog_search_command,
)
from bq_inspector.commands.datasets.get import datasets_get_command
from bq_inspector.commands.jobs.list import run_jobs_list_command
from bq_inspector.commands.jobs.run_jobs_view import (
    jobs_get_command,
    jobs_impact_command,
    jobs_lineage_command,
    jobs_performance_command,
    jobs_query_command,
    jobs_summary_command,
)
from bq_inspector.commands.lineage.graph import lineage_graph_command
from bq_inspector.commands.lineage.links import lineage_links_command
from bq_inspector.commands.tables.get import tables_get_command
from bq_inspector.commands.tables.list import tables_list_command

if TYPE_CHECKING:
    from bq_inspector.commands.command_shared import ParamsCommandRunner

GLOBAL_USAGE = build_global_usage()


@dataclass(frozen=True)
class GroupCommandSpec:
    """Top-level CLI group with help text and nested params commands."""

    name: str
    usage: str
    commands: tuple[ParamsCommandSpec, ...]


@dataclass(frozen=True)
class ParamsCommandSpec:
    """Params-based CLI command."""

    path: tuple[str, ...]
    usage: str
    runner: ParamsCommandRunner


@dataclass(frozen=True)
class ParamsCommandRegistration:
    """Usage metadata and runner for one params-based command."""

    meta: ParamsCommandUsageMeta
    runner: ParamsCommandRunner


def command_path_key(path: tuple[str, ...]) -> str:
    """Return the argv key for a command path."""
    return " ".join(path)


_LINEAGE_TABLE_EXAMPLE = (
    '"location":"us","projectId":"my-proj","datasetId":"analytics","tableId":"events"'
)
_LINEAGE_LINKS_EXAMPLE = "{" + _LINEAGE_TABLE_EXAMPLE + ',"direction":"UPSTREAM"}'
_LINEAGE_GRAPH_EXAMPLE = "{" + _LINEAGE_TABLE_EXAMPLE + ',"direction":"DOWNSTREAM"}'

_CATALOG_SEARCH_EXAMPLE = (
    '{"projectId":"my-proj","query":"customer orders","scope":"projects/analytics-prod"}'
)
_CATALOG_LOOKUP_EXAMPLE = (
    '{"projectId":"my-proj","location":"global",'
    '"entry":"projects/analytics-prod/locations/us/entryGroups/@bigquery/entries/example"}'
)
_CATALOG_GET_EXAMPLE = (
    '{"name":"projects/analytics-prod/locations/us/entryTypes/example-type"}'
)
_CATALOG_LIST_EXAMPLE = '{"parent":"projects/analytics-prod/locations/us","pageSize":100}'


_PARAMS_COMMAND_REGISTRATIONS: tuple[ParamsCommandRegistration, ...] = (
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("jobs", "summary"),
            ParamsBodyKind.JOBS_VIEW,
            '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
            "./jobs-summary.json",
        ),
        jobs_summary_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("jobs", "query"),
            ParamsBodyKind.JOBS_VIEW,
            '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
            "./jobs-query.json",
        ),
        jobs_query_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("jobs", "performance"),
            ParamsBodyKind.JOBS_VIEW,
            '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
            "./jobs-performance.json",
        ),
        jobs_performance_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("jobs", "lineage"),
            ParamsBodyKind.JOBS_VIEW,
            '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
            "./jobs-lineage.json",
        ),
        jobs_lineage_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("jobs", "impact"),
            ParamsBodyKind.JOBS_VIEW,
            '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
            "./jobs-impact.json",
        ),
        jobs_impact_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("jobs", "get"),
            ParamsBodyKind.JOBS_VIEW,
            '{"jobs":[{"projectId":"my-proj","jobId":"abc"}]}',
            "./jobs-get.json",
        ),
        jobs_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("jobs", "list"),
            ParamsBodyKind.JOBS_LIST,
            '{"projectId":"my-proj","allUsers":true,"maxResults":50}',
            "./jobs-list.json",
        ),
        run_jobs_list_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("datasets", "get"),
            ParamsBodyKind.DATASETS_GET,
            '{"projectId":"my-proj","datasetId":"analytics"}',
            "./datasets-get.json",
        ),
        datasets_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("tables", "list"),
            ParamsBodyKind.TABLES_LIST,
            '{"projectId":"my-proj","datasetId":"analytics"}',
            "./tables-list.json",
        ),
        tables_list_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("tables", "get"),
            ParamsBodyKind.TABLES_GET,
            '{"projectId":"my-proj","datasetId":"analytics","tableId":"events"}',
            "./tables-get.json",
        ),
        tables_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("lineage", "links"),
            ParamsBodyKind.LINEAGE,
            _LINEAGE_LINKS_EXAMPLE,
            "./lineage-links.json",
        ),
        lineage_links_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("lineage", "graph"),
            ParamsBodyKind.LINEAGE,
            _LINEAGE_GRAPH_EXAMPLE,
            "./lineage-graph.json",
        ),
        lineage_graph_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "search"),
            ParamsBodyKind.CATALOG_SEARCH,
            _CATALOG_SEARCH_EXAMPLE,
            "./catalog-search.json",
        ),
        catalog_search_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "entries", "lookup"),
            ParamsBodyKind.CATALOG_LOOKUP,
            _CATALOG_LOOKUP_EXAMPLE,
            "./catalog-entries-lookup.json",
        ),
        catalog_entries_lookup_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "entries", "get"),
            ParamsBodyKind.CATALOG_GET,
            _CATALOG_GET_EXAMPLE,
            "./catalog-entries-get.json",
        ),
        catalog_entries_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "entries", "list"),
            ParamsBodyKind.CATALOG_LIST,
            _CATALOG_LIST_EXAMPLE,
            "./catalog-entries-list.json",
        ),
        catalog_entries_list_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "entry-groups", "get"),
            ParamsBodyKind.CATALOG_GET,
            _CATALOG_GET_EXAMPLE,
            "./catalog-entry-groups-get.json",
        ),
        catalog_entry_groups_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "entry-groups", "list"),
            ParamsBodyKind.CATALOG_LIST,
            _CATALOG_LIST_EXAMPLE,
            "./catalog-entry-groups-list.json",
        ),
        catalog_entry_groups_list_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "entry-types", "get"),
            ParamsBodyKind.CATALOG_GET,
            _CATALOG_GET_EXAMPLE,
            "./catalog-entry-types-get.json",
        ),
        catalog_entry_types_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "entry-types", "list"),
            ParamsBodyKind.CATALOG_LIST,
            _CATALOG_LIST_EXAMPLE,
            "./catalog-entry-types-list.json",
        ),
        catalog_entry_types_list_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "aspect-types", "get"),
            ParamsBodyKind.CATALOG_GET,
            _CATALOG_GET_EXAMPLE,
            "./catalog-aspect-types-get.json",
        ),
        catalog_aspect_types_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "aspect-types", "list"),
            ParamsBodyKind.CATALOG_LIST,
            _CATALOG_LIST_EXAMPLE,
            "./catalog-aspect-types-list.json",
        ),
        catalog_aspect_types_list_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "entry-links", "get"),
            ParamsBodyKind.CATALOG_GET,
            _CATALOG_GET_EXAMPLE,
            "./catalog-entry-links-get.json",
        ),
        catalog_entry_links_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "glossaries", "get"),
            ParamsBodyKind.CATALOG_GET,
            _CATALOG_GET_EXAMPLE,
            "./catalog-glossaries-get.json",
        ),
        catalog_glossaries_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "glossaries", "list"),
            ParamsBodyKind.CATALOG_LIST,
            _CATALOG_LIST_EXAMPLE,
            "./catalog-glossaries-list.json",
        ),
        catalog_glossaries_list_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "glossary-categories", "get"),
            ParamsBodyKind.CATALOG_GET,
            _CATALOG_GET_EXAMPLE,
            "./catalog-glossary-categories-get.json",
        ),
        catalog_glossary_categories_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "glossary-categories", "list"),
            ParamsBodyKind.CATALOG_LIST,
            _CATALOG_LIST_EXAMPLE,
            "./catalog-glossary-categories-list.json",
        ),
        catalog_glossary_categories_list_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "glossary-terms", "get"),
            ParamsBodyKind.CATALOG_GET,
            _CATALOG_GET_EXAMPLE,
            "./catalog-glossary-terms-get.json",
        ),
        catalog_glossary_terms_get_command,
    ),
    ParamsCommandRegistration(
        ParamsCommandUsageMeta(
            ("catalog", "glossary-terms", "list"),
            ParamsBodyKind.CATALOG_LIST,
            _CATALOG_LIST_EXAMPLE,
            "./catalog-glossary-terms-list.json",
        ),
        catalog_glossary_terms_list_command,
    ),
)

PARAMS_COMMAND_SPECS: tuple[ParamsCommandSpec, ...] = tuple(
    ParamsCommandSpec(
        registration.meta.path,
        build_params_command_usage(registration.meta),
        registration.runner,
    )
    for registration in _PARAMS_COMMAND_REGISTRATIONS
)

GROUP_COMMAND_SPECS: tuple[GroupCommandSpec, ...] = (
    GroupCommandSpec(
        "jobs",
        build_jobs_group_usage(),
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "jobs"),
    ),
    GroupCommandSpec(
        "datasets",
        build_datasets_group_usage(),
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "datasets"),
    ),
    GroupCommandSpec(
        "tables",
        build_tables_group_usage(),
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "tables"),
    ),
    GroupCommandSpec(
        "lineage",
        build_lineage_group_usage(),
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "lineage"),
    ),
    GroupCommandSpec(
        "catalog",
        build_catalog_group_usage(),
        tuple(spec for spec in PARAMS_COMMAND_SPECS if spec.path[0] == "catalog"),
    ),
)


def _build_help_lookup() -> dict[str, str]:
    lookup = {command_path_key(spec.path): spec.usage for spec in PARAMS_COMMAND_SPECS}
    for group in GROUP_COMMAND_SPECS:
        lookup[group.name] = group.usage
    lookup[""] = GLOBAL_USAGE
    return lookup


_HELP_BY_KEY = _build_help_lookup()


def command_help_for_key(key: str) -> str | None:
    """Return usage text for a command path key."""
    return _HELP_BY_KEY.get(key)
