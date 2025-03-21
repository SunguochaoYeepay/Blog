from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse, CategoryUpdate, CategoryCreate
from app.schemas.response import Response
from app.schemas.pagination import PaginationParams, PaginatedResponse

router = APIRouter(
    tags=["categories"]
)

@router.post("", response_model=Response[CategoryResponse])
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate
) -> Any:
    """创建分类
    
    Args:
        category_in: 创建的分类数据
        db: 数据库会话
    """
    # 检查分类名称是否已存在
    if db.query(Category).filter(Category.name == category_in.name).first():
        raise HTTPException(status_code=400, detail="分类名称已存在")
    
    # 如果有父分类，检查父分类是否存在
    if category_in.parent_id:
        parent = db.query(Category).filter(Category.id == category_in.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父分类不存在")
    
    # 检查 slug 是否已存在
    if category_in.slug:
        if db.query(Category).filter(Category.slug == category_in.slug).first():
            raise HTTPException(status_code=400, detail="分类链接已存在")
    
    # 创建新分类
    try:
        category = Category(**category_in.model_dump())
        db.add(category)
        db.commit()
        db.refresh(category)
        
        # 返回创建的分类
        return Response(
            code=200,
            message="创建分类成功",
            data=category
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=Response[PaginatedResponse[CategoryResponse]])
def get_categories(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """获取分类列表
    
    Args:
        pagination: 分页参数
        db: 数据库会话
    """
    query = db.query(Category)
    
    # 计算总数和总页数
    total = query.count()
    categories = query.offset(pagination.skip).limit(pagination.page_size).all()
    
    # 返回分页响应
    return Response(
        code=200,
        message="获取分类列表成功",
        data={
            "items": categories,
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
            "total_pages": (total + pagination.page_size - 1) // pagination.page_size
        }
    )

@router.put("/{category_id}", response_model=Response[CategoryResponse])
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """更新分类
    
    Args:
        category_id: 分类ID
        category_update: 更新的分类数据
        db: 数据库会话
    """
    # 查找分类
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    try:
        # 更新分类数据
        for field, value in category_update.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        
        # 保存到数据库
        db.commit()
        db.refresh(category)
        
        # 返回更新后的分类
        return Response(
            code=200,
            message="更新分类成功",
            data=category
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{category_id}", response_model=Response)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """删除分类
    
    Args:
        category_id: 分类ID
        db: 数据库会话
    """
    # 查找分类
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查是否有子分类
    children = db.query(Category).filter(Category.parent_id == category_id).all()
    if children:
        raise HTTPException(status_code=400, detail="该分类下有子分类，无法删除")
    
    try:
        # 删除分类
        db.delete(category)
        db.commit()
        
        # 返回成功响应
        return Response(
            code=200,
            message="删除分类成功"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))