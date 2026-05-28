"""Tool envelope builder for bq-inspect responses."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bq_inspect.core.shared.types import ToolEnvelope

_SCHEMA_VERSION = "bq-inspect.v1"


def build_tool_envelope(tool_version: str) -> ToolEnvelope:
    """Return schemaVersion and tool blocks shared by all command outputs."""
    return {
        "schemaVersion": _SCHEMA_VERSION,
        "tool": {
            "name": "bq-inspect",
            "version": tool_version,
            "readOnly": True,
        },
    }
