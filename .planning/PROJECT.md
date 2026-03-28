# AgentForge

## What This Is

AgentForge is a CLI-first experience (web layer later) that ingests a rough, ambiguous project description and outputs a dynamically curated config bundle. It figures out which files are useful for that particular vibe coder's context, then generates only those docs with the right level of detail.

## Core Value

Vibe coders start with exactly the config they need—no more guessing, no irrelevant templates, and no blank AGENT.md.

## Requirements

### Validated

- ✓ **CONFIG-01**: Intent parser derives the project type, scale, and artifacts to generate from a single freeform prompt. — v1.0
- ✓ **CONFIG-02**: System tailors each output file (AGENT.md, STACK.md, etc.) to the project's inferred need instead of using a fixed template. — v1.0
- ✓ **CONFIG-03**: CLI pipeline runs intent parsing → focused search → compression → generation, surfacing the chosen manifest and signals about why each file exists. — v1.0
- ✓ **CONFIG-04**: Tool reports the reasoning behind file choices and exposes flags like `--dry-run`, `--verbose`, and `--no-search` for observability. — v1.0

### Active

- [ ] **AI-01**: Replace test-mode intent parser with real Gemini LLM that parses actual prompts
- [ ] **AI-02**: Wire up real Tavily search API (not mock) for web research
- [ ] **AI-03**: Connect actual LLM generation (not template fallback) for file content
- [ ] **AI-04**: Implement model fallback chain (Gemini → Groq → OpenRouter) with real API calls

### Out of Scope

- Large enterprise orchestration suites — AgentForge targets solo or small-team vibe coders, not full IT programs.
- Auto-deploying generated bundles directly to GitHub or CI — the MVP only produces the files for manual review.
- Mobile apps — CLI-first, web layer later.

## Context

- v1.0 shipped with test-mode only (GSD_TEST_MODE=1 returns hardcoded responses)
- Current pipeline: intent_parser → search → compressor → generator (all in place, need real APIs)
- Tavily API key needed for search
- Gemini/Groq/OpenRouter API keys needed for generation

## Constraints

- **Latency**: Provide a bundle in under 30 seconds so it stays in the coder's flow.
- **Model budget**: Prefer Gemini Flash; automatically fall back to Groq/OpenRouter only when quotas are hit.
- **Output format**: Markdown docs stored under `output/<project-slug>/`; minimal to zero manual polishing.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Intent parser decides file manifest | Avoid irrelevant boilerplate and ensure only necessary docs are generated | ✓ Good - Working in test mode |
| Compression pass before generation | Keeps context signal-rich and model interaction fast | ✓ Good - Working in test mode |
| Model fallback chain | Resilience against quota/availability issues | — Pending - Needs real API keys |

## Evolution

This document evolves at each phase transition and milestone. After each phase transition:

1. Move invalidated requirements to Out of Scope with reasoning.
2. Shift validated requirements into Validated with phase reference.
3. Add new requirements that surface during work to Active.
4. Log decisions triggered by new discoveries.
5. Confirm "What This Is" still matches the lived product.

After milestones, review all sections, reassess the core value, and refresh constraints with current context.

---
*Last updated: 2026-03-29 after v1.0 milestone, starting v1.1 (Real AI Generation)*
