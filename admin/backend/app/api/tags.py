from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagResponse
from app.schemas.response import Response
from app.schemas.pagination import PaginationParams, PaginatedResponse

router = APIRouter(
    tags=["tags"]
)

@router.get("", response_model=Response[PaginatedResponse[TagResponse]])
def get_tags(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """获取标签列表
    
    Args:
        pagination: 分页参数
        db: 数据库会话
    """
    query = db.query(Tag)
    
    # 计算总数和总页数
    total = query.count()
    total_pages = (total + pagination.limit - 1) // pagination.limit
    
    # 获取分页数据
    tags = query.offset(pagination.skip).limit(pagination.limit).all()
    
    return Response(
        code=200,
        message="获取标签列表成功",
        data=PaginatedResponse(
            items=tags,
            total=total,
            page=pagination.page,
            size=pagination.limit,
            total_pages=total_pages
        )
    )