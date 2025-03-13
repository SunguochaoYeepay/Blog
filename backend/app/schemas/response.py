from typing import Any, Optional, TypeVar, Generic
from pydantic.generics import GenericModel

T = TypeVar('T')

class Response(GenericModel, Generic[T]):
    """统一的响应模型"""
    code: int = 200
    message: str = "操作成功"
    data: Optional[T] = None 