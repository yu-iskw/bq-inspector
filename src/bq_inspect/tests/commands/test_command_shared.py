"""Tests for shared params command factory."""

from __future__ import annotations

import pytest

from bq_inspect.commands.command_shared import InspectionCommandOptions, create_run_params_command


@pytest.mark.asyncio
async def test_create_run_params_command_runs_schema_and_execute_paths() -> None:
    executed: list[str] = []

    async def execute(
        input_data: dict[str, str],
        options: InspectionCommandOptions,
    ) -> dict[str, str]:
        del input_data, options
        executed.append("run")
        return {"ok": "true"}

    runner = create_run_params_command(
        "datasets get",
        lambda raw: raw,
        execute,
    )

    input_schema = await runner.run_argv(
        ["--input-schema"], InspectionCommandOptions(tool_version="0.1.0")
    )
    assert input_schema["title"] == "bq-inspect datasets get input"

    output_schema = await runner.run_argv(
        ["--output-schema"], InspectionCommandOptions(tool_version="0.1.0")
    )
    assert output_schema["title"] == "bq-inspect catalog resource output"

    result = await runner.run_argv(
        ["--params", '{"projectId":"p","datasetId":"d"}'],
        InspectionCommandOptions(tool_version="0.1.0"),
    )
    assert result == {"ok": "true"}
    assert executed == ["run"]
