from typing import Optional
from pydantic import BaseModel, Field

class Token(BaseModel):
    """
    令牌模型
    """
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")

class TokenData(BaseModel):
    user_id: int = Field(..., description="用户ID")

class TokenPayload(BaseModel):
    """
    令牌载荷模型
    """
    sub: Optional[int] = None 