"""Tests for impersonation request field helpers."""

from __future__ import annotations

from bq_inspect.core.shared.impersonation_fields import (
    auth_client_options_from_impersonation,
    impersonation_request_fields,
    merge_impersonation_into,
    select_impersonation_fields,
)


def test_returns_empty_object_when_unset() -> None:
    assert not impersonation_request_fields({})


def test_includes_service_account_when_set() -> None:
    assert impersonation_request_fields(
        {"impersonateServiceAccount": "sa@p.iam.gserviceaccount.com"}
    ) == {"impersonateServiceAccount": "sa@p.iam.gserviceaccount.com"}


def test_omits_empty_delegate_list() -> None:
    assert impersonation_request_fields(
        {
            "impersonateServiceAccount": "sa@p.iam.gserviceaccount.com",
            "impersonateDelegates": [],
        }
    ) == {"impersonateServiceAccount": "sa@p.iam.gserviceaccount.com"}


def test_includes_non_empty_delegate_list() -> None:
    assert impersonation_request_fields(
        {"impersonateDelegates": ["d1@p.iam.gserviceaccount.com"]}
    ) == {"impersonateDelegates": ["d1@p.iam.gserviceaccount.com"]}


def test_auth_client_options_from_impersonation_copies_fields() -> None:
    assert auth_client_options_from_impersonation(
        {
            "impersonateServiceAccount": "sa@p.iam.gserviceaccount.com",
            "impersonateDelegates": ["d1@p.iam.gserviceaccount.com"],
        }
    ) == {
        "impersonateServiceAccount": "sa@p.iam.gserviceaccount.com",
        "impersonateDelegates": ["d1@p.iam.gserviceaccount.com"],
    }


def test_merge_impersonation_into_updates_request_in_place() -> None:
    request = {"jobs": [], "view": "summary"}
    merged = merge_impersonation_into(
        request,
        {"impersonateServiceAccount": "sa@p.iam.gserviceaccount.com"},
    )
    assert merged is request
    assert merged["impersonateServiceAccount"] == "sa@p.iam.gserviceaccount.com"


def test_select_impersonation_fields_strips_non_impersonation_keys() -> None:
    assert select_impersonation_fields(
        {
            "impersonateServiceAccount": "sa@p.iam.gserviceaccount.com",
        }
    ) == {"impersonateServiceAccount": "sa@p.iam.gserviceaccount.com"}
