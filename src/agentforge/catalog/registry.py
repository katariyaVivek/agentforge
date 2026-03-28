from typing import Any, Dict, List

from src.agentforge.catalog.models import CatalogEntry as PydanticCatalogEntry
from src.agentforge.catalog.conditions import evaluate_condition


def get_files_to_generate(manifest: Dict[str, Any]) -> List[PydanticCatalogEntry]:
    """Determine which files to generate based on manifest metadata.

    Args:
        manifest: Dict containing project metadata (project_type, domain, scale, etc.)

    Returns:
        List of CatalogEntry objects to generate
    """
    try:
        from file_definitions.catalog import CATALOG
    except ImportError:
        return []

    files_to_generate = []

    for entry in CATALOG:
        if entry.is_core:
            files_to_generate.append(
                PydanticCatalogEntry(
                    name=entry.name,
                    filename=entry.filename,
                    template=entry.template,
                    is_core=True,
                    condition=None,
                    priority=entry.priority,
                )
            )
        elif entry.condition:
            context = {
                "project_type": manifest.get("project_type", ""),
                "domain": manifest.get("domain", ""),
                "scale": manifest.get("scale", ""),
                "stack_hints": manifest.get("stack_hints", []),
                "requirements": manifest.get("requirements", []),
            }
            if evaluate_condition(entry.condition, context):
                files_to_generate.append(
                    PydanticCatalogEntry(
                        name=entry.name,
                        filename=entry.filename,
                        template=entry.template,
                        is_core=False,
                        condition=entry.condition,
                        priority=entry.priority,
                    )
                )

    files_to_generate.sort(key=lambda x: x.priority)
    return files_to_generate
