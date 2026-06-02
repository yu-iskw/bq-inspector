"""Help text resolution for bq-inspector CLI (single help pipeline)."""

from __future__ import annotations

import sys

from bq_inspector.cli.command_registry import GLOBAL_USAGE, command_help_for_key
from bq_inspector.cli.usage_build import JOB_SUBCOMMAND_NAMES


def strip_trailing_help_flags(argv: list[str]) -> tuple[list[str], bool]:
    """Strip trailing --help / -h flags and return cleaned argv."""
    copy = list(argv)
    wants_help = False

    while copy and copy[-1] in ("--help", "-h"):
        wants_help = True
        copy.pop()

    return copy, wants_help


def resolve_help_text(argv: list[str], wants_help: bool) -> str:
    """Return help text when the user asked for help."""
    if not wants_help:
        raise ValueError("resolve_help_text requires wants_help=True")

    key = " ".join(argv)
    usage = command_help_for_key(key)

    if usage is None and len(argv) == 1 and argv[0] in JOB_SUBCOMMAND_NAMES:
        usage = command_help_for_key(f"jobs {argv[0]}")

    if usage is not None:
        return usage

    if argv:
        suggestion = _suggest_command(argv)
        suffix = f". Did you mean: {suggestion}?" if suggestion else ""
        return f"{GLOBAL_USAGE}\n\nUnknown command: {key}{suffix}"

    return GLOBAL_USAGE


def _suggest_command(argv: list[str]) -> str | None:
    if argv and argv[0] in JOB_SUBCOMMAND_NAMES:
        return f"jobs {argv[0]}"
    return None


def write_help_text(text: str) -> None:
    """Write plain-text help to stdout."""
    sys.stdout.write(f"{text}\n")
