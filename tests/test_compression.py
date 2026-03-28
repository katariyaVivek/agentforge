import os
import pytest
from src.pipeline.compressor import CompressionPipeline, CompressedDocument
from src.pipeline.search import SearchResult


os.environ.setdefault("GSD_TEST_MODE", "1")


def test_compressed_document_fields():
    doc = CompressedDocument(
        summary="Test summary",
        source_url="https://example.com",
        source_title="Test",
        version="v1.2.3",
        flags=["--verbose", "--dry-run"],
        tools=["pytest", "black"],
    )
    assert doc.version == "v1.2.3"
    assert "--verbose" in doc.flags
    assert "pytest" in doc.tools


def test_compression_pipeline_init():
    pipeline = CompressionPipeline(llm=None)
    assert pipeline.llm is None


def test_compression_word_count():
    pipeline = CompressionPipeline(llm=None)
    results = [
        SearchResult(
            query="test",
            title="Test",
            url="https://example.com/1",
            content="This is sentence one. This is sentence two. " * 50,
            score=0.9,
        )
    ]
    docs = pipeline.compress(results)
    assert len(docs) == 1
    assert len(docs[0].summary.split()) <= 450


def test_metadata_preservation():
    pipeline = CompressionPipeline(llm=None)
    content = "Use pytest v8.0 with --verbose flag. Black formats code."
    results = [
        SearchResult(
            query="test",
            title="Test",
            url="https://example.com/1",
            content=content,
            score=0.9,
        )
    ]
    docs = pipeline.compress(results)
    assert len(docs) == 1
    assert docs[0].version is not None
    assert "--verbose" in docs[0].flags


def test_empty_search_results():
    pipeline = CompressionPipeline(llm=None)
    docs = pipeline.compress([])
    assert docs == []


def test_deduplication_by_url():
    pipeline = CompressionPipeline(llm=None)
    results = [
        SearchResult(
            query="test",
            title="Test1",
            url="https://x.com",
            content="content",
            score=0.9,
        ),
        SearchResult(
            query="test",
            title="Test2",
            url="https://x.com",
            content="content",
            score=0.9,
        ),
    ]
    docs = pipeline.compress(results)
    assert len(docs) == 1
