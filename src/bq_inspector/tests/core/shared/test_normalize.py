"""Tests for normalize helpers."""

from __future__ import annotations

from bq_inspector.core.shared.normalize import normalize_delegate_list, normalize_optional_trimmed


def test_normalize_optional_trimmed_returns_none_for_blank() -> None:
    assert normalize_optional_trimmed(None) is None
    assert normalize_optional_trimmed("") is None
    assert normalize_optional_trimmed("   ") is None


def test_normalize_optional_trimmed_trims_non_empty_strings() -> None:
    assert normalize_optional_trimmed("  sa@proj.iam.gserviceaccount.com  ") == (
        "sa@proj.iam.gserviceaccount.com"
    )


def test_normalize_delegate_list_returns_empty_for_none() -> None:
    assert normalize_delegate_list(None) == []


def test_normalize_delegate_list_normalizes_single_string() -> None:
    assert normalize_delegate_list("  a@x.iam.gserviceaccount.com  ") == [
        "a@x.iam.gserviceaccount.com"
    ]


def test_normalize_delegate_list_preserves_order() -> None:
    assert normalize_delegate_list(
        [
            "  first@x.iam.gserviceaccount.com ",
            " second@x.iam.gserviceaccount.com",
        ]
    ) == ["first@x.iam.gserviceaccount.com", "second@x.iam.gserviceaccount.com"]


def test_normalize_delegate_list_drops_empty_entries() -> None:
    assert normalize_delegate_list(["valid@x.iam.gserviceaccount.com", "   ", ""]) == [
        "valid@x.iam.gserviceaccount.com"
    ]
