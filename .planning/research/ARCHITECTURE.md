# Architecture Research

**Domain:** LLM-driven dynamic config CLI
**Researched:** 2026-03-28
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
┌───────────────────────────────────────────────────────────┐
│                  CLI Interface                           │
├───────────────────────────────────────────────────────────┤
│  ┌───────────┐   ┌───────────┐   ┌───────────┐             │
│  │Intent     │→  │Search     │→  │Compression│             │
│  │Parser     │   │Layer      │   │Layer      │             │
│  └────┬──────┘   └────┬──────┘   └────┬──────┘             │
│       │               │               │                   │
│       ↓               ↓               ↓                   │
│   ┌────────────────────────────────────────┐              │
│   │         Generation Layer              │              │
│   └────┬──────────────────────────────────┘              │
│        ↓                                             │
│   ┌──────────┐   ┌─────────────┐                        │
│   │Catalog   │   │Output       │                        │
│   │Registry  │   │Manager      │                        │
│   └──────────┘   └─────────────┘                        │
└───────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component        | Responsibility                                                              | Typical Implementation                         |
|------------------|-----------------------------------------------------------------------------|-------------------------------------------------|
| CLI Interface    | Parse commands and flags; orchestrate end-to-end pipeline invocation         | Typer app in `main.py`                          |
| Intent Parser    | Extract project intent and decide dynamic file manifest                      | `pipeline/intent_parser.py` + Gemini prompts    |
| Search Layer     | Generate targeted queries and fetch best-practice docs                       | `pipeline/search.py` using Tavily API           |
| Compression      | Summarize and distill retrieved documents into signal-rich contexts           | `pipeline/compressor.py` + compression prompt    |
| Generation Layer | Generate project-specific config files based on manifest and compressed data  | `pipeline/generator.py` + generate prompt       |
| Catalog Registry | Central registry of all possible output file definitions and generation logic | `file_definitions/catalog.py`                   |
| Output Manager   | Write generated files to disk and manage output directory structure           | Filesystem operations in generator or FS module |
| Prompts Store    | Hold system prompt templates for each pipeline stage                          | Files in `prompts/`                              |
| Templates        | Reference examples for generated bundles                                      | Files under `templates/examples/`                |

## Recommended Project Structure

```
src/
├── main.py                    # CLI entrypoint (Typer)
├── pipeline/
│   ├── intent_parser.py       # Step 1: intent extraction + manifest decision
│   ├── search.py              # Step 2: generate queries + fetch docs
│   ├── compressor.py          # Step 3: summarize sources
│   └── generator.py           # Step 4: generate files
├── prompts/
│   ├── intent.md              # System prompt for intent parsing
│   ├── compress.md            # System prompt for compression
│   └── generate.md            # System prompt for file generation
├── file_definitions/
│   └── catalog.py             # Registry of output file types + metadata
├── templates/
│   └── examples/              # Example bundles for reference/testing
├── output/                    # Generated configs (gitignored)
├── .env                       # Local API keys
├── .env.example               # Example keys file
├── requirements.txt           # Python dependencies
└── README.md                  # Project overview & quickstart
```

### Structure Rationale

