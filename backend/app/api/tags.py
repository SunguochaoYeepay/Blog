from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate, TagResponse
from app.schemas.response import Response
from app.api.auth import get_current_user
from app.models.user import User
from datetime import datetime
import logging
from app.utils.slug import generate_slug

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/tags", response_model=Response[TagResponse], status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建标签"""
    try:
        # 如果没有提供 slug，则根据名称生成
        if not tag.slug:
            tag.slug = generate_slug(tag.name)
            
        db_tag = Tag(
            name=tag.name,
            slug=tag.slug,
            description=tag.description,
            created_at=datetime.utcnow()
        )
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return Response[TagResponse](
            code=201,
            message="标签创建成功",
            data=TagResponse.model_validate(db_tag)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Response(
                code=400,
                message="标签名称已存在",
                data=None
            ).model_dump()
        )

@router.get("/tags", response_model=Response[List[TagResponse]])
async def get_tags(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取标签列表"""
    tags = db.query(Tag).offset(skip).limit(limit).all()
    total = db.query(Tag).count()
    return Response[List[TagResponse]](
        code=200,
        message="获取成功",
        data=[TagResponse.model_validate(tag) for tag in tags]
    )

@router.get("/tags/{tag_id}", response_model=Response[TagResponse])
async def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """获取单个标签"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="标签不存在",
                data=None
            ).model_dump()
        )
    return Response[TagResponse](
        code=200,
        message="获取成功",
        data=TagResponse.model_validate(tag)
    )

@router.put("/tags/{tag_id}", response_model=Response[TagResponse])
async def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新标签"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="标签不存在",
                data=None
            ).model_dump()
        )
    
    try:
        update_data = tag_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_tag, key, value)
        db_tag.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_tag)
        return Response[TagResponse](
            code=200,
            message="更新成功",
            data=TagResponse.model_validate(db_tag)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Response(
                code=400,
                message="标签名称已存在",
                data=None
            ).model_dump()
        )

@router.delete("/tags/{tag_id}", response_model=Response)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除标签"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="标签不存在",
                data=None
            ).model_dump()
        )
    
    try:
        db.delete(db_tag)
        db.commit()
        return Response(
            code=200,
            message="删除成功",
            data=None
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="删除标签失败",
                data=None
            ).model_dump()
        ) 