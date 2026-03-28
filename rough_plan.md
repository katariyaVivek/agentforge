# rough_plan.md — Viveka

## What Is This?

AgentForge is a CLI tool (web app later) that takes a rough project description — even a vague, poorly written one — and generates a **dynamically decided, project-appropriate config bundle** for vibe coders.

The key insight: **the tool decides which files to generate**, not the user. A simple CLI tool needs different docs than a SaaS product. A solo project needs different structure than a team project. AgentForge figures that out automatically and generates exactly what's needed — no more, no less.

---

## The Core Problem

Every vibe coder hits the same wall at project start: staring at a blank `AGENT.md` with no idea where to begin. Writing these config files from scratch is slow, inconsistent, and easy to get wrong. Most people either skip them or write generic low-quality ones — and then their coding agent underperforms because of it.

The second problem: even people who try to write these files don't know *which* files their project actually needs. They copy a template and end up with irrelevant files and missing critical ones.

---

## How It Works (Pipeline)

```
User Input (rough description)
        ↓
1. INTENT PARSER
   - Extract: project type, domain, goals, scale, team size, complexity
   - Decide: which config files this specific project needs + why
   - Output: structured JSON with file manifest + metadata
   - Model: Gemini 2.0 Flash
        ↓
2. SEARCH LAYER
   - Generate targeted search queries based on parsed intent
   - Fetch best-practice docs, READMEs, community configs relevant to this project
   - API: Tavily (free tier, AI-optimized, 1000/mo)
        ↓
3. COMPRESSION
   - Summarize each retrieved doc to ~400 words of pure signal
   - Strip noise, keep patterns, conventions, architecture decisions
        ↓
4. GENERATION
   - Use compressed sources as grounding context
   - Generate exactly the files decided in step 1 — no fixed template
   - Each file is tailored to the specific project, not generic
   - Model: Gemini 2.0 Flash (primary) → Groq (fallback) → OpenRouter (backup)
        ↓
Output: Custom config bundle written to output/<project-slug>/
```

---

## The Dynamic File System (Core Feature)

The intent parser decides which files to generate per project. Below is the full library of possible output files — the parser picks the right subset:

### Always Generated
| File | Purpose |
|---|---|
| `AGENT.md` | Project overview, goals, target user, constraints, non-goals |
| `RULES.md` | Coding conventions, what to always/never do, commit style |
| `STRUCTURE.md` | Folder/file scaffold with purpose annotations |

### Conditionally Generated (intent parser decides)
| File | When to generate |
|---|---|
| `STACK.md` | Any project with real tech decisions to make |
| `ROADMAP.md` | Multi-feature products, anything with phases or milestones |
| `REQUIREMENTS.md` | Products with distinct functional/non-functional requirements |
| `SCHEMA.md` | Database-heavy projects, anything with persistent data models |
| `API.md` | Projects exposing or consuming APIs |
| `AUTH.md` | Any project with user login, roles, or permissions |
| `PAYMENTS.md` | SaaS, marketplaces, anything with billing |
| `COMMANDS.md` | CLI tools — documents all commands, flags, usage |
| `ENV.md` | Projects with complex environment configs or deployment targets |
| `TESTING.md` | Projects where test strategy needs to be explicit |
| `SECURITY.md` | Apps handling sensitive data, auth-heavy, or public-facing |
| `DEPLOYMENT.md` | Projects with non-trivial hosting/CI/CD needs |
| `SKILLS.md` | When the agent needs specific domain knowledge spelled out |
| `INTEGRATIONS.md` | Projects connecting to 3rd party services |
| `UI_PATTERNS.md` | Frontend-heavy projects with design system needs |

> This list grows over time. New file types can be added as patterns emerge from usage.

---

## Intent Parser Output Format

The intent parser must return structured JSON like this:

```json
{
  "project_name": "DevPulse",
  "project_type": "saas web app",
  "domain": "developer productivity",
  "complexity": "medium",
  "scale": "solo",
  "stack_hints": ["next.js", "postgres", "stripe"],
  "search_queries": [
    "nextjs saas boilerplate best practices 2024",
    "postgres schema design multi-tenant saas",
    "stripe subscription integration nextjs"
  ],
  "files_to_generate": [
    { "name": "AGENT.md", "reason": "always required" },
    { "name": "RULES.md", "reason": "always required" },
    { "name": "STRUCTURE.md", "reason": "always required" },
    { "name": "STACK.md", "reason": "multiple non-trivial tech decisions" },
    { "name": "SCHEMA.md", "reason": "postgres with multi-tenant data model" },
    { "name": "AUTH.md", "reason": "user accounts and role-based access" },
    { "name": "PAYMENTS.md", "reason": "stripe subscription billing" },
    { "name": "ROADMAP.md", "reason": "multi-phase saas product" },
    { "name": "DEPLOYMENT.md", "reason": "production saas needs deployment clarity" }
  ]
}
```

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.11+ | Fast iteration, rich AI/HTTP ecosystem |
| CLI framework | Typer | Clean, modern, vibe-friendly |
| AI - Primary | Gemini 2.0 Flash (free tier) | Long context, fast, generous limits |
| AI - Fallback | Groq (llama-3.3-70b) | Speed, free tier |
| AI - Backup | OpenRouter (free models) | Redundancy |
| Web Search | Tavily API (free tier) | AI-optimized, clean output, 1k/mo free |
| HTTP client | httpx | Async-ready |
| Config | python-dotenv | Manage API keys cleanly |
| Output | Markdown files | Plain, portable, agent-ready |

