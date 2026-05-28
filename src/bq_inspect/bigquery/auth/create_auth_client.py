"""Application Default Credentials and service account impersonation."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypedDict

from google.auth import default as auth_default, impersonated_credentials

from bq_inspect.core.shared.normalize import normalize_delegate_list, normalize_optional_trimmed

if TYPE_CHECKING:
    from google.auth.credentials import Credentials

READONLY_SCOPE = "https://www.googleapis.com/auth/bigquery.readonly"
CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"


class AuthClientOptions(TypedDict, total=False):
    impersonateServiceAccount: str
    impersonateDelegates: list[str] | str


async def create_auth_client(options: AuthClientOptions | None = None) -> Credentials:
    """Build credentials for read-only BigQuery access."""
    resolved = options or {}
    target_principal = normalize_optional_trimmed(resolved.get("impersonateServiceAccount"))

    if target_principal is None:
        credentials, _ = await asyncio.to_thread(auth_default, scopes=[READONLY_SCOPE])
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
            target_scopes=[READONLY_SCOPE],
            delegates=delegates,
        )

    return await asyncio.to_thread(_build_impersonated)
