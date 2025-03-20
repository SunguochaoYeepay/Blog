from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse
from app.schemas.response import Response
from app.schemas.pagination import PaginationParams, PaginatedResponse

router = APIRouter(
    tags=["categories"]
)

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
    total_pages = (total + pagination.limit - 1) // pagination.limit
    
    # 获取分页数据
    categories = query.offset(pagination.skip).limit(pagination.limit).all()
    
    return Response(
        code=200,
        message="获取分类列表成功",
        data=PaginatedResponse(
            items=categories,
            total=total,
            page=pagination.page,
            size=pagination.limit,
            total_pages=total_pages
        )
    )