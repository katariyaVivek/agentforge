# AgentForge Research Summary

## Executive Summary

AgentForge is an AI-driven CLI tool designed to generate end-to-end project configuration scaffolds from a single sentence description. By combining intent parsing, best-practice search grounding, context compression, and per-file LLM-driven generation, the recommended approach delivers dynamic, context-rich project bundles with minimal manual intervention. A modular pipeline architecture driven by Python, Typer, and LangChain deep agents ensures clear stage boundaries and testability, while a central registry and template engine provide extensibility and consistency.

This research recommends establishing the core pipeline stages—intent parsing & manifest generation, search integration & compression, file-specific generation, and robust CLI integration—prior to adding advanced interdependent context flows or conditional libraries. Key technologies include Python 3.14, Typer for a modern CLI, LangChain for durable LLM orchestration, Tavily for real-time search grounding, HTTPX for async networking, and Jinja2/Pydantic for templating and data validation.

Major risks include inaccurate intent manifests, search hallucinations, over-compression losing critical metadata, context window overruns causing inter-file inconsistencies, and model quota failovers leading to style drift. Mitigations span schema validation and dry-run confirmation, query refinement and caching, metadata whitelists during compression, unified context bundling, and pre-flight quota checks paired with unified style prompts.

## Key Findings

### Stack
- **Python 3.14.0**: Leverage latest interpreter features (PEP 750, deferred annotations) and AI ecosystem support.
- **Typer 0.24.1**: Modern, type-hinted CLI framework with auto-completion and built-in help.
- **LangChain 1.2.13**: Deep agent orchestration for durable, multistep LLM workflows.
- **Tavily Python SDK 1.1.0**: Real‑time web search grounding to improve output accuracy.
- **HTTPX 0.28.1**: Async-first HTTP client with HTTP/2 support.
- **python-dotenv 1.2.2**: 12‑factor .env management for API keys and config.
- **Pydantic 2.12.5**: Fast, explicit schema validation for pipeline data.
- **Jinja2 3.1.6**: Extensible templating for dynamic code and file scaffolding.
- Supporting libs: rich for console styling, shellingham/click for CLI runtime, langchain-deepagents for advanced agent patterns.
- Dev tools: pre-commit (Black, isort, flake8, mypy), Poetry for reproducible packaging.
- Avoid legacy: argparse, requests, Pydantic v1.x, typer-slim; prefer async, modern stacks.

### Features
#### Table Stakes
- `generate` command, core files (AGENT.md, RULES.md, STRUCTURE.md), intent parser, Tavily search integration, compression pass, per-file generation, file catalog, model fallback, CLI flags (`--out`, `--verbose`, `--dry-run`), graceful failure.

#### Differentiators
- AI-driven dynamic manifests, targeted search query generation, expandable file catalog, interdependent cross-file context, verbose manifest reasoning, zero-edit output readiness.

#### Anti-Features
- No fixed template bundles, manual manifest overrides, raw HTML in context, manual LLM switching, interactive wizards.

#### MVP Prioritization
1. Intent parser & dynamic manifest  
2. Search integration & compression  
3. Per-file generation & file catalog  
4. CLI flags & output writing  
5. Graceful failure & model fallback  
(Advanced interdependent context and conditional library expansion deferred post-MVP)

### Architecture
- **Components**: CLI Interface, Intent Parser, Search Layer, Compression Layer, Generation Layer, Catalog Registry, Output Manager, Prompts Store, Templates.
- **Patterns**: Pipeline (pipes & filters), Registry for file definitions, Circuit-breaker model fallback.
- **Project layout**: `src/main.py`, `pipeline/`, `prompts/`, `file_definitions/catalog.py`, `templates/examples/`, `output/`.
- **Build order**: Catalog → Intent Parser → CLI skeleton → Search → Compression → Generation → Output Manager → Model fallback → E2E integration.
- **Scaling**: Monolithic for 1–10 projects; parallel search/compress for 10–100; async workers for 100+. Prioritize search throttling, parallel compression, caching.

### Pitfalls
- **Intent Parser Misconfiguration**: Schema validation, dry-run tests.  
- **Search Hallucinations**: Fallbacks, whitelists, relevance filtering, caching.  
- **Over-Compression**: Metadata whitelist, retention enforcement.  
- **Context Window Overrun**: Bundle prior outputs, token tracking, chunking strategy.  
- **Model Quota Exhaustion**: Pre-flight quota checks, unified style prompts, verbose failover logs.  
- Additional moderate/minor issues: CLI flag behavior, network errors, env misconfigs, markdown linting, safe-write practices.

## Implications for Roadmap

### Phase 1: Intent Parsing & Dynamic Manifest
**Rationale:** Foundation for all downstream stages; core differentiation.  
**Deliverables:** Schema-driven parser, manifest dry-run, edge-case tests.  
**Pitfalls to Avoid:** Misconfigured intent parser.

### Phase 2: Search Integration & Compression
**Rationale:** Ground outputs in vetted best practices and signal-rich context.  
**Deliverables:** Tavily integration, query optimization, compression with metadata whitelist.  
**Pitfalls to Avoid:** Hallucinations, over-compression.

### Phase 3: Generation & File Catalog
**Rationale:** Drive per-file scaffolding with registry pattern and model fallback.  
**Deliverables:** File catalog registry, generation templates, context bundling, fallback circuit.  
**Pitfalls to Avoid:** Context inconsistencies, quota failover drift.

### Phase 4: CLI Integration & Output Management
**Rationale:** Complete UX flow with flags, error handling, safe writes.  
**Deliverables:** Typer CLI commands, verbose/dry-run flags, env validation, safe-write logic.  
**Pitfalls to Avoid:** Silent failures, env misconfigs, permission issues.

### Phase 5: Scalability & Differentiators (Post-MVP)
**Rationale:** Optimize performance and unlock advanced features.  
**Deliverables:** Parallel search/compress, caching layer, interdependent context, expandable library.  
**Pitfalls to Avoid:** Complex orchestration errors.

#### Research Flags
- **Needs further research:** Phase 2 search relevance metrics; Phase 3 context window strategies; Phase 5 scaling concurrency models.  
- **Standard patterns:** Phase 1 schema validation; Phase 4 CLI integration best practices.

## Confidence Assessment
| Area         | Confidence    | Notes                                           |
|--------------|---------------|-------------------------------------------------|
| Stack        | Medium-High   | Multiple high-quality docs and official sources |
| Features     | Medium        | Based on project brief; lacks user validation   |
| Architecture | Medium        | Derived from initial plan; limited external refs|
| Pitfalls     | Medium        | Informed by internal post-mortems and logs      |

### Gaps to Address
- User interviews to validate feature prioritization.  
- Real-world performance data for compression and scaling.  
- Token cost estimations and quota planning strategies.

## Sources
- .planning/research/STACK.md  
- .planning/research/FEATURES.md  
- .planning/research/ARCHITECTURE.md  
- .planning/research/PITFALLS.md
