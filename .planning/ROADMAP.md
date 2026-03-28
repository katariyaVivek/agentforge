# Roadmap: AgentForge

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-03-28)
- 🚧 **v1.1 Real AI** — Phases 5-8 (in progress)

## Phases

### Phase 5: Intent Parser LLM
**Goal**: Replace test-mode intent parser with real Gemini LLM that parses actual prompts
**Depends on**: v1.0
**Requirements**: AI-01
**Success Criteria** (what must be TRUE):
1. Intent parser calls actual Gemini API with prompt
2. Returns structured IntentManifest with project_type, domain, scale, files_to_generate
3. Handles API errors gracefully with user-friendly messages

### Phase 6: Search Integration
**Goal**: Wire up real Tavily search API for web research
**Depends on**: Phase 5
**Requirements**: AI-02
**Success Criteria** (what must be TRUE):
1. TavilyClient.search() called with manifest-derived queries
2. Returns SearchResult objects with title, url, content
3. Handles missing API key gracefully

### Phase 7: Generator LLM
**Goal**: Connect actual LLM generation for file content
**Depends on**: Phase 6
**Requirements**: AI-03
**Success Criteria** (what must be TRUE):
1. Generator calls LLM with Jinja2 template + context
2. Returns generated file content strings
3. Writes to output/<project-slug>/ directory

### Phase 8: Fallback Chain
**Implement**: Model fallback chain (Gemini → Groq → OpenRouter)
**Depends on**: Phase 7
**Requirements**: AI-04
**Success Criteria** (what must be TRUE):
1. Primary model tried first (Gemini)
2. On failure, fallback to Groq
3. On Groq failure, fallback to OpenRouter
4. Unified prompt ensures consistent output format

## Progress

| Phase             | Milestone | Plans Complete | Status      | Completed  |
| ----------------- | --------- | -------------- | ----------- | ---------- |
| 1. Intent Parsing | v1.0      | 1/1            | Complete    | 2026-03-28 |
| 2. Search         | v1.0      | 1/1            | Complete    | 2026-03-28 |
| 3. Generation     | v1.0      | 1/1            | Complete    | 2026-03-28 |
| 4. CLI Polish     | v1.0      | 1/1            | Complete    | 2026-03-28 |
| 5. Intent LLM     | v1.1      | 0/1            | Not started | -          |
| 6. Search API     | v1.1      | 0/1            | Not started | -          |
| 7. Generator LLM | v1.1      | 0/1            | Not started | -          |
| 8. Fallback Chain | v1.1      | 0/1            | Not started | -          |
