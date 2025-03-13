from pydantic import BaseModel
from typing import Optional

class TagBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None

class Tag(TagBase):
    id: int
    
    class Config:
        from_attributes = True

# 用于响应的标签模型
class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True 