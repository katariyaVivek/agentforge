from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import os

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

from src.pipeline.intent_parser import IntentManifest, ManifestEntry


@dataclass
class SearchResult:
    query: str
    title: str
    url: str
    content: str
    score: float


class SearchError(Exception):
    pass


class SearchPipeline:
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client = None
        if self.api_key and TavilyClient:
            self.client = TavilyClient(api_key=self.api_key)

    def _generate_query(self, entry: ManifestEntry, manifest: IntentManifest) -> str:
        domain = manifest.domain or "software"
        return f"{entry.name} best practices {domain}"

    def search_manifest(
        self, manifest: IntentManifest, max_results: int = 3
    ) -> List[SearchResult]:
        if not self.client:
            return []

        results: List[SearchResult] = []
        for entry in manifest.files_to_generate:
            query = self._generate_query(entry, manifest)
            try:
                response = self.client.search(
                    query=query,
                    search_depth="basic",
                    max_results=max_results,
                )
                for item in response.get("results", []):
                    results.append(
                        SearchResult(
                            query=query,
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            content=item.get("content", ""),
                            score=item.get("score", 0.0),
                        )
                    )
            except Exception:
                continue
        return results
