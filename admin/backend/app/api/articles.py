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
from .auth import get_current_user
from ..dependencies.redis import (
    cache_article,
    get_cached_article,
    delete_article_cache,
    increment_article_view,
    get_article_views,
    toggle_article_like,
    get_article_likes,
    cache_multiple_articles,
    get_cached_multiple_articles
)
from ..models.comment import Comment

logger = setup_logger("articles")
router = APIRouter()

@router.post("/articles", response_model=Response[ArticleResponse], status_code=status.HTTP_201_CREATED)
async def create_article(
    article: ArticleCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Creating new article: {article.title}")
    
    try:
        # 验证分类是否存在
        categories = []
        if article.category_ids:
            categories = db.query(Category).filter(Category.id.in_(article.category_ids)).all()
            if len(categories) != len(article.category_ids):
                missing_ids = set(article.category_ids) - set(c.id for c in categories)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Response(
                        code=400,
                        message=f"部分分类不存在: {missing_ids}"
                    ).model_dump()
                )
        
        # 验证标签是否存在
        tags = []
        if article.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(article.tag_ids)).all()
            if len(tags) != len(article.tag_ids):
                missing_ids = set(article.tag_ids) - set(t.id for t in tags)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Response(
                        code=400,
                        message=f"部分标签不存在: {missing_ids}"
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
            author_id=current_user.id  # 使用当前用户的ID
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
        
        # 缓存新文章
        article_data = ArticleResponse.model_validate(db_article).model_dump()
        cache_article(db_article.id, article_data)
        
        # 清除文章列表缓存
        delete_article_cache("recent")
        delete_article_cache("featured")
        
        logger.info(f"Article created successfully: {db_article.id}")
        return Response[ArticleResponse](
            code=201,
            message="文章创建成功",
            data=ArticleResponse.model_validate(db_article)
        )
    except HTTPException as e:
        db.rollback()
        logger.error(f"Error creating article (HTTP): {str(e.detail)}")
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating article: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message=f"创建文章失败: {str(e)}"
            ).model_dump()
        )

@router.get("/articles", response_model=Response[dict], status_code=status.HTTP_200_OK)
async def list_articles(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str = Query(None, description="搜索关键词"),
    status: str = Query(None, description="文章状态"),
    is_featured: bool = Query(None, description="是否精选"),
    author_id: int = Query(None, description="作者ID"),
    title: str = Query(None, description="文章标题"),
    db: Session = Depends(get_db)
):
    """获取文章列表"""
    logger.info(f"Listing articles with page: {page}, size: {size}, keyword: {keyword}, title: {title}")
    
    # 如果没有过滤条件，尝试从缓存获取
    if not any([keyword, status, is_featured, author_id, title]) and page == 1:
        cached_articles = get_cached_multiple_articles("recent")
        if cached_articles:
            total = len(cached_articles)
            total_pages = (total + size - 1) // size
            return Response[dict](
                code=200,
                message="查询成功",
                data={
                    "items": cached_articles[:size],
                    "total": total,
                    "page": page,
                    "size": size,
                    "total_pages": total_pages
                }
            )
    
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
    
    # 获取总数和计算总页数
    total = query.count()
    total_pages = (total + size - 1) // size
    
    # 处理页码超出范围的情况
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # 获取分页数据
    offset = (page - 1) * size
    articles = query.order_by(Article.created_at.desc()).offset(offset).limit(size).all()
    
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
            "view_count": get_article_views(article.id),  # 从Redis获取浏览量
            "like_count": get_article_likes(article.id),  # 从Redis获取点赞数
            "comment_count": article.comment_count,
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
    
    # 如果是获取首页文章，缓存结果
    if not any([keyword, status, is_featured, author_id, title]) and page == 1:
        cache_multiple_articles(article_responses, "recent")
    
    logger.info(f"Found {len(articles)} articles out of {total} total matches")
    return Response[dict](
        code=200,
        message="查询成功",
        data={
            "items": article_responses,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size
        }
    )

@router.get("/articles/{article_id}", response_model=Response[ArticleResponse], status_code=status.HTTP_200_OK)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """获取文章详情"""
    # 尝试从缓存获取
    cached_article = get_cached_article(article_id)
    if cached_article:
        # 增加浏览次数
        increment_article_view(article_id)
        return Response[ArticleResponse](
            code=200,
            message="查询成功",
            data=ArticleResponse.model_validate(cached_article)
        )
    
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                code=404,
                message="文章不存在"
            ).model_dump()
        )
    
    # 增加浏览次数
    increment_article_view(article_id)
    
    # 缓存文章数据
    article_data = ArticleResponse.model_validate(article).model_dump()
    article_data["view_count"] = get_article_views(article_id)
    article_data["like_count"] = get_article_likes(article_id)
    cache_article(article_id, article_data)
    
    return Response[ArticleResponse](
        code=200,
        message="查询成功",
        data=ArticleResponse.model_validate(article_data)
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
        
        # 更新缓存
        article_data = ArticleResponse.model_validate(article).model_dump()
        cache_article(article.id, article_data)
        
        # 清除文章列表缓存
        delete_article_cache("recent")
        delete_article_cache("featured")
        
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
    try:
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
        
        # 删除文章的分类关联
        article.categories = []
        
        # 删除文章的标签关联
        article.tags = []
        
        # 刷新会话以确保关联更新被保存
        db.flush()
        
        # 删除文章的评论
        db.query(Comment).filter(Comment.article_id == article_id).delete(synchronize_session='fetch')
        
        # 刷新会话以确保评论删除被保存
        db.flush()
        
        # 删除文章本身
        db.delete(article)
        
        # 提交所有更改
        db.commit()
        
        # 删除缓存
        delete_article_cache(article_id)
        delete_article_cache("recent")
        delete_article_cache("featured")
        
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

@router.post("/articles/{article_id}/like", response_model=Response[dict])
async def like_article(
    article_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """点赞/取消点赞文章"""
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
        # 切换点赞状态
        is_liked = toggle_article_like(article_id, current_user.id)
        
        # 获取最新点赞数
        like_count = get_article_likes(article_id)
        
        return Response[dict](
            code=200,
            message="操作成功",
            data={
                "is_liked": is_liked,
                "like_count": like_count
            }
        )
    except Exception as e:
        logger.error(f"Error toggling article like: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Response(
                code=500,
                message="操作失败"
            ).model_dump()
        ) 