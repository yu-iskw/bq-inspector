"""Auth tests for Knowledge Catalog credentials."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from bq_inspector.knowledge_catalog.auth.create_catalog_auth_client import (
    DATAPLEX_READONLY_SCOPE,
    create_catalog_auth_client,
)


@pytest.mark.asyncio
async def test_create_catalog_auth_client_uses_readonly_scope() -> None:
    mock_credentials = MagicMock()
    with patch(
        "bq_inspector.knowledge_catalog.auth.create_catalog_auth_client.auth_default",
        return_value=(mock_credentials, "project"),
    ) as auth_default:
        result = await create_catalog_auth_client()

    auth_default.assert_called_once_with(scopes=[DATAPLEX_READONLY_SCOPE])
    assert result is mock_credentials
