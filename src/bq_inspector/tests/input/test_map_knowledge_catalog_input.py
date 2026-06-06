"""Input mapping tests for Knowledge Catalog commands."""

from __future__ import annotations

import pytest

from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.input.input_parsers import parse_catalog_search_input
from bq_inspector.knowledge_catalog.defaults import (
    CATALOG_SEARCH_LOCATION,
    DEFAULT_CATALOG_SEARCH_PAGE_SIZE,
)


def test_parse_catalog_search_defaults() -> None:
    parsed = parse_catalog_search_input(
        {
            "projectId": " agent-tools-prod ",
            "query": "customer orders",
        }
    )

    assert parsed["projectId"] == "agent-tools-prod"
    assert parsed["query"] == "customer orders"
    assert parsed["location"] == CATALOG_SEARCH_LOCATION
    assert parsed["semanticSearch"] is False
    assert parsed["pageSize"] == DEFAULT_CATALOG_SEARCH_PAGE_SIZE


def test_parse_catalog_search_rejects_unknown_fields() -> None:
    with pytest.raises(BqInspectFailure):
        parse_catalog_search_input(
            {
                "projectId": "p",
                "query": "q",
                "unknownField": True,
            }
        )
