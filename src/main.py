from __future__ import annotations

import json
import os
from typing import Any, List, Optional

import typer

from src.pipeline.compressor import CompressionPipeline, CompressedDocument
from src.pipeline.intent_parser import IntentManifestParser
from src.pipeline.search import SearchPipeline

try:
    from src.agentforge.generation import Generator

    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False


app = typer.Typer()


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="Freeform project description"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show manifest without generating files"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Print manifest rationale"),
    no_search: bool = typer.Option(
        False, "--no-search", help="Skip Tavily search stage"
    ),
    output_dir: str = typer.Option(
        "output", "--out", help="Output directory for generated files"
    ),
) -> None:
    parser = IntentManifestParser()
    manifest = parser.parse_prompt(prompt)

    if verbose or dry_run:
        typer.echo(json.dumps(manifest.model_dump(), indent=2))

    if dry_run:
        typer.echo("Dry run complete — no files written.")
        raise typer.Exit()

    compressed_context: List[CompressedDocument] = []

    if not no_search:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            typer.echo(
                "Warning: TAVILY_API_KEY not set. Use --no-search or set the key."
            )
            typer.echo("Falling back to --no-search mode.")
        else:
            if verbose:
                typer.echo("Running search layer...")

            search_pipeline = SearchPipeline(api_key=api_key)
            search_results = search_pipeline.search_manifest(manifest)

            if verbose:
                typer.echo(f"Found {len(search_results)} search results")

            if verbose:
                typer.echo("Running compression layer...")

            compression_pipeline = CompressionPipeline(llm=None)
            compressed_context = compression_pipeline.compress(search_results)

            if verbose:
                typer.echo(f"Compressed to {len(compressed_context)} documents")

    if verbose and no_search:
        typer.echo("Search stage skipped (--no-search)")

    if GENERATOR_AVAILABLE:
        if verbose:
            typer.echo("Running generation layer...")

        gen = Generator(output_dir=output_dir)
        manifest_dict = manifest.model_dump()
        context_list = (
            [doc.model_dump() for doc in compressed_context]
            if compressed_context
            else []
        )
        generated_files = gen.generate(manifest_dict, context_list)

        if verbose:
            typer.echo(f"Generated {len(generated_files)} files:")
            for name in generated_files:
                typer.echo(f"  - {name}")

        typer.echo(f"Pipeline complete. Output: {output_dir}/")
    else:
        typer.echo(f"Pipeline complete. Context: {len(compressed_context)} documents")
        typer.echo("Note: Generation not available (install langchain packages)")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
