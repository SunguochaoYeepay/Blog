from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    """通用响应模型
    
    Args:
        code: 状态码
        message: 响应消息
        data: 响应数据
    """
    code: int
    message: str
    data: Optional[T] = None