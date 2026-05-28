"""Shared command helpers for building BigQuery clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bq_inspect.bigquery.adapters.google_cloud.sdk_inspection_client import SdkBigQueryClient
from bq_inspect.bigquery.auth.create_auth_client import create_auth_client

if TYPE_CHECKING:
    from bq_inspect.core.shared.impersonation_fields import ImpersonationFields


async def create_sdk_inspection_client_from_input(
    input_data: ImpersonationFields,
) -> SdkBigQueryClient:
    """Create an SDK-backed inspection client from impersonation params."""
    auth_client = await create_auth_client(
        {
            "impersonateServiceAccount": input_data.get("impersonateServiceAccount"),
            "impersonateDelegates": input_data.get("impersonateDelegates"),
        }
    )
    return SdkBigQueryClient(auth_client)
