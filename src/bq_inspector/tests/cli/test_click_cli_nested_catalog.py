"""Tests for nested catalog subgroup routing in the Click CLI."""

from __future__ import annotations

import json
import sys
from io import StringIO

import pytest  # noqa: TC002

from bq_inspector.cli.click_cli import invoke
from bq_inspector.tests.test_support.fixture_catalog_client import (
    FixtureCatalogClient,
    FixtureCatalogInput,
)


def test_invoke_catalog_entries_get_nested_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Depth-3 catalog paths route through subgroup groups (catalog -> entries -> get)."""
    client = FixtureCatalogClient(
        FixtureCatalogInput(
            get_by_name={
                "projects/p/locations/us/entryGroups/g/entries/e": {"name": "projects/p/..."}
            }
        )
    )

    async def fake_create_catalog_client(input_data: object) -> FixtureCatalogClient:
        del input_data
        return client

    monkeypatch.setattr(
        "bq_inspector.commands.catalog._shared.create_sdk_catalog_client_from_input",
        fake_create_catalog_client,
    )
    stdout = StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)

    invoke(
        [
            "catalog",
            "entries",
            "get",
            "--params",
            json.dumps({"name": "projects/p/locations/us/entryGroups/g/entries/e"}),
        ],
    )

    payload = json.loads(stdout.getvalue())
    assert payload["schemaVersion"] == "bq-inspector.v1"
    assert payload["resource"]["name"] == "projects/p/..."
