```markdown
# Stack Research

**Domain:** AI-powered dynamic CLI config generator
**Researched:** Mar 28, 2026
**Confidence:** MEDIUM-HIGH

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

**If heavy agent orchestration required:**
- Use LangChain Deep Agents
- Because it provides durable execution, sub-agent spawning, and in-flight context management

**If simple LLM pipeline suffices:**
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

---
*Stack research for: AgentForge*
*Researched: Mar 28, 2026*
```markdown
