# Requirements: AgentForge

**Defined:** 2026-03-28
**Core Value:** Vibe coders start with exactly the config they need—no more guessing, no irrelevant templates, no blank AGENT.md.

## v1 Requirements

Requirements for the initial CLI MVP. Each aligns to a research-backed phase.

### Pipeline

- [ ] **PIPE-01**: Intent parser extracts project metadata (type, domain, scale) and returns a structured manifest that lists the files to generate along with the rationale for each choice.
- [ ] **PIPE-02**: Search layer turns the manifest into targeted Tavily queries, falls back cleanly when `--no-search` is specified, and buffers responses for compression.
- [ ] **PIPE-03**: Compression stage summarizes retrieved sources to ~400 words per doc while whitelisting version/flag metadata so downstream generation keeps critical constraints intact.
- [ ] **GEN-01**: Generator consumes the manifest plus compressed context to create each file (AGENT.md, RULES.md, STRUCTURE.md plus conditionals) and writes them under `output/<project-slug>/` in a consistent Markdown style.

### Catalog & Context

- [ ] **CAT-01**: Central file catalog (`file_definitions/catalog.py`) drives available file types, their generation prompts, and the conditions that unlock them.
- [ ] **CAT-02**: Generation always produces the core docs (AGENT.md, RULES.md, STRUCTURE.md) while additional files only appear when the catalog conditions signal they are needed.

### CLI Experience

- [ ] **CLI-01**: `agentforge generate <description>` orchestrates the pipeline, exposes `--out`, `--verbose`, `--dry-run`, and `--no-search` flags, and reports manifest reasoning when `--verbose` is used.
- [ ] **CLI-02**: Provide clear, user-friendly logging and exit codes so `--dry-run` previews, `--no-search` runs, and verbose manifest decisions never fail silently.
- [ ] **CLI-03**: Implement graceful failure handling around search/model layers, surfacing errors and ensuring the CLI never crashes without guidance.

### Reliability

- [ ] **REL-01**: Model fallback circuit (Gemini → Groq → OpenRouter) makes generation resilient to quota or availability issues while preserving a unified style prompt.

## v2 Requirements

Deferred differentiators that unlock post-MVP polish.

### Phase 5 Enhancements

- **CTX-01**: Pass earlier generated outputs into subsequent file generations so cross-document references remain consistent and context windows stay bounded.
- **LIB-01**: Allow the catalog to expand with new conditional file types and triggers without editing core generation logic (plug-in catalog entries).

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fixed template bundles | Undermines the AI-driven manifest; produces irrelevant files.
| Manual file manifest overrides | Adds UX friction and bypasses the intent parser’s judgment.
| Interactive wizards for file selection | Breaks the CLI flow; prefer `--verbose`/`--dry-run` previews.
| Auto-pushing generated bundles to GitHub/CI | MVP focuses on local, inspectable artifacts.

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PIPE-01 | Phase 1: Intent Parsing & Dynamic Manifest | Pending |
| PIPE-02 | Phase 2: Search Integration & Compression | Pending |
| PIPE-03 | Phase 2: Search Integration & Compression | Pending |
| GEN-01 | Phase 3: Generation & File Catalog | Pending |
| CAT-01 | Phase 3: Generation & File Catalog | Pending |
| CAT-02 | Phase 3: Generation & File Catalog | Pending |
| CLI-01 | Phase 4: CLI Integration & Output Management | Pending |
| CLI-02 | Phase 4: CLI Integration & Output Management | Pending |
| CLI-03 | Phase 4: CLI Integration & Output Management | Pending |
| REL-01 | Phase 3: Generation & File Catalog | Pending |

**Coverage:**
- v1 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-28*
*Last updated: 2026-03-28 after roadmap creation*
