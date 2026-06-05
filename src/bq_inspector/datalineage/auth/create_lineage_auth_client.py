"""Application Default Credentials for read-only Data Lineage access."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypedDict

from google.auth import default as auth_default, impersonated_credentials

from bq_inspector.core.shared.normalize import normalize_delegate_list, normalize_optional_trimmed

if TYPE_CHECKING:
    from google.auth.credentials import Credentials

DATALINEAGE_READONLY_SCOPE = "https://www.googleapis.com/auth/datalineage.readonly"
CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"


class LineageAuthClientOptions(TypedDict, total=False):
    impersonateServiceAccount: str
    impersonateDelegates: list[str] | str


async def create_lineage_auth_client(
    options: LineageAuthClientOptions | None = None,
) -> Credentials:
    """Build credentials scoped for read-only Data Lineage API access."""
    resolved = options or {}
    target_principal = normalize_optional_trimmed(resolved.get("impersonateServiceAccount"))

    if target_principal is None:
        credentials, _ = await asyncio.to_thread(
            auth_default,
            scopes=[DATALINEAGE_READONLY_SCOPE],
        )
        return credentials

    source_credentials, _ = await asyncio.to_thread(
        auth_default,
        scopes=[CLOUD_PLATFORM_SCOPE],
    )
    delegates = normalize_delegate_list(resolved.get("impersonateDelegates"))

    def _build_impersonated() -> Credentials:
        return impersonated_credentials.Credentials(
            source_credentials=source_credentials,
            target_principal=target_principal,
            target_scopes=[DATALINEAGE_READONLY_SCOPE],
            delegates=delegates,
        )

    return await asyncio.to_thread(_build_impersonated)
