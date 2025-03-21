from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagResponse, TagUpdate, TagCreate
from app.schemas.response import Response
from app.schemas.pagination import PaginationParams, PaginatedResponse

router = APIRouter(
    tags=["tags"]
)

@router.post("", response_model=Response[TagResponse])
def create_tag(
    tag_create: TagCreate,
    db: Session = Depends(get_db)
) -> Any:
    """创建标签
    
    Args:
        tag_create: 创建的标签数据
        db: 数据库会话
    """
    # 检查标签名称是否已存在
    if db.query(Tag).filter(Tag.name == tag_create.name).first():
        raise HTTPException(status_code=400, detail="标签名称已存在")
    
    try:
        # 创建新标签
        tag = Tag(**tag_create.model_dump())
        db.add(tag)
        db.commit()
        db.refresh(tag)
        
        # 返回创建的标签
        return Response(
            code=200,
            message="创建标签成功",
            data=tag
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

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
    try:
        query = db.query(Tag)
        
        # 计算总数和总页数
        total = query.count()
        tags = query.offset(pagination.skip).limit(pagination.page_size).all()
        
        # 返回分页响应
        return Response(
            code=200,
            message="获取标签列表成功",
            data={
                "items": tags,
                "total": total,
                "page": pagination.page,
                "page_size": pagination.page_size,
                "total_pages": (total + pagination.page_size - 1) // pagination.page_size
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{tag_id}", response_model=Response[TagResponse])
def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """更新标签
    
    Args:
        tag_id: 标签ID
        tag_update: 更新的标签数据
        db: 数据库会话
    """
    try:
        # 查找标签
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="标签不存在")
        
        # 检查名称是否已被其他标签使用
        if tag_update.name and tag_update.name != tag.name:
            existing_tag = db.query(Tag).filter(Tag.name == tag_update.name).first()
            if existing_tag:
                raise HTTPException(status_code=400, detail="标签名称已存在")
        
        # 更新标签数据
        for field, value in tag_update.model_dump(exclude_unset=True).items():
            setattr(tag, field, value)
        
        # 保存到数据库
        db.commit()
        db.refresh(tag)
        
        # 返回更新后的标签
        return Response(
            code=200,
            message="更新标签成功",
            data=tag
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{tag_id}", response_model=Response)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """删除标签
    
    Args:
        tag_id: 标签ID
        db: 数据库会话
    """
    try:
        # 查找标签
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="标签不存在")
        
        # 检查标签是否被文章使用
        if tag.articles:
            raise HTTPException(status_code=400, detail="标签已被文章使用，无法删除")
        
        # 删除标签
        db.delete(tag)
        db.commit()
        
        # 返回成功响应
        return Response(
            code=200,
            message="删除标签成功"
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))