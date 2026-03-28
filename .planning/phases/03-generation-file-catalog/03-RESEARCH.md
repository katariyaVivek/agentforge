# Phase 3: Generation & File Catalog - Research

**Researched:** 2026-03-28
**Domain:** AI-powered file generation with fallback circuit and catalog-driven conditional output
**Confidence:** HIGH

## Summary

Phase 3 implements the core generation engine for AgentForge. It consumes the manifest (from Phase 1) and compressed context (from Phase 2) to produce Markdown documentation files. The key innovations are: (1) a central file catalog that drives conditional file generation, and (2) a resilient model fallback circuit that gracefully degrades from Gemini to Groq to OpenRouter when quotas or availability issues occur.

**Primary recommendation:** Use LangChain's `with_fallbacks()` pattern to chain multiple model providers, implement a Pydantic-driven file catalog in `file_definitions/catalog.py`, and use Jinja2 templates for consistent Markdown generation across all output files.

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Model preference**: Gemini Flash as primary, fall back to Groq/OpenRouter on quota hit
- **Output format**: Markdown docs under `output/<project-slug>/`
- **Latency target**: Under 30 seconds total generation time
- **No templates**: AI-driven manifest determines files, not pre-bundled templates

### the agent's Discretion
- Specific fallback chain ordering (Gemini → Groq → OpenRouter is specified, but implementation details are flexible)
- Catalog structure and condition syntax
- Prompt template design for each file type

### Deferred Ideas (OUT OF SCOPE)
- Plugin catalog entries (LIB-01) - deferred to v2
- Cross-document context passing (CTX-01) - deferred to v2

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GEN-01 | Generator consumes manifest + compressed context to create files (AGENT.md, RULES.md, STRUCTURE.md plus conditionals) under `output/<project-slug>/` | LangChain LCEL chains, Jinja2 templating, Pydantic output parsing |
| CAT-01 | Central file catalog (`file_definitions/catalog.py`) drives available file types, their generation prompts, and conditions that unlock them | Pydantic models for catalog entries, conditional evaluation logic |
| CAT-02 | Core docs always generated; additional files only when catalog conditions signal they are needed | Catalog condition evaluation, manifest-driven file selection |
| REL-01 | Model fallback circuit (Gemini → Groq → OpenRouter) for resilience, preserving unified style | LangChain `with_fallbacks()` pattern, model error handling |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| langchain | 1.2.37 | AI orchestration | Standard interface for model providers, fallback chains |
| langchain-google-genai | latest | Gemini model access | Primary model provider per constraints |
| langchain-groq | latest | Groq model access | Fallback provider #1 |
| langchain-openrouter | latest | OpenRouter model access | Fallback provider #2, unified API |
| pydantic | 2.12.5 | Data validation | Catalog schema, output parsing |
| jinja2 | 3.1.6 | Templating | Dynamic prompt and file generation |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.2.2 | API key management | Loading GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY |
| rich | 14.3.3 | Console output | Progress bars during multi-file generation |
| pathlib | stdlib | Path handling | Output directory management |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| LangChain | Direct SDK calls | More boilerplate; LangChain provides unified interface + fallback patterns |
| Jinja2 | f-strings | Jinja2 supports loops/conditionals essential for dynamic file generation |
| Pydantic | dataclasses | Pydantic provides validation + serialization out of box |

**Installation:**
```bash
pip install langchain[langchain-google-genai,langchain-groq,langchain-openrouter] \
  pydantic jinja2 python-dotenv rich
```

**Version verification:**
- langchain: 1.2.37 (verified via pip)
- langchain-google-genai, langchain-groq, langchain-openrouter: Use `latest` (managed by langchain)

## Architecture Patterns

### Recommended Project Structure
```
src/agentforge/
├── generation/
│   ├── __init__.py
│   ├── generator.py          # Main generation orchestrator
│   ├── fallback.py           # Model fallback circuit
│   └── prompts/
│       ├── agent_md.j2       # AGENT.md template
│       ├── rules_md.j2       # RULES.md template
│       └── structure_md.j2   # STRUCTURE.md template
├── catalog/
│   ├── __init__.py
│   ├── models.py            # Pydantic models for catalog entries
│   ├── registry.py          # Catalog registry and condition evaluation
│   └── conditions.py        # Condition helpers (evaluate manifest metadata)
└── output/
    └── writer.py             # File writing utilities

file_definitions/
└── catalog.py               # Central catalog definition (per CAT-01)

output/<project-slug>/       # Generated files (per constraints)
```

