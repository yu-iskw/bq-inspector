# 3. Python port from TypeScript

Date: 2026-05-28

## Status

Accepted

## Context

The `bq-inspect` tool started as a TypeScript CLI and library in the `google-cloud-tools` monorepo (`packages/bq-inspect`). It provides read-only BigQuery inspection for AI agents: job views (`jobs list`, `jobs summary`, `jobs query`, and related commands), dataset and table metadata, JSON Schema discovery (`--input-schema`, `--output-schema`), and structured JSON on stdout with machine-readable errors on stderr.

A standalone Python package is needed for teams that prefer Python tooling, PyPI distribution, and integration with Python-based agent stacks without a Node.js runtime.

## Decision

1. **Bootstrap** this repository (`bq-inspect` on PyPI, import name `bq_inspect`) as a Python port of the TypeScript CLI, targeting **behavioral parity** with the existing command surface, `--params` JSON contract, schema flags, and error codes.
2. **CLI entry point**: `[project.scripts]` maps `bq-inspect` to `bq_inspect.cli:main`, matching the npm binary name `bq-inspect`.
3. **Runtime dependencies** (initial):
   - **`google-cloud-bigquery`** — same BigQuery REST surface as `@google-cloud/bigquery` in the TS package (`jobs.get`, `jobs.list`, `datasets.get`, `tables.*`).
   - **`google-auth`** — Application Default Credentials and optional service-account impersonation (parity with `google-auth-library` usage in TS).
   - **`jsonschema`** — validate `--params` against command input schemas (parity with **Ajv** + `ajv-formats` in TS; Python uses JSON Schema draft support via `jsonschema` rather than shipping Ajv).

Implementation phases after bootstrap will port commands, schemas, and fixtures from `packages/bq-inspect` in `google-cloud-tools`.

## Consequences

- Two implementations must be kept in sync for agent-facing contracts (command names, `--params` shapes, stderr error codes, schema JSON).
- PyPI and npm publish pipelines remain separate; version numbers may diverge until release automation is unified.
- Python agents gain a native install path (`pip install bq-inspect`) without Node.

### Contract notes (Python vs TypeScript)

- **HTTP 4xx** from BigQuery (except 401, 403, 404, 429) map to `BQINSPECT_INPUT_INVALID` (non-retriable, exit 2). The TypeScript CLI maps other unlisted 4xx to `BQINSPECT_API_UNAVAILABLE` (retriable).
- **`jobs list` timestamps** in `--params` must include an explicit timezone (`Z` or numeric offset). Naive ISO strings are rejected at schema validation.
- **`source.fetchedAt`** on job views uses ISO-8601 UTC with millisecond precision (aligned with JavaScript `Date.toISOString()`).
- **`BQINSPECT_JOB_NOT_FOUND`** is emitted for every HTTP 404 (jobs and catalog APIs), matching TypeScript. Catalog 404 responses include an extra stderr `hint`; agents should read `source.api`.
- **`jobs list` `labels` filter** reads `configuration.labels` first, then top-level `labels`. This differs from the TypeScript port (top-level only) and matches typical BigQuery job payloads.

## Alternatives considered

- **Keep TypeScript only** — Rejected; explicit user requirement for a Python package and PyPI distribution.
- **Subprocess wrapper around the npm CLI** — Rejected; adds Node dependency and complicates error/schema handling in Python agents.
- **pydantic instead of jsonschema** — Deferred; JSON Schema files are shared conceptually with TS; `jsonschema` validates the same schema documents Ajv uses without a separate model layer in Phase 0.

## Trade-offs

- **jsonschema vs Ajv**: Slightly different validation messages and draft feature support; tests must assert stable error paths (`BQINSPECT_INPUT_INVALID`) rather than byte-identical Ajv output.
- **Dual maintenance**: Bug fixes and new commands require updates in both repos until one implementation is deprecated (not planned).

## References

- TypeScript source: `google-cloud-tools` monorepo, `packages/bq-inspect`
- [ADR 0001](0001-record-architecture-decisions.md) — ADR process
- [ADR 0002](0002-mise-toolchain-and-attestation-settings.md) — Toolchain for this repo
