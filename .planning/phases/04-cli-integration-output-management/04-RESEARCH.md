# Phase 4: CLI Integration & Output Management - Research

**Researched:** 2026-03-29
**Domain:** CLI error handling, logging, exit codes, graceful failure management
**Confidence:** HIGH

## Summary

Phase 4 builds on an already-functional CLI skeleton in `src/main.py`. The Typer-based CLI supports all required flags (`--out`, `--verbose`, `--dry-run`, `--no-search`). The gap is implementing proper exit codes, structured logging, and graceful error handling across the pipeline layers (search, model, I/O).

**Primary recommendation:** Enhance `src/main.py` with try/except blocks around each pipeline stage, explicit `typer.Exit(code=N)` calls for different failure modes, and a consistent logging pattern using Python's standard `logging` module with optional Rich formatting.

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Python 3.14** - Programming language
- **Typer 0.24.1** - CLI framework
- **Rich 14.3.3** - Console styling

### the agent's Discretion
- Exit code conventions (standard Unix codes vs custom)
- Logging verbosity granularity
- Error message formatting

### Deferred Ideas (OUT OF SCOPE)
- Interactive wizards for file selection
- Auto-pushing to GitHub/CI

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CLI-01 | `agentforge generate <description>` orchestrates pipeline, exposes `--out`, `--verbose`, `--dry-run`, `--no-search` flags, reports manifest reasoning when `--verbose` used | Already implemented in `src/main.py` - verify verbose includes rationale |
| CLI-02 | Clear, user-friendly logging and exit codes so `--dry-run` previews, `--no-search` runs, and verbose manifest decisions never fail silently | Typer supports exit codes via `typer.Exit(code=N)`, Python logging module integration needed |
| CLI-03 | Graceful failure handling around search/model layers, surfacing errors without crashing | try/except per pipeline stage with actionable error messages |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Typer | 0.24.1 | CLI framework | Already in stack, built-in exit code support via `typer.Exit()` |
| Rich | 14.3.3 | Console styling | Already in stack, automatic pretty errors with Typer |
| logging | stdlib | Logging | Python standard, no additional dependency needed |

### Implementation Pattern
| Pattern | Use | Source |
|---------|-----|--------|
| `typer.Exit(code=0)` | Successful completion | Typer docs |
| `typer.Exit(code=1)` | General error | Typer docs |
| `typer.Abort()` | User cancellation | Typer docs |
| `try/except` per pipeline stage | Graceful degradation | Standard Python |

## Architecture Patterns

### Recommended CLI Structure
```
src/main.py                    # Entry point with Typer app
src/agentforge/
  __init__.py                  # CLI import alias
  cli/
    __init__.py                # CLI module
    logging.py                 # Logging configuration
    errors.py                  # Custom exceptions
    exit_codes.py              # Exit code constants
```

### Error Handling Pattern
```python
# Source: Typer docs (typer.tiangolo.com/tutorial/terminating/)
import typer

@app.command()
def generate(...):
    try:
        # Stage 1: Intent parsing
        manifest = parser.parse_prompt(prompt)
    except Exception as e:
        typer.echo(f"Error parsing intent: {e}", err=True)
        raise typer.Exit(code=1)
    
    try:
        # Stage 2: Search (optional)
        if not no_search:
            results = search_pipeline.search_manifest(manifest)
    except Exception as e:
        if no_search:
            typer.echo("Search skipped (--no-search)")
        else:
            typer.echo(f"Warning: Search failed: {e}", err=True)
            typer.echo("Continuing without search results...")
        results = []
    
    # ... generation stages
```

### Exit Code Convention
| Code | Meaning | When Used |
|------|---------|-----------|
| 0 | Success | Normal completion |
| 1 | General error | Any unhandled exception |
| 2 | Usage error | Invalid arguments (Typer default) |
| 130 | Ctrl+C | User interruption |

### Logging Levels
| Level | Use |
|-------|-----|
| DEBUG | Verbose manifest reasoning |
| INFO | Progress messages |
| WARNING | Non-fatal issues (API missing) |
| ERROR | Recoverable failures |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI framework | Custom argparse | Typer | Already chosen, type-hints, auto-completion |
| Exit codes | Custom constants | Typer.Exit(code=N) | Built-in, Unix-compatible |
| Pretty errors | Custom formatting | Rich (via Typer) | Already in stack |

## Common Pitfalls

### Pitfall 1: Silent Failures in Optional Stages
**What goes wrong:** Search or generation fails but CLI reports success
**Why it happens:** Bare `except:` that continues without user notification
**How to avoid:** Always echo warnings when optional stages fail, use non-zero exit codes for mandatory stage failures
**Warning signs:** `--verbose` shows errors but `--quiet` doesn't

