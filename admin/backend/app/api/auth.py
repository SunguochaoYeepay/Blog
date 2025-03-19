from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.database import get_db
from app.models.user import User
from app.schemas.response import Response
from app.schemas.auth import Token, TokenData, UserLogin
from app.logger import setup_logger
from ..config import settings
from ..dependencies.redis import (
    add_token_to_blacklist, 
    is_token_blacklisted,
    cache_user,
    get_cached_user,
    delete_user_cache
)
import time

logger = setup_logger("auth")
router = APIRouter()

# 配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=Response(
            code=401,
            message="无效的认证凭据"
        ).model_dump(),
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 检查令牌是否在黑名单中
        if is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Response(
                    code=401,
                    message="令牌已失效"
                ).model_dump(),
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Response(
                code=401,
                message="认证凭据已过期"
            ).model_dump(),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/auth/login", response_model=Response[Token])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    logger.info(f"Login attempt for user: {form_data.username}")
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Invalid credentials for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Response(
                    code=401,
                    message="用户名或密码错误"
                ).model_dump(),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # 尝试缓存用户信息，但不影响登录流程
        try:
            await cache_user(user)
        except Exception as e:
            logger.warning(f"Failed to cache user data: {str(e)}")
        
        logger.info(f"User {form_data.username} logged in successfully")
        return Response(
            code=200,
            message="登录成功",
            data=Token(
                access_token=access_token,
                token_type="bearer"
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="登录失败，请稍后重试"
            ).model_dump()
        )

@router.post("/auth/register", response_model=Response[Token], status_code=status.HTTP_201_CREATED)
async def register(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Response(
                    code=400,
                    message="用户名已存在"
                ).model_dump()
            )
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            department=user_data.department,
            role=user_data.role,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # 缓存新用户信息
        user_data = {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "department": db_user.department,
            "role": db_user.role,
            "created_at": db_user.created_at.isoformat()
        }
        cache_user(db_user.id, user_data)
        
        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.username}, expires_delta=access_token_expires
        )
        
        logger.info(f"User registered successfully: {db_user.username}")
        return Response(
            code=201,
            message="注册成功",
            data=Token(
                access_token=access_token,
                token_type="bearer"
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="注册失败"
            ).model_dump()
        )

@router.get("/auth/me", response_model=Response[dict])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    try:
        # 尝试从缓存获取用户信息
        cached_user = get_cached_user(current_user.id)
        if cached_user:
            return Response[dict](
                code=200,
                message="获取成功",
                data=cached_user
            )
        
        # 如果缓存未命中，从数据库获取并缓存
        user_data = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "department": current_user.department,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat()
        }
        
        # 缓存用户信息
        cache_user(current_user.id, user_data)
        
        return Response[dict](
            code=200,
            message="获取成功",
            data=user_data
        )
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="获取用户信息失败",
                data=None
            ).model_dump()
        )

@router.post("/auth/logout", response_model=Response)
async def logout(token: str = Depends(oauth2_scheme)):
    """用户登出"""
    try:
        # 验证token的有效性
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            expires = payload.get("exp")
            if not expires or expires < int(time.time()):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=Response(
                        code=401,
                        message="无效的认证凭据"
                    ).model_dump()
                )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Response(
                    code=401,
                    message="无效的认证凭据"
                ).model_dump()
            )
        
        # 将有效的令牌加入黑名单
        try:
            expires_in = expires - int(time.time())
            if expires_in > 0:
                add_token_to_blacklist(token, expires_in)
        except Exception as e:
            logger.warning(f"Failed to add token to blacklist: {str(e)}")
        
        return Response(
            code=200,
            message="注销成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="注销失败，请稍后重试"
            ).model_dump()
        ) 