### Pattern 1: Model Fallback Chain
**What:** Sequential model providers that activate on failure
**When to use:** When primary model (Gemini) may hit quotas
**Example:**
```python
# Source: LangChain with_fallbacks pattern
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openrouter import ChatOpenRouter
from langchain_core.runnables import RunnableWithFallbacks

# Define models in fallback order
primary_model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=4096
)

fallback_groq = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=4096
)

fallback_openrouter = ChatOpenRouter(
    model="anthropic/claude-3.5-sonnet",
    temperature=0.7,
    max_tokens=4096
)

# Chain with fallbacks - tries primary, then each fallback in order
model_with_fallback = primary_model.with_fallbacks(
    fallbacks=[fallback_groq, fallback_openrouter]
)
```

**Key insight:** The fallback chain preserves the same prompt template, ensuring consistent formatting regardless of which model ultimately generates the output.

### Pattern 2: File Catalog Registry
**What:** Central registry mapping file types to generation prompts and unlock conditions
**When to use:** To implement CAT-01 and CAT-02 - core files always, conditional files on demand
**Example:**
```python
# file_definitions/catalog.py
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class FileType(str, Enum):
    AGENT = "agent"
    RULES = "rules"
    STRUCTURE = "structure"
    TESTING = "testing"
    DEPLOY = "deploy"
    # ... additional types

class CatalogEntry(BaseModel):
    file_type: FileType
    filename: str
    template: str  # Jinja2 template name
    is_core: bool = True  # CAT-02: core files always generated
    condition: Optional[str] = None  # e.g., "project_type == 'web'"
    description: str

# Core files - always generated (CAT-02)
CATALOG = [
    CatalogEntry(
        file_type=FileType.AGENT,
        filename="AGENT.md",
        template="agent_md.j2",
        is_core=True,
        description="Agent configuration and role definition"
    ),
    CatalogEntry(
        file_type=FileType.RULES,
        filename="RULES.md",
        template="rules_md.j2",
        is_core=True,
        description="Coding rules and conventions"
    ),
    CatalogEntry(
        file_type=FileType.STRUCTURE,
        filename="STRUCTURE.md",
        template="structure_md.j2",
        is_core=True,
        description="Project structure and organization"
    ),
    # Conditional files - generated when conditions met (CAT-02)
    CatalogEntry(
        file_type=FileType.TESTING,
        filename="TESTING.md",
        template="testing_md.j2",
        is_core=False,
        condition="scale == 'large' or 'testing' in requirements",
        description="Testing strategy for large projects"
    ),
    CatalogEntry(
        file_type=FileType.DEPLOY,
        filename="DEPLOY.md",
        template="deploy_md.j2",
        is_core=False,
        condition="domain == 'web' or 'deployment' in requirements",
        description="Deployment configuration"
    ),
]

def get_files_to_generate(manifest: dict) -> list[CatalogEntry]:
    """Filter catalog entries based on manifest metadata (CAT-02)."""
    generated = [entry for entry in CATALOG if entry.is_core]
    conditional = [entry for entry in CATALOG if not entry.is_core]
    
    for entry in conditional:
        if evaluate_condition(entry.condition, manifest):
            generated.append(entry)
    
    return generated

def evaluate_condition(condition: str, context: dict) -> bool:
    """Simple condition evaluator for catalog entries."""
    # Use eval with limited globals for safety
    allowed_names = {
        "project_type": context.get("project_type", ""),
        "domain": context.get("domain", ""),
        "scale": context.get("scale", ""),
        "requirements": context.get("requirements", []),
    }
    try:
        return bool(eval(condition, {"__builtins__": {}}, allowed_names))
    except Exception:
        return False
```

### Pattern 3: Jinja2 Prompt Template with Context
**What:** Use Jinja2 templates for generating file content with compressed context injected
**When to use:** For consistent Markdown output across all file types
**Example:**
```python
# src/agentforge/generation/prompts/agent_md.j2
# Template for AGENT.md
# {% include 'style_guide.md.j2' %}

# {{ agent_config.role }}

## Overview
{{ context.overview }}

## Tools & Capabilities
{% for tool in context.tools %}
- {{ tool.name }}: {{ tool.description }}
{% endfor %}

## Constraints
{% for constraint in context.constraints %}
- {{ constraint }}
{% endfor %}

## Context from Research
{{ context.research_summary }}
```

