# Changelog

## Unreleased

### Removed

- **`bq-inspector schema` subcommand** — use per-command `--input-schema` and `--output-schema`.

### Added

- Flat job subcommands (`bq-inspector summary` equivalent to `jobs summary`).
- Composite job IDs in `jobId` (`project:location.jobId`).
- Full REST payloads from SDK `_properties` for jobs, datasets, and tables.

### Fixed

- Job views and `jobs list` now include `status` and `statistics` where the API provides them.
