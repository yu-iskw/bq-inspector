"""Lineage graph command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.commands.lineage._shared import (
    base_lineage_request,
    create_asset_lineage_params_command,
)
from bq_inspector.core.asset_lineage.search_graph import search_table_lineage_graph
from bq_inspector.input.input_parsers import parse_lineage_graph_input

if TYPE_CHECKING:
    from bq_inspector.core.asset_lineage.requests import LineageGraphRequest
    from bq_inspector.input.parsed_input_types import ParsedLineageGraphInput


def _build_graph_request(input_data: ParsedLineageGraphInput) -> LineageGraphRequest:
    request: LineageGraphRequest = {**base_lineage_request(input_data)}
    if "maxDepth" in input_data:
        request["maxDepth"] = input_data["maxDepth"]
    if "maxResults" in input_data:
        request["maxResults"] = input_data["maxResults"]
    return request


lineage_graph_command = create_asset_lineage_params_command(
    "lineage graph",
    parse_lineage_graph_input,
    _build_graph_request,
    search_table_lineage_graph,
)
run_lineage_graph = lineage_graph_command.run_argv
