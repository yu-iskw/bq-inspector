"""Shared Click definitions for operational CLI flags."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import click

if TYPE_CHECKING:
    from collections.abc import Callable

_PARAMS_SPEC: dict[str, Any] = {"type": str, "default": None}
_INPUT_SCHEMA_SPEC: dict[str, Any] = {"is_flag": True, "default": False}
_OUTPUT_SCHEMA_SPEC: dict[str, Any] = {"is_flag": True, "default": False}


def operational_flag_options() -> tuple[click.Option, ...]:
    """Return Click Option objects for operational argv parsing."""
    return (
        click.Option(["--params"], **_PARAMS_SPEC),
        click.Option(["--input-schema"], **_INPUT_SCHEMA_SPEC),
        click.Option(["--output-schema"], **_OUTPUT_SCHEMA_SPEC),
    )


def operational_flag_decorators() -> tuple[Callable[..., Any], ...]:
    """Return Click option decorators for operational flags."""
    return (
        click.option("--params", **_PARAMS_SPEC),
        click.option("--input-schema", **_INPUT_SCHEMA_SPEC),
        click.option("--output-schema", **_OUTPUT_SCHEMA_SPEC),
    )
