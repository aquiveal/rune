from pydantic import BaseModel, Field

__all__ = ["RuleMetadata", "RuleSchema"]


class RuleMetadata(BaseModel):
    internal: bool = False


class RuleSchema(BaseModel):
    name: str
    description: str
    metadata: RuleMetadata | None = Field(default_factory=RuleMetadata)
    path: str | None = None
