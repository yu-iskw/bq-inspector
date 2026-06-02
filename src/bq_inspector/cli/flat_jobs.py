"""Flat job subcommand argv and help policy."""

from __future__ import annotations

from bq_inspector.cli.jobs_subcommands import JOB_SUBCOMMAND_NAMES


def is_flat_job_command(name: str) -> bool:
    return name in JOB_SUBCOMMAND_NAMES


def normalize_flat_job_argv(argv: list[str]) -> list[str]:
    """Allow `bq-inspector summary` as shorthand for `bq-inspector jobs summary`."""
    if argv and is_flat_job_command(argv[0]):
        return ["jobs", *argv]
    return argv


def flat_help_command_key(argv: list[str]) -> str | None:
    """Map ['summary'] to 'jobs summary' for help lookup."""
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
