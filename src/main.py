from __future__ import annotations

import json
from typing import List

import typer

from src.pipeline.intent_parser import IntentManifestParser, ManifestEntry


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
) -> None:
    parser = IntentManifestParser()
    manifest = parser.parse_prompt(prompt)

    if verbose or dry_run:
        typer.echo(json.dumps(manifest.model_dump(), indent=2))

    if dry_run:
        typer.echo("Dry run complete — no files written.")
        raise typer.Exit()

    typer.echo("Ready to run search/compress/generate pipeline (future phases)")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
