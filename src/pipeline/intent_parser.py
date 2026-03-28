from __future__ import annotations

import json
import logging
import os
from typing import Any, List, Optional

import typer

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class ManifestEntry(BaseModel):
    name: str = Field(..., description="Output file name")
    reason: str = Field(..., description="Why this file matters")


class IntentManifest(BaseModel):
    project_type: str = Field(
        ..., description="Type of project: cli, web_app, saas, library, etc."
    )
    domain: str = Field(
        ..., description="Domain area: developer_tools, fintech, social_media, etc."
    )
    scale: str = Field(..., description="Project scale: solo, startup, medium, large")
    stack_hints: List[str] = Field(
        default_factory=list, description="Technology hints inferred from prompt"
    )
    files_to_generate: List[ManifestEntry] = Field(
        ..., description="List of files to generate with rationale"
    )


class ManifestParserError(Exception):
    pass


INTENT_PROMPT = """You are an AI assistant that analyzes project descriptions and determines what configuration files are needed.

Analyze this project description and return a JSON object with:
- project_type: Type of project (cli, web_app, saas, library, api, etc.)
- domain: Domain area (developer_tools, fintech, social_media, e-commerce, etc.)
- scale: Project scale (solo, startup, medium, large)
- stack_hints: Technology hints from the description (e.g., python, nextjs, postgres, etc.)
- files_to_generate: List of files to generate, each with name and reason

Only generate files that are truly needed:
- Always: AGENT.md (project overview), RULES.md (conventions), STRUCTURE.md (folder structure)
- For SaaS/web apps with users: AUTH.md, API.md, SCHEMA.md, PAYMENTS.md if billing
- For trading/finance: SCHEMA.md, API.md
- For CLI tools: COMMANDS.md
- For complex projects: TESTING.md, DEPLOYMENT.md, STACK.md

Project description: {prompt}

Return ONLY valid JSON, no other text."""


class IntentManifestParser:
    def __init__(self, model: str | None = None) -> None:
        self.model_name = model or "gemini-2.0-flash"
        self._test_mode = os.getenv("GSD_TEST_MODE")
        self.llm: Optional[Any] = None

        self._init_llm()

    def _init_llm(self) -> None:
        """Initialize the LLM."""
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            logger.warning("GEMINI_API_KEY not set, using test mode")
            return

        if ChatGoogleGenerativeAI:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=api_key,
                    temperature=0.3,
                    max_tokens=2048,
                    convert_system_message_to_human=True,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
        else:
            logger.warning("langchain-google-genai not installed")

    def parse_prompt(self, prompt: str) -> IntentManifest:
        """Parse a prompt and return structured manifest."""

        # Test mode fallback
        if self._test_mode or not self.llm:
            return self._test_parse(prompt)

        try:
            response = self.llm.invoke(INTENT_PROMPT.format(prompt=prompt))
            content = response.content

            # Extract JSON from response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ManifestParserError("No JSON found in response")

            json_str = content[json_start:json_end]
            data = json.loads(json_str)

            # Convert to Pydantic
            files = [ManifestEntry(**f) for f in data.get("files_to_generate", [])]

            return IntentManifest(
                project_type=data.get("project_type", "web_app"),
                domain=data.get("domain", "general"),
                scale=data.get("scale", "solo"),
                stack_hints=data.get("stack_hints", []),
                files_to_generate=files,
            )

        except Exception as e:
            logger.warning(f"LLM parsing failed: {e}, using test mode")
            return self._test_parse(prompt)

    def _test_parse(self, prompt: str) -> IntentManifest:
        """Test mode parsing with keyword detection."""
        prompt_lower = prompt.lower()

        # Detect project type from prompt
        if any(
            w in prompt_lower
            for w in [
                "saas",
                "dashboard",
                "subscription",
                "invoice",
                "billing",
                "marketplace",
                "platform",
            ]
        ):
            project_type = "saas"
            domain = "business_software"
            scale = "startup"
            files = [
                ManifestEntry(name="AGENT.md", reason="Core overview for SaaS"),
                ManifestEntry(name="RULES.md", reason="Coding conventions"),
                ManifestEntry(name="STRUCTURE.md", reason="Project organization"),
                ManifestEntry(name="AUTH.md", reason="User authentication required"),
                ManifestEntry(name="PAYMENTS.md", reason="Billing integration"),
                ManifestEntry(name="SCHEMA.md", reason="Database schema"),
                ManifestEntry(name="API.md", reason="REST API endpoints"),
            ]
        elif any(
            w in prompt_lower
            for w in ["twitter", "social", "facebook", "instagram", "tiktok"]
        ):
            project_type = "saas"
            domain = "social_media"
            scale = "startup"
            files = [
                ManifestEntry(
                    name="AGENT.md", reason="Core overview for social platform"
                ),
                ManifestEntry(name="RULES.md", reason="Coding conventions"),
                ManifestEntry(name="STRUCTURE.md", reason="Project organization"),
                ManifestEntry(name="AUTH.md", reason="User authentication required"),
                ManifestEntry(name="API.md", reason="REST API endpoints"),
            ]
        elif any(
            w in prompt_lower
            for w in ["trade", "chart", "finance", "crypto", "stock", "trading"]
        ):
            project_type = "web_app"
            domain = "fintech"
            scale = "startup"
            files = [
                ManifestEntry(
                    name="AGENT.md", reason="Core overview for trading platform"
                ),
                ManifestEntry(name="RULES.md", reason="Coding conventions"),
                ManifestEntry(name="STRUCTURE.md", reason="Project organization"),
                ManifestEntry(name="API.md", reason="Trading API endpoints"),
                ManifestEntry(
                    name="SCHEMA.md", reason="Database schema for financial data"
                ),
            ]
        elif any(
            w in prompt_lower for w in ["cli", "tool", "command", "script", "utility"]
        ):
            project_type = "cli"
            domain = "developer_tools"
            scale = "solo"
            files = [
                ManifestEntry(name="AGENT.md", reason="Core overview"),
                ManifestEntry(name="RULES.md", reason="Coding conventions"),
                ManifestEntry(name="STRUCTURE.md", reason="Project organization"),
                ManifestEntry(name="COMMANDS.md", reason="CLI commands documentation"),
            ]
        else:
            project_type = "web_app"
            domain = "general"
            scale = "solo"
            files = [
                ManifestEntry(name="AGENT.md", reason="Core overview"),
                ManifestEntry(name="RULES.md", reason="Coding conventions"),
                ManifestEntry(name="STRUCTURE.md", reason="Project organization"),
            ]

        return IntentManifest(
            project_type=project_type,
            domain=domain,
            scale=scale,
            stack_hints=["python", "typer"],
            files_to_generate=files,
        )


def print_manifest(manifest: IntentManifest) -> None:
    typer.echo("Manifest metadata:")
    typer.echo(f"- Project type: {manifest.project_type}")
    typer.echo(f"- Domain: {manifest.domain}")
    typer.echo(f"- Scale: {manifest.scale}")
    typer.echo("Files to generate:")
    for entry in manifest.files_to_generate:
        typer.echo(f"  - {entry.name}: {entry.reason}")
