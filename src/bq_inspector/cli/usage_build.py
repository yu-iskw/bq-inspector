"""Build CLI usage strings from shared templates (single source for help text)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class ParamsBodyKind(Enum):
    """Params section body for a command's --help text."""

    JOBS_VIEW = "jobs_view"
    JOBS_LIST = "jobs_list"
    DATASETS_GET = "datasets_get"
    TABLES_LIST = "tables_list"
    TABLES_GET = "tables_get"


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
}

_JOBS_SUBCOMMANDS: tuple[tuple[str, str], ...] = (
    ("summary", "Job status, timing, bytes/slots (default inspection)"),
    ("query", "SQL, configuration, and light lineage stats"),
    ("performance", "Query plan, timeline, performanceInsights, script/session stats"),
    ("lineage", "Referenced tables, routines, datasets, destinations"),
    ("impact", "DML stats, load/export/ML/search/spark side-effect stats"),
    ("get", "Full BigQuery Job JSON"),
    ("list", "List jobs (optional client-side filters in params)"),
)


def build_global_usage() -> str:
    """Root bq-inspector usage."""
    subcommand_lines = "\n".join(f"  {name:<14} {desc}" for name, desc in _JOBS_SUBCOMMANDS)
    return f"""
bq-inspector — read-only BigQuery job and metadata inspection (JSON on stdout).

Usage:
  bq-inspector <command> --params '<json>' | --params @file.json [options]

Commands (each supports --input-schema / --output-schema for JSON Schema on stdout):
{subcommand_lines}
  datasets get     Dataset metadata
  tables list      List tables in a dataset
  tables get       Table metadata

Legacy:
  schema         Same contracts as above (see: bq-inspector schema --help)

Global:
  bq-inspector --help | -h
  bq-inspector <command> --help

Agent workflow: jobs list → jobs summary | jobs query | jobs performance | jobs lineage | jobs impact | jobs get

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
    lines = "\n".join(f"  {name:<12} {desc}" for name, desc in _JOBS_SUBCOMMANDS)
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


def build_schema_group_usage() -> str:
    """Usage for the legacy schema command group."""
    return """
Usage:
  bq-inspector schema <input|output> --format json-schema

Legacy JSON Schema (prefer per-command --input-schema / --output-schema).

Subcommands:
  input     Jobs get input JSON Schema
  output    Response JSON Schema (oneOf across commands)

Examples:
  bq-inspector schema input --format json-schema
  bq-inspector schema output --format json-schema

Run bq-inspector schema <subcommand> --help for a short reminder.
""".strip()


def build_schema_subcommand_usage(name: Literal["input", "output"]) -> str:
    """Usage for schema input or output."""
    return f"""
Usage:
  bq-inspector schema {name} --format json-schema
""".strip()
