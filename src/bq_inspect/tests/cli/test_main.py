"""Tests for CLI main entry dispatch."""

from __future__ import annotations

import json
from io import StringIO

import pytest

from bq_inspect.cli import main


def test_main_unknown_command_writes_json_error_to_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspect", "not-a-command"])
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    payload = json.loads(stderr.getvalue())
    assert payload["code"] == "BQINSPECT_INPUT_INVALID"
    assert "Unknown command" in payload["message"]


def test_main_empty_argv_prints_global_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    stdout = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspect"])
    monkeypatch.setattr("sys.stdout", stdout)

    main()

    output = stdout.getvalue()
    assert "bq-inspect" in output
    assert "jobs summary" in output