- **pipeline/** groups atomic stages of the processing pipeline for clarity and testability.
- **prompts/** isolates LLM system prompts, enabling easy updates and reuse.
- **file_definitions/** centralizes file metadata, allowing dynamic manifest decisions.
- **templates/examples/** provides live samples to validate generator output.
- **output/** cleanly separates generated artifacts from source code.
- **main.py** serves as the single orchestration layer connecting CLI to pipeline.

## Architectural Patterns

### Pattern 1: Pipeline (Pipes & Filters)
**What:** Staged processing where each component transforms input for the next stage.
**When to use:** Clear separation of concerns in data transformations.
**Trade-offs:** Easy to extend/graft new stages; adds indirection.
**Example:**
```python
def run_pipeline(input_text):
    manifest = intent_parser.parse(input_text)
    docs = search.fetch(manifest['search_queries'])
    compressed = compressor.compress(docs)
    return generator.generate(manifest, compressed)
```

### Pattern 2: Registry Pattern for File Definitions
**What:** Central catalog drives what files can be generated and how.
**When to use:** Dynamic file lists based on project intent.
**Trade-offs:** Increases flexibility; requires disciplined catalog updates.
**Example:**
```python
FILE_CATALOG = {
    'AGENT.md': {'template': 'agent.md.j2', 'condition': lambda ctx: True},
    'STACK.md': {'template': 'stack.md.j2', 'condition': has_stack_hints},
    # ...
}
```

### Pattern 3: Model Fallback Circuit-Breaker
**What:** Automatically switch LLM providers on quota/error.
**When to use:** Maintain reliability across provider limits.
**Trade-offs:** Higher complexity; unpredictable cost profiles across models.
**Example:**
```python
for model in ['gemini', 'groq', 'openrouter']:
    try:
        return generate_with(model, prompt)
    except QuotaExceededError:
        continue
raise RuntimeError("All models failed")
```

## Data Flow

### Request Flow
```
User runs CLI command
    ↓
CLI Interface → Intent Parser → Search Layer → Compression Layer → Generation Layer → Output Manager → File System
    ↓                             ↓              ↓              ↓              ↓             ↓
  Arguments                   Queries         Summaries      Config objects   Write files   Directory
```

### State Management
```
pipeline_context = {
  'manifest': dict,
  'raw_docs': list,
  'compressed_docs': list,
  'generated_files': dict
}
```

### Key Data Flows
1. **Intent Extraction:** User input → structured manifest JSON.
2. **Document Processing:** manifest.queries → remote docs → compressed context.
3. **Config Generation:** manifest + compressed context → tailored file contents.
4. **Artifact Output:** generated contents → filesystem under `output/<project>/`.

## Build Order

1. **File Catalog** – define file types and generation metadata in `catalog.py`.
2. **Intent Parser** – implement manifest decision logic and validate with varied inputs.
3. **CLI Skeleton** – wire Typer commands and flags (`--verbose`, `--dry-run`).
4. **Search Layer** – integrate Tavily API and test query generation.
5. **Compression Stage** – build summarization component to distill docs.
6. **Generation Stage** – tie compressed sources and templates into file generator.
7. **Output Manager** – implement filesystem writing, directory scaffolding.
8. **Model Fallback Logic** – add circuit-breaker for LLM provider switching.
9. **End-to-End Integration** – connect all stages, add logging and error handling.

## Scaling Considerations

| Scale         | Architecture Adjustments                                 |
|---------------|----------------------------------------------------------|
| 1–10 projects | Monolithic CLI; sequential pipeline is sufficient        |
| 10–100 projects | Enable parallel search/compress for faster throughput   |
| 100+ projects | Extract processing into async worker pool or server tier |

### Scaling Priorities
1. **Search throttling** – handle rate limits from Tavily.
2. **Parallel compression** – batch summarization across docs.
3. **Cache compressed contexts** – avoid redundant fetch/compress cycles.

## Anti-Patterns

### Anti-Pattern 1: Hardcoded File List
**What people do:** Use fixed templates instead of dynamic registry.
**Why it's wrong:** Loses product flexibility; unnecessary files added/omitted.
**Do this instead:** Drive file manifest from `catalog.py` based on intent.

### Anti-Pattern 2: Monolithic Prompt for All Files
**What people do:** Dump entire prompt+context into one generation call.
**Why it's wrong:** Context window waste; interdependent prompts get noisy.
**Do this instead:** Generate per-file with focused prompt and context slice.

## Integration Points

### External Services
| Service    | Integration Pattern       | Notes                       |
|------------|---------------------------|-----------------------------|
| Tavily     | REST API calls            | Handle pagination & errors  |
| Gemini     | gRPC/HTTP API             | Primary LLM, watch quotas   |
| Groq       | HTTP with retry on quota  | Fallback provider           |
| OpenRouter | HTTP backup provider      | Last-resort for generation  |

### Internal Boundaries
| Boundary                       | Communication      | Notes                             |
|--------------------------------|--------------------|-----------------------------------|
| CLI ↔ Pipeline                 | direct function calls | Minimal conversion           |
| Pipeline ↔ Catalog Registry    | in-memory registry | Single source of truth             |
| Pipeline ↔ Prompts Store       | file reads         | Prompts version-controlled         |
| Generation ↔ Output Manager    | Python objects     | Serialize before write             |

## Sources
- `rough_plan.md` — initial project pipeline & structure (only source)

---
*Architecture research for: LLM-driven dynamic config CLI*
*Researched: 2026-03-28*
