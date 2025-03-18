from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None
    is_approved: Optional[bool] = False
    is_spam: Optional[bool] = False

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    content: str

class CommentQuery(BaseModel):
    keyword: Optional[str] = None
    status: Optional[str] = None
    article_id: Optional[int] = None
    article_title: Optional[str] = None
    user_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    size: int = 10

class CommentResponse(CommentBase):
    id: int
    article_id: int
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_approved: bool = False
    is_spam: bool = False
    like_count: int = 0
    user_name: Optional[str] = None
    article_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True) 