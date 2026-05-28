"""Usage strings for bq-inspect commands."""

GLOBAL_USAGE = """
bq-inspect — read-only BigQuery job and metadata inspection (JSON on stdout).

Usage:
  bq-inspect <command> --params '<json>' | --params @file.json [options]

Commands (each supports --input-schema / --output-schema for JSON Schema on stdout):
  jobs summary     Job status, timing, bytes/slots (default inspection)
  jobs query       SQL, configuration, and light lineage stats
  jobs performance Query plan, timeline, performanceInsights, script/session stats
  jobs lineage     Referenced tables, routines, datasets, destinations
  jobs impact      DML stats, load/export/ML/search/spark side-effect stats
  jobs get         Full BigQuery Job JSON
  jobs list        List jobs (optional client-side filters in params)
  datasets get     Dataset metadata
  tables list      List tables in a dataset
  tables get       Table metadata

Legacy:
  schema         Same contracts as above (see: bq-inspect schema --help)

Global:
  bq-inspect --help | -h
  bq-inspect <command> --help

Agent workflow: jobs list → jobs summary | jobs query | jobs performance | jobs lineage | jobs impact | jobs get

Errors are JSON on stderr; success is JSON on stdout (except plain-text --help).
""".strip()

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

JOBS_SUMMARY_USAGE = f"""
Usage:
  bq-inspect jobs summary --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

{_JOBS_VIEW_PARAMS}

Examples:
  bq-inspect jobs summary --params '{{"jobs":[{{"projectId":"my-proj","jobId":"abc"}}]}}'
  bq-inspect jobs summary --params @./jobs-summary.json
""".strip()

JOBS_QUERY_USAGE = f"""
Usage:
  bq-inspect jobs query --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

{_JOBS_VIEW_PARAMS}

Examples:
  bq-inspect jobs query --params '{{"jobs":[{{"projectId":"my-proj","jobId":"abc"}}]}}'
  bq-inspect jobs query --params @./jobs-query.json
""".strip()

JOBS_PERFORMANCE_USAGE = f"""
Usage:
  bq-inspect jobs performance --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

{_JOBS_VIEW_PARAMS}

Examples:
  bq-inspect jobs performance --params '{{"jobs":[{{"projectId":"my-proj","jobId":"abc"}}]}}'
  bq-inspect jobs performance --params @./jobs-performance.json
""".strip()

JOBS_LINEAGE_USAGE = f"""
Usage:
  bq-inspect jobs lineage --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

{_JOBS_VIEW_PARAMS}

Examples:
  bq-inspect jobs lineage --params '{{"jobs":[{{"projectId":"my-proj","jobId":"abc"}}]}}'
  bq-inspect jobs lineage --params @./jobs-lineage.json
""".strip()

JOBS_IMPACT_USAGE = f"""
Usage:
  bq-inspect jobs impact --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

{_JOBS_VIEW_PARAMS}

Examples:
  bq-inspect jobs impact --params '{{"jobs":[{{"projectId":"my-proj","jobId":"abc"}}]}}'
  bq-inspect jobs impact --params @./jobs-impact.json
""".strip()

JOBS_GET_USAGE = f"""
Usage:
  bq-inspect jobs get --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

{_JOBS_VIEW_PARAMS}

Examples:
  bq-inspect jobs get --params '{{"jobs":[{{"projectId":"my-proj","jobId":"abc"}}]}}'
  bq-inspect jobs get --params @./jobs-get.json
""".strip()

JOBS_LIST_USAGE = f"""
Usage:
  bq-inspect jobs list --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

Params (see --input-schema):
  projectId            Required
  API (jobs.list): minCreationTime, maxCreationTime, pageToken, maxResults, allUsers, state, parentJobId
  Post-list (current page): minSlotMs, minBytesBilled, labels
  impersonateServiceAccount, impersonateDelegates

  In shared projects use allUsers: true or jobs.list may return an empty array.
  Copy jobReference.location from list output into job view commands (jobs.get requires location for non-default regions).

Examples:
  bq-inspect jobs list --params '{{"projectId":"my-proj","allUsers":true,"maxResults":50}}'
  bq-inspect jobs list --params @./jobs-list.json
""".strip()

DATASETS_GET_USAGE = f"""
Usage:
  bq-inspect datasets get --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

Params (see --input-schema):
  projectId, datasetId
  impersonateServiceAccount, impersonateDelegates

Examples:
  bq-inspect datasets get --params '{{"projectId":"my-proj","datasetId":"analytics"}}'
  bq-inspect datasets get --params @./datasets-get.json
""".strip()

TABLES_LIST_USAGE = f"""
Usage:
  bq-inspect tables list --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

Params (see --input-schema):
  projectId, datasetId
  impersonateServiceAccount, impersonateDelegates

Examples:
  bq-inspect tables list --params '{{"projectId":"my-proj","datasetId":"analytics"}}'
  bq-inspect tables list --params @./tables-list.json
""".strip()

TABLES_GET_USAGE = f"""
Usage:
  bq-inspect tables get --params '<json>' | --params @file.json [options]

{_PARAMS_DISCOVERY}

Params (see --input-schema):
  projectId, datasetId, tableId
  impersonateServiceAccount, impersonateDelegates

Examples:
  bq-inspect tables get --params '{{"projectId":"my-proj","datasetId":"analytics","tableId":"events"}}'
  bq-inspect tables get --params @./tables-get.json
""".strip()

JOBS_GROUP_USAGE = """
Usage:
  bq-inspect jobs <subcommand> --params '<json>' | --params @file.json [options]

Subcommands:
  summary      Job status, timing, bytes/slots (default inspection)
  query        SQL, configuration, and light lineage stats
  performance  Query plan, timeline, performanceInsights, script/session stats
  lineage      Referenced tables, routines, datasets, destinations
  impact       DML stats, load/export/ML/search/spark side-effect stats
  get          Full BigQuery Job JSON
  list         List jobs (optional client-side filters in params)

Run bq-inspect jobs <subcommand> --help for params and examples.
""".strip()

DATASETS_GROUP_USAGE = """
Usage:
  bq-inspect datasets get --params '<json>' | --params @file.json [options]

Subcommands:
  get          Dataset metadata

Run bq-inspect datasets get --help for params and examples.
""".strip()

TABLES_GROUP_USAGE = """
Usage:
  bq-inspect tables <subcommand> --params '<json>' | --params @file.json [options]

Subcommands:
  list         List tables in a dataset
  get          Table metadata

Run bq-inspect tables <subcommand> --help for params and examples.
""".strip()

SCHEMA_USAGE = """
Usage:
  bq-inspect schema <input|output> --format json-schema

Legacy JSON Schema (prefer per-command --input-schema / --output-schema).

Subcommands:
  input     Jobs get input JSON Schema
  output    Response JSON Schema (oneOf across commands)

Examples:
  bq-inspect schema input --format json-schema
  bq-inspect schema output --format json-schema

Run bq-inspect schema <subcommand> --help for a short reminder.
""".strip()

SCHEMA_INPUT_USAGE = """
Usage:
  bq-inspect schema input --format json-schema
""".strip()

SCHEMA_OUTPUT_USAGE = """
Usage:
  bq-inspect schema output --format json-schema
""".strip()