### Pitfall 2: Overly Verbose Error Messages
**What goes wrong:** Full tracebacks leak to users, confusing non-developers
**Why it happens:** Not catching exceptions, letting Typer's pretty exceptions surface
**How to avoid:** Catch specific exceptions, provide actionable messages, reserve full traces for `--verbose`
**Warning signs:** Users see "TypeError: object NoneType" without context

### Pitfall 3: Exit Code Inconsistency
**What goes wrong:** Some errors return 0, breaking scripts that call the CLI
**Why it happens:** Missing `raise typer.Exit(code=1)` after error echo
**How to avoid:** Always pair error message with exit code

### Pitfall 4: Missing Environment Variable Hints
**What goes wrong:** Users see "API key missing" without knowing which env var
**Why it happens:** Generic error messages
**How to avoid:** Include env var name and setup instruction in error

## Code Examples

### Enhanced CLI with Error Handling
```python
# Source: typer.tiangolo.com/tutorial/terminating/
import typer
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = typer.Typer()

class CLIErrors:
    """Exit code constants"""
    SUCCESS = 0
    PARSE_ERROR = 1
    SEARCH_ERROR = 2
    GENERATION_ERROR = 3
    IO_ERROR = 4

@app.command()
def generate(
    prompt: str = typer.Argument(..., help="Freeform project description"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show manifest without generating files"),
    verbose: bool = typer.Option(False, "--verbose", help="Print manifest rationale"),
    no_search: bool = typer.Option(False, "--no-search", help="Skip Tavily search stage"),
    output_dir: str = typer.Option("output", "--out", help="Output directory"),
):
    """Generate AgentForge configuration files from a project description."""
    
    # Stage 1: Intent parsing
    try:
        parser = IntentManifestParser()
        manifest = parser.parse_prompt(prompt)
        
        if verbose:
            typer.echo("=== Intent Manifest ===")
            for entry in manifest.files_to_generate:
                typer.echo(f"  - {entry.name}: {entry.rationale}")
                
    except Exception as e:
        typer.echo(f"Error parsing intent: {e}", err=True)
        raise typer.Exit(code=CLIErrors.PARSE_ERROR)
    
    if dry_run:
        typer.echo("Dry run complete — no files written.")
        raise typer.Exit(code=CLIErrors.SUCCESS)
    
    # Stage 2: Search (optional)
    search_results = []
    if not no_search:
        try:
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                typer.echo("Warning: TAVILY_API_KEY not set. Skipping search.", err=True)
                typer.echo("Set TAVILY_API_KEY or use --no-search to skip.")
            else:
                if verbose:
                    typer.echo("Running search layer...")
                search_pipeline = SearchPipeline(api_key=api_key)
                search_results = search_pipeline.search_manifest(manifest)
                if verbose:
                    typer.echo(f"Found {len(search_results)} results")
        except Exception as e:
            typer.echo(f"Warning: Search failed: {e}", err=True)
            typer.echo("Continuing without search results...")
            if verbose:
                logger.exception("Search error details")
    
    # Stage 3: Compression
    try:
        if verbose and search_results:
            typer.echo("Running compression layer...")
        
        compression_pipeline = CompressionPipeline(llm=None)
        compressed_context = compression_pipeline.compress(search_results)
        
        if verbose:
            typer.echo(f"Compressed to {len(compressed_context)} documents")
    except Exception as e:
        typer.echo(f"Error during compression: {e}", err=True)
        raise typer.Exit(code=CLIErrors.GENERATION_ERROR)
    
    # Stage 4: Generation
    if GENERATOR_AVAILABLE:
        try:
            if verbose:
                typer.echo("Running generation layer...")
            
            gen = Generator(output_dir=output_dir)
            generated_files = gen.generate(manifest.model_dump(), [doc.model_dump() for doc in compressed_context])
            
            if verbose:
                typer.echo(f"Generated {len(generated_files)} files:")
                for name in generated_files:
                    typer.echo(f"  - {name}")
                    
        except Exception as e:
            typer.echo(f"Error during generation: {e}", err=True)
            raise typer.Exit(code=CLIErrors.GENERATION_ERROR)
    
    # Success
    typer.echo(f"Pipeline complete. Output: {output_dir}/")
    raise typer.Exit(code=CLIErrors.SUCCESS)
```

