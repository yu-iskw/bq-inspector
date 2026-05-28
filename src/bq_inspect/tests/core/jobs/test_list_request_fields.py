"""Tests for jobs.list request field mapping helpers."""

from datetime import datetime, timezone

from bq_inspect.core.jobs.list_request_fields import (
    apply_list_request_optionals_to_mapping,
    build_list_jobs_response_echo,
    list_request_from_validated_params,
    list_request_to_sdk_kwargs,
    parse_iso_timestamp_to_millis,
)


def test_parse_iso_timestamp_to_millis_treats_naive_values_as_utc() -> None:
    naive = "2026-05-17T00:00:00"
    with_offset = "2026-05-17T00:00:00+00:00"
    with_z = "2026-05-17T00:00:00Z"

    assert parse_iso_timestamp_to_millis(naive) == parse_iso_timestamp_to_millis(with_offset)
    assert parse_iso_timestamp_to_millis(naive) == parse_iso_timestamp_to_millis(with_z)
    assert parse_iso_timestamp_to_millis(naive) == int(
        datetime(2026, 5, 17, tzinfo=timezone.utc).timestamp() * 1000
    )


def test_list_request_from_validated_params_maps_api_fields() -> None:
    request = list_request_from_validated_params(
        {
            "projectId": " p ",
            "allUsers": True,
            "minCreationTime": "2026-05-17T00:00:00.000Z",
            "maxCreationTime": "2026-05-18T00:00:00.000Z",
            "pageToken": " tok ",
            "maxResults": 25,
            "state": " DONE ",
            "parentJobId": " parent ",
        }
    )

    assert request == {
        "projectId": "p",
        "allUsers": True,
        "minCreationTime": parse_iso_timestamp_to_millis("2026-05-17T00:00:00.000Z"),
        "maxCreationTime": parse_iso_timestamp_to_millis("2026-05-18T00:00:00.000Z"),
        "pageToken": "tok",
        "maxResults": 25,
        "state": "DONE",
        "parentJobId": "parent",
    }


def test_list_request_to_sdk_kwargs_maps_snake_case_fields() -> None:
    millis = parse_iso_timestamp_to_millis("2026-05-17T00:00:00.000Z")
    kwargs = list_request_to_sdk_kwargs(
        {
            "projectId": "p",
            "allUsers": True,
            "minCreationTime": millis,
            "maxCreationTime": millis + 1,
            "pageToken": "tok",
            "maxResults": 10,
            "state": "DONE",
            "parentJobId": "parent",
        }
    )

    assert kwargs["project"] == "p"
    assert kwargs["all_users"] is True
    assert kwargs["page_token"] == "tok"
    assert kwargs["max_results"] == 10
    assert kwargs["state_filter"] == "done"
    assert kwargs["parent_job"] == "parent"
    assert kwargs["min_creation_time"].tzinfo == timezone.utc
    assert kwargs["max_creation_time"].tzinfo == timezone.utc


def test_apply_list_request_optionals_to_mapping_skips_empty_strings() -> None:
    target: dict[str, object] = {}
    apply_list_request_optionals_to_mapping(
        target,
        {
            "projectId": "p",
            "pageToken": "",
            "state": "",
        },
    )

    assert not target


def test_build_list_jobs_response_echo_includes_filters_and_impersonation() -> None:
    echo = build_list_jobs_response_echo(
        {
            "projectId": "p",
            "allUsers": True,
            "state": "DONE",
        },
        {"minSlotMs": 1000},
        {"impersonateServiceAccount": "sa@p.iam.gserviceaccount.com"},
    )

    assert echo["projectId"] == "p"
    assert echo["filters"] == {"minSlotMs": 1000}
    assert echo["allUsers"] is True
    assert echo["state"] == "DONE"
    assert echo["impersonateServiceAccount"] == "sa@p.iam.gserviceaccount.com"
