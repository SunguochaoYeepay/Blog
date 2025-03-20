from datetime import timedelta
from typing import Any, Union, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Form, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.response import Response
from app.schemas.token import Token
from app.schemas.user import User as UserSchema
from app.schemas.auth import ChangePassword, UserLogin
from app.database import get_db
from app.schemas.msg import Msg

router = APIRouter(
    tags=["auth"]
)

@router.post("/login", response_model=Response[Token])
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    elif not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return Response(
        code=200,
        message="登录成功",
        data=Token(access_token=access_token, token_type="bearer")
    )

@router.post("/login/json", response_model=Response[Token])
def login_json(
    *,
    db: Session = Depends(get_db),
    username: str = Body(...),
    password: str = Body(...)
) -> Any:
    """
    JSON compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    elif not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return Response(
        code=200,
        message="登录成功",
        data=Token(access_token=access_token, token_type="bearer")
    )

@router.get("/me", response_model=Response[UserSchema])
def get_current_user(
    current_user: User = Depends(deps.get_current_active_user)
) -> Response[UserSchema]:
    """
    获取当前用户信息
    
    需要登录后访问，返回当前登录用户的详细信息
    """
    return Response(
        code=200,
        message="获取用户信息成功",
        data=current_user
    )

@router.post("/refresh", response_model=Response[Token])
def refresh_token(
    current_user: User = Depends(deps.get_current_active_user)
) -> Response[Token]:
    """
    刷新访问令牌
    
    需要登录后访问，返回新的访问令牌
    """
    access_token = security.create_access_token(current_user.id)
    return Response(
        code=200,
        message="刷新令牌成功",
        data=Token(access_token=access_token, token_type="bearer")
    )

@router.post("/change-password", response_model=Response)
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Response:
    """
    修改密码
    
    需要登录后访问，验证当前密码后更新为新密码
    """
    if not security.verify_password(
        password_data.current_password, 
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="当前密码错误"
        )
    
    current_user.hashed_password = security.get_password_hash(
        password_data.new_password
    )
    db.add(current_user)
    db.commit()
    
    return Response(
        code=200,
        message="密码修改成功"
    )

@router.post("/test-token", response_model=Response[UserSchema])
def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return Response(
        code=200,
        message="Token验证成功",
        data=current_user
    )

@router.post("/logout", response_model=Response)
def logout() -> Any:
    """
    Logout current user
    """
    return Response(
        code=200,
        message="退出登录成功"
    )