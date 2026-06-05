"""Lineage links command."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.commands.lineage._shared import (
    base_lineage_request,
    create_asset_lineage_params_command,
)
from bq_inspector.core.asset_lineage.search_links import search_table_links
from bq_inspector.input.input_parsers import parse_lineage_links_input

if TYPE_CHECKING:
    from bq_inspector.core.asset_lineage.requests import LineageLinksRequest
    from bq_inspector.input.parsed_input_types import ParsedLineageInput


def _build_links_request(input_data: ParsedLineageInput) -> LineageLinksRequest:
    request: LineageLinksRequest = {**base_lineage_request(input_data)}
    if "pageSize" in input_data:
        request["pageSize"] = input_data["pageSize"]
    if "pageToken" in input_data:
        request["pageToken"] = input_data["pageToken"]
    return request


lineage_links_command = create_asset_lineage_params_command(
    "lineage links",
    parse_lineage_links_input,
    _build_links_request,
    search_table_links,
)
run_lineage_links = lineage_links_command.run_argv
