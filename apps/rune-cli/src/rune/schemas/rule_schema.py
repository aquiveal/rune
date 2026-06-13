from pydantic import BaseModel, Field
from typing import Optional

class RuleMetadata(BaseModel):
    internal: bool = False

class RuleSchema(BaseModel):
    name: str
    description: str
    metadata: Optional[RuleMetadata] = Field(default_factory=RuleMetadata)
    path: Optional[str] = None
