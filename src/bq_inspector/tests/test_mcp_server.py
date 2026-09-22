"""Tests for the MCP stdio server adapter."""

from __future__ import annotations

import json
from typing import Any

import pytest

from bq_inspector import mcp_server
from bq_inspector.cli.command_registry import ParamsCommandSpec
from bq_inspector.commands.command_shared import ParamsCommandRunner


def test_build_tools_uses_registry_schemas() -> None:
    tools = mcp_server.build_tools()

    assert tools
    assert len(tools) == len(mcp_server.PARAMS_COMMAND_SPECS)
    assert len({tool.name for tool in tools}) == len(tools)
    assert all(tool.name.startswith("bq_inspector_") for tool in tools)
    assert all(tool.inputSchema for tool in tools)
    assert all(tool.outputSchema for tool in tools)


@pytest.mark.asyncio
async def test_call_tool_dispatches_arguments_as_params(monkeypatch: pytest.MonkeyPatch) -> None:
    received: dict[str, Any] = {}

    async def run_argv(argv: list[str], options: Any) -> dict[str, Any]:
        received["argv"] = argv
        received["tool_version"] = options.tool_version
        return {"ok": True}

    async def run_operational(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("run_operational should not be called")

    spec = ParamsCommandSpec(
        path=("jobs", "summary"),
        usage="Inspect job summary.",
        runner=ParamsCommandRunner(run_argv=run_argv, run_operational=run_operational),
    )
    monkeypatch.setattr(mcp_server, "PARAMS_COMMAND_SPECS", (spec,))
    monkeypatch.setattr(mcp_server, "_tool_version", lambda: "9.9.9")

    content = await mcp_server.call_tool(
        "bq_inspector_jobs_summary",
        {"jobs": [{"projectId": "project", "jobId": "job"}]},
    )

    assert json.loads(received["argv"][1]) == {
        "jobs": [{"projectId": "project", "jobId": "job"}]
    }
    assert received["argv"][0] == "--params"
    assert received["tool_version"] == "9.9.9"
    assert json.loads(content[0].text) == {"ok": True}


@pytest.mark.asyncio
async def test_call_tool_rejects_unknown_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mcp_server, "PARAMS_COMMAND_SPECS", ())

    with pytest.raises(ValueError, match="Unknown MCP tool"):
        await mcp_server.call_tool("missing", {})
