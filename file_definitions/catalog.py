from enum import Enum
from typing import Optional

from pydantic import Field


class FileType(Enum):
    AGENT = "agent"
    RULES = "rules"
    STRUCTURE = "structure"
    TESTING = "testing"
    DEPLOY = "deploy"
    STACK = "stack"
    SCHEMA = "schema"
    API = "api"
    AUTH = "auth"
    PAYMENTS = "payments"
    COMMANDS = "commands"
    ENV = "env"
    SECURITY = "security"
    INTEGRATIONS = "integrations"
    UI_PATTERNS = "ui_patterns"


class CatalogEntry:
    name: str
    filename: str
    template: str
    is_core: bool
    condition: Optional[str]
    priority: int

    def __init__(
        self,
        name: str,
        filename: str,
        template: str,
        is_core: bool = False,
        condition: Optional[str] = None,
        priority: int = 0,
    ):
        self.name = name
        self.filename = filename
        self.template = template
        self.is_core = is_core
        self.condition = condition
        self.priority = priority


CATALOG = [
    CatalogEntry(
        name="AGENT",
        filename="AGENT.md",
        template="agent_md.j2",
        is_core=True,
        priority=1,
    ),
    CatalogEntry(
        name="RULES",
        filename="RULES.md",
        template="rules_md.j2",
        is_core=True,
        priority=2,
    ),
    CatalogEntry(
        name="STRUCTURE",
        filename="STRUCTURE.md",
        template="structure_md.j2",
        is_core=True,
        priority=3,
    ),
    CatalogEntry(
        name="AUTH",
        filename="AUTH.md",
        template="auth_md.j2",
        is_core=False,
        condition="project_type in ['saas', 'web_app']",
        priority=5,
    ),
    CatalogEntry(
        name="API",
        filename="API.md",
        template="api_md.j2",
        is_core=False,
        condition="project_type in ['saas', 'web_app', 'api']",
        priority=6,
    ),
    CatalogEntry(
        name="PAYMENTS",
        filename="PAYMENTS.md",
        template="payments_md.j2",
        is_core=False,
        condition="project_type == 'saas'",
        priority=7,
    ),
    CatalogEntry(
        name="TESTING",
        filename="TESTING.md",
        template="testing_md.j2",
        is_core=False,
        condition="scale == 'large'",
        priority=10,
    ),
    CatalogEntry(
        name="DEPLOY",
        filename="DEPLOYMENT.md",
        template="deployment_md.j2",
        is_core=False,
        condition="domain == 'web'",
        priority=11,
    ),
    CatalogEntry(
        name="STACK",
        filename="STACK.md",
        template="stack_md.j2",
        is_core=False,
        condition="len(stack_hints) > 0",
        priority=12,
    ),
    CatalogEntry(
        name="SCHEMA",
        filename="SCHEMA.md",
        template="schema_md.j2",
        is_core=False,
        condition="project_type in ['saas', 'web_app']",
        priority=13,
    ),
]
