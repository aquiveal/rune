from pydantic import BaseModel, Field

__all__ = ["IndexItemSchema", "IndexManifestSchema"]


class IndexItemSchema(BaseModel):
    name: str
    path: str
    item_type: str
    origin_scope: str


class IndexManifestSchema(BaseModel):
    items: dict[str, IndexItemSchema] = Field(default_factory=dict)
