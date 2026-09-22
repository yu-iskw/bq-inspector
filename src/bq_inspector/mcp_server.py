"""Model Context Protocol server for bq-inspector.

The server intentionally uses stdio as the default transport so that local coding
agents can launch it without opening a network listener. Every CLI command is
exposed as a read-only MCP tool generated from the canonical command registry.
"""

from __future__ import annotations

import asyncio
import json
import re
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from bq_inspector.cli.command_registry import PARAMS_COMMAND_SPECS, ParamsCommandSpec
from bq_inspector.commands.command_shared import InspectionCommandOptions
from bq_inspector.schemas.command_schemas import CommandId, get_command_schema

_SERVER_NAME = "bq-inspector"
_TOOL_PREFIX = "bq_inspector"


def _tool_version() -> str:
    try:
        return version("bq-inspector")
    except PackageNotFoundError:
        return "0.0.0"


def tool_name(path: tuple[str, ...]) -> str:
    """Return a spec-compliant MCP tool name for a command path."""
    normalized = "_".join(path)
    normalized = re.sub(r"[^A-Za-z0-9_.-]", "_", normalized)
    return f"{_TOOL_PREFIX}_{normalized}"


def _description(spec: ParamsCommandSpec) -> str:
    first_line = next(
        (line.strip() for line in spec.usage.splitlines() if line.strip()),
        "Run a read-only bq-inspector command.",
    )
    return f"{first_line} Command: {' '.join(spec.path)}."


def _command_id(spec: ParamsCommandSpec) -> CommandId:
    return " ".join(spec.path)  # type: ignore[return-value]


def build_tools() -> list[Tool]:
    """Build MCP tools from the same registry and schemas used by the CLI."""
    return [
        Tool(
            name=tool_name(spec.path),
            description=_description(spec),
            inputSchema=get_command_schema(_command_id(spec), "input"),
            outputSchema=get_command_schema(_command_id(spec), "output"),
        )
        for spec in PARAMS_COMMAND_SPECS
    ]


def _spec_by_tool_name() -> dict[str, ParamsCommandSpec]:
    return {tool_name(spec.path): spec for spec in PARAMS_COMMAND_SPECS}


server = Server(_SERVER_NAME)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Advertise all registered read-only inspection tools."""
    return build_tools()


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute one registered command using its canonical parser and runner."""
    spec = _spec_by_tool_name().get(name)
    if spec is None:
        raise ValueError(f"Unknown MCP tool: {name}")

    options = InspectionCommandOptions(tool_version=_tool_version())
    result = await spec.runner.run_argv(
        ["--params", json.dumps(arguments, separators=(",", ":"))],
        options,
    )
    return [TextContent(type="text", text=json.dumps(result, separators=(",", ":")))]


async def run() -> None:
    """Run the MCP server using the standard stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Console-script entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
