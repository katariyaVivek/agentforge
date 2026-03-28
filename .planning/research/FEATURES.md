# Feature Landscape

**Domain:** AI-driven config generation CLI (AgentForge)
**Researched:** 2026-03-28

## Table Stakes
Features users expect. Missing these = product feels incomplete.

| Feature                         | Why Expected                                                            | Complexity | Notes                                                                                  |
|---------------------------------|--------------------------------------------------------------------------|------------|----------------------------------------------------------------------------------------|
| `generate` CLI command          | Core entrypoint to produce config bundle from a one-sentence description | Low        | Basic command setup; foundation of UX                                                  |
| Core files (`AGENT.md`, `RULES.md`, `STRUCTURE.md`) | Essential project overview scaffold                                      | Low        | Always produced, minimal domain knowledge required                                     |
| Intent parser                   | Extract project metadata & decide file manifest                          | High       | Central to determining dynamic output; requires robust prompt engineering & validation  |
| Search integration (Tavily)     | Gather best-practice docs to ground config generation                    | Medium     | Improves quality; network dependency; can be disabled (`--no-search`)                  |
| Compression pass                | Summarize sources to ~400 words of signal                                 | Medium     | Reduces noise for LLM; important for context window management                         |
| Per-file generation             | Generate each file tailored to manifest                                   | Medium     | Iterative calls to LLM; dependent on prior pipeline steps                               |
| File catalog (`catalog.py`)     | Registry of available file types & generation instructions                | Medium     | Enables dynamic file library; single source of truth                                   |
| Model fallback (Gemini → Groq → OpenRouter) | Resilient LLM availability                                               | Medium     | Automatic quota/e2e failure handling                                                  |
| Output writing & flags (`--out`, `--verbose`, `--dry-run`) | UX controls & diagnostics                                                 | Low        | Standard CLI flags for directory choice & visibility                                   |
| Graceful failure handling       | Never crash silently; fallback when search or model fails                 | Medium     | Improves reliability; required for production readiness                                |

## Differentiators
Features that set AgentForge apart. Not expected in generic config tools.

| Feature                                 | Value Proposition                                                      | Complexity | Notes                                                                                   |
|-----------------------------------------|------------------------------------------------------------------------|------------|-----------------------------------------------------------------------------------------|
| Dynamic file manifest selection         | AI decides exactly which files a project needs                          | High       | Core product insight; replaces fixed templates                                          |
| Targeted search query generation        | Intent-driven search queries for best-practice retrieval                | High       | Precision improves config relevance                                                      |
| Expandable conditional file library     | Add new file types as patterns emerge                                   | Low        | Future-proof file generation catalog                                                    |
| Interdependent context across files     | Pass prior outputs (STACK→STRUCTURE→SCHEMA) in a single LLM session      | High       | Ensures consistency across generated documents                                         |
| Verbose manifest reasoning              | Explain why each file was chosen                                         | Medium     | Improves transparency, trust, & debuggability                                           |
| Zero-edit output readiness              | Drop bundle into agents/Cursor/Windsurf without manual edits             | Low        | Reduces friction for users                                                               |

## Anti-Features
Features to explicitly NOT build.

| Anti-Feature                      | Why Avoid                                                           | What to Do Instead                                                               |
|----------------------------------|---------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Fixed template bundles           | Rigid; generates irrelevant or missing files                         | Use AI-driven manifest to tailor output                                          |
| Manual file manifest overrides   | Undermines dynamic intent parser; adds UX friction                   | Surface manifest via `--verbose`, but don’t require user selection                |
| Raw HTML in context              | Noisy; wastes context window                                       | Always compress to signal-rich summaries                                         |
| Manual LLM provider switching     | Frustrates users; error-prone                                      | Automate model fallback in pipeline                                              |
| Interactive wizards for file types | Breaks CLI flow; slows scripting                                    | Rely on intent parser and dry-run UX to preview without interactive prompts       |

## Feature Dependencies
```text
Intent Parser → Dynamic Manifest → Search Layer → Compression → Generation → Output Writing
         ↳ File Catalog
Model Fallback ↳ Generation
CLI Flags (--no-search, --dry-run, --verbose) ↳ modifies Search/Generation/Output
``` 

## MVP Recommendation
Prioritize foundational table stakes before differentiators:
1. Intent parser & dynamic manifest output (High impact, core differentiation)
2. Search integration + compression pipeline (Medium impact, quality baseline)
3. Per-file generation & file catalog (Medium impact, core UX)
4. CLI flags (`--out`, `--verbose`, `--dry-run`) & output writing (Low impact, UX polish)
5. Graceful failure & model fallback (Medium impact, production readiness)

Defer advanced interdependent context splitting and conditional library expansion until post-MVP due to high complexity.

## Sources
- rough_plan.md (project design brief)
