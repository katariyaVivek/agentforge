<!-- GSD:project-start source:PROJECT.md -->
## Project

**AgentForge**

AgentForge is a CLI-first experience (web layer later) that ingests a rough, ambiguous project description and outputs a dynamically curated config bundle. It figures out which files are useful for that particular vibe coder’s context, then generates only those docs with the right level of detail.

**Core Value:** Vibe coders start with exactly the config they need—no more guessing, no irrelevant templates, and no blank AGENT.md.

### Constraints

- **Latency**: Provide a bundle in under 30 seconds so it stays in the coder’s flow.
- **Model budget**: Prefer Gemini Flash; automatically fall back to Groq/OpenRouter only when quotas are hit.
- **Output format**: Markdown docs stored under `output/<project-slug>/`; minimal to zero manual polishing.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Technologies
| Technology         | Version  | Purpose               | Why Recommended                                                                 |
|--------------------|----------|-----------------------|----------------------------------------------------------------------------------|
| Python             | 3.14.0   | Programming language  | Latest stable release with free-threaded interpreter, PEP 750, deferred annotations, and broad ecosystem support for AI/HTTP tools |
| Typer              | 0.24.1   | CLI framework         | Modern type-hint based interface, auto-completion, built-in help; the FastAPI of CLIs                                          |
| LangChain          | 1.2.13   | AI orchestration      | Batteries‑included agent framework (Deep Agents) for robust multi-step LLM workflows and context management                    |
| Tavily Python SDK  | 1.1.0    | Web search integration| AI-optimized, real-time search & extraction API for grounding LLM queries with fresh web context                                |
| HTTPX              | 0.28.1   | HTTP client           | Async-first, HTTP/2 support, requests-compatible API for performant networking                                                     |
| python-dotenv      | 1.2.2    | Config management     | 12-factor .env support with CLI extras for clean API key and environment handling                                                 |
| Pydantic           | 2.12.5   | Data validation       | Fast, explicit schema handling for intent parser outputs and API models                                                            |
| Jinja2             | 3.1.6    | Templating engine     | Extensible templating for dynamic file scaffolding and code generation                                                            |
### Supporting Libraries
| Library            | Version  | Purpose                   | When to Use                                      |
|--------------------|----------|---------------------------|---------------------------------------------------|
| rich               | 14.3.3   | Console styling           | Human-friendly logs, progress bars, and error formatting                                         |
| shellingham        | (via Typer) | Shell autodetection     | Required for Typer’s auto-completion installation                                              |
| click              | 8.x      | CLI runtime               | Implicit dependency powering Typer’s command parsing                                          |
| langchain-deepagents| latest  | Advanced agent patterns   | For durable execution, sub-agent spawning, and in-flight context compression                   |
### Development Tools
| Tool               | Purpose                   | Notes                                                     |
|--------------------|---------------------------|-----------------------------------------------------------|
| pre-commit         | Git hook manager          | Enforce Black, isort, flake8, mypy via pre-commit hooks (v4.5.1) |
| black              | Code formatter            | Consistent code style                                      |
| isort              | Import sorter             | Automated import ordering via pre-commit                    |
| mypy               | Static typing             | Validate type hints for CLI correctness                     |
| flake8             | Linting                   | Catch style and complexity issues                           |
| Poetry             | Packaging & dependencies  | Lockfile reproducibility and virtualenv management          |
## Alternatives Considered
| Recommended      | Alternative                  | When to Use Alternative                                      |
|------------------|------------------------------|--------------------------------------------------------------|
| Typer            | Click                        | In legacy Click codebases or for minimal direct dependency   |
| LangChain        | Direct OpenAI SDK            | For single-step LLM calls when full orchestration layer is overkill |
| Tavily SDK       | Bing Web Search API          | Enterprise or custom search domain requirements               |
| Jinja2           | Python string templates      | Very simple file generation without logic or loops            |
## What NOT to Use
| Avoid            | Why                          | Use Instead                                                  |
|------------------|------------------------------|--------------------------------------------------------------|
| argparse         | Verbose boilerplate          | Typer for type-hinted, auto-complete CLI                     |
| requests         | Blocking, no HTTP/2          | HTTPX for async and HTTP/2 support                           |
| typer-slim       | Deprecated subset            | Official Typer package for full feature set                  |
| Pydantic v1.x    | Legacy API, migrating soon   | Pydantic v2 for performance and modern validation features   |
## Stack Patterns by Variant
- Use LangChain Deep Agents
- Because it provides durable execution, sub-agent spawning, and in-flight context management
- Use OpenAI Python SDK directly
- Because lower overhead when multi-step orchestration is not needed
## Version Compatibility
| Package          | Compatible With          | Notes                                                        |
|------------------|--------------------------|--------------------------------------------------------------|
| Python 3.14.0    | Typer 0.24.x, Pydantic 2.12.x, LangChain 1.2.x | Leverages latest interpreter features                         |
| Jinja2 3.1.6     | Python >=3.7, <=3.14     | Stable template API                                          |
| HTTPX 0.28.1     | Python >=3.8             | HTTP/2 optional via httpx[http2]                             |
| python-dotenv 1.2.2 | Python >=3.10         | Includes CLI extras ([cli])                                  |
## Sources
- Python 3.14 release notes (python.org) — MEDIUM
- Typer 0.24.1 PyPI & docs (typer.tiangolo.com) — HIGH
- LangChain docs (langchain.com) — HIGH
- Tavily SDK reference (docs.tavily.com) — MEDIUM
- HTTPX docs (httpx.org) — HIGH
- python-dotenv PyPI & docs — MEDIUM
- Pydantic docs (pydantic.dev) — HIGH
- Jinja2 docs (jinja.palletsprojects.com) — HIGH
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
