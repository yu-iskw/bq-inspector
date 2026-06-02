# Contributing to bq-inspect

This document is for **developers** working on the Python `bq-inspect` package in this repository. End-user documentation lives in [README.md](README.md).

Repository-wide conventions (lint, test, git workflow, security) are in [AGENTS.md](AGENTS.md).

The TypeScript reference implementation lives in the [google-cloud-tools](https://github.com/yu-iskw/google-cloud-tools) monorepo under `packages/bq-inspect`. Keep agent-facing contracts (command names, `--params` shapes, stderr error codes, schema JSON) aligned across both implementations.

## Prerequisites

- **Python** 3.10+ (see [`.python-version`](.python-version); CI also tests 3.10–3.12).
- **[uv](https://github.com/astral-sh/uv)** — package and venv management (`requirements.setup.txt`).
- **[mise](https://mise.jdx.dev/)** — optional but recommended for Trunk, Trivy, OSV-Scanner, Grype, and CodeQL (`make setup-tools`).

## Clone and install

```bash
git clone https://github.com/yu-iskw/bq-inspect.git
cd bq-inspect
make setup
```

`make setup` runs `make setup-tools` (mise toolchain + Trunk install) then `make setup-python` (`uv sync` with development dependencies).

If you only need Python (no mise/Trunk):

```bash
make setup-python
```

## Build, test, and lint

From the repository root:

```bash
make build    # hatchling wheel/sdist via dev/build.sh
make test     # pytest with coverage (alias: make coverage)
make lint     # Trunk check via mise
make format   # Trunk format + ssort
```

CI runs `uv run bash dev/test_python.sh` on Python 3.10–3.12 (see [`.github/workflows/test.yml`](.github/workflows/test.yml)).

Before a change that might affect tooling or dead code:

```bash
make dead-code   # Vulture
make scan-vulnerabilities
```

### Test coverage

`make test` runs pytest with **pytest-cov** over `src/bq_inspect/tests/` and reports line and branch coverage in the terminal plus `coverage.xml`.

There is no enforced coverage gate in CI yet. Match the TypeScript package’s intent: **strong coverage on critical paths** (`core/`, `cli/input/`, `cli/params/`, `bigquery/`, `schemas/`). The TS workspace targets **85%** lines/functions/statements and **80%** branches for those areas; aim for similar coverage when adding or changing behavior.

Prefer state-based tests on observable JSON output; avoid new mocks unless necessary.

### Run the CLI from the repo

After `make setup-python` or `make setup`:

```bash
uv run bq-inspect --help
uv run bq-inspect jobs get --help
uv run bq-inspect jobs summary --input-schema
```

Or use the editable install entrypoint:

```bash
bq-inspect --help
```

### Manual smoke (optional)

After a CLI or BigQuery client change, re-run a short live check against a project you control (ADC via `gcloud auth application-default login`, or CI credentials). Do not commit project IDs, service account emails, or params files with secrets.

1. `make setup-python`
2. `uv run bq-inspect jobs list --params '{"projectId":"YOUR_PROJECT","allUsers":true,"maxResults":10}'` (add `impersonateServiceAccount` in JSON when testing impersonation)
3. Copy `jobReference.location` from list output into a job view, e.g. `jobs summary`
4. Spot-check `datasets get` and `tables list` on a dataset you can read

See [README.md — Troubleshooting](README.md#troubleshooting) for empty lists, 403 vs not-found on `jobs.get`, and post-filter behavior.

## CLI and agent workflow

Operational commands accept only:

- **`--params`** — JSON object or `@path` to a JSON file (required to run).
- **`--input-schema`** / **`--output-schema`** — print JSON Schema and exit (no BigQuery call).

Parsing layers:

- [`src/bq_inspect/operational/`](src/bq_inspect/operational/) — operational flag types, Click flag specs, `parse_operational_argv`, and `resolve_params_value` (used by CLI and commands).
- [`src/bq_inspect/cli/command_registry.py`](src/bq_inspect/cli/command_registry.py) — canonical command paths, usage strings (from templates), and runners.
- [`src/bq_inspect/cli/usage_build.py`](src/bq_inspect/cli/usage_build.py) — shared usage templates; registry builds per-command help text.
- [`src/bq_inspect/cli/click_cli.py`](src/bq_inspect/cli/click_cli.py) — Click command tree built from the registry.
- [`src/bq_inspect/cli/help.py`](src/bq_inspect/cli/help.py) — single help pipeline (`--help` / `-h` → registry lookup).
- [`src/bq_inspect/schemas/validate_input.py`](src/bq_inspect/schemas/validate_input.py) — `jsonschema` validation against the same JSON Schema as `--input-schema`.
- [`src/bq_inspect/cli/input/map_input.py`](src/bq_inspect/cli/input/map_input.py) — domain mapping (epoch ms, list filters split, impersonation trim).
- [`src/bq_inspect/cli/input/input_parsers.py`](src/bq_inspect/cli/input/input_parsers.py) — `validate_input` + `map*` per command.
- [`src/bq_inspect/commands/`](src/bq_inspect/commands/) — wire parsers to core use cases.

**Agent workflow:** `bq-inspect <command> --input-schema` → build params JSON → `bq-inspect <command> --params @file.json` (or inline JSON). Tests should pass `--params` with `json.dumps({...})` rather than legacy kebab-case flags.

## CLI help text (source of truth)

Published usage strings are built from:

- [`src/bq_inspect/cli/usage_build.py`](src/bq_inspect/cli/usage_build.py) — shared templates and `ParamsBodyKind` sections.
- [`src/bq_inspect/cli/command_registry.py`](src/bq_inspect/cli/command_registry.py) — command paths, runners, and generated usage (source of truth for paths and help lookup).
- [`src/bq_inspect/cli/help.py`](src/bq_inspect/cli/help.py) — resolves argv keys to usage via the registry for `bq-inspect … --help`.

**Rule:** Any new or changed params field must:

1. Update JSON Schema in [`src/bq_inspect/schemas/input_schema.py`](src/bq_inspect/schemas/input_schema.py) (runtime validation follows automatically).
2. Update [`src/bq_inspect/cli/input/map_input.py`](src/bq_inspect/cli/input/map_input.py) only if the field needs domain mapping beyond schema shape.
3. Add or extend a `ParamsCommandUsageMeta` row in [`command_registry.py`](src/bq_inspect/cli/command_registry.py) and adjust `ParamsBodyKind` text in [`usage_build.py`](src/bq_inspect/cli/usage_build.py) when the params section changes.
4. Update [README.md](README.md) if the field is user-facing in examples or narrative.

Keep [README.md](README.md) examples aligned with `--help` output; end users treat **`--help`** as authoritative.

## Architecture (minimal hexagonal)

Layer flow: **`cli/`** → **`commands/`** → **`core/`** → **`bigquery/`** → **`schemas/`**

- **`cli/`** — CLI package (`cli/__init__.py` exports `main` from `dispatch.py`): Click tree (`click_cli.py`, `command_registry.py`), help (`help.py`), and input mapping (`input/`); operational parsing lives in **`operational/`**.
- **`commands/`** — Thin CLI adapters grouped by resource (`jobs/`, `datasets/`, `tables/`), plus shared `command_shared.py` and meta `schema.py`: parse operational argv, build the BigQuery client, call application functions.
- **`core/`** — Use cases grouped by resource (`jobs`, `datasets`, `tables`) plus pure helpers (`project_job`, `shared`).
- **`bigquery/`** — Transport layer (`auth/`, `types/`, `port/`, `errors/`, `adapters/google_cloud/`); not split by REST resource.
- **`schemas/`** — JSON Schema contracts for agents; [`command_schemas.py`](src/bq_inspect/schemas/command_schemas.py) resolves per-command schemas for `--input-schema` / `--output-schema`.

## Package layout (`src/bq_inspect/`)

- `bigquery/auth` — ADC + impersonation (`create_auth_client`)
- `bigquery/types` — transport DTOs (`DatasetRef`, `ListJobsRequest`, …)
- `bigquery/port` — `BigQueryInspectionClient` port
- `bigquery/errors` — Google API error → `BqInspectFailure` mapping
- `bigquery/adapters/google_cloud` — `SdkBigQueryClient`
- `cli/usage` — `*_USAGE` strings for `--help`
- `cli/help` — argv → usage mapping for `--help`
- `cli/argv` — operational flags (`--params`, schemas)
- `cli/params` — JSON / `@file` resolution
- `cli/input` — validate + map + parsed types
- `commands/` — CLI subcommands (`jobs/`, `datasets/`, `tables/`, plus shared `command_shared.py`, `schema.py`)
- `core/jobs` — `inspect_jobs` with job views (`summary`, `query`, `performance`, `lineage`, `impact`, `full`) and `jobs list` (+ client-side filters)
- `core/datasets` — `datasets get`
- `core/tables` — `tables list` and `tables get`
- `core/jobs/project_job` — in-process projection of `jobs.get` payloads per view
- `core/shared` — Types, errors, envelopes, IAM hints, catalog error helper
- `schemas/` — Agent contracts and schema exports

## Tests and fakes

Tests live under [`src/bq_inspect/tests/`](src/bq_inspect/tests/) (colocated with the package; excluded from the published wheel).

- **Core job inspection:** `inspect_jobs` with a job client port.
- **List jobs / catalog:** `BigQueryInspectionClient` with `SdkBigQueryClient` or fakes.
- **CLI parity in tests:** Invoke command runners with `['--params', json.dumps({...})]` (and inject `client` when avoiding ADC), or use `--input-schema` / `--output-schema` for schema-only paths.
- **Fakes:**
  - [`FixtureJobClient`](src/bq_inspect/tests/test_support/fixture_job_client.py) — in-memory job-only client for `jobs.get` and job view tests.
  - `FixtureBigQueryClient` — full port fake for list/catalog tests (same module).

Example (core):

```python
from bq_inspect.tests.test_support.fixture_job_client import FixtureJobClient

client = FixtureJobClient({"job_123": job_fixture})
result = await inspect_jobs(client, refs, view="summary")
```

Example (CLI integration): see [`src/bq_inspect/tests/cli/test_jobs_integration.py`](src/bq_inspect/tests/cli/test_jobs_integration.py).

JSON fixtures for job payloads: [`src/bq_inspect/tests/fixtures/`](src/bq_inspect/tests/fixtures/).

## Pull request checklist

- [ ] `make lint`
- [ ] `make test`
- [ ] `make build` (when packaging or entrypoints change)
- [ ] CLI or flag changes: `cli/usage_build.py` / `cli/command_registry.py` (+ README if user-visible)
- [ ] New params fields: JSON Schema + map_input + usage + README as needed

## License

Apache 2.0 — [LICENSE](LICENSE).
