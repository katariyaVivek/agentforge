from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, List, Optional

import typer

from src.pipeline.compressor import CompressionPipeline, CompressedDocument
from src.pipeline.intent_parser import IntentManifestParser
from src.pipeline.search import SearchPipeline

from src.agentforge.cli.exit_codes import CLIErrors
from src.agentforge.cli.errors import (
    CompressionError,
    GenerationError,
    IntentParseError,
)

try:
    from src.agentforge.generation import Generator

    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False


app = typer.Typer()
logger = logging.getLogger(__name__)


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
    if verbose:
        logging.basicConfig(
            level=logging.DEBUG, format="%(message)s", stream=sys.stdout
        )
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)

    manifest = None
    try:
        parser = IntentManifestParser()
        manifest = parser.parse_prompt(prompt)
        if verbose:
            typer.echo("=== Intent Manifest ===")
            typer.echo(f"Project type: {manifest.project_type}")
            typer.echo(f"Domain: {manifest.domain}")
            typer.echo(f"Scale: {manifest.scale}")
            typer.echo("Files to generate:")
            for entry in manifest.files_to_generate:
                typer.echo(f"  - {entry.name}: {entry.reason}")
    except Exception as e:
        typer.echo(f"Error parsing intent: {e}", err=True)
        raise typer.Exit(code=CLIErrors.PARSE_ERROR)

    if verbose or dry_run:
        typer.echo(json.dumps(manifest.model_dump(), indent=2))

    if dry_run:
        typer.echo("Dry run complete — no files written.")
        raise typer.Exit(code=CLIErrors.SUCCESS)

    compressed_context: List[CompressedDocument] = []
    search_results = []

    if not no_search:
        try:
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                typer.echo("Warning: TAVILY_API_KEY not set.", err=True)
                typer.echo("Use --no-search to skip or set the key.")
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
        except Exception as e:
            typer.echo(f"Warning: Search/compression failed: {e}", err=True)
            typer.echo("Continuing without search results...")
            if verbose:
                logger.exception("Search error details")

    if verbose and no_search:
        typer.echo("Search stage skipped (--no-search)")

    if GENERATOR_AVAILABLE:
        if verbose:
            typer.echo("Running generation layer...")

        GeneratorClass = Generator
        try:
            gen = GeneratorClass(output_dir=output_dir)
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
        except Exception as e:
            typer.echo(f"Error during generation: {e}", err=True)
            raise typer.Exit(code=CLIErrors.GENERATION_ERROR)
    else:
        typer.echo(f"Pipeline complete. Context: {len(compressed_context)} documents")
        typer.echo("Note: Generation not available (install langchain packages)")

    raise typer.Exit(code=CLIErrors.SUCCESS)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
