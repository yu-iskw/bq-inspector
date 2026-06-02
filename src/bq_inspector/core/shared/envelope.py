"""Tool envelope builder for bq-inspector responses."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bq_inspector.core.shared.types import ToolEnvelope

_SCHEMA_VERSION = "bq-inspector.v1"


def build_tool_envelope(tool_version: str) -> ToolEnvelope:
    """Return schemaVersion and tool blocks shared by all command outputs."""
    return {
        "schemaVersion": _SCHEMA_VERSION,
        "tool": {
            "name": "bq-inspector",
            "version": tool_version,
            "readOnly": True,
        },
    }
