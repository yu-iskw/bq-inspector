"""Data Lineage inspection client protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from bq_inspector.datalineage.types.requests import (
        SearchLineageGraphRequest,
        SearchLineageGraphResult,
        SearchLinksPage,
        SearchLinksRequest,
    )


class LineageInspectionClient(Protocol):
    """Port for read-only Data Lineage graph inspection."""

    async def search_links(self, request: SearchLinksRequest) -> SearchLinksPage:
        """Fetch immediate upstream or downstream links for an asset."""
        raise NotImplementedError

    async def search_lineage_graph(
        self,
        request: SearchLineageGraphRequest,
    ) -> SearchLineageGraphResult:
        """Fetch a multi-hop lineage graph for an asset."""
        raise NotImplementedError
