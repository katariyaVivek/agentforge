import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader

from src.agentforge.catalog import get_files_to_generate
from src.agentforge.output.writer import write_file


logger = logging.getLogger(__name__)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


def _create_llm():
    """Create LLM with fallback chain."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        ChatGoogleGenerativeAI = None

    try:
        from langchain_groq import ChatGroq
    except ImportError:
        ChatGroq = None

    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    # Try Gemini first
    if gemini_key and ChatGoogleGenerativeAI:
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_key,
                temperature=0.3,
                max_tokens=2048,
                convert_system_message_to_human=True,
            )
        except Exception as e:
            logger.warning(f"Gemini init failed: {e}")

    # Fallback to Groq
    if groq_key and ChatGroq:
        try:
            return ChatGroq(
                model="llama-3.3-70b-versatile",
                groq_api_key=groq_key,
                temperature=0.3,
                max_tokens=2048,
            )
        except Exception as e:
            logger.warning(f"Groq init failed: {e}")

    return None


GENERATION_PROMPT = """You are an expert technical writer creating configuration files for AI coding assistants.

Generate the content for {filename} based on:

Project Info:
- Type: {project_type}
- Domain: {domain}
- Scale: {scale}
- Stack: {stack_hints}

{files_section}

Research Context (use this to inform your content):
{research_summary}

Requirements:
- Write in clear, concise Markdown
- Include actionable guidance
- Focus on what's important for this specific project type
- Don't use placeholders like [TODO] - be specific
- Keep it professional and useful

Generate {filename} now:"""


class Generator:
    def __init__(
        self,
        output_dir: str = "output",
        template_dir: Optional[str] = None,
        test_mode: bool = False,
    ):
        self.output_dir = output_dir
        self.test_mode = test_mode or bool(os.getenv("GSD_TEST_MODE"))
        self.llm = None

        if not self.test_mode:
            self.llm = _create_llm()
            if self.llm:
                logger.info("Generator LLM initialized")
            else:
                logger.warning("No LLM available for generation")

        if template_dir:
            self.env = Environment(loader=FileSystemLoader(template_dir))
        else:
            default_dir = Path(__file__).parent / "prompts"
            if default_dir.exists():
                self.env = Environment(loader=FileSystemLoader(str(default_dir)))
            else:
                self.env = None

    def generate(
        self,
        manifest: Dict[str, Any],
        compressed_context: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Path]:
        project_name = slugify(manifest.get("project_type", "project"))
        output_path = Path(self.output_dir) / project_name
        output_path.mkdir(parents=True, exist_ok=True)

        files = get_files_to_generate(manifest)
        generated_files = {}

        context = {
            **manifest,
            "goals": manifest.get("goals", []),
            "requirements": manifest.get("requirements", []),
        }

        if compressed_context:
            context["research_summary"] = "\n\n".join(
                doc.get("summary", "") for doc in compressed_context
            )
        else:
            context["research_summary"] = "No research context available."

        for entry in files:
            content = self._generate_content(entry, context)
            filepath = output_path / entry.filename
            write_file(filepath, content)
            generated_files[entry.filename] = filepath

        return generated_files

    def _generate_content(self, entry: Any, context: Dict[str, Any]) -> str:
        """Generate content for a single file."""
        filename = entry.filename if hasattr(entry, "filename") else str(entry)

        # If we have an LLM, use it
        if self.llm:
            try:
                return self._llm_generate(entry, context)
            except Exception as e:
                logger.warning(f"LLM generation failed for {filename}: {e}")

        # Fallback to templates
        if self.env:
            try:
                template = self.env.get_template(entry.template)
                return template.render(**context)
            except Exception:
                pass

        # Final fallback to test content
        return self._test_content(entry, context)

    def _llm_generate(self, entry: Any, context: Dict[str, Any]) -> str:
        """Generate content using LLM."""
        filename = entry.filename if hasattr(entry, "filename") else str(entry)

        # Get list of files being generated
        files_list = context.get("files_to_generate", [])
        files_section = "\n".join(
            f"- {f.get('name', 'Unknown')}: {f.get('reason', 'Not specified')}"
            for f in files_list
        )

        prompt = GENERATION_PROMPT.format(
            filename=filename,
            project_type=context.get("project_type", "project"),
            domain=context.get("domain", "general"),
            scale=context.get("scale", "medium"),
            stack_hints=", ".join(context.get("stack_hints", [])),
            files_section=files_section or "Files to generate: " + filename,
            research_summary=context.get("research_summary", "No research available."),
        )

        response = self.llm.invoke(prompt)
        content = response.content

        # Clean up if there's markdown wrapper
        if content.startswith("```markdown"):
            content = content[11:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        return content.strip()

    def _test_content(self, entry: Any, context: Dict[str, Any]) -> str:
        """Fallback test content."""
        filename = entry.filename if hasattr(entry, "filename") else str(entry)
        project_type = context.get("project_type", "project")
        domain = context.get("domain", "general")

        if filename == "AGENT.md":
            return f"""# {filename}

## Project Overview

- **Project Type:** {project_type}
- **Domain:** {domain}
- **Scale:** {context.get("scale", "medium")}

## Goals

- Generate high-quality config files for vibe coders
- Provide exactly the docs needed, no more no less

## Constraints

- Latency under 30 seconds
- Prefer Gemini Flash for cost efficiency
"""
        elif filename == "RULES.md":
            return """# Coding Rules & Conventions

## General

- Keep code simple and readable
- Follow PEP 8
- Write tests for new features
"""
        elif filename == "STRUCTURE.md":
            return f"""# Project Structure

```
{project_type}/
├── src/
├── tests/
└── README.md
```
"""
        else:
            return f"# {filename}\n\nGenerated for {project_type} project.\n"
