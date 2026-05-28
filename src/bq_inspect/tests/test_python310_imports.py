"""Smoke tests for Python 3.10-compatible imports."""

from __future__ import annotations

from bq_inspect.cli.dispatch import main
from bq_inspect.core.shared.types import InspectJobResponse


def test_core_types_imports_on_supported_python() -> None:
    assert "schemaVersion" in InspectJobResponse.__annotations__


def test_cli_entry_imports_on_supported_python() -> None:
    assert callable(main)
