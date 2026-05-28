"""Tests for CLI dispatch and main entry behavior."""

from __future__ import annotations

import json
from io import StringIO

import pytest

from bq_inspect.cli import main


def test_main_keyboard_interrupt_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_interrupt(argv: list[str] | None = None) -> None:
        del argv
        raise KeyboardInterrupt

    monkeypatch.setattr("bq_inspect.cli.dispatch.invoke", raise_interrupt)
    monkeypatch.setattr("sys.argv", ["bq-inspect", "jobs", "get"])

    with pytest.raises(KeyboardInterrupt):
        main()


def test_main_help_flag_prints_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    stdout = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspect", "jobs", "get", "--help"])
    monkeypatch.setattr("sys.stdout", stdout)

    main()

    output = stdout.getvalue()
    assert "jobs get" in output


def test_main_jobs_group_help_prints_group_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    stdout = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspect", "jobs", "--help"])
    monkeypatch.setattr("sys.stdout", stdout)

    main()

    output = stdout.getvalue()
    assert "summary" in output
    assert "Subcommands:" in output


def test_main_partial_command_is_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspect", "jobs"])
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    payload = json.loads(stderr.getvalue())
    assert payload["code"] == "BQINSPECT_INPUT_INVALID"
    assert payload["message"] == "Unknown command: jobs"


def test_main_nested_unknown_command_uses_full_path(monkeypatch: pytest.MonkeyPatch) -> None:
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspect", "jobs", "bogus"])
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    payload = json.loads(stderr.getvalue())
    assert payload["code"] == "BQINSPECT_INPUT_INVALID"
    assert payload["message"] == "Unknown command: jobs bogus"
    assert "usage:" not in stderr.getvalue().lower()


def test_main_jobs_list_missing_params_value_writes_json_only_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspect", "jobs", "list", "--params"])
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    output = stderr.getvalue()
    assert "usage:" not in output
    payload = json.loads(output)
    assert payload["code"] == "BQINSPECT_INPUT_INVALID"
    assert "expected one argument" in payload["message"]


def test_main_input_schema_writes_json_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    stdout = StringIO()
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspect", "jobs", "get", "--input-schema"])
    monkeypatch.setattr("sys.stdout", stdout)
    monkeypatch.setattr("sys.stderr", stderr)

    main()

    payload = json.loads(stdout.getvalue())
    assert payload["title"] == "bq-inspect jobs get input"
    assert stderr.getvalue() == ""
