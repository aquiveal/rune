from pydantic import BaseModel
from typing import Optional

class ModuleSchema(BaseModel):
    name: str
    url: str
    path: str
    type: str  # 'skill' or 'rule'