---

## Folder Structure

```
Viveka/
├── main.py                    # CLI entry point (Typer app)
├── pipeline/
│   ├── intent_parser.py       # Step 1: extract intent + decide file manifest
│   ├── search.py              # Step 2: Tavily search queries
│   ├── compressor.py          # Step 3: summarize retrieved docs
│   └── generator.py           # Step 4: generate each file in the manifest
├── prompts/
│   ├── intent.md              # System prompt: intent extraction + file manifest decision
│   ├── compress.md            # System prompt: doc compression
│   └── generate.md            # System prompt: per-file generation (with file-type context)
├── file_definitions/
│   └── catalog.py             # Registry of all possible output files + their generation instructions
├── templates/
│   └── examples/              # Example generated bundles for reference
├── output/                    # Generated configs go here (gitignored)
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

---

## CLI Interface

```bash
# Basic usage
agentforge generate "a twitter clone for developers"

# With output dir
agentforge generate "saas dashboard for freelancers" --out ./my-project

# Verbose: see pipeline steps + which files were chosen and why
agentforge generate "vibe coded todo app" --verbose

# Skip web search (offline mode, lower quality)
agentforge generate "anything" --no-search

# Preview only: show which files would be generated without generating
agentforge generate "anything" --dry-run
```

---

## Key Rules for the Agent Building This

- **Intent parser decides the file manifest — not the user, not hardcoded logic.** This is the core product differentiation. Do not shortcut it with a fixed list.
- **Intent parser is the most critical piece.** Test it with 20+ bad/vague inputs before building anything else. Wrong intent = wrong files + wrong searches = garbage output.
- **The file catalog (`catalog.py`) is the source of truth.** Every possible output file type lives there with its generation instructions. Generator reads from catalog, not from hardcoded prompts.
- **Compression is not optional.** Raw fetched HTML dumped into context = noise. Always compress to ~400 words of signal per source.
- **Fail gracefully.** If search fails, fall back to generation without sources (flag it in output). Never crash silently.
- **Generate all files in one context window if possible.** The files are interdependent — STACK informs STRUCTURE, SCHEMA informs AGENT, etc. If splitting across calls, pass prior outputs as context.
- **Model switching must be automatic.** Gemini quota hit → try Groq → try OpenRouter. Never ask the user to switch manually.
- **Output must be immediately usable.** Drop the folder into a project, feed to Cursor/Windsurf/Claude, start building. Zero editing required.

---

## MVP Scope

- [ ] Working CLI with `generate` command
- [ ] Intent parser with dynamic file manifest output (JSON)
- [ ] Tavily search integration
- [ ] Compression pass
- [ ] Generator that iterates over manifest and generates each file
- [ ] `file_definitions/catalog.py` with at least 10 file types defined
- [ ] Output written to `output/<project-slug>/`
- [ ] `--verbose` and `--dry-run` flags
- [ ] Graceful fallback if search or model fails

## Post-MVP

- [ ] Web UI (Next.js or simple HTML+JS)
- [ ] Stack presets (speed up intent parsing for known project types)
- [ ] Community bundle sharing
- [ ] GitHub integration (push bundle directly to repo)
- [ ] Bundle versioning / diffing
- [ ] Custom file type definitions (user can add their own to catalog)

---

## API Keys Needed

```
GEMINI_API_KEY=        # aistudio.google.com — free
GROQ_API_KEY=          # console.groq.com — free
OPENROUTER_API_KEY=    # openrouter.ai — free tier
TAVILY_API_KEY=        # tavily.com — free, 1000 searches/month
```

---

## Success Metric for MVP

A vibe coder types a one-sentence description and gets back a custom, project-appropriate config bundle in under 30 seconds — with exactly the files their project needs and none it doesn't. Good enough to feed straight into their coding agent without touching a single line.
