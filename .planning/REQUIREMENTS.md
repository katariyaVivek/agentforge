# Requirements: AgentForge v1.1

**Defined:** 2026-03-29
**Core Value:** Vibe coders start with exactly the config they need—no more guessing, no irrelevant templates, and no blank AGENT.md.

## v1.1 Requirements

Requirements for v1.1: Real AI Generation. Each aligns to research-backed phases.

### AI Integration

- [ ] **AI-01**: Replace test-mode intent parser with real Gemini LLM that parses actual prompts and returns structured manifest
- [ ] **AI-02**: Wire up real Tavily search API for web research (not mock)
- [ ] **AI-03**: Connect actual LLM generation for file content (not template fallback)
- [ ] **AI-04**: Implement model fallback chain (Gemini → Groq → OpenRouter) with real API calls and graceful degradation

### Out of Scope

| Feature | Reason |
|---------|--------|
| Web UI | CLI-first, defer to future milestone |
| Auto-deploy to GitHub | Manual review of generated files first |
| Custom templates | Default templates sufficient for v1.1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AI-01 | Phase 5: Intent Parser LLM | Pending |
| AI-02 | Phase 6: Search Integration | Pending |
| AI-03 | Phase 7: Generator LLM | Pending |
| AI-04 | Phase 8: Fallback Chain | Pending |

---
*Requirements defined: 2026-03-29*
