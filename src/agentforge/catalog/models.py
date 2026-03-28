from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class FileTypeEnum(str, Enum):
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


class CatalogEntry(BaseModel):
    name: str = Field(..., description="Human-readable name")
    filename: str = Field(..., description="Output filename including extension")
    template: str = Field(..., description="Jinja2 template name")
    is_core: bool = Field(True, description="Always generated if True")
    condition: Optional[str] = Field(
        None, description="Python condition for conditional files"
    )
    priority: int = Field(0, description="Generation order priority")
    context_keys: List[str] = Field(
        default_factory=list, description="Required context keys"
    )

    class Config:
        frozen = True


class ManifestContext(BaseModel):
    project_type: str
    domain: str
    scale: str
    stack_hints: List[str] = []
    requirements: List[str] = []

    class Config:
        frozen = True
