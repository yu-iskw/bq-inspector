"""Impersonation field helpers for request echo."""

from __future__ import annotations

from typing import TypedDict


class ImpersonationFields(TypedDict, total=False):
    impersonateServiceAccount: str
    impersonateDelegates: list[str]


def impersonation_request_fields(
    fields: ImpersonationFields,
) -> dict[str, str | list[str]]:
    """Return impersonation fields suitable for request echo."""
    output: dict[str, str | list[str]] = {}
    service_account = fields.get("impersonateServiceAccount")
    if service_account is not None:
        output["impersonateServiceAccount"] = service_account
    delegates = fields.get("impersonateDelegates")
    if delegates is not None and delegates:
        output["impersonateDelegates"] = delegates
    return output
