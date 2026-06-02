"""Map Click CLI exceptions to bq-inspector input failures."""

from __future__ import annotations

import click  # noqa: TC002

from bq_inspector.core.shared.errors import BqInspectFailure, create_input_failure


def normalize_click_exception_message(error: click.ClickException) -> str:
    """Map Click CLI errors to stable bq-inspector input messages."""
    message = error.format_message()
    if "requires an argument" in message and "--params" in message:
        return "expected one argument"
    if message.startswith("No such command "):
        command_name = message.removeprefix("No such command ").strip(".'\"")
        return f"Unknown command: {command_name}"
    return message


def click_exception_to_failure(error: click.ClickException) -> BqInspectFailure:
    """Convert a Click exception into a structured input failure."""
    return create_input_failure(normalize_click_exception_message(error))
