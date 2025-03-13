from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.response import Response
from app.api.auth import get_current_user
from app.models.user import User
from datetime import datetime
import logging
from app.utils.slug import generate_slug

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/categories", response_model=Response[CategoryResponse], status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建分类"""
    logger.info(f"Creating new category: {category.name}")
    
    # 检查分类名称是否已存在
    if db.query(Category).filter(Category.name == category.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Response(
                code=400,
                message="分类名称已存在"
            ).model_dump()
        )
    
    try:
        # 创建分类
        db_category = Category(
            name=category.name,
            slug=category.slug or generate_slug(category.name),
            description=category.description,
            parent_id=category.parent_id
        )
        
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        logger.info(f"Category created successfully: {db_category.id}")
        return Response[CategoryResponse](
            code=201,
            message="分类创建成功",
            data=CategoryResponse.model_validate(db_category)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="创建分类失败"
            ).model_dump()
        )

@router.get("/categories", response_model=Response[List[CategoryResponse]])
async def get_categories(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    try:
        categories = db.query(Category).filter(Category.parent_id.is_(None)).offset(skip).limit(limit).all()
        total = db.query(Category).filter(Category.parent_id.is_(None)).count()
        return Response[List[CategoryResponse]](
            code=200,
            message="获取成功",
            data=[CategoryResponse.model_validate(category) for category in categories],
            meta={"total": total, "skip": skip, "limit": limit}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message=f"获取失败: {str(e)}",
                data=None
            ).model_dump()
        )

@router.get("/categories/{category_id}", response_model=Response[CategoryResponse])
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """获取单个分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="分类不存在",
                data=None
            ).model_dump()
        )
    return Response[CategoryResponse](
        code=200,
        message="获取成功",
        data=CategoryResponse.model_validate(category)
    )

@router.put("/categories/{category_id}", response_model=Response[CategoryResponse])
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新分类"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="分类不存在",
                data=None
            ).model_dump()
        )

    try:
        update_data = category_update.model_dump(exclude_unset=True)
        
        # 检查父分类是否存在
        if "parent_id" in update_data and update_data["parent_id"]:
            parent = db.query(Category).filter(Category.id == update_data["parent_id"]).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Response(
                        code=400,
                        message="父分类不存在",
                        data=None
                    ).model_dump()
                )
                
        # 如果更新了名称但没有提供新的 slug，则自动生成
        if "name" in update_data and "slug" not in update_data:
            update_data["slug"] = generate_slug(update_data["name"])
            
        for key, value in update_data.items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
        return Response[CategoryResponse](
            code=200,
            message="更新成功",
            data=CategoryResponse.model_validate(db_category)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Response(
                code=400,
                message="分类已存在",
                data=None
            ).model_dump()
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message=f"更新失败: {str(e)}",
                data=None
            ).model_dump()
        )

@router.delete("/categories/{category_id}", response_model=Response)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除分类"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="分类不存在",
                data=None
            ).model_dump()
        )

    try:
        # 检查是否有子分类
        if db.query(Category).filter(Category.parent_id == category_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Response(
                    code=400,
                    message="请先删除子分类",
                    data=None
                ).model_dump()
            )
            
        db.delete(db_category)
        db.commit()
        return Response(
            code=200,
            message="删除成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message=f"删除失败: {str(e)}",
                data=None
            ).model_dump()
        ) 