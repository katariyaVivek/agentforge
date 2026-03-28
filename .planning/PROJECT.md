# AgentForge

## What This Is

AgentForge is a CLI-first experience (web layer later) that ingests a rough, ambiguous project description and outputs a dynamically curated config bundle. It figures out which files are useful for that particular vibe coder’s context, then generates only those docs with the right level of detail.

## Core Value

Vibe coders start with exactly the config they need—no more guessing, no irrelevant templates, and no blank AGENT.md.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **CONFIG-01**: Intent parser derives the project type, scale, and artifacts to generate from a single freeform prompt.
- [ ] **CONFIG-02**: System tailors each output file (AGENT.md, STACK.md, etc.) to the project’s inferred need instead of using a fixed template.
- [ ] **CONFIG-03**: CLI pipeline runs intent parsing → focused search → compression → generation, surfacing the chosen manifest and signals about why each file exists.
- [ ] **CONFIG-04**: Tool reports the reasoning behind file choices and exposes flags like `--dry-run`, `--verbose`, and `--no-search` for observability.

### Out of Scope

- Large enterprise orchestration suites — AgentForge targets solo or small-team vibe coders, not full IT programs.
- Auto-deploying generated bundles directly to GitHub or CI — the MVP only produces the files for manual review.

## Context

- Vibe coders hit a blank `AGENT.md` and struggle to know what to write.
- Hard to decide which config docs a project needs; templates are either missing pieces or bloated with irrelevant files.
- Gemini-based AI stack will power intent understanding, with Tavily for searching best practices and Groq/OpenRouter as fallback models.
- Pipeline is explicit about why each file exists (always vs. conditional) to keep output explainable.

## Constraints

- **Latency**: Provide a bundle in under 30 seconds so it stays in the coder’s flow.
- **Model budget**: Prefer Gemini Flash; automatically fall back to Groq/OpenRouter only when quotas are hit.
- **Output format**: Markdown docs stored under `output/<project-slug>/`; minimal to zero manual polishing.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Intent parser decides file manifest | Avoid irrelevant boilerplate and ensure only necessary docs are generated | — Pending |
| Compression pass before generation | Keeps context signal-rich and model interaction fast | — Pending |

## Evolution

This document evolves at each phase transition and milestone. After each phase transition:

1. Move invalidated requirements to Out of Scope with reasoning.
2. Shift validated requirements into Validated with phase reference.
3. Add new requirements that surface during work to Active.
4. Log decisions triggered by new discoveries.
5. Confirm “What This Is” still matches the lived product.

After milestones, review all sections, reassess the core value, and refresh constraints with current context.

---
*Last updated: 2026-03-28 after initialization*
