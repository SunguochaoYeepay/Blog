from typing import TypeVar, Generic, List
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')

class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    limit: int = Field(default=10, ge=1, le=100, description="每页数量")
    
    @property
    def skip(self) -> int:
        return (self.page - 1) * self.limit

class PaginatedResponse(GenericModel, Generic[T]):
    """分页响应模型"""
    items: List[T]
    total: int
    page: int
    size: int
    total_pages: int 