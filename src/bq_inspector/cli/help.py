"""Help text resolution for bq-inspector CLI (single help pipeline)."""

from __future__ import annotations

import sys

from bq_inspector.cli.command_registry import GLOBAL_USAGE, command_help_for_key
from bq_inspector.cli.flat_jobs import flat_command_suggestion, flat_help_command_key


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

    flat_key = flat_help_command_key(argv)
    key = flat_key if flat_key is not None else " ".join(argv)
    usage = command_help_for_key(key)

    if usage is not None:
        return usage

    if argv:
        suggestion = flat_command_suggestion(argv)
        suffix = f". Did you mean: {suggestion}?" if suggestion else ""
        return f"{GLOBAL_USAGE}\n\nUnknown command: {' '.join(argv)}{suffix}"

    return GLOBAL_USAGE


def write_help_text(text: str) -> None:
    """Write plain-text help to stdout."""
    sys.stdout.write(f"{text}\n")
