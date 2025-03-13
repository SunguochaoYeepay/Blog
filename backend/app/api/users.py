from fastapi import APIRouter, Depends, HTTPException, Query, status
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

# 创建用户模块的日志记录器
logger = setup_logger("users")

router = APIRouter()

@router.post("/users", response_model=Response[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
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
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    logger.info(f"Searching users with query: username={query.username} email={query.email} department={query.department} role={query.role}, skip: {skip}, limit: {limit}")
    
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

        db_users = db.query(User)
        if filters:
            logger.debug(f"Applying filters: {filters}")
            db_users = db_users.filter(or_(*filters))
        
        total = db_users.count()
        users = db_users.offset(skip).limit(limit).all()
        
        logger.info(f"Found {len(users)} users out of {total} total matches")
        return Response(
            code=200,
            message="获取成功",
            data={
                "data": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "department": user.department,
                        "role": user.role,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at
                    } for user in users
                ],
                "total": total
            }
        )
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
    db: Session = Depends(get_db)
):
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
    db: Session = Depends(get_db)
):
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
    db: Session = Depends(get_db)
):
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