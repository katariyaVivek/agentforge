<!-- markdownlint-disable-next-line -->
<p align="center">
  <img src="https://img.shields.io/badge/AgentForge-FF6B35?style=for-the-badge&logo=firefox&logoColor=white" alt="AgentForge">
  <br>
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License">
  <img src="https://img.shields.io/badge/Status-v1.1 Released-blue?style=flat" alt="Status">
</p>

---

## The Problem

Every vibe coder hits the same wall at project start:

> Staring at a blank `AGENT.md` with no idea where to begin.

Writing these config files from scratch is slow, inconsistent, and easy to get wrong. Most people either skip them or write generic low-quality ones — and then their coding agent underperforms because of it.

**AgentForge solves this.** Give it a rough, even vague project description — it generates exactly the config bundle your project needs.

---

## Why AgentForge?

| Traditional Approach | AgentForge |
|---------------------|------------|
| Copy-paste generic templates | Dynamic — decides what you actually need |
| Wrong files for your project type | Only generates relevant files |
| Manual research & writing | AI does the heavy lifting |
| 30+ minutes of setup | **Under 30 seconds** |

---

## Features

### 🔍 Intent Parsing
AI analyzes your vague description and understands:
- Project type (SaaS, CLI, library, etc.)
- Domain & goals
- Scale (solo, team, enterprise)
- Tech stack hints

### 🌐 Web Search
Grounds outputs in real best practices — fetches relevant docs, tutorials, and community configs for your specific project type.

### 📄 Dynamic Generation
Not a fixed template. Generates exactly the files your project needs:

- **Always:** `AGENT.md`, `RULES.md`, `STRUCTURE.md`
- **Conditional:** `STACK.md`, `SCHEMA.md`, `API.md`, `AUTH.md`, `PAYMENTS.md`, `ROADMAP.md`, and more

### 🛡️ Fallback Chain
Works even when AI APIs are unavailable:
```
Groq → Jinja2 Templates → Keyword-based fallback
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/katariyaVivek/agentforge.git
cd agentforge

# 2. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run
python agentforge.py "a twitter clone for developers"
```

### Get Your Free API Keys

| Service | Free Tier | Link |
|---------|-----------|------|
| **Groq** | 500K tokens/day | [groq.com](https://groq.com) |
| **Tavily** | 1,000 searches/month | [tavily.com](https://tavily.com) |

---

## CLI Options

```bash
# Basic usage
python agentforge.py "your project idea"

# Preview which files would be generated (no writing)
python agentforge.py "..." --dry-run

# See detailed pipeline steps
python agentforge.py "..." --verbose

# Skip web search (faster, lower quality)
python agentforge.py "..." --no-search

# Custom output directory
python agentforge.py "..." --out ./my-output
```

---

## Output Example

```
output/my-twitter-clone/
├── AGENT.md         # Project overview, goals, constraints
├── RULES.md         # Coding conventions
├── STRUCTURE.md     # Folder scaffold with purpose
├── STACK.md         # Tech decisions
├── SCHEMA.md        # Database models
├── AUTH.md          # User auth config
├── PAYMENTS.md      # Stripe integration
└── ROADMAP.md       # Feature phases
```

---

## Architecture

```
User Input (vague description)
         ↓
1. Intent Parser (Groq)
   → Extracts project type, domain, files needed
         ↓
2. Search Layer (Tavily)
   → Fetches relevant best practices
         ↓
3. Context Compression
   → Summarizes to ~400 words of signal
         ↓
4. File Generator (Groq)
   → Creates tailored config files
         ↓
Output: output/<project-slug>/
```

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.14 |
| CLI | Typer |
| AI | Groq (primary), Gemini (fallback) |
| Search | Tavily |
| Templating | Jinja2 |

---

## Future Prospects

### 🚀 Phase 2: Web UI
- Simple browser-based interface
- Drag-and-drop bundle customization
- Visual file preview

### 🔌 Integrations
- **GitHub**: Push generated bundles directly to repos
- **VS Code / Cursor**: Extension for instant config generation
- **CLI Alias**: `ag "my project"` short alias

### 📦 Advanced Features
- **Stack Presets**: Pre-configured templates for common project types (Next.js SaaS, Python CLI, etc.)
- **Bundle Sharing**: Community gallery of verified config bundles
- **Custom File Types**: User-defined file definitions in `catalog.py`
- **Bundle Diffing**: Version control for your configs

### 🤖 Model Flexibility
- OpenRouter fallback for broader model selection
- Local models (Ollama) support
- Custom prompt templates

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Submit a PR

---

## License

MIT License — free for personal and commercial use.

---

<p align="center">
  <sub>Built for vibe coders, by vibe coders.</sub>
</p>