```python
# Using the template
from jinja2 import Environment, FileSystemLoader, select_autoescape

def generate_file(entry: CatalogEntry, manifest: dict, compressed_context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader("src/agentforge/generation/prompts"),
        autoescape=select_autoescape()
    )
    
    template = env.get_template(entry.template)
    content = template.render(
        manifest=manifest,
        context=compressed_context,
        project_slug=manifest.get("project_slug", "unnamed")
    )
    
    return content
```

### Pattern 4: Generator Orchestrator
**What:** Coordinates manifest + context → file generation → output writing
**When to use:** Main entry point for GEN-01
**Example:**
```python
# src/agentforge/generation/generator.py
from pathlib import Path
from langchain_core.runnables import RunnableWithFallbacks
from agentforge.catalog import get_files_to_generate
from agentforge.output.writer import write_file

class Generator:
    def __init__(self, model: RunnableWithFallbacks):
        self.model = model
        self.output_dir = Path("output")
    
    async def generate(self, manifest: dict, compressed_context: dict) -> dict:
        """Generate all files per catalog (GEN-01)."""
        files_to_generate = get_files_to_generate(manifest)
        project_slug = manifest.get("project_slug", "unnamed")
        output_path = self.output_dir / project_slug
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {}
        for entry in files_to_generate:
            content = await self._generate_content(entry, manifest, compressed_context)
            file_path = output_path / entry.filename
            write_file(file_path, content)
            results[entry.filename] = str(file_path)
        
        return results
    
    async def _generate_content(self, entry, manifest, context) -> str:
        """Generate single file content using model."""
        prompt = self._build_prompt(entry, manifest, context)
        response = await self.model.ainvoke(prompt)
        return response.content
    
    def _build_prompt(self, entry, manifest, context) -> str:
        """Build generation prompt with unified style."""
        return f"""Generate {entry.filename} for a {manifest.get('project_type')} project.

## Project Context
- Type: {manifest.get('project_type')}
- Domain: {manifest.get('domain')}
- Scale: {manifest.get('scale')}

## Compressed Context (from search)
{context.get('summary', 'No additional context.')}

## Instructions
{entry.description}

Generate the file in consistent Markdown format with:
- Clear hierarchical structure
- Actionable content
- Project-specific customization
"""
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|------------|-----|
| Model provider switching | Custom HTTP client with retry logic | LangChain with_fallbacks | Built-in error handling, unified interface, automatic retry |
| Conditional file logic | Hardcoded if/else chains | Catalog registry with condition strings | Extensible, declarative, easy to audit |
| Markdown formatting | Manual string concatenation | Jinja2 templates | Supports loops/conditionals, testable, version-controlled |
| Output parsing | Regex/string splitting | PydanticOutputParser | Type safety, validation, structured output |

**Key insight:** The model fallback must use the SAME prompt template regardless of which provider succeeds. This ensures consistent Markdown formatting across all output files.

## Common Pitfalls

### Pitfall 1: Fallback Chain Uses Different Prompts
**What goes wrong:** Each fallback model uses a slightly different prompt, causing inconsistent formatting
**Why it happens:** Developers copy-paste generation code for each provider
**How to avoid:** Always wrap the model in `with_fallbacks()` before any prompt customization; the fallback receives the exact same prompt as the primary
**Warning signs:** AGENT.md looks different from RULES.md despite similar generation logic

### Pitfall 2: Catalog Conditions Too Complex
**What goes wrong:** Condition evaluation fails silently, files not generated when expected
**Why it happens:** Using Python features beyond simple comparisons in condition strings
**How to avoid:** Limit conditions to simple equality/membership checks; use `eval()` with restricted globals
**Warning signs:** Conditional files appear/disappear unexpectedly without errors

### Pitfall 3: Context Overflow
**What goes wrong:** Compressed context too large, generation exceeds token limits
**Why it happens:** Passing full Phase 2 output instead of summarized chunks
**How to avoid:** Use the 400-word summaries from Phase 2 compression; select relevant chunks per file type
**Warning signs:** Model returns truncated content or errors about max tokens

### Pitfall 4: Blocking I/O in Generation
**What goes wrong:** Generation takes >30 seconds due to sequential file writes
**Why it happens:** Using synchronous file I/O in async generation pipeline
**How to avoid:** Use `aiofiles` for async file writing; consider parallel generation for independent files
**Warning signs:** CLI feels unresponsive; total time exceeds latency target

## Code Examples

### Unified Style Prompt (REL-01)
```python
# Source: LangChain best practices - same prompt regardless of model
STYLE_PROMPT = """You are an expert technical writer creating AI agent configuration files.

Output MUST follow these rules:
1. Use Markdown with clear hierarchical headings
2. Keep paragraphs concise (3-4 sentences max)
3. Use bullet points for lists of items
4. Include concrete examples where helpful
5. Never use placeholder text like [TODO] or [INSERT]
6. Tailor content to the specific project type and domain

Respond with ONLY the requested file content, no explanations."""
```

### Catalog Entry with Manifest Binding
```python
# Source: Pydantic + catalog pattern
from pydantic import BaseModel, Field
from typing import Optional

