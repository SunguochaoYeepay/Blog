from pydantic import BaseModel
from typing import Optional

class TagBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    name: Optional[str] = None
    slug: Optional[str] = None

class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True 