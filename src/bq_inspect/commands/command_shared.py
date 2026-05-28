"""Shared command helpers for building BigQuery clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspect.bigquery.adapters.google_cloud.sdk_inspection_client import SdkBigQueryClient
from bq_inspect.bigquery.auth.create_auth_client import AuthClientOptions, create_auth_client

if TYPE_CHECKING:
    from bq_inspect.core.shared.impersonation_fields import ImpersonationFields


async def create_sdk_inspection_client_from_input(
    input_data: ImpersonationFields,
) -> SdkBigQueryClient:
    """Create an SDK-backed inspection client from impersonation params."""
    options: AuthClientOptions = {}
    service_account = input_data.get("impersonateServiceAccount")
    if service_account is not None:
        options["impersonateServiceAccount"] = service_account
    delegates = input_data.get("impersonateDelegates")
    if delegates is not None:
        options["impersonateDelegates"] = delegates
    auth_client = await create_auth_client(options)
    return SdkBigQueryClient(auth_client)
