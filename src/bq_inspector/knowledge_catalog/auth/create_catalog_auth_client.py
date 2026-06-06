"""Application Default Credentials for read-only Knowledge Catalog access."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypedDict

from google.auth import default as auth_default, impersonated_credentials

from bq_inspector.core.shared.normalize import normalize_delegate_list, normalize_optional_trimmed

if TYPE_CHECKING:
    from google.auth.credentials import Credentials

DATAPLEX_READONLY_SCOPE = "https://www.googleapis.com/auth/dataplex.readonly"


class CatalogAuthClientOptions(TypedDict, total=False):
    impersonateServiceAccount: str
    impersonateDelegates: list[str] | str


async def create_catalog_auth_client(
    options: CatalogAuthClientOptions | None = None,
) -> Credentials:
    """Build credentials for Knowledge Catalog (Dataplex) API access."""
    resolved = options or {}
    target_principal = normalize_optional_trimmed(resolved.get("impersonateServiceAccount"))

    if target_principal is None:
        credentials, _ = await asyncio.to_thread(
            auth_default,
            scopes=[DATAPLEX_READONLY_SCOPE],
        )
        return credentials

    source_credentials, _ = await asyncio.to_thread(
        auth_default,
        scopes=[DATAPLEX_READONLY_SCOPE],
    )
    delegates = normalize_delegate_list(resolved.get("impersonateDelegates"))

    def _build_impersonated() -> Credentials:
        return impersonated_credentials.Credentials(
            source_credentials=source_credentials,
            target_principal=target_principal,
            target_scopes=[DATAPLEX_READONLY_SCOPE],
            delegates=delegates,
        )

    return await asyncio.to_thread(_build_impersonated)
