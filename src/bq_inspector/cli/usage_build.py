"""Build CLI usage strings from shared templates (single source for help text)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from bq_inspector.cli.jobs_subcommands import JOBS_SUBCOMMANDS


class ParamsBodyKind(Enum):
    """Params section body for a command's --help text."""

    JOBS_VIEW = "jobs_view"
    JOBS_LIST = "jobs_list"
    DATASETS_GET = "datasets_get"
    TABLES_LIST = "tables_list"
    TABLES_GET = "tables_get"
    LINEAGE = "lineage"
    CATALOG_SEARCH = "catalog_search"
    CATALOG_LOOKUP = "catalog_lookup"
    CATALOG_GET = "catalog_get"
    CATALOG_LIST = "catalog_list"


@dataclass(frozen=True)
class ParamsCommandUsageMeta:
    """Metadata to build usage for a params-based command."""

    path: tuple[str, ...]
    body: ParamsBodyKind
    example_inline: str
    example_file: str


_PARAMS_DISCOVERY = """
Discovery:
  --input-schema     Print this command's input JSON Schema and exit
  --output-schema    Print this command's output JSON Schema and exit

Required:
  --params <json>    JSON object matching the input schema, or @path to a JSON file
""".strip()

_JOBS_VIEW_PARAMS = """
Params (see --input-schema for full schema):
  jobs                 Non-empty array of { projectId, jobId, location? }
  impersonateServiceAccount, impersonateDelegates
""".strip()

_PARAMS_BODIES: dict[ParamsBodyKind, str] = {
    ParamsBodyKind.JOBS_VIEW: _JOBS_VIEW_PARAMS,
    ParamsBodyKind.JOBS_LIST: """
Params (see --input-schema):
  projectId            Required
  API (jobs.list): minCreationTime, maxCreationTime, pageToken, maxResults, allUsers, state, parentJobId
  Post-list (current page): minSlotMs, minBytesBilled, labels
  impersonateServiceAccount, impersonateDelegates

  In shared projects use allUsers: true or jobs.list may return an empty array.
  Copy jobReference.location from list output into job view commands (jobs.get requires location for non-default regions).
""".strip(),
    ParamsBodyKind.DATASETS_GET: """
Params (see --input-schema):
  projectId, datasetId
  impersonateServiceAccount, impersonateDelegates
""".strip(),
    ParamsBodyKind.TABLES_LIST: """
Params (see --input-schema):
  projectId, datasetId
  impersonateServiceAccount, impersonateDelegates
""".strip(),
    ParamsBodyKind.TABLES_GET: """
Params (see --input-schema):
  projectId, datasetId, tableId
  impersonateServiceAccount, impersonateDelegates
""".strip(),
    ParamsBodyKind.LINEAGE: """
Params (see --input-schema):
  location             Required Data Lineage API location (us, eu, global, ...)
  projectId, datasetId, tableId
  direction            UPSTREAM or DOWNSTREAM
  clientProjectId      Optional API billing project (defaults to projectId)
  lineage links only: pageSize, pageToken
  lineage graph only: maxDepth, maxResults
  impersonateServiceAccount, impersonateDelegates
""".strip(),
    ParamsBodyKind.CATALOG_SEARCH: """
Params (see --input-schema):
  projectId            Search request project (billing, quota, dataplex.projects.search)
  query                Knowledge Catalog search query
  location             global (default; P0 supports global search only)
  scope                Optional project or organization scope
  semanticSearch       false by default; set true for semantic search
  orderBy, pageSize, pageToken
  impersonateServiceAccount, impersonateDelegates
""".strip(),
    ParamsBodyKind.CATALOG_LOOKUP: """
Params (see --input-schema):
  projectId, location, entry
  view, aspectTypes, paths (optional entry view controls)
  impersonateServiceAccount, impersonateDelegates
""".strip(),
    ParamsBodyKind.CATALOG_GET: """
Params (see --input-schema):
  name                 Canonical Dataplex resource name
  view, aspectTypes, paths (entries get only)
  impersonateServiceAccount, impersonateDelegates
""".strip(),
    ParamsBodyKind.CATALOG_LIST: """
Params (see --input-schema):
  parent               Canonical parent resource (projects/.../locations/...)
  pageSize, pageToken, filter, orderBy
  impersonateServiceAccount, impersonateDelegates
""".strip(),
}


