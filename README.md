# AgentForge

CLI tool that generates dynamic, project-appropriate config bundles from rough project descriptions. Built for vibe coders who want exactly the configs they need—no more guessing.

## Quick Start

```bash
# Clone and setup
pip install -e .

# Add your keys to .env
cp .env.example .env
# Edit .env with GROQ_API_KEY and TAVILY_API_KEY

# Run
python agentforge.py "my project idea"
```

## Features

- **Intent Parsing** - AI understands your vague project descriptions
- **Web Search** - Grounding with relevant context from the web
- **Dynamic Generation** - Creates only the configs you need
- **Fallback Chain** - Works even when AI APIs are unavailable

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Get from [groq.com](https://groq.com) |
| `TAVILY_API_KEY` | Yes | Get from [tavily.com](https://tavily.com) |
| `GSD_TEST_MODE` | No | Set to `1` for development without API keys |

## CLI Options

```bash
python agentforge.py "your project"    # Run normally
python agentforge.py "..." --dry-run   # Preview without generating files
python agentforge.py "..." --verbose   # Detailed output
python agentforge.py "..." --no-search # Skip web search
python agentforge.py "..." --out ./output # Custom output directory
```

## Output

Generated configs are saved to `output/<project-slug>/`
