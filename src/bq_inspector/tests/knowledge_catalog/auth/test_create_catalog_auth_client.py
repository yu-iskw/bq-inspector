"""Auth tests for Knowledge Catalog credentials."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from bq_inspector.knowledge_catalog.auth.create_catalog_auth_client import (
    CLOUD_PLATFORM_SCOPE,
    create_catalog_auth_client,
)


@pytest.mark.asyncio
async def test_create_catalog_auth_client_without_impersonation_uses_cloud_platform_scope() -> None:
    mock_credentials = MagicMock()
    with patch(
        "bq_inspector.knowledge_catalog.auth.create_catalog_auth_client.auth_default",
        return_value=(mock_credentials, "project"),
    ) as auth_default:
        result = await create_catalog_auth_client()

    auth_default.assert_called_once_with(scopes=[CLOUD_PLATFORM_SCOPE])
    assert result is mock_credentials


@pytest.mark.asyncio
async def test_create_catalog_auth_client_with_impersonation_builds_target_credentials() -> None:
    source_credentials = MagicMock()
    impersonated = MagicMock()

    with (
        patch(
            "bq_inspector.knowledge_catalog.auth.create_catalog_auth_client.auth_default",
            return_value=(source_credentials, "project"),
        ) as auth_default,
        patch(
            "bq_inspector.knowledge_catalog.auth.create_catalog_auth_client.impersonated_credentials.Credentials",
            return_value=impersonated,
        ) as impersonated_ctor,
    ):
        result = await create_catalog_auth_client(
            {
                "impersonateServiceAccount": " target@p.iam.gserviceaccount.com ",
                "impersonateDelegates": [" d@p.iam.gserviceaccount.com ", ""],
            }
        )

    assert result is impersonated
    auth_default.assert_called_once_with(scopes=[CLOUD_PLATFORM_SCOPE])
    impersonated_ctor.assert_called_once_with(
        source_credentials=source_credentials,
        target_principal="target@p.iam.gserviceaccount.com",
        target_scopes=[CLOUD_PLATFORM_SCOPE],
        delegates=["d@p.iam.gserviceaccount.com"],
    )
