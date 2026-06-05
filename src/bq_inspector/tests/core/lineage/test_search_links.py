"""Tests for lineage search use cases."""

from __future__ import annotations

import pytest

from bq_inspector.core.lineage.search_graph import search_table_lineage_graph
from bq_inspector.core.lineage.search_links import search_table_links
from bq_inspector.tests.test_support.fixture_lineage_client import (
    FixtureLineageClient,
    FixtureLineageInput,
)

_TABLE = {
    "projectId": "data-proj",
    "datasetId": "analytics",
    "tableId": "events",
}
_FQN = "bigquery:data-proj.analytics.events"


@pytest.mark.asyncio
async def test_search_table_links_upstream() -> None:
    client = FixtureLineageClient(
        FixtureLineageInput(
            links_by_fqn_direction={
                (_FQN, "UPSTREAM"): [
                    {
                        "source": {"fullyQualifiedName": "bigquery:data-proj.raw.events"},
                        "target": {"fullyQualifiedName": _FQN},
                    }
                ]
            }
        )
    )

    response = await search_table_links(
        {
            "clientProjectId": "billing-proj",
            "location": "us",
            "table": _TABLE,
            "direction": "UPSTREAM",
        },
        client=client,
        tool_version="0.1.0",
    )

    assert response["schemaVersion"] == "bq-inspector.v1"
    assert response["request"]["fullyQualifiedName"] == _FQN
    assert len(response["links"]) == 1
    assert response["errors"] == []


@pytest.mark.asyncio
async def test_search_table_lineage_graph_merges_stream_chunks() -> None:
    client = FixtureLineageClient(
        FixtureLineageInput(
            graph_chunks_by_fqn_direction={
                (_FQN, "DOWNSTREAM"): [
                    {
                        "links": [
                            {
                                "source": {"fullyQualifiedName": _FQN},
                                "target": {"fullyQualifiedName": "bigquery:data-proj.marts.events"},
                                "depth": 1,
                            }
                        ],
                        "unreachable": ["projects/123/locations/us-east1"],
                    },
                    {
                        "links": [
                            {
                                "source": {"fullyQualifiedName": "bigquery:data-proj.marts.events"},
                                "target": {"fullyQualifiedName": "bigquery:data-proj.marts.report"},
                                "depth": 2,
                            }
                        ],
                        "unreachable": [],
                    },
                ]
            }
        )
    )

    response = await search_table_lineage_graph(
        {
            "clientProjectId": "billing-proj",
            "location": "us",
            "table": _TABLE,
            "direction": "DOWNSTREAM",
            "maxDepth": 5,
        },
        client=client,
        tool_version="0.1.0",
    )

    assert len(response["links"]) == 2
    assert response["unreachable"] == ["projects/123/locations/us-east1"]
    assert len(response["warnings"]) == 1
    assert response["warnings"][0]["code"] == "LINEAGE_UNREACHABLE"
    assert response["errors"] == []
