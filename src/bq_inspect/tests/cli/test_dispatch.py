"""Tests for CLI dispatch and main entry behavior."""

from __future__ import annotations

import json
from io import StringIO

import pytest

from bq_inspect.cli import main


def test_main_keyboard_interrupt_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    async def raise_interrupt(_argv: list[str]) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr("bq_inspect.cli.dispatch._dispatch", raise_interrupt)
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


def test_main_partial_command_is_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    stderr = StringIO()
    monkeypatch.setattr("sys.argv", ["bq-inspect", "jobs"])
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    payload = json.loads(stderr.getvalue())
    assert payload["code"] == "BQINSPECT_INPUT_INVALID"
