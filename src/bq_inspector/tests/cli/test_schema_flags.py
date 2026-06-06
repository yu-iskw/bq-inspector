"""Tests for per-command --input-schema and --output-schema flags."""

import json

import pytest

from bq_inspector.commands.command_shared import InspectionCommandOptions
from bq_inspector.commands.datasets.get import run_datasets_get
from bq_inspector.commands.jobs.list import run_jobs_list
from bq_inspector.commands.jobs.run_jobs_view import (
    run_jobs_get,
    run_jobs_impact,
    run_jobs_lineage,
    run_jobs_summary,
)
from bq_inspector.commands.tables.get import run_tables_get
from bq_inspector.commands.tables.list import run_tables_list
from bq_inspector.core.shared.errors import BqInspectFailure


@pytest.mark.asyncio
async def test_jobs_get_input_schema() -> None:
    schema = await run_jobs_get(["--input-schema"], InspectionCommandOptions(tool_version="0.2.0"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["title"] == "bq-inspector jobs get input"
    encoded = json.dumps(schema)
    assert "selector" not in encoded
    assert '"jobs"' in encoded


@pytest.mark.asyncio
async def test_jobs_get_output_schema() -> None:
    schema = await run_jobs_get(["--output-schema"], InspectionCommandOptions(tool_version="0.2.0"))
    assert schema["title"] == "bq-inspector jobs get output"


@pytest.mark.asyncio
async def test_jobs_summary_output_schema_includes_view_const() -> None:
    schema = await run_jobs_summary(
        ["--output-schema"],
        InspectionCommandOptions(tool_version="0.2.0"),
    )
    assert schema["title"] == "bq-inspector jobs summary output"
    assert '"summary"' in json.dumps(schema)


@pytest.mark.asyncio
async def test_jobs_lineage_output_schema_includes_view_const() -> None:
    schema = await run_jobs_lineage(
        ["--output-schema"],
        InspectionCommandOptions(tool_version="0.2.0"),
    )
    assert schema["title"] == "bq-inspector jobs lineage output"
    assert '"lineage"' in json.dumps(schema)


@pytest.mark.asyncio
async def test_jobs_impact_output_schema_includes_view_const() -> None:
    schema = await run_jobs_impact(
        ["--output-schema"],
        InspectionCommandOptions(tool_version="0.2.0"),
    )
    assert schema["title"] == "bq-inspector jobs impact output"
    assert '"impact"' in json.dumps(schema)


@pytest.mark.asyncio
async def test_rejects_both_schema_flags_on_jobs_get() -> None:
    with pytest.raises(BqInspectFailure) as exc_info:
        await run_jobs_get(
            ["--input-schema", "--output-schema"],
            InspectionCommandOptions(tool_version="0.2.0"),
        )
    assert exc_info.value.details["code"] == "BQINSPECTOR_INPUT_INVALID"
    assert "not both" in exc_info.value.details["message"]


@pytest.mark.asyncio
async def test_jobs_list_input_schema() -> None:
    schema = await run_jobs_list(["--input-schema"], InspectionCommandOptions(tool_version="0.2.0"))
    assert schema["title"] == "bq-inspector jobs list input"


@pytest.mark.asyncio
async def test_datasets_get_output_schema() -> None:
    schema = await run_datasets_get(
        ["--output-schema"],
        InspectionCommandOptions(tool_version="0.2.0"),
    )
    assert schema["title"] == "bq-inspector dataset/table resource output"


@pytest.mark.asyncio
async def test_tables_list_output_schema() -> None:
    schema = await run_tables_list(
        ["--output-schema"],
        InspectionCommandOptions(tool_version="0.2.0"),
    )
    assert schema["title"] == "bq-inspector tables list output"


@pytest.mark.asyncio
async def test_tables_get_input_schema_includes_table_id() -> None:
    schema = await run_tables_get(
        ["--input-schema"],
        InspectionCommandOptions(tool_version="0.2.0"),
    )
    assert "tableId" in json.dumps(schema)
    assert schema["title"] == "bq-inspector tables get input"


@pytest.mark.asyncio
async def test_mutual_exclusion_is_bq_inspector_failure() -> None:
    with pytest.raises(BqInspectFailure):
        await run_jobs_list(
            ["--input-schema", "--output-schema"],
            InspectionCommandOptions(tool_version="0.2.0"),
        )
