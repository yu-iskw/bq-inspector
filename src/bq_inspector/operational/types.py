"""Operational CLI flag shapes shared by CLI and command layers."""

from __future__ import annotations

from typing import Literal, TypedDict


class InputSchemaArgv(TypedDict):
    kind: Literal["input-schema"]


class OutputSchemaArgv(TypedDict):
    kind: Literal["output-schema"]


class RunArgv(TypedDict):
    kind: Literal["run"]
    params: str


OperationalArgv = InputSchemaArgv | OutputSchemaArgv | RunArgv
