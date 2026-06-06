"""Knowledge Catalog command registry builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.cli.usage_build import (
    ParamsBodyKind,
    ParamsCommandUsageMeta,
    build_params_command_usage,
)
from bq_inspector.commands.catalog.commands import (
    build_knowledge_catalog_command_runners,
    catalog_entries_lookup_command,
    catalog_search_command,
)
from bq_inspector.knowledge_catalog.resource_specs import (
    CATALOG_GET_EXAMPLE,
    CATALOG_LIST_EXAMPLE,
    KNOWLEDGE_CATALOG_GET_RESOURCES,
    KNOWLEDGE_CATALOG_LIST_RESOURCES,
    knowledge_catalog_command_path,
    knowledge_catalog_export_name,
)

if TYPE_CHECKING:
    from bq_inspector.commands.command_shared import ParamsCommandRunner

_CATALOG_SEARCH_EXAMPLE = (
    '{"projectId":"my-proj","query":"customer orders","scope":"projects/analytics-prod"}'
)
_CATALOG_LOOKUP_EXAMPLE = (
    '{"projectId":"my-proj","location":"global",'
    '"entry":"projects/analytics-prod/locations/us/entryGroups/@bigquery/entries/example"}'
)


def knowledge_catalog_body_kind(verb: str) -> ParamsBodyKind:
    """Return params body kind for a Knowledge Catalog verb."""
    if verb == "get":
        return ParamsBodyKind.CATALOG_GET
    if verb == "list":
        return ParamsBodyKind.CATALOG_LIST
    raise ValueError(f"Unsupported Knowledge Catalog verb: {verb}")


def build_knowledge_catalog_registrations() -> tuple[
    tuple[ParamsCommandUsageMeta, ParamsCommandRunner],
    ...,
]:
    """Build registry entries for all Knowledge Catalog commands."""
    runners = build_knowledge_catalog_command_runners()

    registrations: list[tuple[ParamsCommandUsageMeta, ParamsCommandRunner]] = [
        (
            ParamsCommandUsageMeta(
                ("catalog", "search"),
                ParamsBodyKind.CATALOG_SEARCH,
                _CATALOG_SEARCH_EXAMPLE,
                "./catalog-search.json",
            ),
            catalog_search_command,
        ),
        (
            ParamsCommandUsageMeta(
                ("catalog", "entries", "lookup"),
                ParamsBodyKind.CATALOG_LOOKUP,
                _CATALOG_LOOKUP_EXAMPLE,
                "./catalog-entries-lookup.json",
            ),
            catalog_entries_lookup_command,
        ),
    ]

    for spec in KNOWLEDGE_CATALOG_GET_RESOURCES:
        path = knowledge_catalog_command_path(spec.subgroup, "get")
        runner = runners[knowledge_catalog_export_name(spec.subgroup, "get")]
        registrations.append(
            (
                ParamsCommandUsageMeta(
                    path,
                    knowledge_catalog_body_kind("get"),
                    CATALOG_GET_EXAMPLE,
                    spec.example_file,
                ),
                runner,
            )
        )

    for spec in KNOWLEDGE_CATALOG_LIST_RESOURCES:
        path = knowledge_catalog_command_path(spec.subgroup, "list")
        runner = runners[knowledge_catalog_export_name(spec.subgroup, "list")]
        registrations.append(
            (
                ParamsCommandUsageMeta(
                    path,
                    knowledge_catalog_body_kind("list"),
                    CATALOG_LIST_EXAMPLE,
                    spec.example_file,
                ),
                runner,
            )
        )

    return tuple(registrations)


def knowledge_catalog_command_specs() -> tuple[
    tuple[tuple[str, ...], str, ParamsCommandRunner], ...
]:
    """Return (path, usage, runner) tuples for Knowledge Catalog commands."""
    return tuple(
        (
            meta.path,
            build_params_command_usage(meta),
            runner,
        )
        for meta, runner in build_knowledge_catalog_registrations()
    )
