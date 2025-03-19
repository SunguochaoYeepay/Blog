from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.comment import Comment
from app.models.article import Article
from app.models.user import User
from app.schemas.common import ResponseModel, ErrorResponse
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate, CommentQuery
from app.schemas.response import Response
from app.schemas.pagination import PaginatedResponse
from app.logger import setup_logger
from app.api.auth import get_current_user
from sqlalchemy import or_, and_
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

@router.get("/articles/{article_id}/comments", response_model=Response[PaginatedResponse[CommentResponse]], status_code=status.HTTP_200_OK)
async def get_article_comments(
    article_id: int,
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(10, ge=1, le=100, description="每页大小，1-100之间"),
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
        
        # 获取总数和计算总页数
        total = db.query(Comment).filter(Comment.article_id == article_id).count()
        total_pages = (total + size - 1) // size
        
        # 处理页码超出范围的情况
        if total > 0 and page > total_pages:
            page = total_pages
        
        # 获取分页数据
        offset = (page - 1) * size
        comments = db.query(Comment)\
            .filter(Comment.article_id == article_id)\
            .order_by(Comment.created_at.desc())\
            .offset(offset)\
            .limit(size)\
            .all()
        
        # 处理评论数据
        comment_responses = []
        for comment in comments:
            comment_data = CommentResponse.model_validate(comment).model_dump()
            # 添加点赞数
            try:
                comment_data["like_count"] = get_comment_likes(comment.id)
            except Exception as e:
                logger.error(f"Error getting comment likes: {str(e)}")
                comment_data["like_count"] = 0
            comment_responses.append(comment_data)
            # 缓存评论
            try:
                cache_comment(comment.id, comment_data)
            except Exception as e:
                logger.error(f"Error caching comment: {str(e)}")
        
        # 构造分页响应
        paginated_response = PaginatedResponse[CommentResponse](
            items=comment_responses,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages
        )
        
        return Response[PaginatedResponse[CommentResponse]](
            code=200,
            message="查询成功",
            data=paginated_response
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
    """删除评论及其所有回复"""
    try:
        # 获取评论及其所有回复
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ResponseModel(
                    code=404,
                    message="评论不存在"
                ).model_dump()
            )
        
        # 检查权限（只有评论作者或管理员可以删除）
        if comment.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ResponseModel(
                    code=403,
                    message="没有权限删除此评论"
                ).model_dump()
            )
        
        # 删除所有回复评论
        db.query(Comment).filter(Comment.parent_id == comment_id).delete(synchronize_session='fetch')
        db.flush()
        
        # 删除主评论
        db.delete(comment)
        
        # 提交更改
        db.commit()
        
        # 删除缓存
        delete_comment_cache(comment_id)
        
        logger.info(f"Comment and its replies deleted successfully: {comment_id}")
        return ResponseModel(
            code=200,
            message="删除成功"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting comment and replies: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseModel(
                code=500,
                message="删除评论失败"
            ).model_dump()
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

@router.get("/comments", response_model=Response[PaginatedResponse[CommentResponse]], status_code=status.HTTP_200_OK)
async def get_comments(
    query: CommentQuery = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取评论列表，支持多种筛选条件和多级评论"""
    try:
        # 构建基础查询
        base_query = db.query(Comment)\
            .join(Article, Comment.article_id == Article.id)\
            .join(User, Comment.user_id == User.id)\
            .options(
                joinedload(Comment.article),
                joinedload(Comment.user),
                joinedload(Comment.replies).joinedload(Comment.user)  # 预加载回复及其用户信息
            )

        # 应用筛选条件
        filters = []
        
        # 只查询根评论
        if query.only_root:
            filters.append(Comment.parent_id.is_(None))
            
        # 关键词搜索
        if query.keyword:
            filters.append(Comment.content.ilike(f"%{query.keyword}%"))
            
        # 状态筛选
        if query.status:
            if query.status == "approved":
                filters.append(Comment.is_approved == True)
                filters.append(Comment.is_spam == False)
            elif query.status == "pending":
                filters.append(Comment.is_approved == False)
                filters.append(Comment.is_spam == False)
            elif query.status == "spam":
                filters.append(Comment.is_spam == True)
            # 如果是 "all" 则不添加过滤条件
                
        # 文章标题搜索
        if query.article_title:
            filters.append(Article.title.ilike(f"%{query.article_title}%"))
                
        # 文章ID筛选
        if query.article_id:
            filters.append(Comment.article_id == query.article_id)
            
        # 用户筛选
        if query.user_id:
            filters.append(Comment.user_id == query.user_id)
            
        # 日期筛选
        if query.start_date:
            filters.append(Comment.created_at >= query.start_date)
        
        if query.end_date:
            filters.append(Comment.created_at <= query.end_date)
            
        # 应用所有筛选条件
        if filters:
            base_query = base_query.filter(and_(*filters))
            
        # 获取总数
        total = base_query.count()
        total_pages = (total + query.size - 1) // query.size
        
        # 处理页码超出范围的情况
        if total > 0 and query.page > total_pages:
            query.page = total_pages
            
        # 获取分页数据
        offset = (query.page - 1) * query.size
        comments = base_query\
            .order_by(Comment.created_at.desc())\
            .offset(offset)\
            .limit(query.size)\
            .all()
            
        # 处理评论数据
        comment_responses = []
        for comment in comments:
            # 确保所有必需的布尔字段都有默认值
            comment_dict = {
                "id": comment.id,
                "content": comment.content,
                "article_id": comment.article_id,
                "user_id": comment.user_id,
                "parent_id": comment.parent_id,
                "ip_address": comment.ip_address,
                "user_agent": comment.user_agent,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "is_approved": comment.is_approved if comment.is_approved is not None else False,
                "is_spam": comment.is_spam if comment.is_spam is not None else False,
                "like_count": 0,
                "user_name": comment.user.username if comment.user else None,
                "article_title": comment.article.title if comment.article else None,
                "reply_count": 0,
                "replies": None
            }
            
            comment_data = CommentResponse.model_validate(comment_dict)
            
            # 处理回复
            if query.include_replies and not query.only_root:
                replies = []
                reply_count = 0
                for reply in comment.replies or []:
                    if not reply.is_spam:
                        reply_dict = {
                            "id": reply.id,
                            "content": reply.content,
                            "article_id": reply.article_id,
                            "user_id": reply.user_id,
                            "parent_id": reply.parent_id,
                            "ip_address": reply.ip_address,
                            "user_agent": reply.user_agent,
                            "created_at": reply.created_at,
                            "updated_at": reply.updated_at,
                            "is_approved": reply.is_approved if reply.is_approved is not None else False,
                            "is_spam": reply.is_spam if reply.is_spam is not None else False,
                            "like_count": get_comment_likes(reply.id),
                            "user_name": reply.user.username if reply.user else None,
                            "article_title": reply.article.title if reply.article else None,
                            "reply_count": 0,
                            "replies": None
                        }
                        reply_data = CommentResponse.model_validate(reply_dict)
                        replies.append(reply_data)
                        reply_count += 1
                
                comment_data.replies = replies
                comment_data.reply_count = reply_count
            else:
                comment_data.replies = None
                comment_data.reply_count = len([r for r in (comment.replies or []) if not r.is_spam])
            
            # 添加点赞数
            try:
                comment_data.like_count = get_comment_likes(comment.id)
            except Exception as e:
                logger.error(f"Error getting comment likes: {str(e)}")
                comment_data.like_count = 0
            
            comment_responses.append(comment_data)
            # 缓存评论
            try:
                cache_comment(comment.id, comment_data)
            except Exception as e:
                logger.error(f"Error caching comment: {str(e)}")
            
        # 构造分页响应
        paginated_response = PaginatedResponse[CommentResponse](
            items=comment_responses,
            total=total,
            page=query.page,
            size=query.size,
            total_pages=total_pages
        )
        
        return Response[PaginatedResponse[CommentResponse]](
            code=200,
            message="查询成功",
            data=paginated_response
        )
    except Exception as e:
        logger.error(f"Error getting comments: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取评论失败"
        )

@router.get("/comments/{comment_id}/replies", response_model=Response[List[CommentResponse]], status_code=status.HTTP_200_OK)
async def get_comment_replies(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定评论的回复列表"""
    try:
        # 检查评论是否存在
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
            
        # 获取回复列表
        replies = db.query(Comment)\
            .filter(Comment.parent_id == comment_id)\
            .filter(Comment.is_spam == False)\
            .options(
                joinedload(Comment.user),
                joinedload(Comment.article)
            )\
            .order_by(Comment.created_at.asc())\
            .all()
            
        # 处理回复数据
        reply_responses = []
        for reply in replies:
            reply_data = CommentResponse.model_validate(reply).model_dump()
            reply_data["user_name"] = reply.user.username if reply.user else None
            reply_data["article_title"] = reply.article.title if reply.article else None
            reply_data["like_count"] = get_comment_likes(reply.id)
            reply_responses.append(reply_data)
            
        return Response[List[CommentResponse]](
            code=200,
            message="查询成功",
            data=reply_responses
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting comment replies: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取评论回复失败"
        ) 