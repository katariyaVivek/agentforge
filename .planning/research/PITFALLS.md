# Domain Pitfalls

**Domain:** AI-powered CLI for dynamic config generation  
**Researched:** 2026-03-28

## Critical Pitfalls

Mistakes that cause rewrites or major issues.

### Pitfall 1: Intent Parser Misconfiguration
**What goes wrong:** The intent parser produces an inaccurate file manifest, leading to missing or irrelevant config files.
**Why it happens:** Ambiguous or poorly structured user descriptions and insufficient validation logic.
**Consequences:** Key configuration files omitted or unnecessary files generated, causing project scaffolds to fail or require manual correction.
**Prevention (Phase 1 - Intent Parsing):** Implement schema validation for parser output, require dry-run confirmation, and build a suite of edge-case tests before generation.
**Detection:** Frequent user manual edits to manifest; high usage of dry-run flag; discrepancies between user expectation and generated manifest in verbose logs.

### Pitfall 2: Search Layer Failures and Hallucinations
**What goes wrong:** Search queries return irrelevant or outdated documentation, or the system hallucinates based on weak grounding.
**Why it happens:** Over-reliance on a single search provider, lack of query refinement, and poor source filtering.
**Consequences:** Generator uses incorrect patterns or conventions, producing suboptimal or incorrect config structures.
**Prevention (Phase 2 - Search Layer):** Implement fallback strategies, source whitelisting, query optimization, and post-search relevance filtering. Maintain a cache of vetted best-practice templates.
**Detection:** Low relevance scores in compression summaries; repeated fallback warnings in logs; user complaints about poor-quality patterns.

### Pitfall 3: Over-Compression Losing Critical Context
**What goes wrong:** Summarization strips out essential details like version constraints or platform-specific instructions.
**Why it happens:** Aggressive compression heuristics prioritize brevity over retaining key metadata.
**Consequences:** Generated files lack required version pins, flags, or platform guidance, leading to build failures.
**Prevention (Phase 3 - Compression):** Whitelist and preserve schema-like information (versions, flags, code snippets) during summarization. Monitor and enforce a minimum retention of key metadata.
**Detection:** Missing version tables in STACK.md; build errors referencing unknown dependencies or flags.

### Pitfall 4: Context Window Overrun and Inter-File Inconsistency
**What goes wrong:** Generator exceeds model context window or generates files in isolation, causing inconsistencies (e.g., mismatched references between STRUCTURE.md and SCHEMA.md).
**Why it happens:** Splitting generation into separate calls without passing prior outputs and hitting token limits.
**Consequences:** Contradictory instructions across files, manual reconciliation required, and breakdown of the dynamic file system promise.
**Prevention (Phase 4 - Generation):** Bundle manifest and compressed sources in a single context when possible, and feed earlier outputs into subsequent calls. Track token usage and adjust chunking strategy.
**Detection:** Context window warnings in logs; version or reference mismatches across generated files.

### Pitfall 5: Model Quota Exhaustion and Abrupt Failover
**What goes wrong:** Primary model exceeds quota mid-generation, fallback model yields style or accuracy drift.
**Why it happens:** Lack of pre-flight quota checks and inconsistent orchestration logic.
**Consequences:** Mixed tone/style across files, unexpected failures requiring manual retry or edit.
**Prevention (Phase 4 - Generation):** Perform pre-flight quota checks, estimate token usage for the generation batch, and enforce a unified style prompt across model switches. Surface failover events prominently in verbose logs.
**Detection:** Logs indicating quota exceeded or fallback usage; inconsistent document style flagged by markdown linting.

## Moderate Pitfalls

### Silent Failures in CLI Flags
**What goes wrong:** `--no-search`, `--dry-run`, or `--verbose` flags behave unpredictably or silently fail.
**Prevention (Phase 5 - CLI Integration):** Add explicit user feedback, clear exit codes for each flag branch, and integration tests validating flag behavior.

### Inadequate Error Handling on Network/API Errors
**What goes wrong:** Unhandled Tavily or model API timeouts lead to crashes or hanging CLI.
**Prevention (Phase 5 - CLI Integration):** Wrap all external calls with retry/backoff logic and clear, user-friendly error messages.

### Environment Variable Misconfiguration
**What goes wrong:** Missing or invalid API keys cause silent fallback to offline mode or obscure errors.
**Prevention (Phase 5 - CLI Integration):** Validate `.env` at startup, fail fast with descriptive errors for missing or malformed credentials.

## Minor Pitfalls

### Markdown Formatting Inconsistencies
**What goes wrong:** Generated files have inconsistent headings, code fences, or list formatting.
**Prevention (Phase 4 - Generation):** Enforce a markdown linting pass (e.g., markdownlint) after generation.

### File Permission and Overwrite Issues
**What goes wrong:** Existing project directories get overwritten or file permissions block writing.
**Prevention (Phase 5 - CLI Integration):** Implement safe-write practices: check for existing files, prompt or backup, and respect OS file permissions.

## Phase-Specific Warnings

| Phase Topic         | Likely Pitfall                                   | Mitigation                                   |
|---------------------|---------------------------------------------------|----------------------------------------------|
| Intent Parsing      | Misinterpreting user intent                       | Schema validation, dry-run confirmation      |
| Search Layer        | Low relevance or hallucinations                   | Source whitelisting, fallback caches         |
| Compression         | Stripping version and code snippet details        | Whitelist metadata, enforce retention        |
| Generation          | Token overruns and inter-file inconsistencies      | Single-context generation, track token usage |
| CLI Integration     | Silent flag failures and env misconfigs            | Exit codes, startup validation, verbose logs |
| Model Orchestration | Quota exhaustion leading to style drift            | Pre-flight quota checks, unified style prompt|

## Sources

- `rough_plan.md` (project pipeline and core rules)
- Internal team bug reports and post-mortems on config generator tools
