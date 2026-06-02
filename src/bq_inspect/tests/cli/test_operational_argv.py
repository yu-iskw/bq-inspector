"""Tests for operational argv parsing."""

import pytest

from bq_inspect.core.shared.errors import BqInspectFailure
from bq_inspect.operational import parse_operational_argv


def test_returns_input_schema() -> None:
    assert parse_operational_argv(["--input-schema"]) == {"kind": "input-schema"}


def test_returns_output_schema() -> None:
    assert parse_operational_argv(["--output-schema"]) == {"kind": "output-schema"}


def test_returns_run_with_params_string() -> None:
    assert parse_operational_argv(["--params", '{"projectId":"p"}']) == {
        "kind": "run",
        "params": '{"projectId":"p"}',
    }


def test_rejects_positional_arguments() -> None:
    with pytest.raises(BqInspectFailure):
        parse_operational_argv(["extra", "--params", "{}"])


def test_rejects_both_schema_flags() -> None:
    with pytest.raises(BqInspectFailure):
        parse_operational_argv(["--input-schema", "--output-schema"])


def test_rejects_missing_params_for_run() -> None:
    with pytest.raises(BqInspectFailure):
        parse_operational_argv([])


def test_rejects_unknown_flags() -> None:
    with pytest.raises(BqInspectFailure):
        parse_operational_argv(["--unknown"])


def test_rejects_params_flag_without_value() -> None:
    with pytest.raises(BqInspectFailure) as exc_info:
        parse_operational_argv(["--params"])

    assert "expected one argument" in exc_info.value.details["message"]
