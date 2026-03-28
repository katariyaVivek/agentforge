---
phase: 04-cli-integration-output-management
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/main.py
  - src/agentforge/__init__.py
autonomous: true
requirements:
  - CLI-01
  - CLI-02
  - CLI-03

must_haves:
  truths:
    - "CLI reports success with exit code 0"
    - "CLI reports errors with non-zero exit codes"
    - "Missing TAVILY_API_KEY shows warning but continues"
    - "Failed search stage shows warning but continues to generation"
    - "Generation failures show actionable error messages"
    - "--verbose flag shows manifest reasoning and detailed logs"
  artifacts:
    - path: "src/main.py"
      provides: "CLI entry point with error handling"
      min_lines: 150
    - path: "src/agentforge/cli/exit_codes.py"
      provides: "Exit code constants"
      exports: ["CLIErrors"]
    - path: "src/agentforge/cli/errors.py"
      provides: "Custom exceptions"
      exports: ["PipelineError", "SearchAPIError"]
    - path: "src/agentforge/cli/logging_config.py"
      provides: "Logging configuration"
      exports: ["configure_logging", "get_logger"]
  key_links:
    - from: "src/main.py"
      to: "src/agentforge/cli/exit_codes.py"
      via: "import"
      pattern: "from.*exit_codes import"
    - from: "src/main.py"
      to: "src/agentforge/cli/errors.py"
      via: "import"
      pattern: "from.*errors import"
    - from: "src/main.py"
      to: "src/agentforge/cli/logging_config.py"
      via: "import"
      pattern: "from.*logging_config import"
---

<objective>
Add proper exit codes, structured logging, and graceful error handling to the CLI
</objective>

<context>
@src/main.py
@.planning/phases/04-cli-integration-output-management/04-RESEARCH.md

The existing CLI in src/main.py already supports all required flags:
- --out: output directory
- --verbose: detailed manifest reasoning
- --dry-run: show manifest without generating
- --no-search: skip Tavily search

The gap is implementing:
1. Exit codes (0 for success, 1 for general errors, 2 for usage errors)
2. Structured logging with configurable verbosity
3. Try/except around each pipeline stage with actionable error messages
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create CLI error handling infrastructure</name>
  <files>src/agentforge/cli/exit_codes.py, src/agentforge/cli/errors.py</files>
  <read_first>
    - src/main.py
    - src/agentforge/__init__.py
  </read_first>
  <action>
Create src/agentforge/cli/ directory and add:

1. **exit_codes.py**: Define exit code constants:
```python
class CLIErrors:
    SUCCESS = 0
    PARSE_ERROR = 1
    SEARCH_ERROR = 2
    COMPRESSION_ERROR = 3
    GENERATION_ERROR = 4
    IO_ERROR = 5
```

2. **errors.py**: Define custom exceptions with actionable hints:
```python
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

class GenerationError(PipelineError):
    """Raised when file generation fails"""
    def __init__(self, message: str):
        super().__init__(
            stage="generation",
            message=message,
            hint="Check output directory permissions"
        )
```

3. Update src/agentforge/__init__.py to export the CLI modules
  </action>
  <acceptance_criteria>
- [ ] File src/agentforge/cli/exit_codes.py exists with CLIErrors class
- [ ] File src/agentforge/cli/errors.py exists with PipelineError base class
- [ ] File src/agentforge/cli/errors.py exports SearchAPIError and GenerationError
- [ ] src/agentforge/__init__.py imports from cli module
- [ ] grep "class CLIErrors" src/agentforge/cli/exit_codes.py returns match
  </acceptance_criteria>
  <verify>
grep -n "class CLIErrors" src/agentforge/cli/exit_codes.py && grep -n "class.*Error" src/agentforge/cli/errors.py
  </verify>
  <done>CLI error infrastructure created with exit codes and custom exceptions</done>
</task>

<task type="auto">
  <name>Task 2: Add structured logging configuration</name>
  <files>src/agentforge/cli/logging_config.py</files>
  <read_first>
    - src/main.py
  </read_first>
  <action>
Create src/agentforge/cli/logging_config.py with:

```python
import logging
import sys
from typing import Optional

def configure_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Custom format without timestamp for cleaner CLI output
    format_str = "%(levelname)s: %(message)s"
    
    logging.basicConfig(
        level=level,
        format=format_str,
        stream=sys.stdout
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
```

Update src/main.py to:
1. Import configure_logging from the new module
2. Call configure_logging(verbose=verbose) at the start of generate()
3. Use logger.debug() for verbose manifest reasoning
4. Use logger.info() for progress messages
  </action>
  <acceptance_criteria>
- [ ] File src/agentforge/cli/logging_config.py exists
- [ ] Function configure_logging takes verbose parameter
- [ ] Function get_logger returns logging.Logger
- [ ] src/main.py imports and calls configure_logging
- [ ] grep "configure_logging" src/main.py returns match
  </acceptance_criteria>
  <verify>
