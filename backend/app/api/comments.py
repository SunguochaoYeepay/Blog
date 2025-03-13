from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.comment import Comment
from app.models.article import Article
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.comment import CommentCreate, CommentResponse
from app.logger import setup_logger
from app.api.auth import get_current_user

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
                detail="文章不存在"
            )
        
        if not article.allow_comments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该文章不允许评论"
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
        
        logger.info(f"Comment created successfully: {db_comment.id}")
        return ResponseModel(
            code=status.HTTP_201_CREATED,
            message="评论创建成功",
            data=db_comment
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating comment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建评论失败"
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
        
        return ResponseModel(
            code=200,
            message="查询成功",
            data=comments
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comments: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取评论失败"
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