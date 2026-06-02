"""Impersonation field helpers for request echo."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, TypedDict

if TYPE_CHECKING:
    from bq_inspect.bigquery.auth.create_auth_client import AuthClientOptions

TRequest = TypeVar("TRequest", bound=dict[str, Any])


class ImpersonationFields(TypedDict, total=False):
    impersonateServiceAccount: str
    impersonateDelegates: list[str]


def merge_impersonation_into(request: TRequest, fields: ImpersonationFields) -> TRequest:
    """Merge impersonation echo fields into a request mapping."""
    request.update(impersonation_request_fields(fields))
    return request


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


def auth_client_options_from_impersonation(fields: ImpersonationFields) -> AuthClientOptions:
    """Build auth client options from parsed impersonation params."""
    options: AuthClientOptions = {}
    service_account = fields.get("impersonateServiceAccount")
    if service_account is not None:
        options["impersonateServiceAccount"] = service_account
    delegates = fields.get("impersonateDelegates")
    if delegates is not None:
        options["impersonateDelegates"] = delegates
    return options


def select_impersonation_fields(fields: ImpersonationFields) -> ImpersonationFields:
    """Return only impersonation keys from a parsed input object."""
    selected: ImpersonationFields = {}
    service_account = fields.get("impersonateServiceAccount")
    if service_account is not None:
        selected["impersonateServiceAccount"] = service_account
    delegates = fields.get("impersonateDelegates")
    if delegates is not None and delegates:
        selected["impersonateDelegates"] = delegates
    return selected
