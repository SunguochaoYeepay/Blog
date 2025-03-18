from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from typing import List
from ..schemas.user import UserResponse, UserQuery, UserCreate, UserUpdate
from ..schemas.response import Response
from ..models.user import User
from ..database import get_db
from sqlalchemy import or_
from ..logger import setup_logger
from datetime import datetime
from ..utils.security import get_password_hash
from pydantic import BaseModel
from .auth import get_current_user
from ..utils.cache import cache_user

# 创建用户模块的日志记录器
logger = setup_logger("users")

router = APIRouter()

class BatchDeleteRequest(BaseModel):
    ids: List[int]

def check_admin_permission(current_user: User):
    """检查是否具有管理员权限"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Response(
                code=403,
                message="权限不足，需要管理员权限"
            ).model_dump()
        )

@router.post("/users", response_model=Response[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查权限
    check_admin_permission(current_user)
    
    logger.info(f"Creating new user: {user.username}")
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Response(
                code=400,
                message="用户名已存在"
            ).model_dump()
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Response(
                code=400,
                message="邮箱已存在"
            ).model_dump()
        )
    
    try:
        # 创建用户
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            department=user.department,
            role=user.role,
            hashed_password=get_password_hash(user.password),
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User created successfully: {db_user.id}")
        return Response(
            code=201,
            message="用户创建成功",
            data=UserResponse.model_validate(db_user)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="创建用户失败"
            ).model_dump()
        )

@router.get("/users", response_model=Response[dict], status_code=status.HTTP_200_OK)
async def search_users(
    query: UserQuery = Depends(),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查权限
    check_admin_permission(current_user)
    
    logger.info(f"Searching users with query: {query}, page: {page}, size: {size}")
    
    try:
        filters = []
        if query.username:
            filters.append(User.username.ilike(f"%{query.username}%"))
        if query.email:
            filters.append(User.email.ilike(f"%{query.email}%"))
        if query.department:
            filters.append(User.department.ilike(f"%{query.department}%"))
        if query.role:
            filters.append(User.role.ilike(f"%{query.role}%"))

        base_query = db.query(User)
        if filters:
            logger.debug(f"Applying filters: {filters}")
            base_query = base_query.filter(or_(*filters))
        
        # 添加按创建时间倒序排序
        base_query = base_query.order_by(User.created_at.desc())
        
        # 计算总数和总页数
        total = base_query.count()
        total_pages = (total + size - 1) // size
        
        # 处理页码超出范围的情况
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        # 获取分页数据
        offset = (page - 1) * size
        users = base_query.offset(offset).limit(size).all()
        
        logger.info(f"Found {len(users)} users out of {total} total matches")
        return Response(
            code=200,
            message="获取成功",
            data={
                "items": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "department": user.department,
                        "role": user.role,
                        "avatar": user.avatar,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at
                    } for user in users
                ],
                "total": total,
                "page": page,
                "size": size,
                "total_pages": total_pages
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="查询用户失败"
            ).model_dump()
        )

@router.get("/users/{user_id}", response_model=Response[UserResponse], status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查权限（允许用户查看自己的信息）
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Response(
                code=403,
                message="权限不足"
            ).model_dump()
        )
    
    logger.info(f"Fetching user with id: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="用户不存在"
            ).model_dump()
        )
    return Response(
        code=200,
        message="获取成功",
        data=UserResponse.model_validate(user)
    )

@router.put("/users/{user_id}", response_model=Response[UserResponse], status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查权限（允许用户更新自己的信息，但只有管理员可以更新角色）
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Response(
                code=403,
                message="权限不足"
            ).model_dump()
        )
    
    # 如果不是管理员，不允许修改角色
    if current_user.role != "admin" and user_update.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Response(
                code=403,
                message="无权修改用户角色"
            ).model_dump()
        )
    
    logger.info(f"Updating user: {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="用户不存在"
            ).model_dump()
        )
    
    try:
        # 检查邮箱是否被其他用户使用
        if user_update.email and user_update.email != db_user.email:
            if db.query(User).filter(User.email == user_update.email).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Response(
                        code=400,
                        message="邮箱已被使用"
                    ).model_dump()
                )
        
        # 更新用户信息
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        logger.info(f"User updated successfully: {user_id}")
        return Response(
            code=200,
            message="更新成功",
            data=UserResponse.model_validate(db_user)
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="更新用户失败"
            ).model_dump()
        )

@router.delete("/users/{user_id}", response_model=Response, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查权限
    check_admin_permission(current_user)
    
    logger.info(f"Deleting user: {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="用户不存在"
            ).model_dump()
        )
    
    try:
        db.delete(db_user)
        db.commit()
        logger.info(f"User deleted successfully: {user_id}")
        return Response(
            code=200,
            message="删除成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="删除用户失败"
            ).model_dump()
        )

@router.delete("/batch-users", response_model=Response, status_code=status.HTTP_200_OK)
async def batch_delete_users(
    request: BatchDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查权限
    check_admin_permission(current_user)
    
    logger.info(f"Batch deleting users with ids: {request.ids}")
    try:
        deleted_count = db.query(User).filter(User.id.in_(request.ids)).delete(synchronize_session=False)
        db.commit()
        logger.info(f"Successfully deleted {deleted_count} users")
        return Response(
            code=200,
            message=f"成功删除 {deleted_count} 个用户"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch deleting users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="批量删除用户失败"
            ).model_dump()
        )

@router.put("/users/{user_id}/avatar", response_model=Response[UserResponse])
async def update_user_avatar(
    user_id: int,
    avatar_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户头像"""
    # 检查权限（允许用户更新自己的头像）
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Response(
                code=403,
                message="权限不足"
            ).model_dump()
        )
    
    logger.info(f"Updating avatar for user: {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="用户不存在"
            ).model_dump()
        )
    
    try:
        db_user.avatar = avatar_data.get("avatar")
        db_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        
        # 更新缓存中的用户信息
        user_data = {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "department": db_user.department,
            "role": db_user.role,
            "avatar": db_user.avatar,
            "created_at": db_user.created_at.isoformat()
        }
        cache_user(db_user.id, user_data)
        
        logger.info(f"Avatar updated successfully for user: {user_id}")
        return Response(
            code=200,
            message="头像更新成功",
            data=UserResponse.model_validate(db_user)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating avatar: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="头像更新失败"
            ).model_dump()
        )