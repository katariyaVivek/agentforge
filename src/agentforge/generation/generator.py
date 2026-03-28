import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader

from src.agentforge.catalog import get_files_to_generate
from src.agentforge.generation.fallback import create_model_with_fallback
from src.agentforge.output.writer import write_file


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


class Generator:
    def __init__(
        self,
        output_dir: str = "output",
        template_dir: Optional[str] = None,
        test_mode: bool = False,
    ):
        self.output_dir = output_dir
        self.test_mode = test_mode or bool(os.getenv("GSD_TEST_MODE"))
        self.model = None

        if not self.test_mode:
            try:
                self.model = create_model_with_fallback()
            except Exception:
                pass

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

        for entry in files:
            content = self._generate_content(entry, context)
            filepath = output_path / entry.filename
            write_file(filepath, content)
            generated_files[entry.filename] = filepath

        return generated_files

    def _generate_content(self, entry, context: Dict[str, Any]) -> str:
        if self.test_mode:
            return self._test_content(entry, context)

        if self.env:
            try:
                template = self.env.get_template(entry.template)
                return template.render(**context)
            except Exception:
                pass

        return self._test_content(entry, context)

    def _test_content(self, entry, context: Dict[str, Any]) -> str:
        filename = entry.filename
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
