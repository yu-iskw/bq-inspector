"""Request echo blocks for asset-lineage responses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.core.asset_lineage.fqn import table_ref_to_fqn
from bq_inspector.core.shared.types import LineageRequestEcho

if TYPE_CHECKING:
    from bq_inspector.core.asset_lineage.requests import (
        LineageGraphRequest,
        LineageLinksRequest,
        TableLineageRequest,
    )


def build_table_lineage_request_echo(request: TableLineageRequest) -> LineageRequestEcho:
    """Echo shared table-lineage request fields in the response envelope."""
    table = request["table"]
    return LineageRequestEcho(
        clientProjectId=request["clientProjectId"],
        location=request["location"],
        projectId=table["projectId"],
        datasetId=table["datasetId"],
        tableId=table["tableId"],
        direction=request["direction"],
        fullyQualifiedName=table_ref_to_fqn(table),
    )


def build_lineage_links_request_echo(request: LineageLinksRequest) -> LineageRequestEcho:
    """Echo links request fields including optional pagination."""
    echo = build_table_lineage_request_echo(request)
    page_size = request.get("pageSize")
    if page_size is not None:
        echo["pageSize"] = page_size
    page_token = request.get("pageToken")
    if page_token is not None:
        echo["pageToken"] = page_token
    return echo


def build_lineage_graph_request_echo(request: LineageGraphRequest) -> LineageRequestEcho:
    """Echo graph request fields including depth and result limits."""
    echo = build_table_lineage_request_echo(request)
    max_depth = request.get("maxDepth")
    if max_depth is not None:
        echo["maxDepth"] = max_depth
    max_results = request.get("maxResults")
    if max_results is not None:
        echo["maxResults"] = max_results
    return echo
