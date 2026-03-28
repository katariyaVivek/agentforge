from __future__ import annotations

import re
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from src.pipeline.search import SearchResult


class CompressedDocument(BaseModel):
    summary: str = Field(..., description="~400 word summary of the source")
    source_url: str
    source_title: str
    version: Optional[str] = Field(
        None, description="Version number if found (e.g., v1.2.3)"
    )
    flags: List[str] = Field(
        default_factory=list, description="CLI flags found in content"
    )
    tools: List[str] = Field(
        default_factory=list, description="Tools mentioned in content"
    )


VERSION_PATTERN = re.compile(r"\bv?\d+\.\d+(?:\.\d+)?\b")
FLAG_PATTERN = re.compile(r"--\w+(?:-\w+)*")
COMMON_TOOLS = {
    "pytest",
    "black",
    "ruff",
    "mypy",
    "flake8",
    "isort",
    "pre-commit",
    "git",
    "docker",
    "npm",
    "pip",
    "poetry",
    "uv",
    "typer",
    "click",
    "langchain",
    "openai",
    "gemini",
    "httpx",
    "requests",
    "pydantic",
}


class CompressionPipeline:
    def __init__(self, llm: Any = None) -> None:
        self.llm = llm

    def _extract_version(self, content: str) -> Optional[str]:
        match = VERSION_PATTERN.search(content)
        if match:
            return match.group(0)
        return None

    def _extract_flags(self, content: str) -> List[str]:
        flags = FLAG_PATTERN.findall(content)
        return list(set(flags))[:5]

    def _extract_tools(self, content: str) -> List[str]:
        found = []
        content_lower = content.lower()
        for tool in COMMON_TOOLS:
            if tool.lower() in content_lower:
                found.append(tool)
        return found[:5]

    def _summarize(self, content: str) -> str:
        if self.llm:
            return self._llm_summarize(content)
        return self._rule_based_summarize(content)

    def _llm_summarize(self, content: str) -> str:
        return f"Summary of {len(content)} chars (LLM placeholder)"

    def _rule_based_summarize(self, content: str) -> str:
        sentences = content.split(". ")
        summary_parts = []
        word_count = 0
        target_words = 400
        for sent in sentences:
            words = sent.split()
            if word_count + len(words) <= target_words:
                summary_parts.append(sent)
                word_count += len(words)
            else:
                break
        result = ". ".join(summary_parts)
        if not result.endswith("."):
            result += "."
        return result

    def compress(self, search_results: List[SearchResult]) -> List[CompressedDocument]:
        if not search_results:
            return []

        docs: List[CompressedDocument] = []
        seen_urls = set()

        for result in search_results:
            if result.url in seen_urls:
                continue
            seen_urls.add(result.url)

            summary = self._summarize(result.content)
            version = self._extract_version(result.content)
            flags = self._extract_flags(result.content)
            tools = self._extract_tools(result.content)

            docs.append(
                CompressedDocument(
                    summary=summary,
                    source_url=result.url,
                    source_title=result.title,
                    version=version,
                    flags=flags,
                    tools=tools,
                )
            )
        return docs