### Custom Exception with Actionable Message
```python
# Source: Best practice pattern
class PipelineError(Exception):
    """Base exception for pipeline errors"""
    def __init__(self, stage: str, message: str, hint: str = ""):
        self.stage = stage
        self.hint = hint
        super().__init__(message)

class SearchAPIError(PipelineError):
    """Raised when search API fails"""
    def __init__(self, message: str):
        super().__init__(
            stage="search",
            message=message,
            hint="Set TAVILY_API_KEY or use --no-search to skip"
        )

def handle_search_error(e: Exception, no_search: bool) -> list:
    """Handle search errors gracefully"""
    if no_search:
        return []
    
    typer.echo(f"Search error: {e}", err=True)
    if hasattr(e, 'hint'):
        typer.echo(f"Hint: {e.hint}", err=True)
    return []
```

### Exit Code Testing
```python
# Source: typer.tiangolo.com/tutorial/testing/
from typer.testing import CliRunner
import pytest

runner = CliRunner()

def test_generate_success():
    result = runner.invoke(app, ["generate", "build a CLI"])
    assert result.exit_code == 0

def test_generate_parse_error():
    result = runner.invoke(app, ["generate", ""])  # Empty prompt
    assert result.exit_code == 2  # Usage error

def test_generate_verbose_shows_rationale():
    result = runner.invoke(app, ["--verbose", "build a CLI"])
    assert "rationale" in result.stdout.lower() or "rationale" in result.stdout
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Print statements | Python logging module | Standard | Structured, configurable |
| sys.exit(1) | typer.Exit(code=1) | Typer adoption | Unix-compatible, testable |
| Raw exception propagation | try/except with hints | This phase | User-friendly errors |

## Open Questions

1. **Logging verbosity levels**
   - What we know: `--verbose` flag exists
   - What's unclear: Should there be `--quiet` or multiple `-v` levels?
   - Recommendation: Keep simple - `--verbose` enables DEBUG level, default is INFO

2. **Error message detail**
   - What we know: Typer shows pretty exceptions by default
   - What's unclear: When to show full traceback vs. short message
   - Recommendation: Show short message by default, full traceback only in verbose mode

3. **Backward compatibility**
   - What we know: Current CLI has no explicit exit codes
   - What's unclear: Any scripts depend on current behavior?
   - Recommendation: Document the new exit code behavior in release notes

## Environment Availability

Step 2.6: SKIPPED (no external dependencies - this phase modifies existing CLI code only)

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + typer.testing.CliRunner |
| Config file | pytest.ini (if exists) |
| Quick run command | `pytest tests/test_cli_flags.py -x` |
| Full suite command | `pytest tests/ -x` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CLI-01 | CLI supports all flags | unit | `pytest tests/test_cli_flags.py -x` | ✅ exists |
| CLI-02 | Exit codes correct | unit | `pytest tests/test_exit_codes.py -x` | ❌ create |
| CLI-02 | Verbose shows rationale | unit | `pytest tests/test_cli_flags.py::test_generate_verbose_outputs_manifest_json -x` | ✅ exists |
| CLI-03 | Graceful error handling | integration | `pytest tests/test_error_handling.py -x` | ❌ create |

### Wave 0 Gaps
- [ ] `tests/test_exit_codes.py` — covers CLI-02 exit codes
- [ ] `tests/test_error_handling.py` — covers CLI-03 graceful failures

### Current Test Coverage
Existing test file `tests/test_cli_flags.py` already covers:
- `test_generate_command_dry_run` - dry-run flag
- `test_generate_verbose_outputs_manifest_json` - verbose flag

### Recommendations
1. Add `test_exit_codes.py` to test:
   - Success exits with code 0
   - Parse errors exit with code 1
   - Missing required args exit with code 2

2. Add `test_error_handling.py` to test:
   - Missing TAVILY_API_KEY shows warning
   - Failed search continues gracefully
   - Generation failure shows actionable message

## Sources

### Primary (HIGH confidence)
- Typer docs - Terminating (typer.tiangolo.com/tutorial/terminating/) - Exit codes, typer.Exit()
- Typer docs - Exceptions (typer.tiangolo.com/tutorial/exceptions/) - Pretty exceptions, error handling
- Typer docs - Testing (typer.tiangolo.com/tutorial/testing/) - CliRunner for exit code testing

### Secondary (MEDIUM confidence)
- Python logging docs (docs.python-guide.org/writing/logging) - Standard logging patterns

### Tertiary (LOW confidence)
- Real Python - Python Logging - Logging best practices

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Typer already in stack, documented APIs
- Architecture: HIGH - Simple extension of existing main.py
- Pitfalls: HIGH - Well-understood patterns from research

**Research date:** 2026-03-29
**Valid until:** 2026-05-01 (CLI patterns are stable)
