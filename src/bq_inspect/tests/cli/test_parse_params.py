"""Tests for --params JSON and @file parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from bq_inspect.cli.params.parse_params import resolve_params_value
from bq_inspect.core.shared.errors import BqInspectFailure

if TYPE_CHECKING:
    from pathlib import Path


def test_parses_inline_json_objects() -> None:
    assert resolve_params_value('{"projectId":"p"}') == {"projectId": "p"}


def test_reads_json_from_at_file_relative_to_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    params_file = tmp_path / "params.json"
    params_file.write_text('{"jobs":[{"projectId":"p","jobId":"j"}]}', encoding="utf-8")

    assert resolve_params_value("@params.json") == {
        "jobs": [{"projectId": "p", "jobId": "j"}],
    }


def test_rejects_empty_inline_params() -> None:
    with pytest.raises(BqInspectFailure):
        resolve_params_value("   ")


def test_rejects_at_without_path() -> None:
    with pytest.raises(BqInspectFailure):
        resolve_params_value("@")


def test_rejects_invalid_json() -> None:
    with pytest.raises(BqInspectFailure):
        resolve_params_value("{not json}")


def test_rejects_missing_at_file() -> None:
    with pytest.raises(BqInspectFailure):
        resolve_params_value("@./does-not-exist.json")
