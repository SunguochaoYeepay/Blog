from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag
from app.models.user import User
from app.schemas.response import Response
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse
)
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.utils.slug import slugify

router = APIRouter(
    tags=["articles"]
)

@router.post("", response_model=Response[ArticleResponse])
def create_article(
    *,
    db: Session = Depends(deps.get_db),
    article_in: ArticleCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """创建文章"""
    try:
        # 验证分类和标签是否存在
        categories = []
        tags = []
        
        if article_in.category_ids:
            categories = db.query(Category).filter(Category.id.in_(article_in.category_ids)).all()
            if len(categories) != len(article_in.category_ids):
                raise HTTPException(status_code=422, detail="分类不存在")
        
        if article_in.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(article_in.tag_ids)).all()
            if len(tags) != len(article_in.tag_ids):
                raise HTTPException(status_code=422, detail="标签不存在")
        
        # 如果没有提供 slug，则从标题生成
        if not article_in.slug:
            article_in.slug = slugify(article_in.title)
        
        # 检查 slug 是否已存在
        if db.query(Article).filter(Article.slug == article_in.slug).first():
            raise HTTPException(status_code=400, detail="文章链接已存在")
        
        db_article = Article(
            title=article_in.title,
            slug=article_in.slug,
            content=article_in.content,
            summary=article_in.summary,
            meta_title=article_in.meta_title,
            meta_description=article_in.meta_description,
            keywords=article_in.keywords,
            status=article_in.status,
            is_featured=article_in.is_featured,
            allow_comments=article_in.allow_comments,
            is_published=article_in.is_published,
            author_id=current_user.id
        )
        
        # 添加分类和标签
        if categories:
            db_article.categories = categories
        if tags:
            db_article.tags = tags
        
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        return Response(
            code=201,
            message="创建文章成功",
            data=db_article
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=Response[PaginatedResponse[ArticleResponse]])
def get_articles(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(deps.get_db)
):
    """获取文章列表
    
    Args:
        pagination: 分页参数
        search: 搜索关键词
        category_id: 分类ID
        tag_id: 标签ID
        status: 文章状态
    """
    try:
        query = db.query(Article).options(
            joinedload(Article.author),
            joinedload(Article.categories),
            joinedload(Article.tags)
        )
        
        # 搜索
        if search:
            query = query.filter(
                Article.title.ilike(f"%{search}%") | Article.content.ilike(f"%{search}%")
            )
        
        # 筛选
        if category_id:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                raise HTTPException(status_code=404, detail="分类不存在")
            query = query.filter(Article.categories.any(id=category_id))
        
        if tag_id:
            tag = db.query(Tag).filter(Tag.id == tag_id).first()
            if not tag:
                raise HTTPException(status_code=404, detail="标签不存在")
            query = query.filter(Article.tags.any(id=tag_id))
        
        if status:
            query = query.filter(Article.status == status)
        
        # 计算总数和总页数
        total = query.count()
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        
        # 获取分页数据
        offset = (pagination.page - 1) * pagination.page_size
        articles = query.offset(offset).limit(pagination.page_size).all()
        
        return Response(
            code=200,
            message="获取文章列表成功",
            data={
                "items": articles,
                "total": total,
                "page": pagination.page,
                "page_size": pagination.page_size,
                "total_pages": total_pages
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{article_id}", response_model=Response[ArticleResponse])
def get_article(article_id: int, db: Session = Depends(deps.get_db)):
    """获取文章详情"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        return Response(
            code=200,
            message="获取文章详情成功",
            data=article
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{article_id}", response_model=Response[ArticleResponse])
def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """更新文章"""
    try:
        db_article = db.query(Article).filter(Article.id == article_id).first()
        if not db_article:
            raise HTTPException(status_code=404, detail="文章不存在")
        if db_article.author_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 验证分类和标签是否存在
        if article_update.category_ids is not None:
            categories = db.query(Category).filter(Category.id.in_(article_update.category_ids)).all()
            if len(categories) != len(article_update.category_ids):
                raise HTTPException(status_code=422, detail="分类不存在")
            db_article.categories = categories
        
        if article_update.tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(article_update.tag_ids)).all()
            if len(tags) != len(article_update.tag_ids):
                raise HTTPException(status_code=422, detail="标签不存在")
            db_article.tags = tags
        
        # 更新其他字段
        for field, value in article_update.model_dump(exclude={'category_ids', 'tag_ids'}, exclude_unset=True).items():
            setattr(db_article, field, value)
        
        # 如果标题改变，更新 slug
        if article_update.title:
            new_slug = slugify(article_update.title)
            # 检查新的 slug 是否已被其他文章使用
            existing_article = db.query(Article).filter(
                Article.slug == new_slug,
                Article.id != article_id
            ).first()
            if existing_article:
                raise HTTPException(status_code=400, detail="文章链接已存在")
            db_article.slug = new_slug
        
        db.commit()
        db.refresh(db_article)
        return Response(
            code=200,
            message="更新文章成功",
            data=db_article
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{article_id}", response_model=Response)
def delete_article(
    article_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """删除文章"""
    try:
        db_article = db.query(Article).filter(Article.id == article_id).first()
        if not db_article:
            raise HTTPException(status_code=404, detail="文章不存在")
        if db_article.author_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 检查文章是否有关联的评论
        if db_article.comments:
            raise HTTPException(status_code=400, detail="文章存在评论，无法删除")
        
        db.delete(db_article)
        db.commit()
        return Response(
            code=200,
            message="删除文章成功"
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))