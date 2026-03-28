from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

from src.agentforge.catalog.models import CatalogEntry as PydanticCatalogEntry
from src.agentforge.catalog.conditions import evaluate_condition


def _get_catalog():
    """Import CATALOG with path resolution for installed package."""
    try:
        from file_definitions.catalog import CATALOG

        return CATALOG
    except ImportError:
        pass

    # Try to find file_definitions relative to this file
    # registry.py is at src/agentforge/catalog/registry.py
    # file_definitions is at AgentForge/file_definitions/
    try:
        registry_dir = Path(__file__).resolve().parent
        agentforge_root = registry_dir.parent.parent.parent
        file_defs_path = agentforge_root / "file_definitions"
        if file_defs_path.exists():
            sys.path.insert(0, str(agentforge_root))
            from file_definitions.catalog import CATALOG

            return CATALOG
    except Exception:
        pass

    return []


def get_files_to_generate(manifest: Dict[str, Any]) -> List[PydanticCatalogEntry]:
    """Determine which files to generate based on manifest metadata.

    Args:
        manifest: Dict containing project metadata (project_type, domain, scale, etc.)

    Returns:
        List of CatalogEntry objects to generate
    """
    CATALOG = _get_catalog()
    if not CATALOG:
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
