"""Search multi-hop lineage graphs for a table."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.core.asset_lineage.fqn import lineage_parent, table_ref_to_fqn
from bq_inspector.core.asset_lineage.request_echo import build_lineage_graph_request_echo
from bq_inspector.core.asset_lineage.search_runner import run_asset_lineage_search
from bq_inspector.core.asset_lineage.warnings import unreachable_warnings
from bq_inspector.core.shared.types import (
    BqInspectSchemaVersion,
    LineageGraphResponse,
    ToolBlock,
)

if TYPE_CHECKING:
    from bq_inspector.core.asset_lineage.requests import LineageGraphRequest
    from bq_inspector.datalineage.port.lineage_client import LineageInspectionClient
    from bq_inspector.datalineage.types.requests import SearchLineageGraphRequest


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
) -> LineageGraphResponse:
    """Return a multi-hop lineage graph for a BigQuery table."""
    request_echo = build_lineage_graph_request_echo(request)
    fqn = table_ref_to_fqn(request["table"])
    sdk_request = _build_search_lineage_graph_request(request, fqn=fqn)

    async def search(
        schema_version: BqInspectSchemaVersion,
        tool: ToolBlock,
    ) -> LineageGraphResponse:
        result = await client.search_lineage_graph(sdk_request)
        unreachable = result["unreachable"]
        return LineageGraphResponse(
            schemaVersion=schema_version,
            tool=tool,
            request=request_echo,
            links=result["links"],
            unreachable=unreachable,
            warnings=unreachable_warnings(unreachable),
            errors=[],
        )

    return await run_asset_lineage_search(
        tool_version=tool_version,
        request_echo=request_echo,
        response_kind="graph",
        search=search,
    )
