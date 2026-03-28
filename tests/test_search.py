import os
import pytest
from src.pipeline.search import SearchPipeline, SearchResult
from src.pipeline.intent_parser import IntentManifest, ManifestEntry


os.environ.setdefault("GSD_TEST_MODE", "1")


def test_search_result_dataclass():
    result = SearchResult(
        query="pytest best practices",
        title="Pytest Guide",
        url="https://example.com/pytest",
        content="Pytest is a testing framework...",
        score=0.95,
    )
    assert result.query == "pytest best practices"
    assert result.title == "Pytest Guide"
    assert result.score == 0.95


def test_search_pipeline_init_no_key():
    pipeline = SearchPipeline(api_key=None)
    assert pipeline.client is None
    assert pipeline.api_key is None


def test_search_pipeline_init_with_key():
    os.environ["TAVILY_API_KEY"] = "test-key"
    pipeline = SearchPipeline()
    assert pipeline.api_key == "test-key"
    os.environ.pop("TAVILY_API_KEY", None)


def test_targeted_query_generation():
    pipeline = SearchPipeline()
    manifest = IntentManifest(
        project_type="cli",
        domain="developer_tools",
        scale="solo",
        stack_hints=["python", "typer"],
        files_to_generate=[
            ManifestEntry(name="AGENT.md", reason="Core overview"),
        ],
    )
    entry = manifest.files_to_generate[0]
    query = pipeline._generate_query(entry, manifest)
    assert "AGENT.md" in query
    assert "developer_tools" in query


def test_no_search_returns_empty():
    pipeline = SearchPipeline(api_key=None)
    manifest = IntentManifest(
        project_type="cli",
        domain="dev",
        scale="solo",
        stack_hints=[],
        files_to_generate=[],
    )
    results = pipeline.search_manifest(manifest)
    assert results == []
