from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from ..schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, ArticleQuery
from ..schemas.response import Response
from ..models.article import Article
from ..models.category import Category
from ..models.tag import Tag
from ..database import get_db
from ..logger import setup_logger
from sqlalchemy import or_
from ..utils.slug import generate_slug

logger = setup_logger("articles")
router = APIRouter()

@router.post("/articles", response_model=Response[ArticleResponse], status_code=status.HTTP_201_CREATED)
async def create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Creating new article: {article.title}")
    
    try:
        # 验证分类是否存在
        categories = []
        if article.category_ids:
            categories = db.query(Category).filter(Category.id.in_(article.category_ids)).all()
            if len(categories) != len(article.category_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Response(
                        code=400,
                        message="部分分类不存在"
                    ).model_dump()
                )
        
        # 验证标签是否存在
        tags = []
        if article.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(article.tag_ids)).all()
            if len(tags) != len(article.tag_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Response(
                        code=400,
                        message="部分标签不存在"
                    ).model_dump()
                )
        
        # 如果没有提供 slug，则根据标题生成
        if not article.slug:
            article.slug = generate_slug(article.title)
        
        # 创建文章
        db_article = Article(
            title=article.title,
            slug=article.slug,
            content=article.content,
            summary=article.summary,
            meta_title=article.meta_title,
            meta_description=article.meta_description,
            keywords=article.keywords,
            status=article.status,
            is_featured=article.is_featured,
            allow_comments=article.allow_comments,
            author_id=1  # TODO: 从当前用户获取
        )
        
        db.add(db_article)
        db.flush()  # 获取文章ID但不提交事务
        
        # 添加分类和标签关联
        if categories:
            db_article.categories = categories
        if tags:
            db_article.tags = tags
        
        db.commit()
        db.refresh(db_article)
        
        logger.info(f"Article created successfully: {db_article.id}")
        return Response[ArticleResponse](
            code=201,
            message="文章创建成功",
            data=ArticleResponse.model_validate(db_article)
        )
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating article: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="创建文章失败"
            ).model_dump()
        )

@router.get("/articles", response_model=Response[dict], status_code=status.HTTP_200_OK)
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    keyword: str = Query(None),
    status: str = Query(None),
    is_featured: bool = Query(None),
    author_id: int = Query(None),
    title: str = Query(None),
    db: Session = Depends(get_db)
):
    """获取文章列表"""
    logger.info(f"Listing articles with skip: {skip}, limit: {limit}, keyword: {keyword}, title: {title}")
    
    # 构建查询
    query = db.query(Article)
    
    # 应用过滤条件
    if keyword:
        search_keyword = f"%{keyword}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_keyword),
                Article.content.ilike(search_keyword),
                Article.summary.ilike(search_keyword)
            )
        )
    
    if title:
        query = query.filter(Article.title.ilike(f"%{title}%"))
    
    if status:
        query = query.filter(Article.status == status)
    
    if is_featured is not None:
        query = query.filter(Article.is_featured == is_featured)
    
    if author_id:
        query = query.filter(Article.author_id == author_id)
    
    # 获取总数
    total = query.count()
    
    # 分页
    articles = query.offset(skip).limit(limit).all()
    
    # 序列化文章数据
    article_responses = []
    for article in articles:
        article_dict = {
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "content": article.content,
            "summary": article.summary,
            "meta_title": article.meta_title,
            "meta_description": article.meta_description,
            "keywords": article.keywords,
            "status": article.status,
            "is_featured": article.is_featured,
            "allow_comments": article.allow_comments,
            "created_at": article.created_at,
            "updated_at": article.updated_at,
            "published_at": article.published_at,
            "view_count": article.view_count,
            "comment_count": article.comment_count,
            "like_count": article.like_count,
            "author": {
                "id": article.author.id,
                "username": article.author.username,
                "full_name": article.author.full_name
            } if article.author else None,
            "categories": [
                {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug
                }
                for category in article.categories
            ],
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "slug": tag.slug
                }
                for tag in article.tags
            ]
        }
        article_responses.append(article_dict)
    
    logger.info(f"Found {len(articles)} articles out of {total} total matches")
    return Response[dict](
        code=200,
        message="查询成功",
        data={
            "data": article_responses,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )

@router.get("/articles/{article_id}", response_model=Response[ArticleResponse], status_code=status.HTTP_200_OK)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """获取文章详情"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="文章不存在"
            ).model_dump()
        )
    
    return Response[ArticleResponse](
        code=200,
        message="查询成功",
        data=ArticleResponse.model_validate(article)
    )

@router.put("/articles/{article_id}", response_model=Response[ArticleResponse], status_code=status.HTTP_200_OK)
async def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    db: Session = Depends(get_db)
):
    """更新文章"""
    # 检查文章是否存在
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="文章不存在"
            ).model_dump()
        )
    
    try:
        # 更新文章基本信息
        for key, value in article_update.model_dump(exclude_unset=True).items():
            if key not in ["category_ids", "tag_ids"]:
                setattr(article, key, value)
        
        # 更新分类
        if article_update.category_ids is not None:
            categories = db.query(Category).filter(Category.id.in_(article_update.category_ids)).all()
            if len(categories) != len(article_update.category_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Response(
                        code=400,
                        message="部分分类不存在"
                    ).model_dump()
                )
            article.categories = categories
        
        # 更新标签
        if article_update.tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(article_update.tag_ids)).all()
            if len(tags) != len(article_update.tag_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Response(
                        code=400,
                        message="部分标签不存在"
                    ).model_dump()
                )
            article.tags = tags
        
        db.commit()
        db.refresh(article)
        
        logger.info(f"Article updated successfully: {article.id}")
        return Response[ArticleResponse](
            code=200,
            message="更新成功",
            data=ArticleResponse.model_validate(article)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating article: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="更新文章失败"
            ).model_dump()
        )

@router.delete("/articles/{article_id}", response_model=Response, status_code=status.HTTP_200_OK)
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """删除文章"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="文章不存在"
            ).model_dump()
        )
    
    try:
        db.delete(article)
        db.commit()
        
        logger.info(f"Article deleted successfully: {article_id}")
        return Response(
            code=200,
            message="删除成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting article: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="删除文章失败"
            ).model_dump()
        ) 