"""Flat argv normalization and help policy for job subcommand shorthands."""

from __future__ import annotations

from bq_inspector.cli.command_registry import GROUP_COMMAND_SPECS, PARAMS_COMMAND_SPECS
from bq_inspector.cli.jobs_subcommands import JOB_SUBCOMMAND_NAMES

_MIN_GROUP_ARGV_LEN = 2

_REGISTERED_GROUP_PATHS: frozenset[tuple[str, ...]] = frozenset(
    spec.path[:_MIN_GROUP_ARGV_LEN]
    for spec in PARAMS_COMMAND_SPECS
    if len(spec.path) >= _MIN_GROUP_ARGV_LEN
)
_TOP_LEVEL_GROUP_NAMES: frozenset[str] = frozenset(group.name for group in GROUP_COMMAND_SPECS)


def is_flat_job_command(name: str) -> bool:
    return name in JOB_SUBCOMMAND_NAMES


def is_registered_group_argv(argv: list[str]) -> bool:
    """Return True when argv begins with a registered top-level group subcommand."""
    if len(argv) < _MIN_GROUP_ARGV_LEN:
        return False
    return tuple(argv[:_MIN_GROUP_ARGV_LEN]) in _REGISTERED_GROUP_PATHS


def is_top_level_group_name(name: str) -> bool:
    return name in _TOP_LEVEL_GROUP_NAMES


def normalize_flat_job_argv(argv: list[str]) -> list[str]:
    """Allow `bq-inspector summary` as shorthand for `bq-inspector jobs summary`."""
    if not argv or not is_flat_job_command(argv[0]):
        return argv
    if is_registered_group_argv(argv):
        return argv
    return ["jobs", *argv]


def flat_help_command_key(argv: list[str]) -> str | None:
    """Map ['summary'] to 'jobs summary' for help lookup."""
    if len(argv) != 1 or not is_flat_job_command(argv[0]):
        return None
    if is_top_level_group_name(argv[0]):
        return None
    return f"jobs {argv[0]}"


def flat_command_suggestion(argv: list[str]) -> str | None:
    if argv and is_flat_job_command(argv[0]):
        name = argv[0]
        return f"{name} (or jobs {name})"
    return None


def flat_unknown_command_hint(cmd_name: str) -> str | None:
    if is_flat_job_command(cmd_name):
        return f"{cmd_name} (or jobs {cmd_name})"
    return None
