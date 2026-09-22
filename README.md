# bq-inspector

**bq-inspector** is a read-only CLI and MCP server for BigQuery: it fetches job metadata (`jobs.get` / `jobs.list`) and dataset or table metadata (`datasets.get`, `tables.list`, `tables.get`). The CLI prints **one JSON document on stdout** on success. Errors are **JSON on stderr** with a non-zero exit code (except plain-text `--help`).

Operational commands take a single **`--params`** JSON object (or `@path` to a file). Field names match the command’s **`--input-schema`** output. For flags and options, **`bq-inspector --help`** and **`bq-inspector <command> --help`** are authoritative; this README may summarize and can lag behind the CLI.

This repository is the **Python** implementation (`pip install bq-inspector`, import name `bq_inspector`). The original **TypeScript** CLI and library live in the [google-cloud-tools](https://github.com/yu-iskw/google-cloud-tools) monorepo under `packages/bq-inspect`. Both implementations target the same agent-facing contracts (command names, `--params` shapes, error codes, and JSON Schema discovery).

## Usage

```bash
bq-inspector <command> --params '<json>' | --params @file.json [options]
```

Every operational command also supports `--input-schema` and `--output-schema` (JSON Schema on stdout, no BigQuery call).

## MCP server

The package includes a read-only MCP server built with the stable MCP Python SDK (`mcp>=1.28,<2`). It uses the standard stdio transport and generates its tools from the same command registry and JSON Schemas as the CLI.

```bash
bq-inspector-mcp
```

Example client configuration:

```json
{
  "mcpServers": {
    "bq-inspector": {
      "command": "uvx",
      "args": ["--from", "bq-inspector", "bq-inspector-mcp"]
    }
  }
}
```

The MCP server inherits the CLI's Application Default Credentials and optional service-account impersonation parameters. It does not open a network listener. Each CLI command is exposed as a namespaced tool such as `bq_inspector_jobs_summary` or `bq_inspector_catalog_search`, with both `inputSchema` and `outputSchema` advertised during tool discovery.

## Install

From PyPI:

```bash
pip install bq-inspector
```

Or install as a standalone tool with [uv](https://github.com/astral-sh/uv):

```bash
uv tool install bq-inspector
```

From source (development or unreleased changes):

```bash
git clone https://github.com/yu-iskw/bq-inspector.git
cd bq-inspector
pip install .
# or: uv sync && uv run bq-inspector --help
```

Requires [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials) (ADC) unless you only use schema discovery flags (see below).

## Help

```bash
bq-inspector --help
bq-inspector <command> --help
```

Use `-h` anywhere `--help` is accepted.

Unknown commands print global usage plus `Unknown command: <argv>`.

## Agent workflow

1. Discover the params shape: `bq-inspector <command> --input-schema` (stdout is JSON Schema).
2. Build a JSON object with the required fields (camelCase keys such as `projectId`, `jobId`, `datasetId`).
3. Run the command with inline JSON or a file.

**Pipeline:** `jobs list` → `jobs summary` | `jobs query` | `jobs performance` | `jobs lineage` | `jobs impact` | `jobs get`

**Catalog / asset lineage:** `tables get` → `lineage links` → `lineage graph` (Data Lineage API; see [Lineage commands](#lineage-commands))

**Knowledge Catalog (Dataplex):** `catalog search` → `catalog entries lookup` → `catalog aspect-types get` (see [Knowledge Catalog commands](#knowledge-catalog-commands))

**Command forms:** Nested `jobs summary` and flat `summary` are equivalent for job views and `jobs list` → `list`.

**Job id formats:** Pass `jobId` alone, or a Console-style composite id in `jobId`:
`"my-proj:US.bquxjob_abc"` (location is parsed automatically; `projectId` must match if both are set).

**Verifying lineage/impact:** Use a job that references tables. Trivial queries like `SELECT 1` legitimately return empty lineage/impact fields.

**Smoke checklist:** `jobs list` with `allUsers: true` → `jobs summary` and flat `summary` with composite or split job ref.

**Which job command?**

| Goal                                             | Command            |
| ------------------------------------------------ | ------------------ |
| Find job ids (optional client-side filters)      | `jobs list`        |
| Status, timing, bytes/slots (default inspection) | `jobs summary`     |
| SQL, configuration, and light lineage stats      | `jobs query`       |
| Query plan, timeline, performanceInsights        | `jobs performance` |
| Tables, routines, datasets touched               | `jobs lineage`     |
| DML/load/ML/search/export side-effect stats      | `jobs impact`      |
| Full BigQuery Job resource                       | `jobs get`         |

**Asset lineage (table-centric, multi-hop via Data Lineage API):**

| Goal                                          | Command         |
| --------------------------------------------- | --------------- |
| Immediate upstream/downstream table neighbors | `lineage links` |
| Multi-hop lineage graph                       | `lineage graph` |

`jobs lineage` reports what a **single job** touched. `lineage links` / `lineage graph` query platform-wide table relationships (requires Data Lineage API enabled in GCP).

**Knowledge Catalog (governed metadata via Dataplex API):**

| Goal                                                  | Command                                              |
| ----------------------------------------------------- | ---------------------------------------------------- |
| Discover catalog entries (keyword or semantic search) | `catalog search`                                     |
| Resolve a discovered entry canonically                | `catalog entries lookup`                             |
| Retrieve entry, type, or glossary resources           | `catalog entries get`, `catalog entry-types get`, …  |
| List entries, types, glossaries (one page per call)   | `catalog entries list`, `catalog glossaries list`, … |
| Retrieve a known entry link                           | `catalog entry-links get`                            |

There is **no** `catalog entry-links list` command—the Dataplex API does not expose a general list method for entry links.

Each view command calls `jobs.get` once per job and projects the response in memory. **`jobs get` returns the full [Job](https://cloud.google.com/bigquery/docs/reference/rest/v2/Job) resource** from the API; other commands slice it for smaller, task-focused JSON. Field names match [Job statistics](https://cloud.google.com/bigquery/docs/reference/rest/v2/Job#JobStatistics); many nested blocks (for example `statistics.mlStatistics`) appear only for matching job kinds.

**Shared / sandbox projects:** `jobs list` returns your own jobs unless you set `allUsers: true`. In busy sandboxes, list with `allUsers: true`, then pass each job’s `jobReference.location` into job view commands. Omitting `location` on `jobs.get` often returns `BQINSPECTOR_PERMISSION_DENIED` (403), not a clear location error—the CLI hint will suggest adding `location` when that happens.

Example:

```bash
bq-inspector jobs summary --params '{"jobs":[{"projectId":"YOUR_PROJECT","jobId":"YOUR_JOB_ID"}]}'
bq-inspector summary --params '{"jobs":[{"projectId":"YOUR_PROJECT","jobId":"YOUR_PROJECT:US.bquxjob_abc"}]}'
```

Optional: `bq-inspector <command> --output-schema` for the response shape.

Invalid params fail with `BQINSPECTOR_INPUT_INVALID` and JSON Schema error paths on stderr; treat `--input-schema` as the contract for `--params`. See [Error codes](#error-codes) for other codes.

## Quickstart

### Inspect jobs

```bash
# Summary (default inspection — no SQL, no query plan)
bq-inspector jobs summary --params "$(cat <<'EOF'
{
  "jobs": [{ "projectId": "YOUR_PROJECT", "jobId": "YOUR_JOB_ID" }]
}
EOF
)"

# Set location from jobs.list jobReference (required for non-default regions)
bq-inspector jobs summary --params '{"jobs":[{"projectId":"YOUR_PROJECT","jobId":"YOUR_JOB_ID","location":"asia-northeast1"}]}'

# Other job views: include location from jobs.list when jobs are regional (same shape as summary above)
bq-inspector jobs query --params '{"jobs":[{"projectId":"YOUR_PROJECT","jobId":"YOUR_JOB_ID","location":"asia-northeast1"}]}'
bq-inspector jobs performance --params '{"jobs":[{"projectId":"YOUR_PROJECT","jobId":"YOUR_JOB_ID","location":"asia-northeast1"}]}'
bq-inspector jobs lineage --params '{"jobs":[{"projectId":"YOUR_PROJECT","jobId":"YOUR_JOB_ID","location":"asia-northeast1"}]}'
bq-inspector jobs impact --params '{"jobs":[{"projectId":"YOUR_PROJECT","jobId":"YOUR_JOB_ID","location":"asia-northeast1"}]}'
bq-inspector jobs get --params '{"jobs":[{"projectId":"YOUR_PROJECT","jobId":"YOUR_JOB_ID","location":"asia-northeast1"}]}'
```

### List jobs (`jobs list`)

Field list: [Params reference](#params-reference) (`jobs list`). Full schema: `bq-inspector jobs list --input-schema`.

In shared projects, set `"allUsers": true` or the list may be empty even when jobs exist. Use `jobReference.location` from list output for job view commands.

```bash
bq-inspector jobs list --params "$(cat <<'EOF'
{
  "projectId": "YOUR_PROJECT",
  "allUsers": true,
  "minCreationTime": "2026-05-17T00:00:00Z",
  "maxCreationTime": "2026-05-18T00:00:00Z",
  "minSlotMs": "60000",
  "labels": { "dbt_invocation_id": "abc123" },
  "maxResults": 50
}
EOF
)"
```

### Dataset and table metadata

```bash
bq-inspector datasets get --params '{"projectId":"YOUR_PROJECT","datasetId":"YOUR_DATASET"}'
bq-inspector tables list --params '{"projectId":"YOUR_PROJECT","datasetId":"YOUR_DATASET"}'
bq-inspector tables get --params '{"projectId":"YOUR_PROJECT","datasetId":"YOUR_DATASET","tableId":"YOUR_TABLE"}'
```

### Asset lineage (`lineage links`, `lineage graph`)

Requires the [Data Lineage API](https://cloud.google.com/dataplex/docs/reference/data-lineage/rest) enabled and `roles/datalineage.viewer` on `clientProjectId` (defaults to `projectId` when omitted). The `location` param is the **Lineage API location** (`us`, `eu`, `global`, …), not the BigQuery dataset location.

```bash
# Immediate upstream sources (1 hop)
bq-inspector lineage links --params '{"location":"us","projectId":"YOUR_PROJECT","datasetId":"YOUR_DATASET","tableId":"YOUR_TABLE","direction":"UPSTREAM"}'

# Multi-hop downstream graph (default maxDepth 5)
bq-inspector lineage graph --params '{"location":"us","projectId":"YOUR_PROJECT","datasetId":"YOUR_DATASET","tableId":"YOUR_TABLE","direction":"DOWNSTREAM","maxDepth":10}'
```

## Commands overview

| Command            | What it returns (from help)                          | BigQuery APIs (typical)  | Suggested predefined role                                      |
| ------------------ | ---------------------------------------------------- | ------------------------ | -------------------------------------------------------------- |
| `jobs summary`     | Job status, timing, bytes/slots (default inspection) | `jobs.get`               | `roles/bigquery.resourceViewer`                                |
| `jobs query`       | SQL, configuration, light lineage stats              | `jobs.get`               | `roles/bigquery.resourceViewer`                                |
| `jobs performance` | Query plan, timeline, performanceInsights            | `jobs.get`               | `roles/bigquery.resourceViewer`                                |
| `jobs lineage`     | Tables, routines, datasets touched                   | `jobs.get`               | `roles/bigquery.resourceViewer`                                |
| `jobs impact`      | DML/load/ML/search/export/spark side-effect stats    | `jobs.get`               | `roles/bigquery.resourceViewer`                                |
| `jobs get`         | Full BigQuery Job JSON                               | `jobs.get`               | `roles/bigquery.resourceViewer`                                |
| `jobs list`        | List jobs (optional client-side filters in params)   | `jobs.list`              | `roles/bigquery.resourceViewer`                                |
| `datasets get`     | Dataset metadata                                     | `datasets.get`           | `roles/bigquery.metadataViewer` (often granted on the dataset) |
| `tables list`      | List tables in a dataset                             | `tables.list`            | `roles/bigquery.metadataViewer`                                |
| `tables get`       | Table metadata                                       | `tables.get`             | `roles/bigquery.metadataViewer`                                |
| `lineage links`    | Immediate upstream/downstream table links            | `searchLinks`            | `roles/datalineage.viewer` on `clientProjectId`                |
| `lineage graph`    | Multi-hop table lineage graph                        | `searchLineageStreaming` | `roles/datalineage.viewer` on `clientProjectId`                |

Project-wide `datasets list` is not supported (it would need `datasets.list`, which is outside the usual metadata-only posture).

## Lineage commands

- **`jobs lineage`** — job-local: tables/routines/datasets referenced by one BigQuery job (`jobs.get` projection).
- **`lineage links`** — asset-centric: immediate neighbors via Data Lineage API (`searchLinks`).
- **`lineage graph`** — asset-centric: multi-hop graph via Data Lineage API (`searchLineageStreaming`).

Lineage commands use the `cloud-platform` OAuth scope (required by `searchLinks`; requested only when those commands run). Access is still constrained by IAM (`roles/datalineage.viewer`).

## Params reference

Summaries from per-command `--help`; full types and constraints: `bq-inspector <command> --input-schema`.

**All commands:** optional `impersonateServiceAccount`, `impersonateDelegates`.

**Job view commands** (`jobs summary`, `jobs query`, `jobs performance`, `jobs lineage`, `jobs impact`, `jobs get`):
