"""Knowledge Catalog response warnings."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import BqInspectWarning


def unreachable_search_warnings(unreachable: list[str]) -> list[BqInspectWarning]:
    """Return warnings when catalog search returned partial results."""
    if len(unreachable) == 0:
        return []
    return [
        {
            "code": "BQINSPECTOR_PARTIAL_RESULTS",
            "message": (
                "Knowledge Catalog search returned partial results because one or more "
                "locations were unreachable."
            ),
        }
    ]
