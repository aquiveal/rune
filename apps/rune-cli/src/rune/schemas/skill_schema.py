import re

from pydantic import BaseModel, Field, field_validator

__all__ = ["SkillMetadata", "SkillSchema"]


class SkillMetadata(BaseModel):
    internal: bool = False


class SkillSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str = Field(..., min_length=1, max_length=1024)
    license: str | None = None
    compatibility: str | None = Field(None, max_length=500)
    metadata: SkillMetadata | None = Field(default_factory=SkillMetadata)
    path: str | None = None  # Path within the repo

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError(
                "Name must contain only lowercase letters, numbers, and hyphens. Cannot start/end with a hyphen or have consecutive hyphens."
            )
        return v
