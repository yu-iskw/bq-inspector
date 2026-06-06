# bq-inspector

**bq-inspector** is a read-only CLI for BigQuery: it fetches job metadata (`jobs.get` / `jobs.list`) and dataset or table metadata (`datasets.get`, `tables.list`, `tables.get`). It prints **one JSON document on stdout** on success. Errors are **JSON on stderr** with a non-zero exit code (except plain-text `--help`).

Operational commands take a single **`--params`** JSON object (or `@path` to a file). Field names match the command’s **`--input-schema`** output. For flags and options, **`bq-inspector --help`** and **`bq-inspector <command> --help`** are authoritative; this README may summarize and can lag behind the CLI.

This repository is the **Python** implementation (`pip install bq-inspector`, import name `bq_inspector`). The original **TypeScript** CLI and library live in the [google-cloud-tools](https://github.com/yu-iskw/google-cloud-tools) monorepo under `packages/bq-inspect`. Both implementations target the same agent-facing contracts (command names, `--params` shapes, error codes, and JSON Schema discovery).

## Usage

```bash
bq-inspector <command> --params '<json>' | --params @file.json [options]
```

Every operational command also supports `--input-schema` and `--output-schema` (JSON Schema on stdout, no BigQuery call).

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
| `jobs lineage`     | Referenced tables, routines, datasets, destinations  | `jobs.get`               | `roles/bigquery.resourceViewer`                                |
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

- `jobs`: non-empty array of `{ projectId, jobId, location? }` — include `location` from `jobs.list` output when jobs are not in the default region

**`jobs list`:**

- `projectId` (required)
- **Forwarded to `jobs.list` (API):** `minCreationTime`, `maxCreationTime`, `pageToken`, `maxResults`, `allUsers`, `state`, `parentJobId` (`allUsers: true` is often needed in shared sandboxes)
- **Post-list (current page only):** `minSlotMs`, `minBytesBilled`, `labels` — paginate with `pageToken` if you need more matches. The Python port matches labels under `configuration.labels` (typical BigQuery shape); the TypeScript port only checks top-level `labels`.
- Regional jobs: read `jobReference.location` from list output; pass `location` on job view commands, not on `jobs list` (BigQuery does not support a location query param on `jobs.list`)

**Catalog** (`datasets get`, `tables list`, `tables get`):

- `projectId`, `datasetId` (`tableId` required for `tables get`)
- `tables list` returns all tables in the dataset (the SDK auto-paginates `tables.list`). Unlike `jobs list`, there is no `pageToken` on this command.

**Lineage** (`lineage links`, `lineage graph`):

- `location` (required) — Data Lineage API location (`us`, `eu`, `global`, …)
- `projectId`, `datasetId`, `tableId` (required) — table to search from
- `direction` (required) — `UPSTREAM` or `DOWNSTREAM`
- `clientProjectId` (optional) — API billing/quota project; defaults to `projectId`
- `lineage links` only: `pageSize`, `pageToken`
- `lineage graph` only: `maxDepth` (default 5), `maxResults` (default 1000)

**Knowledge Catalog** (`catalog search`, `catalog entries lookup`, …):

- `catalog search`: `projectId`, `query` (required); `location` defaults to `global`; optional `scope`, `semanticSearch` (default `false`), `orderBy`, `pageSize` (default 50), `pageToken`
- `catalog entries lookup`: `projectId`, `location`, `entry` (required); optional `view`, `aspectTypes`, `paths`
- Get commands: canonical Dataplex `name` (required); entries get also supports `view`, `aspectTypes`, `paths`
- List commands: `parent` (required); optional `pageSize` (default 100), `pageToken`, `filter`, `orderBy`
- List and search commands return **one upstream API page** per invocation (no hidden auto-pagination)

## JSON Schema discovery

- **Discovery:** `--input-schema` or `--output-schema` (use one at a time; prints JSON Schema on stdout and exits without calling BigQuery).
- **Required for runs:** `--params` as JSON or `@path` to a JSON file.

Examples:

```bash
bq-inspector jobs summary --input-schema
bq-inspector jobs summary --output-schema
bq-inspector jobs get --input-schema
bq-inspector jobs list --input-schema
bq-inspector datasets get --output-schema
bq-inspector lineage links --input-schema
bq-inspector lineage graph --output-schema
bq-inspector catalog search --input-schema
bq-inspector catalog entries lookup --output-schema
```

## Knowledge Catalog commands

Read-only [Knowledge Catalog](https://docs.cloud.google.com/dataplex/docs/introduction) inspection via the Dataplex API. CLI command group: `catalog`. Internal package: `knowledge_catalog`.

```bash
bq-inspector catalog search --params '{"projectId":"YOUR_SEARCH_PROJECT","query":"YOUR_TERM","pageSize":50}'
bq-inspector catalog entries lookup --params @lookup.json
bq-inspector catalog entry-types list --params '{"parent":"projects/YOUR_PROJECT/locations/global","pageSize":5}'
bq-inspector catalog glossaries list --params '{"parent":"projects/YOUR_PROJECT/locations/YOUR_LOCATION","pageSize":5}'
```

**IAM (least privilege):**

- **Search request project:** `roles/dataplex.catalogViewer` (includes `dataplex.projects.search`)
- **BigQuery-backed search results:** also requires `roles/bigquery.metadataViewer` on relevant datasets/projects
- **Impersonation:** `roles/iam.serviceAccountTokenCreator` on the target service account

Catalog commands use OAuth scope `https://www.googleapis.com/auth/cloud-platform` (required by Dataplex Universal Catalog REST methods such as `lookupEntry` and `searchEntries`).

**Empty search results** are successful (not an error). They may indicate no matches, narrow scope, missing source-system metadata visibility, or VPC Service Controls boundaries.

**Metadata sensitivity:** catalog output may include schemas, descriptions, ownership, classifications, and glossary terms. Treat stdout as potentially sensitive in CI and agent environments.

## Error codes

Errors are JSON on stderr with a `code` field. Schema validation failures include `schemaErrors` with JSON Pointer paths.

| Code                            | Typical cause                                                                                                   |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `BQINSPECTOR_INPUT_INVALID`     | Bad `--params` or flags; schema validation; HTTP 4xx (except 401/403/404/429).                                  |
| `BQINSPECTOR_PERMISSION_DENIED` | IAM or ADC; on `jobs.get`, often missing `location` or wrong job ref (see [Troubleshooting](#troubleshooting)). |
| `BQINSPECTOR_JOB_NOT_FOUND`     | HTTP 404 from BigQuery (job or catalog). Read `source.api` and `hint` for the resource type.                    |
| `BQINSPECTOR_LOCATION_REQUIRED` | Reserved; prefer `location` on job refs (see hints on 403).                                                     |
| `BQINSPECTOR_API_RATE_LIMITED`  | HTTP 429; retryable.                                                                                            |
| `BQINSPECTOR_API_UNAVAILABLE`   | Transient API / 5xx.                                                                                            |
| `BQINSPECTOR_INTERNAL`          | Unexpected CLI failure.                                                                                         |

## Troubleshooting

Symptom-first checks when JSON looks wrong but the CLI is working:

**`jobs list` returns `"jobs": []`**

- In shared sandboxes, set `"allUsers": true` in `--params` (default list is only your user’s jobs).
- With impersonation: the caller needs **Service Account Token Creator** on the target; the impersonated identity needs **BigQuery job list** access (`roles/bigquery.resourceViewer` or equivalent).

**Job view commands return per-job `BQINSPECTOR_PERMISSION_DENIED` (403)**

- **`location` omitted:** copy `jobReference.location` from `jobs list` into each job ref (required for many regional jobs).
- **`location` set:** BigQuery may still return **403 Access Denied** for a wrong `jobId`, wrong region, or IAM—not only missing `location`. Confirm `projectId` and `jobId` from `jobs list`; do not assume the code will be `BQINSPECTOR_JOB_NOT_FOUND`.

**`BQINSPECTOR_JOB_NOT_FOUND`**

- Typical for a wrong **project** on a job ref, a missing **dataset** or **table**, or catalog APIs returning HTTP 404.
- The error code matches the TypeScript port for all 404 responses. Use **`source.api`** (`bigquery.jobs.get` vs `bigquery.datasets.get`, etc.) and the stderr **`hint`** to tell jobs from catalog resources apart.

**Post-filters on `jobs list`** (`minSlotMs`, `minBytesBilled`, `labels`)

- Applied to the **current API page only**. If results are empty, increase `maxResults` or follow `pageToken` until matches appear.

**Multi-job `--params`**

- The process can exit **0** while individual entries in `jobs[]` include `errors`. Inspect each job element.

## Authentication

The CLI uses the official **BigQuery** client with **Application Default Credentials** from `google-auth`.

- **Default:** credentials are scoped to `https://www.googleapis.com/auth/bigquery.readonly` for BigQuery job and catalog commands.
- **Lineage commands** (`lineage links`, `lineage graph`) use `https://www.googleapis.com/auth/cloud-platform` (required by the Data Lineage `searchLinks` API; requested only when those commands run).
- **Knowledge Catalog commands** (`catalog …`) use `https://www.googleapis.com/auth/cloud-platform` (required by Dataplex Universal Catalog REST APIs).
- **Impersonation:** set `impersonateServiceAccount` (and optional `impersonateDelegates`) in `--params`. The source principal must have **Service Account Token Creator** on the target (and on each delegate). While impersonating, access is still requested with `bigquery.readonly` on the **target** identity. The source ADC client uses `https://www.googleapis.com/auth/cloud-platform` only for the token exchange path.

Example params fragment:

```json
{
  "impersonateServiceAccount": "TARGET@PROJECT_ID.iam.gserviceaccount.com",
  "impersonateDelegates": ["FIRST_DELEGATE@PROJECT_ID.iam.gserviceaccount.com"]
}
```

Service account **JSON key files** are not a dedicated CLI option; ADC may still resolve a key via environment if your platform configures it that way.

## IAM guidance

Prefer narrow read access:

- **Job commands / `jobs list`:** `roles/bigquery.resourceViewer` (or a custom role with `bigquery.jobs.get` / `bigquery.jobs.list`) on the **identity that calls BigQuery** (the impersonated service account when using impersonation).
- **`datasets get` / `tables list` / `tables get`:** `roles/bigquery.metadataViewer` on the dataset or project (or a custom metadata-only role with `datasets.get`, `tables.list`, `tables.get`).
- **`lineage links` / `lineage graph`:** `roles/datalineage.viewer` on `clientProjectId`; enable the Data Lineage API in that project.
- **`catalog search`:** `roles/dataplex.catalogViewer` on the search request project; BigQuery-backed results also need `roles/bigquery.metadataViewer` on source datasets/projects.
- **Other `catalog` commands:** `roles/dataplex.catalogViewer` on the relevant catalog resources.
- Grant the calling principal `roles/iam.serviceAccountTokenCreator` on the target service account (and delegates, if any) when using impersonation.
- Avoid `roles/bigquery.dataViewer` and `roles/bigquery.jobUser` for inspection-only workflows.

## Programmatic use (Python)

The primary surface is the **`bq-inspector` CLI**. For in-process use, import from the `bq_inspector` package (for example core use cases under `bq_inspector.core`, ports under `bq_inspector.bigquery.port`, and JSON Schema helpers under `bq_inspector.schemas`). The package does not yet expose a stable public API beyond what the CLI uses internally; prefer subprocess invocation or the TypeScript library in [google-cloud-tools](https://github.com/yu-iskw/google-cloud-tools/tree/main/packages/bq-inspect) if you need a documented library entrypoint today.

See [CONTRIBUTING.md](CONTRIBUTING.md) for architecture and test patterns when extending the Python implementation.

## Security notes

**Read-only metadata:** job resources and dataset/table metadata only. No table row reads and no arbitrary query execution. Job output may include SQL, user emails, and other fields from the BigQuery API; the caller is responsible for where JSON is stored or logged.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) for setup, lint, and test commands.

```bash
make setup
make lint
make test
```
