from typing import Generator, Optional, Union
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.database import SessionLocal, get_db
from app.core.config import settings
from app.core import security
from app.models.user import User
from app.schemas.token import TokenPayload

# OAuth2 认证配置
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前用户
    
    通过解析JWT token获取当前用户信息
    如果token无效或用户不存在则抛出异常
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户
    
    检查用户是否已激活，未激活则抛出异常
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=400,
            detail="用户未激活"
        )
    return current_user

def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    获取当前超级用户
    
    检查用户是否是超级管理员，不是则抛出异常
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="权限不足"
        )
    return current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_superuser),
) -> User:
    """
    获取当前活跃的超级用户
    
    检查用户是否是活跃的超级管理员，不是则抛出异常
    """
    return current_user 