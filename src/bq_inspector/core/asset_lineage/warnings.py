"""Asset-lineage response warnings."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import BqInspectWarning


def unreachable_warnings(unreachable: list[str]) -> list[BqInspectWarning]:
    """Return warnings when the lineage graph may be incomplete."""
    if len(unreachable) == 0:
        return []
    return [
        {
            "code": "LINEAGE_UNREACHABLE",
            "message": ("Some lineage locations were unreachable; the link set may be incomplete."),
        }
    ]
