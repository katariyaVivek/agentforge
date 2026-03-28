from __future__ import annotations

from typing import Any, List

import os
import typer
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel, Field


class ManifestEntry(BaseModel):
    name: str = Field(..., description="Output file name")
    reason: str = Field(..., description="Why this file matters")


class IntentManifest(BaseModel):
    project_type: str
    domain: str
    scale: str
    stack_hints: List[str]
    files_to_generate: List[ManifestEntry]


class ManifestParserError(Exception):
    pass


class IntentManifestParser:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or "gemini"
        self._test_mode = os.getenv("GSD_TEST_MODE")
        self.agent: Any = None
        if not self._test_mode:
            self.agent = create_agent(
                model=self.model,
                response_format=ToolStrategy(IntentManifest),
            )

    def parse_prompt(self, prompt: str) -> IntentManifest:
        if self._test_mode:
            return IntentManifest(
                project_type="cli",
                domain="developer_tools",
                scale="solo",
                stack_hints=["python", "typer"],
                files_to_generate=[
                    ManifestEntry(name="AGENT.md", reason="Core overview"),
                ],
            )
        result = self.agent.run(prompt)
        if isinstance(result, IntentManifest):
            return result
        raise ManifestParserError("Unexpected manifest response")


def print_manifest(manifest: IntentManifest) -> None:
    typer.echo("Manifest metadata:")
    typer.echo(f"- Project type: {manifest.project_type}")
    typer.echo(f"- Domain: {manifest.domain}")
    typer.echo(f"- Scale: {manifest.scale}")
    typer.echo("Files to generate:")
    for entry in manifest.files_to_generate:
        typer.echo(f"  - {entry.name}: {entry.reason}")
