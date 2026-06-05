"""Tests for lineage input mapping."""

from __future__ import annotations

import pytest

from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.datalineage.defaults import (
    DEFAULT_LINEAGE_GRAPH_MAX_DEPTH,
    DEFAULT_LINEAGE_GRAPH_MAX_RESULTS,
)
from bq_inspector.input.map_input import map_lineage_graph_input, map_lineage_input


def test_map_lineage_graph_input_applies_defaults() -> None:
    parsed = map_lineage_graph_input(
        {
            "projectId": "p",
            "location": "us",
            "datasetId": "d",
            "tableId": "t",
            "direction": "UPSTREAM",
        }
    )
    assert parsed["maxDepth"] == DEFAULT_LINEAGE_GRAPH_MAX_DEPTH
    assert parsed["maxResults"] == DEFAULT_LINEAGE_GRAPH_MAX_RESULTS


def test_map_lineage_input_rejects_invalid_direction() -> None:
    with pytest.raises(BqInspectFailure) as exc_info:
        map_lineage_input(
            {
                "projectId": "p",
                "location": "us",
                "datasetId": "d",
                "tableId": "t",
                "direction": "SIDEWAYS",
            }
        )
    assert exc_info.value.details["code"] == "BQINSPECTOR_INPUT_INVALID"
