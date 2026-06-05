"""Flat job subcommand argv and help policy."""

from __future__ import annotations

from bq_inspector.cli.jobs_subcommands import JOB_SUBCOMMAND_NAMES

_LINEAGE_GROUP_SUBCOMMANDS = frozenset({"links", "graph"})
_MIN_LINEAGE_GROUP_ARGV_LEN = 2


def is_flat_job_command(name: str) -> bool:
    return name in JOB_SUBCOMMAND_NAMES


def _is_lineage_group_argv(argv: list[str]) -> bool:
    return (
        len(argv) >= _MIN_LINEAGE_GROUP_ARGV_LEN
        and argv[0] == "lineage"
        and argv[1] in _LINEAGE_GROUP_SUBCOMMANDS
    )


def normalize_flat_job_argv(argv: list[str]) -> list[str]:
    """Allow `bq-inspector summary` as shorthand for `bq-inspector jobs summary`."""
    if _is_lineage_group_argv(argv):
        return argv
    if argv and is_flat_job_command(argv[0]):
        return ["jobs", *argv]
    return argv


def flat_help_command_key(argv: list[str]) -> str | None:
    """Map ['summary'] to 'jobs summary' for help lookup."""
    if _is_lineage_group_argv(argv):
        return None
    if len(argv) == 1 and argv[0] == "lineage":
        return None
    if len(argv) == 1 and is_flat_job_command(argv[0]):
        return f"jobs {argv[0]}"
    return None


def flat_command_suggestion(argv: list[str]) -> str | None:
    if argv and is_flat_job_command(argv[0]):
        name = argv[0]
        return f"{name} (or jobs {name})"
    return None


def flat_unknown_command_hint(cmd_name: str) -> str | None:
    if is_flat_job_command(cmd_name):
        return f"{cmd_name} (or jobs {cmd_name})"
    return None