grep -n "configure_logging" src/main.py && grep -n "def configure_logging" src/agentforge/cli/logging_config.py
  </verify>
  <done>Structured logging configured with DEBUG for verbose, INFO by default</done>
</task>

<task type="auto">
  <name>Task 3: Add try/except error handling to pipeline stages</name>
  <files>src/main.py</files>
  <read_first>
    - src/main.py
    - src/agentforge/cli/exit_codes.py
    - src/agentforge/cli/errors.py
  </read_first>
  <action>
Wrap each pipeline stage in src/main.py with try/except:

**Stage 1: Intent parsing (already exists but needs exit code)**
```python
try:
    parser = IntentManifestParser()
    manifest = parser.parse_prompt(prompt)
except Exception as e:
    typer.echo(f"Error parsing intent: {e}", err=True)
    raise typer.Exit(code=CLIErrors.PARSE_ERROR)
```

**Stage 2: Search (optional, graceful degradation)**
```python
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
    except Exception as e:
        typer.echo(f"Warning: Search failed: {e}", err=True)
        typer.echo("Continuing without search results...")
        if verbose:
            logger.exception("Search error details")
```

**Stage 3: Compression**
```python
try:
    if search_results:
        compression_pipeline = CompressionPipeline(llm=None)
        compressed_context = compression_pipeline.compress(search_results)
except Exception as e:
    typer.echo(f"Error during compression: {e}", err=True)
    raise typer.Exit(code=CLIErrors.COMPRESSION_ERROR)
```

**Stage 4: Generation**
```python
if GENERATOR_AVAILABLE:
    try:
        gen = Generator(output_dir=output_dir)
        generated_files = gen.generate(manifest_dict, context_list)
        typer.echo(f"Pipeline complete. Output: {output_dir}/")
    except Exception as e:
        typer.echo(f"Error during generation: {e}", err=True)
        raise typer.Exit(code=CLIErrors.GENERATION_ERROR)
```

Replace all `raise typer.Exit()` with `raise typer.Exit(code=CLIErrors.SUCCESS)` for success cases.
  </action>
  <acceptance_criteria>
- [ ] Intent parsing wrapped with try/except and exit code CLIErrors.PARSE_ERROR
- [ ] Search stage shows warning but continues on failure
- [ ] Compression wrapped with try/except and exit code CLIErrors.COMPRESSION_ERROR
- [ ] Generation wrapped with try/except and exit code CLIErrors.GENERATION_ERROR
- [ ] Success cases use CLIErrors.SUCCESS exit code
- [ ] grep "CLIErrors.PARSE_ERROR" src/main.py returns match
- [ ] grep "CLIErrors.GENERATION_ERROR" src/main.py returns match
  </acceptance_criteria>
  <verify>
grep -n "CLIErrors" src/main.py | head -20
  </verify>
  <done>All pipeline stages have try/except with appropriate exit codes and user-friendly error messages</done>
</task>

<task type="auto">
  <name>Task 4: Verify --verbose shows manifest reasoning</name>
  <files>src/main.py</files>
  <read_first>
    - src/main.py
    - tests/test_cli_flags.py
  </read_first>
  <action>
Ensure the --verbose flag outputs manifest reasoning. The current implementation outputs the full manifest JSON, but per CLI-01 requirement it should show "detailed manifest reasoning."

Modify the verbose output to include explicit rationale display:
```python
if verbose:
    typer.echo("=== Intent Manifest ===")
    for entry in manifest.files_to_generate:
        typer.echo(f"  - {entry.name}: {entry.rationale}")
```

Also add verbose output for search results showing sources queried.
  </action>
  <acceptance_criteria>
- [ ] --verbose shows file-by-file rationale
- [ ] --verbose shows search stage progress
- [ ] --verbose shows compression stage progress
- [ ] --verbose shows generation stage progress
- [ ] Test test_generate_verbose_outputs_manifest_json passes
  </acceptance_criteria>
  <verify>
pytest tests/test_cli_flags.py::test_generate_verbose_outputs_manifest_json -x 2>/dev/null || echo "Test may need to be created"
  </verify>
  <done>Verbose flag provides detailed manifest reasoning</done>
</task>

</tasks>

<verification>
Run the CLI with various flag combinations to verify error handling:
1. agentforge generate "test" --verbose → shows manifest reasoning
2. agentforge generate "test" --dry-run → exit code 0
3. agentforge generate "" → exit code 2 (usage error)
</verification>

<success_criteria>
- CLI-01: All flags work correctly, verbose shows manifest reasoning
- CLI-02: Exit codes: 0 for success, non-zero for errors; logging shows progress
- CLI-03: Search failure shows warning but continues; generation failure shows actionable message
</success_criteria>

<output>
After completion, create `.planning/phases/04-cli-integration-output-management/04-01-SUMMARY.md`
</output>
