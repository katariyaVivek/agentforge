# Phase 01: Intent Parsing & Dynamic Manifest - Research

**Researched:** 2026-03-28
**Domain:** LLM-driven intent manifest pipeline
**Confidence:** MEDIUM

## Summary

Phase 1 must guarantee that a single freeform prompt yields a deterministic project intent, metadata (type, domain, scale), and a manifest of files with human-readable rationale before any generation happens. The safest way to achieve that is to *engineer a strict schema* for the manifest, compel the LLM to validate against it, and expose CLI guards (`--dry-run`, `--verbose`, `--no-search`) so the user can audit the manifest without making filesystem changes. Typer + LangChain structured output with Pydantic validation satisfy those needs and are the baseline for everything built later in the pipeline.

The project already prescribes the stack (Python 3.x, LangChain, Tavily, Typer), so research focuses on how to orchestrate the intent parser, the manifest rationale, and the CLI controls within that stack. Key risks to mitigate include schema drift, silent failures, and manifest choices that cannot be easily audited; addressing them now keeps downstream search/compression/generation reliable.

**Primary recommendation:** Use LangChain’s structured output tooling with a Pydantic manifest schema and Typer CLI flags that run the pipeline in `--dry-run`/`--verbose` modes before touching the filesystem.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
_No CONTEXT.md provided; there are currently no locked decisions beyond the project instructions already gathered._

### the agent's Discretion
_Not provided; standard research freedom applies._

### Deferred Ideas (OUT OF SCOPE)
_None listed._
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PIPE-01 | Intent parser extracts project metadata (type, domain, scale) and returns a structured manifest with file reasons. | Sections *Standard Stack* (LangChain + Pydantic schema), *Architecture Patterns* (structured output schema + pipeline), *Code Examples* (LangChain structured output snippet), and *Common Pitfalls* (schema validation handling) detail how to implement this requirement with confidence.
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Typer | 0.24.1 | CLI orchestration, option parsing | Modern type-hinted CLI builder that integrates `Option` defaults, flags, and help text without writing boilerplate `argparse`. Verified via `pip index versions typer` (latest 0.24.1, matched project docs). |
| LangChain | 1.2.13 | Structured output + agent orchestration | Provides `create_agent` plus `StructuredOutput` tooling for schema validation, retries, and fallback strategies rather than manual text parsing. Verified via `pip index versions langchain` (latest 1.2.13). |
| Pydantic | 2.12.5 | Manifest schema & validation | Fast, explicit schema for intent metadata and file manifest entries; integrates with LangChain structured output. Verified via `pip index versions pydantic`. |
| HTTPX | 0.28.1 | Tavily / provider API calls | Async-ready HTTP client used across search/compression layers to keep pipeline non-blocking. Verified via `pip index versions httpx`. |
| python-dotenv | 1.2.2 | Config management | Keeps API keys (Gemini, Tavily, Groq, OpenRouter) and CLI defaults external to code. Verified via `pip index versions python-dotenv`. |
| Tavily Python SDK | 1.1.0 | Search grounding | Structured search results for later compression; aligns with phase 2. Verified via `pip index versions tavily` (latest 1.1.0). |
| Jinja2 | 3.1.6 | Template-driven rationale | Optional for formatting manifest rationale or file descriptions before generation. Verified via `pip index versions jinja2`. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| rich | 14.3.3 | Console output | User-friendly logs explaining manifest choices; use when verbose helps explain intent parsing. |
| shellingham | via Typer | Shell autodetection | Required indirectly by Typer’s completion helpers. |
| click | 8.x | CLI runtime underpinning Typer | Implicit dependency—no direct import, but understanding ensures compatibility with Typer. |
| langchain-deepagents | latest | Durable execution patterns | Use if manifest decisions spawn sub-agents (anticipated as project matures). |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| LangChain | Direct OpenAI SDK or custom prompts | More manual control but lacks LangChain’s structured-output retry/error handling; increases maintenance burden for manifest validation. |
| Typer | Click (manual) | Click can still build CLI but requires more boilerplate for `--dry-run`/`--verbose` docstrings; Typer already in project stack. |
| Pydantic | Hand-rolled JSON validation | Harder to maintain for manifest evolution, no automatic docs or LangChain schema integration. |

**Installation:**
```bash
pip install typer==0.24.1 langchain==1.2.13 pydantic==2.12.5 httpx==0.28.1 python-dotenv==1.2.2 tavily==1.1.0 jinja2==3.1.6 rich==14.3.3
```

**Version verification:**
- `pip index versions typer` → 0.24.1 (current)
- `pip index versions langchain` → 1.2.13 (current)
- `pip index versions pydantic` → 2.12.5 (current)
- `pip index versions httpx` → 0.28.1 (current)
- `pip index versions tavily` → 1.1.0 (current)
- `pip index versions jinja2` → 3.1.6 (current)

## Architecture Patterns

