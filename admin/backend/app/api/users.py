from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status, File, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api import deps
from app.core import security
from app.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserUpdateMe
from app.schemas.response import Response
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.services.storage import storage_service

router = APIRouter(
    tags=["users"]
)

@router.get("", response_model=Response[PaginatedResponse[UserResponse]])
def get_users(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """获取用户列表"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    query = db.query(User)
    total = query.count()
    users = query.offset(pagination.skip).limit(pagination.limit).all()

    return Response(
        code=200,
        message="获取用户列表成功",
        data={
            "items": users,
            "total": total,
            "page": pagination.page,
            "size": pagination.limit,
            "total_pages": (total + pagination.limit - 1) // pagination.limit
        }
    )

@router.post("", response_model=Response[UserResponse], status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
):
    """创建用户"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        department=user_in.department,
        role=user_in.role,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return Response(
        code=201,
        message="创建用户成功",
        data=db_user
    )

@router.get("/{user_id}", response_model=Response[UserResponse])
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """获取用户详情"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return Response(
        code=200,
        message="获取用户详情成功",
        data=user
    )

@router.put("/{user_id}", response_model=Response[UserResponse])
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """更新用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户名是否已存在
    if user_update.username and user_update.username != db_user.username:
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
    
    # 检查邮箱是否已存在
    if user_update.email and user_update.email != db_user.email:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    # 更新密码
    if user_update.password:
        db_user.hashed_password = security.get_password_hash(user_update.password)
    
    # 更新其他字段
    for field, value in user_update.dict(exclude={'password'}, exclude_unset=True).items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return Response(
        code=200,
        message="更新用户成功",
        data=db_user
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """删除用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    db.delete(db_user)
    db.commit()
    return Response(
        code=204,
        message="删除用户成功"
    )

@router.put("/me", response_model=Response[UserResponse])
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdateMe,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    更新当前用户信息
    
    需要登录后访问
    """
    if user_in.email:
        user = db.query(User).filter(
            User.email == user_in.email,
            User.id != current_user.id
        ).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="该邮箱已被注册"
            )
    
    if user_in.username:
        user = db.query(User).filter(
            User.username == user_in.username,
            User.id != current_user.id
        ).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="该用户名已被使用"
            )
    
    for field, value in user_in.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return Response(
        code=200,
        message="更新用户信息成功",
        data=current_user
    )

@router.put("/{user_id}/avatar", response_model=Response)
async def update_avatar(
    user_id: int,
    file: UploadFile = File(...),
    current_user = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户头像
    """
    # 检查用户权限
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="没有权限更新其他用户的头像"
        )
    
    # 获取用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 上传图片
    result = await storage_service.upload_image(file, prefix='avatars')
    
    # 更新用户头像
    user.avatar = result['url']
    db.commit()
    
    return Response(
        code=200,
        message="头像更新成功",
        data={"avatar": result['url']}
    )