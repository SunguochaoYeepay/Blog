from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, ArticleQuery
from ..models.article import Article
from ..models.article_relationships import ArticleCategory, ArticleTag
from ..database import get_db
from ..logger import setup_logger
from sqlalchemy import or_

logger = setup_logger("articles")
router = APIRouter()

@router.post("/articles/", response_model=ArticleResponse)
async def create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Creating new article: {article.title}")
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
    
    try:
        db.add(db_article)
        db.flush()  # 获取文章ID
        
        # 添加分类关联
        for category_id in article.category_ids:
            db.add(ArticleCategory(article_id=db_article.id, category_id=category_id))
        
        # 添加标签关联
        for tag_id in article.tag_ids:
            db.add(ArticleTag(article_id=db_article.id, tag_id=tag_id))
        
        db.commit()
        db.refresh(db_article)
        logger.info(f"Article created successfully: {db_article.id}")
        return db_article
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating article: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/articles/", response_model=List[ArticleResponse])
async def list_articles(
    query: ArticleQuery = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    logger.info(f"Listing articles with query: {query}, skip: {skip}, limit: {limit}")
    
    # 构建查询
    articles_query = db.query(Article)
    
    # 应用过滤条件
    if query.keyword:
        keyword = f"%{query.keyword}%"
        articles_query = articles_query.filter(
            or_(
                Article.title.ilike(keyword),
                Article.content.ilike(keyword),
                Article.summary.ilike(keyword)
            )
        )
    
    if query.status:
        articles_query = articles_query.filter(Article.status == query.status)
    
    if query.is_featured is not None:
        articles_query = articles_query.filter(Article.is_featured == query.is_featured)
    
    if query.author_id:
        articles_query = articles_query.filter(Article.author_id == query.author_id)
    
    # 获取总数
    total = articles_query.count()
    
    # 分页
    articles = articles_query.offset(skip).limit(limit).all()
    
    logger.info(f"Found {len(articles)} articles out of {total} total matches")
    return articles

@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching article with id: {article_id}")
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        logger.warning(f"Article not found: {article_id}")
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"Updating article: {article_id}")
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if db_article is None:
        logger.warning(f"Article not found: {article_id}")
        raise HTTPException(status_code=404, detail="Article not found")
    
    try:
        # 更新文章基本信息
        for field, value in article_update.dict(exclude_unset=True).items():
            if field not in ['category_ids', 'tag_ids']:
                setattr(db_article, field, value)
        
        # 更新分类关联
        if article_update.category_ids is not None:
            db.query(ArticleCategory).filter(
                ArticleCategory.article_id == article_id
            ).delete()
            for category_id in article_update.category_ids:
                db.add(ArticleCategory(article_id=article_id, category_id=category_id))
        
        # 更新标签关联
        if article_update.tag_ids is not None:
            db.query(ArticleTag).filter(
                ArticleTag.article_id == article_id
            ).delete()
            for tag_id in article_update.tag_ids:
                db.add(ArticleTag(article_id=article_id, tag_id=tag_id))
        
        db.commit()
        db.refresh(db_article)
        logger.info(f"Article updated successfully: {article_id}")
        return db_article
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating article: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"Deleting article: {article_id}")
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if db_article is None:
        logger.warning(f"Article not found: {article_id}")
        raise HTTPException(status_code=404, detail="Article not found")
    
    try:
        # 删除关联数据
        db.query(ArticleCategory).filter(ArticleCategory.article_id == article_id).delete()
        db.query(ArticleTag).filter(ArticleTag.article_id == article_id).delete()
        
        # 删除文章
        db.delete(db_article)
        db.commit()
        logger.info(f"Article deleted successfully: {article_id}")
        return {"message": "Article deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting article: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 