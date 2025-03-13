from pydantic import BaseModel
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True 