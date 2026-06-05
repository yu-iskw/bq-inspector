"""Run blocking Google SDK calls on a worker thread with shared error mapping."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypeVar

from bq_inspector.bigquery.errors.google_api_errors import map_google_error_to_bq_inspector_failure
from bq_inspector.core.shared.errors import BqInspectFailure

_T = TypeVar("_T")

if TYPE_CHECKING:
    from collections.abc import Callable

    from bq_inspector.core.shared.api_error_hints import ApiErrorHintContext


async def invoke_sync(
    fn: Callable[..., _T],
    *,
    api: str,
    context: ApiErrorHintContext | None = None,
) -> _T:
    """Invoke a synchronous SDK callable without blocking the event loop."""
    try:
        return await asyncio.to_thread(fn)
    except BqInspectFailure:
        raise
    except Exception as error:
        raise map_google_error_to_bq_inspector_failure(error, api, context) from error
