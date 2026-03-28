from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import os

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

from src.pipeline.intent_parser import IntentManifest


logger = logging.getLogger(__name__)


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
        self._init_client()

    def _init_client(self) -> None:
        """Initialize Tavily client."""
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not set, search will be skipped")
            return

        if not TavilyClient:
            logger.warning("tavily package not installed")
            return

        try:
            self.client = TavilyClient(api_key=self.api_key)
            logger.info("Tavily search client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Tavily client: {e}")

    def _generate_query(self, entry: Any, manifest: Dict[str, Any]) -> str:
        """Generate search query from file entry."""
        filename = entry.name if hasattr(entry, "name") else str(entry)
        domain = manifest.get("domain", "software")
        project_type = manifest.get("project_type", "project")
        return f"{filename.replace('.md', '')} best practices {project_type} {domain}"

    def search_manifest(
        self, manifest: Dict[str, Any], max_results: int = 3
    ) -> List[SearchResult]:
        """Search for each file in the manifest."""
        if not self.client:
            logger.info("Search skipped: no Tavily client")
            return []

        results: List[SearchResult] = []
        files = manifest.get("files_to_generate", [])

        logger.info(f"Searching for {len(files)} file types...")

        for entry in files:
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
                logger.info(
                    f"Found {len(response.get('results', []))} results for {query}"
                )
            except Exception as e:
                logger.warning(f"Search failed for {query}: {e}")
                continue

        logger.info(f"Total search results: {len(results)}")
        return results
