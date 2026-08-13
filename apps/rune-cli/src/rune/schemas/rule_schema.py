from pydantic import BaseModel, Field

__all__ = ["Page", "RuleMetadata", "RuleSchema", "Site"]


class RuleMetadata(BaseModel):
    internal: bool = False


class RuleSchema(BaseModel):
    name: str
    description: str
    metadata: RuleMetadata | None = Field(default_factory=RuleMetadata)
    path: str | None = None


class Page(BaseModel):
    title: str
    url: str
    description: str | None = None
    section: str | None = None


class Site(BaseModel):
    name: str
    title: str
    source_url: str
    description: str = ""
    pages: list[Page] = Field(default_factory=list)
    crawl_instructions: str | None = None
