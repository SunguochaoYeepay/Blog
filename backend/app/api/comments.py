from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.comment import Comment
from app.models.article import Article
from app.models.user import User
from app.schemas.common import ResponseModel, ErrorResponse
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.schemas.response import Response
from app.logger import setup_logger
from app.api.auth import get_current_user
from ..dependencies.redis import (
    cache_comment,
    get_cached_comment,
    delete_comment_cache,
    toggle_comment_like,
    get_comment_likes
)

logger = setup_logger("comments")
router = APIRouter()

@router.post("/articles/{article_id}/comments", response_model=ResponseModel[CommentResponse], status_code=status.HTTP_201_CREATED)
async def create_comment(
    article_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建评论"""
    try:
        # 检查文章是否存在且允许评论
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ResponseModel(
                    code=404,
                    message="文章不存在"
                ).model_dump()
            )
        
        if not article.allow_comments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ResponseModel(
                    code=400,
                    message="该文章不允许评论"
                ).model_dump()
            )
        
        # 创建评论
        db_comment = Comment(
            content=comment.content,
            article_id=article_id,
            user_id=current_user.id,
            parent_id=comment.parent_id,
            created_at=datetime.utcnow()
        )
        
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        
        # 缓存评论数据
        comment_data = CommentResponse.model_validate(db_comment).model_dump()
        cache_comment(db_comment.id, comment_data)
        
        logger.info(f"Comment created successfully: {db_comment.id}")
        return ResponseModel[CommentResponse](
            code=201,
            message="评论创建成功",
            data=CommentResponse.model_validate(db_comment)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating comment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseModel(
                code=500,
                message="创建评论失败"
            ).model_dump()
        )

@router.get("/articles/{article_id}/comments", response_model=ResponseModel[List[CommentResponse]], status_code=status.HTTP_200_OK)
async def get_article_comments(
    article_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取文章评论列表"""
    try:
        # 检查文章是否存在
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文章不存在"
            )
        
        # 获取评论列表
        comments = db.query(Comment)\
            .filter(Comment.article_id == article_id)\
            .order_by(Comment.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        # 处理评论数据
        comment_responses = []
        for comment in comments:
            comment_data = CommentResponse.model_validate(comment).model_dump()
            # 添加点赞数
            comment_data["like_count"] = get_comment_likes(comment.id)
            comment_responses.append(comment_data)
            # 缓存评论
            cache_comment(comment.id, comment_data)
        
        return ResponseModel(
            code=200,
            message="查询成功",
            data=comment_responses
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comments: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取评论失败"
        )

@router.get("/comments/{comment_id}", response_model=ResponseModel[CommentResponse], status_code=status.HTTP_200_OK)
async def get_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """获取评论详情"""
    # 尝试从缓存获取
    cached_comment = get_cached_comment(comment_id)
    if cached_comment:
        return ResponseModel[CommentResponse](
            code=200,
            message="查询成功",
            data=CommentResponse.model_validate(cached_comment)
        )
    
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseModel(
                code=404,
                message="评论不存在"
            ).model_dump()
        )
    
    # 缓存评论数据
    comment_data = CommentResponse.model_validate(comment).model_dump()
    cache_comment(comment.id, comment_data)
    
    return ResponseModel[CommentResponse](
        code=200,
        message="查询成功",
        data=CommentResponse.model_validate(comment)
    )

@router.put("/comments/{comment_id}", response_model=ResponseModel[CommentResponse], status_code=status.HTTP_200_OK)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新评论"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查权限
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改此评论"
        )
    
    try:
        # 更新评论
        comment.content = comment_update.content
        db.commit()
        db.refresh(comment)
        
        # 更新缓存
        comment_data = CommentResponse.model_validate(comment).model_dump()
        comment_data["like_count"] = get_comment_likes(comment.id)
        cache_comment(comment.id, comment_data)
        
        logger.info(f"Comment updated successfully: {comment_id}")
        return ResponseModel(
            code=200,
            message="更新成功",
            data=CommentResponse.model_validate(comment_data)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating comment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新评论失败"
        )

@router.delete("/comments/{comment_id}", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除评论"""
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
        
        # 检查权限（只有评论作者或管理员可以删除）
        if comment.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限删除此评论"
            )
        
        db.delete(comment)
        db.commit()
        
        # 删除缓存
        delete_comment_cache(comment_id)
        
        logger.info(f"Comment deleted successfully: {comment_id}")
        return ResponseModel(
            code=200,
            message="删除成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting comment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除评论失败"
        )

@router.post("/comments/{comment_id}/like", response_model=ResponseModel[dict], status_code=status.HTTP_200_OK)
async def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """点赞/取消点赞评论"""
    # 检查评论是否存在
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseModel(
                code=404,
                message="评论不存在"
            ).model_dump()
        )
    
    try:
        # 切换点赞状态
        is_liked = toggle_comment_like(comment_id, current_user.id)
        
        # 获取最新点赞数
        like_count = get_comment_likes(comment_id)
        
        logger.info(f"Comment like toggled successfully: {comment_id}")
        return ResponseModel[dict](
            code=200,
            message="操作成功",
            data={
                "is_liked": is_liked,
                "like_count": like_count
            }
        )
    except Exception as e:
        logger.error(f"Error toggling comment like: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseModel(
                code=500,
                message="操作失败"
            ).model_dump()
        )

@router.put("/comments/{comment_id}/approve", response_model=ResponseModel[CommentResponse], status_code=status.HTTP_200_OK)
async def approve_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """审核评论"""
    try:
        # 检查评论是否存在
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
        
        # 检查权限（只有管理员可以审核评论）
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限审核评论"
            )
        
        # 更新评论状态
        comment.is_approved = True
        comment.is_spam = False
        comment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(comment)
        
        logger.info(f"Comment approved successfully: {comment_id}")
        return ResponseModel(
            code=200,
            message="评论审核成功",
            data=comment
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving comment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="审核评论失败"
        )

@router.put("/comments/{comment_id}/mark-spam", response_model=ResponseModel[CommentResponse], status_code=status.HTTP_200_OK)
async def mark_comment_spam(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记评论为垃圾评论"""
    try:
        # 检查评论是否存在
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
        
        # 检查权限（只有管理员可以标记垃圾评论）
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限标记垃圾评论"
            )
        
        # 更新评论状态
        comment.is_spam = True
        comment.is_approved = False
        comment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(comment)
        
        logger.info(f"Comment marked as spam successfully: {comment_id}")
        return ResponseModel(
            code=200,
            message="评论已标记为垃圾评论",
            data=comment
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking comment as spam: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="标记垃圾评论失败"
        ) 