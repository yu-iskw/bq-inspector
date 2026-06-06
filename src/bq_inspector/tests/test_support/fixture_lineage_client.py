"""In-memory fake for Data Lineage inspection tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bq_inspector.datalineage.types.requests import (
        SearchLineageGraphRequest,
        SearchLineageGraphResult,
        SearchLinksPage,
        SearchLinksRequest,
    )


@dataclass
class FixtureLineageInput:
    """Canned lineage responses keyed by FQN and direction."""

    links_by_fqn_direction: dict[tuple[str, str], list[dict[str, object]]] = field(
        default_factory=dict
    )
    graph_by_fqn_direction: dict[tuple[str, str], SearchLineageGraphResult] = field(
        default_factory=dict
    )
    graph_chunks_by_fqn_direction: dict[
        tuple[str, str],
        list[SearchLineageGraphResult],
    ] = field(default_factory=dict)


class FixtureLineageClient:
    """LineageInspectionClient fake backed by canned responses."""

    def __init__(self, fixture: FixtureLineageInput) -> None:
        self._fixture = fixture

    async def search_links(self, request: SearchLinksRequest) -> SearchLinksPage:
        key = (request["fqn"], request["direction"])
        links = list(self._fixture.links_by_fqn_direction.get(key, []))
        return {"links": links}

    async def search_lineage_graph(
        self,
        request: SearchLineageGraphRequest,
    ) -> SearchLineageGraphResult:
        key = (request["fqn"], request["direction"])
        chunks = self._fixture.graph_chunks_by_fqn_direction.get(key)
        if chunks is not None:
            merged_links: list[dict[str, object]] = []
            unreachable: list[str] = []
            for chunk in chunks:
                merged_links.extend(chunk["links"])
                unreachable.extend(chunk["unreachable"])
            return {"links": merged_links, "unreachable": unreachable}

        return self._fixture.graph_by_fqn_direction.get(
            key,
            {"links": [], "unreachable": []},
        )
