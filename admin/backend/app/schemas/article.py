from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from .category import CategoryResponse
from .tag import TagResponse
from .user import UserResponse

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    content: str
    summary: Optional[str] = Field(None, max_length=500)
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    keywords: Optional[str] = Field(None, max_length=200)
    status: str = Field("draft", pattern="^(draft|published|archived)$")
    is_featured: bool = False
    allow_comments: bool = True

    model_config = ConfigDict(from_attributes=True)

class ArticleCreate(ArticleBase):
    category_ids: List[int] = []
    tag_ids: List[int] = []

class ArticleUpdate(ArticleBase):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None

class ArticleInDB(ArticleBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    view_count: int
    comment_count: int
    like_count: int

class ArticleResponse(ArticleInDB):
    categories: List[CategoryResponse] = []
    tags: List[TagResponse] = []
    author: UserResponse

class ArticleQuery(BaseModel):
    keyword: Optional[str] = None
    status: Optional[str] = None
    category_id: Optional[int] = None
    tag_id: Optional[int] = None
    author_id: Optional[int] = None
    is_featured: Optional[bool] = None 