"""Search immediate upstream or downstream lineage links for a table."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from bq_inspector.core.asset_lineage.error_envelope import lineage_error_envelope
from bq_inspector.core.asset_lineage.fqn import lineage_parent, table_ref_to_fqn
from bq_inspector.core.asset_lineage.request_echo import build_lineage_links_request_echo
from bq_inspector.core.shared.envelope import build_tool_envelope
from bq_inspector.core.shared.errors import BqInspectFailure
from bq_inspector.core.shared.types import LineageLinksPageBlock, LineageLinksResponse

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
    envelope = build_tool_envelope(tool_version)
    schema_version = envelope["schemaVersion"]
    tool = envelope["tool"]
    request_echo = build_lineage_links_request_echo(request)
    fqn = table_ref_to_fqn(request["table"])

    try:
        page = await client.search_links(_build_search_links_request(request, fqn=fqn))
        page_block: LineageLinksPageBlock = {}
        next_page_token = page.get("nextPageToken")
        if isinstance(next_page_token, str) and len(next_page_token) > 0:
            page_block["nextPageToken"] = next_page_token

        return LineageLinksResponse(
            schemaVersion=schema_version,
            tool=tool,
            request=request_echo,
            links=cast("list[object]", page["links"]),
            page=page_block,
            warnings=[],
            errors=[],
        )
    except BqInspectFailure as error:
        return lineage_error_envelope(
            schema_version,
            tool,
            request_echo,
            error,
            response_kind="links",
        )
