"""Tests for CLI dispatch and main entry behavior."""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

import pytest

from bq_inspector.cli import main
from bq_inspector.cli.click_cli import invoke
from bq_inspector.tests.test_support.fixture_job_client import FixtureJobClient

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _load_fixture(name: str = "successful-query-job.json") -> dict[str, object]:
    with (_FIXTURES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def test_main_keyboard_interrupt_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_interrupt(argv: list[str] | None = None) -> None:
        del argv
        raise KeyboardInterrupt

    monkeypatch.setattr("bq_inspector.cli.dispatch.invoke", raise_interrupt)
    monkeypatch.setattr("sys.argv", ["bq-inspector", "jobs", "get"])

    with pytest.raises(KeyboardInterrupt):
        main()


def test_main_help_flag_prints_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    stdout = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspector", "jobs", "get", "--help"])
    monkeypatch.setattr("sys.stdout", stdout)

    main()

    output = stdout.getvalue()
    assert "jobs get" in output


def test_main_jobs_group_help_prints_group_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    stdout = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspector", "jobs", "--help"])
    monkeypatch.setattr("sys.stdout", stdout)

    main()

    output = stdout.getvalue()
    assert "summary" in output
    assert "Subcommands:" in output


def test_main_partial_command_is_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspector", "jobs"])
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    payload = json.loads(stderr.getvalue())
    assert payload["code"] == "BQINSPECTOR_INPUT_INVALID"
    assert payload["message"] == "Unknown command: jobs"


def test_main_nested_unknown_command_uses_full_path(monkeypatch: pytest.MonkeyPatch) -> None:
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspector", "jobs", "bogus"])
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    payload = json.loads(stderr.getvalue())
    assert payload["code"] == "BQINSPECTOR_INPUT_INVALID"
    assert payload["message"] == "Unknown command: jobs bogus"
    assert "usage:" not in stderr.getvalue().lower()


def test_main_jobs_list_missing_params_value_writes_json_only_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspector", "jobs", "list", "--params"])
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    output = stderr.getvalue()
    assert "usage:" not in output
    payload = json.loads(output)
    assert payload["code"] == "BQINSPECTOR_INPUT_INVALID"
    assert "expected one argument" in payload["message"]


def test_main_input_schema_writes_json_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    stdout = StringIO()
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspector", "jobs", "get", "--input-schema"])
    monkeypatch.setattr("sys.stdout", stdout)
    monkeypatch.setattr("sys.stderr", stderr)

    main()

    payload = json.loads(stdout.getvalue())
    assert payload["title"] == "bq-inspector jobs get input"
    assert stderr.getvalue() == ""


def test_main_flat_jobs_subcommand_help_prints_command_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stdout = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspector", "get", "--help"])
    monkeypatch.setattr("sys.stdout", stdout)

    main()

    output = stdout.getvalue()
    assert "jobs get" in output
    assert "--params" in output


def test_main_flat_jobs_subcommand_routes_to_jobs_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspector", "performance"])
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    payload = json.loads(stderr.getvalue())
    assert payload["code"] == "BQINSPECTOR_INPUT_INVALID"
    assert payload["message"] == "--params is required (JSON object or @path to a JSON file)."


def test_invoke_flat_summary_returns_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """Flat argv shim + jobs summary runner produce stdout JSON (no live GCP)."""
    job = _load_fixture()
    client = FixtureJobClient({"job_123": job})

    async def fake_create_sdk_client(input_data: object) -> FixtureJobClient:
        del input_data
        return client

    monkeypatch.setattr(
        "bq_inspector.commands.jobs.run_jobs_view.create_sdk_inspection_client_from_input",
        fake_create_sdk_client,
    )
    stdout = StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)

    invoke(
        [
            "summary",
            "--params",
            json.dumps(
                {
                    "jobs": [
                        {
                            "projectId": "analytics-prod",
                            "jobId": "job_123",
                            "location": "US",
                        }
                    ]
                }
            ),
        ]
    )

    payload = json.loads(stdout.getvalue())
    assert payload["schemaVersion"] == "bq-inspector.v1"
    assert payload["jobs"][0]["jobRef"]["jobId"] == "job_123"
