from pydantic import BaseModel
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

class Category(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True

class CategoryWithChildren(Category):
    children: List['CategoryWithChildren'] = []

class CategoryResponse(CategoryBase):
    id: int
    children: Optional[List['CategoryResponse']] = None

    class Config:
        from_attributes = True

CategoryResponse.model_rebuild()  # 解决循环引用问题 