### Recommended Project Structure
```
src/
├── main.py                    # Typer CLI entrypoint exposes `generate` + flags
├── pipeline/
│   ├── intent_parser.py       # Step 1: structured intent parsing + manifest
│   ├── search.py              # Tavily search queries (phase 2 prep)
│   ├── compressor.py          # Compress docs (~400 words each)
│   └── generator.py           # Generate files from file_definitions/catalog
├── prompts/
│   ├── intent.md              # System prompt + schema definition
│   ├── compress.md            # Compression prompt
│   └── generate.md            # File-specific generation prompt
├── file_definitions/
│   └── catalog.py             # Registry of conditional files + triggers
├── templates/                 # Reference bundles or manifest scaffolds
├── output/                    # Generated bundles (gitignored)
├── .env                       # API keys (Gemini, Tavily, Groq, OpenRouter)
└── README.md
```

### Pattern 1: Structured Output Schema for Intent + Manifest
**What:** Define a strict Pydantic schema (project metadata + list of files with rationale) and feed it to LangChain’s `StructuredOutput` tooling so the model returns validated objects instead of free text.
**When to use:** Always for the intent parser—Phase 1 cannot progress unless the manifest is machine-readable.
**Example:**
```python
from pydantic import BaseModel, Field
from typing import List
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

class ManifestEntry(BaseModel):
    name: str
    reason: str

class IntentManifest(BaseModel):
    project_type: str
    domain: str
    scale: str
    files_to_generate: List[ManifestEntry]

agent = create_agent(
    model="gpt-5",
    response_format=ToolStrategy(IntentManifest),
)
```
_Source: LangChain Structured Output docs (Provider & Tool strategy sections)._ 

### Pattern 2: CLI Preview Flags (`--dry-run`, `--verbose`, `--no-search`)
**What:** Use Typer `Option`s to gate each pipeline stage and conditionally suppress file writes.
**When to use:** Always expose `--dry-run`/`--verbose`; prevention of accidental file creation is key to manifest trust.
**Example:**
```python
import typer

@typer.command()
def generate(
    prompt: str,
    dry_run: bool = typer.Option(False, "--dry-run", help="Show manifest without writing files"),
    verbose: bool = typer.Option(False, "--verbose", help="Log manifest reasoning"),
    no_search: bool = typer.Option(False, "--no-search", help="Skip Tavily search stage"),
):
    typer.echo(f"Dry run: {dry_run}; Verbose: {verbose}")
    # Intent parser → search/compress → generator
```
_Source: Typer Options tutorial (CLI Options page)._ 

### Pattern 3: Pipeline Orchestration (Pipes & Filters)
**What:** Each stage transforms the context (intent → search queries → compressed docs → generation requests) and stores manifest + rationale in shared context.
**When to use:** Always; makes it easy to reason about failure handling and dry-run reports.
**Example:**
```python
def run_pipeline(prompt: str):
    manifest = intent_parser.parse(prompt)
    docs = search_layer.fetch(manifest.search_queries)
    compressed = compressor.summarize(docs)
    return generator.generate(manifest, compressed)
```
_Source: `rough_plan.md` pipeline diagram._

### Anti-Patterns to Avoid
- **Hardcoded file list:** defeats the intent parser; always consult `catalog.py` so manifest justification drives generation.
- **Monolithic prompts for manifest + files:** wastes context and makes validation brittle; keep intent parsing separate and use targeted schema enforcement.

## Don't Hand-Roll
| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Schema validation for user intent | Regex/parsing that tries to pull project_type/domain/scale manually | LangChain StructuredOutput + Pydantic schema | LangChain handles retries, errors, and ensures the manifest is valid JSON before downstream stages consume it. |
| Manifest reasoning report | Custom heuristics to guess why a file was chosen | Embed `reason` field in schema and let the model explain; log via `--verbose` | Prevents drift between what the model meant and what the pipeline reports; rationale stays synchronized with file definition. |
| Dry-run guard | Writing files before confirming manifest | Typer `--dry-run` flag that stops before generator/FileSystem stage | Keeps phase 1 focused on manifest correctness; prevents expensive I/O when manifest still being tuned. |

**Key insight:** Phase 1 succeeds when manifest data is structured, validated, and human-readable—every addition after that depends on this clean foundation.

## Common Pitfalls

### Pitfall 1: Schema validation failure loops
**What goes wrong:** LLM returns partially valid manifest (missing `files_to_generate`) and pipeline crashes or writes incomplete data.
**Why it happens:** Without LangChain’s structured output safeguards, retries are manual and inconsistent.
**How to avoid:** Use `ToolStrategy`/`ProviderStrategy` with `handle_errors=True` so LangChain automatically prompts the model to fix schema issues (can even customize `handle_errors`).
**Warning signs:** Agent logs multiple `StructuredOutputValidationError` messages or the manifest is missing keys.

### Pitfall 2: Silent file writes without preview
**What goes wrong:** CLI defaults to generation and overwrites output even if manifest isn’t correct.
**Why it happens:** No `--dry-run` guard and generator runs immediately after parsing.
**How to avoid:** Build the CLI to stop after manifest + rationale (phase 1 deliverable) unless the user explicitly removes `--dry-run`; keep `--verbose` on by default during research.
**Warning signs:** Outputs appear with wrong file sets; logs show no manifest preview.