def build_global_usage() -> str:
    """Root bq-inspector usage."""
    subcommand_lines = "\n".join(f"  jobs {name:<12} {desc}" for name, desc in JOBS_SUBCOMMANDS)
    return f"""
bq-inspector — read-only BigQuery job and metadata inspection (JSON on stdout).

Usage:
  bq-inspector <command> --params '<json>' | --params @file.json [options]

Commands (each supports --input-schema / --output-schema for JSON Schema on stdout):
{subcommand_lines}
  datasets get     Dataset metadata
  tables list      List tables in a dataset
  tables get       Table metadata
  lineage links    Immediate upstream/downstream table lineage (1 hop)
  lineage graph    Multi-hop table lineage graph
  catalog search   Search Knowledge Catalog entries
  catalog entries  Lookup, get, or list catalog entries
  catalog entry-groups, entry-types, aspect-types, entry-links
  catalog glossaries, glossary-categories, glossary-terms

Global:
  bq-inspector --help | -h
  bq-inspector <command> --help

Agent workflow: jobs list → jobs summary | jobs query | jobs performance | jobs lineage | jobs impact | jobs get
  Catalog/lineage: tables get → lineage links → lineage graph
  Knowledge Catalog: catalog search → catalog entries lookup → catalog aspect-types get
  (job subcommands also work without the jobs prefix, e.g. bq-inspector summary)

Errors are JSON on stderr; success is JSON on stdout (except plain-text --help).
""".strip()


def build_params_command_usage(meta: ParamsCommandUsageMeta) -> str:
    """Usage text for one params-based command."""
    command = " ".join(meta.path)
    body = _PARAMS_BODIES[meta.body]
    return f"""
Usage:
  bq-inspector {command} --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

{body}

Examples:
  bq-inspector {command} --params '{meta.example_inline}'
  bq-inspector {command} --params @{meta.example_file}
""".strip()


def build_jobs_group_usage() -> str:
    """Usage for the jobs command group."""
    lines = "\n".join(f"  {name:<12} {desc}" for name, desc in JOBS_SUBCOMMANDS)
    return f"""
Usage:
  bq-inspector jobs <subcommand> --params '<json>' | --params @file.json [options]

Subcommands:
{lines}

Run bq-inspector jobs <subcommand> --help for params and examples.
""".strip()


def build_datasets_group_usage() -> str:
    """Usage for the datasets command group."""
    return """
Usage:
  bq-inspector datasets get --params '<json>' | --params @file.json [options]

Subcommands:
  get          Dataset metadata

Run bq-inspector datasets get --help for params and examples.
""".strip()


def build_tables_group_usage() -> str:
    """Usage for the tables command group."""
    return """
Usage:
  bq-inspector tables <subcommand> --params '<json>' | --params @file.json [options]

Subcommands:
  list         List tables in a dataset
  get          Table metadata

Run bq-inspector tables <subcommand> --help for params and examples.
""".strip()


def build_lineage_group_usage() -> str:
    """Usage for the lineage command group."""
    return """
Usage:
  bq-inspector lineage <subcommand> --params '<json>' | --params @file.json [options]

Subcommands:
  links        Immediate upstream/downstream links for a table
  graph        Multi-hop lineage graph for a table

Run bq-inspector lineage <subcommand> --help for params and examples.
""".strip()


def build_catalog_group_usage() -> str:
    """Usage for the catalog command group."""
    return """
Usage:
  bq-inspector catalog <subcommand> --params '<json>' | --params @file.json [options]

Subcommands:
  search               Search Knowledge Catalog entries
  entries lookup       Resolve an entry by canonical name
  entries get          Retrieve an entry by resource name
  entries list         List entries under an entry group
  entry-groups get|list
  entry-types get|list
  aspect-types get|list
  entry-links get      Retrieve a known entry link (no list command)
  glossaries get|list
  glossary-categories get|list
  glossary-terms get|list

Run bq-inspector catalog <subcommand> --help for params and examples.
""".strip()
