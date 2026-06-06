"""Shared get/lookup orchestration for Knowledge Catalog resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from bq_inspector.core.knowledge_catalog.search_runner import run_catalog_use_case

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bq_inspector.core.shared.types import BqInspectSchemaVersion, ToolBlock
    from bq_inspector.knowledge_catalog.port.catalog_client import CatalogInspectionClient

_ParamsT = TypeVar("_ParamsT")
_RequestT = TypeVar("_RequestT")


async def fetch_catalog_resource(  # noqa: PLR0913
    params: _ParamsT,
    *,
    client: CatalogInspectionClient,
    tool_version: str,
    build_echo: Callable[[_ParamsT], dict[str, Any]],
    build_request: Callable[[_ParamsT], _RequestT],
    fetch: Callable[[CatalogInspectionClient, _RequestT], Awaitable[dict[str, object]]],
) -> dict[str, Any]:
    """Retrieve a Knowledge Catalog resource and return a stable JSON envelope."""
    request_echo = build_echo(params)
    sdk_request = build_request(params)

    async def execute(
        schema_version: BqInspectSchemaVersion,
        tool: ToolBlock,
    ) -> dict[str, Any]:
        resource = await fetch(client, sdk_request)
        return {
            "schemaVersion": schema_version,
            "tool": tool,
            "request": request_echo,
            "resource": resource,
            "warnings": [],
            "errors": [],
        }

    return await run_catalog_use_case(
        tool_version=tool_version,
        request_echo=request_echo,
        response_fields_on_error={"resource": {}},
        execute=execute,
    )