### Pitfall 3: Loose CLI flag definitions
**What goes wrong:** Missing `--no-search` causes search-rate-limit errors even when user wants to skip.
**Why it happens:** Early-phase CLI may only accept `prompt` and `--out`, ignoring other behaviors.
**How to avoid:** Add Typer options for search toggle, dry-run, and verbosity now; ensures Phase 1 API already matches requirements.
**Warning signs:** Users flood Tavily and cannot reproduce manifest without hitting search limits.

## Code Examples

### Intent parser enforcing manifest schema
```python
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel
from typing import List

class FileEntry(BaseModel):
    name: str
    reason: str

class IntentManifest(BaseModel):
    project_type: str
    domain: str
    scale: str
    files_to_generate: List[FileEntry]

agent = create_agent(
    model="gpt-5",
    response_format=ToolStrategy(IntentManifest),
)
```
_Source: LangChain Structured Output documentation (Provider & Tool strategy sections)._ 

### Typer CLI preview flags
```python
import typer

@typer.command()
def generate(
    prompt: str,
    dry_run: bool = typer.Option(False, "--dry-run", help="Show manifest without generating files"),
    verbose: bool = typer.Option(False, "--verbose", help="Print manifest reasoning"),
    no_search: bool = typer.Option(False, "--no-search", help="Skip Tavily search for rapid prototyping"),
):
    typer.echo("Computing manifest...")
    manifest = intent_parser.parse(prompt)
    if dry_run:
        typer.echo(manifest.json(indent=2))
        return
    # Continue with search/compression/generation
```
_Source: Typer CLI Options guide._

## State of the Art
| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Freeform LLM response parsing | LangChain structured output with schema | 2025+ LangChain docs | Eliminates brittle string parsing and provides higher reliability in manifest extraction. |
| Immediate generation | CLI preview (`--dry-run`) and verbose logging | Project requirements from CLOUDE/rough_plan | Prevents irreversible writes until manifest is audited, aligning with Phase 1 success criteria. |

**Deprecated/outdated:**
- Rolling your own JSON extractor from LLM text: replaced by LangChain structured output and Pydantic.

## Open Questions
1. **Should the manifest schema include optional stack hints/search queries or keep them separate?**
   - What we know: stack hints help search layer (per `rough_plan.md`).
   - What's unclear: whether the intent parser should emit search queries directly or pass metadata to a dedicated query generator.
   - Recommendation: capture stack hints + domain metadata now, but centralize query generation in Phase 2 to keep Phase 1 focused on manifest rationale.
2. **How verbose should `--verbose` output be during Phase 1?**
   - What we know: requirement is to “report manifest reasoning when `--verbose` is used.”
   - What's unclear: whether verbose mode should print raw schema or a human-friendly summary.
   - Recommendation: log each file/reason pair plus project metadata, leaving formatting (JSON vs Markdown) to future refinements.

## Environment Availability
| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | CLI + pipeline | ✓ | 3.11.9 | — |
| pip | package installs | ✓ | 26.0.1 | — |
| Typer | CLI flags | ✓ | 0.24.1 (PyPI) | — |
| LangChain | Structured output | ✓ | 1.2.13 (PyPI) | — |
| Tavily API | Search grounding | ✗ | — | Fallback: skip search entirely via `--no-search`, but phase 2 drop-off (dry-run still works). |
| Gemini / Groq / OpenRouter API keys | Intent parsing + generation | ✗ | — | Requires secrets (.env) before generation; fallback is to mock model responses for testing. |

**Missing dependencies with no fallback:**
- Tavily API key + rate limits (plan needs actual key before Phase 2). Phase 1 can still run `--dry-run` since search is optional, but future phases will depend on it.

**Missing dependencies with fallback:**
- Gemini/Groq/OpenRouter keys: fallback to easier models (Claude, GPT) for early testing, but production-run needs those keys to obey Core Value (Gemini Flash preference). Keep them in `.env` and guard with warnings when absent.

## Sources
### Primary (HIGH confidence)
- LangChain Structured Output docs (`https://docs.langchain.com/oss/python/langchain/structured-output`) — schema strategies, tool/provider fallback, and error handling.
- Typer CLI Options docs (`https://typer.tiangolo.com/tutorial/options/`) — canonical way to declare `--dry-run`, `--verbose`, and other flags.

### Secondary (MEDIUM confidence)
- `rough_plan.md` — outlines pipeline flow, dynamic manifest intent, and requirements for manifest/dry-run.

### Tertiary (LOW confidence)
- None — all critical claims backed by Primary or Secondary sources.

## Metadata
**Confidence breakdown:**
- Standard Stack: MEDIUM — package versions confirmed via PyPI but need future updates.
- Architecture: MEDIUM — based on `rough_plan.md` and standard pipeline practices.
- Pitfalls: MEDIUM — derived from LangChain/Typer docs and early warning signs.

**Research date:** 2026-03-28
**Valid until:** 2026-04-27 (30 days for stable stack)
