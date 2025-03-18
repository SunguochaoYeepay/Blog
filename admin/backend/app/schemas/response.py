from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    """统一的响应模型"""
    code: int = 200
    message: str = "操作成功"
    data: Optional[T] = None