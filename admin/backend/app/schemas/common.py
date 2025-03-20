from typing import TypeVar, Generic, Optional
from pydantic import BaseModel
from enum import Enum

T = TypeVar('T')

class OrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"

class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"

class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10

class ResponseModel(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

class ErrorResponse(BaseModel):
    code: int
    message: str 