class CatalogEntry(BaseModel):
    """Single file definition in the catalog (CAT-01)."""
    name: str = Field(description="Human-readable name")
    filename: str = Field(description="Output filename with extension")
    template: str = Field(description="Jinja2 template name")
    is_core: bool = Field(
        default=True,
        description="If true, always generated (CAT-02)"
    )
    condition: Optional[str] = Field(
        default=None,
        description="Python expression evaluated against manifest"
    )
    priority: int = Field(
        default=0,
        description="Generation order (higher = generated first)"
    )
    context_keys: list[str] = Field(
        default_factory=list,
        description="Which manifest/context fields this file needs"
    )
```

### Fallback with Exception Handling
```python
# Source: LangChain RunnableWithFallbacks
from langchain_core.runnables import RunnableWithFallbacks
from langchain_core.exceptions import OutputParserException

# Define which exceptions trigger fallback
fallback_config = {
    "exceptions_to_handle": [
        Exception,  # Catch all for safety
    ]
}

model_with_resilience = primary_model.with_fallbacks(
    fallbacks=[fallback_groq, fallback_openrouter],
    exceptions_to_handle=[Exception]
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single model with hardcoded retry | LangChain with_fallbacks chain | LangChain 0.2+ | Automatic failover, unified interface |
| Template inheritance for file content | Jinja2 with manifest context | Industry standard | Flexible, testable generation |
| Hardcoded file list | Declarative catalog registry | This phase | Conditional generation without code changes |

**Deprecated/outdated:**
- `with_retry()` alone: Only handles transient errors, not quota exhaustion
- String templating (f-strings): Cannot handle loops/conditionals needed for dynamic content

## Open Questions

1. **Context selection per file type**
   - What we know: Compression outputs ~400 words per document
   - What's unclear: Should each file type get all compressed context, or filtered subsets?
   - Recommendation: Pass full context initially; optimize to per-file subsets if latency exceeds target

2. **Fallback logging**
   - What we know: Need to know which model succeeded for debugging
   - What's unclear: How much detail to log without slowing generation
   - Recommendation: Log model name on completion (info level), full fallback chain on final failure (error level)

3. **Catalog extension**
   - What we know: v2 will support plugin catalog entries (LIB-01)
   - What's unclear: How to design the plugin interface now to avoid breaking changes
   - Recommendation: Design catalog to load from `file_definitions/` directory; treat core catalog as first plugin

## Environment Availability

Step 2.6: SKIPPED (no external dependencies beyond Python packages - all available via pip)

## Sources

### Primary (HIGH confidence)
- LangChain 1.2.37 - Verified version
- langchain-google-genai, langchain-groq, langchain-openrouter - Official LangChain integrations
- Pydantic 2.12.5 - From project STACK.md
- Jinja2 3.1.6 - From project STACK.md

### Secondary (MEDIUM confidence)
- LangChain fallback patterns - LangChain documentation
- Jinja2 for LLM prompts - Instructor blog, Microsoft Semantic Kernel docs

### Tertiary (LOW confidence)
- Specific model error codes - Needs verification during implementation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified versions, well-documented libraries
- Architecture: HIGH - LangChain LCEL patterns are stable and widely used
- Pitfalls: MEDIUM - Based on common LangChain patterns, not project-specific testing

**Research date:** 2026-03-28
**Valid until:** 60 days (library APIs stable; only model-specific details may change)
