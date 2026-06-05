"""Search multi-hop lineage graphs for a table."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

from bq_inspector.core.lineage.fqn import lineage_parent, table_ref_to_fqn
from bq_inspector.core.lineage.lineage_error_envelope import (
    lineage_error_envelope,
    unreachable_warnings,
)
from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure

if TYPE_CHECKING:
    from bq_inspector.bigquery.types.refs import TableRef
    from bq_inspector.datalineage.port.lineage_client import LineageInspectionClient
    from bq_inspector.datalineage.types.requests import (
        LineageDirection,
        SearchLineageGraphRequest,
    )


class LineageGraphRequest(TypedDict):
    clientProjectId: str
    location: str
    table: TableRef
    direction: LineageDirection
    maxDepth: NotRequired[int]
    maxResults: NotRequired[int]


def build_lineage_graph_request_echo(request: LineageGraphRequest) -> dict[str, object]:
    """Echo request fields in the response envelope."""
    table = request["table"]
    echo: dict[str, object] = {
        "clientProjectId": request["clientProjectId"],
        "location": request["location"],
        "projectId": table["projectId"],
        "datasetId": table["datasetId"],
        "tableId": table["tableId"],
        "direction": request["direction"],
        "fullyQualifiedName": table_ref_to_fqn(table),
    }
    if "maxDepth" in request and request["maxDepth"] is not None:
        echo["maxDepth"] = request["maxDepth"]
    if "maxResults" in request and request["maxResults"] is not None:
        echo["maxResults"] = request["maxResults"]
    return echo


def _build_search_lineage_graph_request(
    request: LineageGraphRequest,
    *,
    fqn: str,
) -> SearchLineageGraphRequest:
    sdk_request: SearchLineageGraphRequest = {
        "parent": lineage_parent(request["clientProjectId"], request["location"]),
        "location": request["location"],
        "fqn": fqn,
        "direction": request["direction"],
    }
    max_depth = request.get("maxDepth")
    if max_depth is not None:
        sdk_request["maxDepth"] = max_depth
    max_results = request.get("maxResults")
    if max_results is not None:
        sdk_request["maxResults"] = max_results
    return sdk_request


async def search_table_lineage_graph(
    request: LineageGraphRequest,
    *,
    client: LineageInspectionClient,
    tool_version: str,
) -> dict[str, object]:
    """Return a multi-hop lineage graph for a BigQuery table."""
    envelope = build_tool_envelope(tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]
    request_echo = build_lineage_graph_request_echo(request)
    fqn = table_ref_to_fqn(request["table"])

    try:
        result = await client.search_lineage_graph(
            _build_search_lineage_graph_request(request, fqn=fqn)
        )
        unreachable = result["unreachable"]
        return {
            "schemaVersion": schema_version,
            "tool": tool,
            "request": request_echo,
            "links": result["links"],
            "unreachable": unreachable,
            "warnings": unreachable_warnings(unreachable),
            "errors": [],
        }
    except BqInspectFailure as error:
        return lineage_error_envelope(
            schema_version,
            tool,
            request_echo,
            error,
            response_kind="graph",
        )
