"""Search immediate upstream or downstream lineage links for a table."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspector.core.asset_lineage.fqn import lineage_parent, table_ref_to_fqn
from bq_inspector.core.asset_lineage.request_echo import build_lineage_links_request_echo
from bq_inspector.core.asset_lineage.search_runner import run_asset_lineage_search
from bq_inspector.core.shared.types import (
    BqInspectSchemaVersion,
    LineageLinksPageBlock,
    LineageLinksResponse,
    ToolBlock,
)

if TYPE_CHECKING:
    from bq_inspector.core.asset_lineage.requests import LineageLinksRequest
    from bq_inspector.datalineage.port.lineage_client import LineageInspectionClient
    from bq_inspector.datalineage.types.requests import SearchLinksRequest


def _build_search_links_request(
    request: LineageLinksRequest,
    *,
    fqn: str,
) -> SearchLinksRequest:
    sdk_request: SearchLinksRequest = {
        "parent": lineage_parent(request["clientProjectId"], request["location"]),
        "fqn": fqn,
        "direction": request["direction"],
    }
    page_size = request.get("pageSize")
    if page_size is not None:
        sdk_request["pageSize"] = page_size
    page_token = request.get("pageToken")
    if page_token is not None:
        sdk_request["pageToken"] = page_token
    return sdk_request


async def search_table_links(
    request: LineageLinksRequest,
    *,
    client: LineageInspectionClient,
    tool_version: str,
) -> LineageLinksResponse:
    """Return immediate lineage links for a BigQuery table."""
    request_echo = build_lineage_links_request_echo(request)
    fqn = table_ref_to_fqn(request["table"])
    sdk_request = _build_search_links_request(request, fqn=fqn)

    async def search(
        schema_version: BqInspectSchemaVersion,
        tool: ToolBlock,
    ) -> LineageLinksResponse:
        page = await client.search_links(sdk_request)
        page_block: LineageLinksPageBlock = {}
        next_page_token = page.get("nextPageToken")
        if isinstance(next_page_token, str) and len(next_page_token) > 0:
            page_block["nextPageToken"] = next_page_token

        return LineageLinksResponse(
            schemaVersion=schema_version,
            tool=tool,
            request=request_echo,
            links=page["links"],
            page=page_block,
            warnings=[],
            errors=[],
        )

    return await run_asset_lineage_search(
        tool_version=tool_version,
        request_echo=request_echo,
        response_kind="links",
        search=search,
    )
