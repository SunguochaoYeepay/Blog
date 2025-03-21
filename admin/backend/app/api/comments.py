from typing import Any, List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, ConfigDict

from app.api import deps
from app.database import get_db
from app.models.comment import Comment
from app.models.user import User
from app.models.article import Article
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse, CommentQuery
from app.schemas.response import Response
from app.schemas.pagination import PaginationParams, PaginatedResponse

router = APIRouter(
    tags=["comments"]
)

class BatchCommentIds(BaseModel):
    """批量评论ID请求模型"""
    comment_ids: List[int]
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

@router.get("", response_model=Response[PaginatedResponse[CommentResponse]])
def get_comments(
    pagination: PaginationParams = Depends(),
    keyword: str = Query(None),
    status: str = Query(None),
    article_id: int = Query(None),
    article_title: str = Query(None),
    user_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    include_replies: bool = Query(True),
    only_root: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """获取评论列表，支持多种筛选条件"""
    try:
        query = db.query(Comment)
        
        # 应用筛选条件
        if keyword:
            query = query.filter(Comment.content.ilike(f"%{keyword}%"))
        if status:
            if status == "approved":
                query = query.filter(Comment.is_approved == True)
            elif status == "pending":
                query = query.filter(Comment.is_approved == False, Comment.is_spam == False)
            elif status == "spam":
                query = query.filter(Comment.is_spam == True)
            elif status != "all":  # 添加对 "all" 状态的支持
                raise HTTPException(status_code=400, detail="无效的状态值，支持的值：all、approved、pending、spam")
        
        if article_id:
            article = db.query(Article).filter(Article.id == article_id).first()
            if not article:
                raise HTTPException(status_code=404, detail="文章不存在")
            query = query.filter(Comment.article_id == article_id)
            
        if article_title:
            query = query.join(Article).filter(Article.title.ilike(f"%{article_title}%"))
            
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            query = query.filter(Comment.user_id == user_id)
            
        if start_date:
            query = query.filter(Comment.created_at >= start_date)
        if end_date:
            query = query.filter(Comment.created_at <= end_date)
        if only_root:
            query = query.filter(Comment.parent_id == None)
        
        # 计算总数和总页数
        total = query.count()
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        
        # 获取分页数据
        comments = query.offset(pagination.skip).limit(pagination.page_size).all()
        
        # 处理评论数据
        comment_responses = []
        for comment in comments:
            comment_dict = CommentResponse.model_validate(comment).model_dump()
            # 添加用户名和文章标题
            comment_dict["user_name"] = comment.user.username if comment.user else None
            comment_dict["article_title"] = comment.article.title if comment.article else None
            # 计算回复数
            comment_dict["reply_count"] = db.query(Comment).filter(Comment.parent_id == comment.id).count()
            comment_responses.append(CommentResponse(**comment_dict))
        
        return Response(
            code=200,
            message="获取评论列表成功",
            data=PaginatedResponse(
                items=comment_responses,
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=total_pages
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("", response_model=Response[CommentResponse])
def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """创建新评论"""
    try:
        # 检查文章是否存在
        article = db.query(Article).filter(Article.id == comment_data.article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        # 检查文章是否允许评论
        if not article.allow_comments:
            raise HTTPException(status_code=403, detail="该文章不允许评论")
        
        # 如果指定了父评论，检查父评论是否存在
        if comment_data.parent_id:
            parent_comment = db.query(Comment).filter(Comment.id == comment_data.parent_id).first()
            if not parent_comment:
                raise HTTPException(status_code=404, detail="父评论不存在")
            if parent_comment.article_id != comment_data.article_id:
                raise HTTPException(status_code=400, detail="父评论必须属于同一篇文章")
            # 检查父评论是否已被标记为垃圾评论
            if parent_comment.is_spam:
                raise HTTPException(status_code=400, detail="无法回复垃圾评论")
        
        # 创建新评论
        comment = Comment(
            content=comment_data.content,
            article_id=comment_data.article_id,
            user_id=current_user.id,
            parent_id=comment_data.parent_id,
            is_approved=False,  # 默认需要审核
            is_spam=False
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        # 构建响应数据
        comment_dict = CommentResponse.model_validate(comment).model_dump()
        comment_dict["user_name"] = current_user.username
        comment_dict["article_title"] = article.title
        comment_dict["reply_count"] = 0
        
        return Response(
            code=200,
            message="创建评论成功",
            data=CommentResponse(**comment_dict)
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tree/{article_id}", response_model=Response[List[CommentResponse]])
def get_comment_tree(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """获取文章评论的树状结构"""
    try:
        # 检查文章是否存在
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        # 获取所有评论，并按创建时间排序
        comments = db.query(Comment).filter(
            Comment.article_id == article_id
        ).order_by(Comment.created_at.desc()).all()
        
        # 构建评论字典，用于快速查找
        comment_dict = {}
        root_comments = []
        
        # 第一遍遍历：构建评论字典
        for comment in comments:
            comment_data = {
                "id": comment.id,
                "content": comment.content,
                "article_id": comment.article_id,
                "user_id": comment.user_id,
                "parent_id": comment.parent_id,
                "is_approved": comment.is_approved,
                "is_spam": comment.is_spam,
                "ip_address": comment.ip_address,
                "user_agent": comment.user_agent,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "user_name": comment.user.username if comment.user else None,
                "article_title": comment.article.title if comment.article else None,
                "reply_count": 0,
                "replies": []
            }
            comment_dict[comment.id] = comment_data
            
            # 如果是根评论，添加到根评论列表
            if comment.parent_id is None:
                root_comments.append(comment_data)
        
        # 第二遍遍历：构建树结构
        for comment in comments:
            if comment.parent_id is not None:
                parent_data = comment_dict.get(comment.parent_id)
                if parent_data:
                    parent_data["replies"].append(comment_dict[comment.id])
                    parent_data["reply_count"] += 1
        
        # 将字典数据转换为 Pydantic 模型
        root_responses = []
        for comment_data in root_comments:
            # 递归转换子评论
            def convert_to_response(comment_data):
                replies = [convert_to_response(reply) for reply in comment_data["replies"]]
                comment_data["replies"] = replies
                return CommentResponse(**comment_data)
            
            root_responses.append(convert_to_response(comment_data))
        
        return Response(
            code=200,
            message="获取评论树成功",
            data=root_responses
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{comment_id}/children", response_model=Response[PaginatedResponse[CommentResponse]])
def get_child_comments(
    comment_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """获取子评论列表"""
    try:
        # 验证父评论是否存在
        parent_comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="父评论不存在")
        
        # 查询子评论，按创建时间排序
        query = db.query(Comment).filter(
            Comment.parent_id == comment_id
        ).order_by(Comment.created_at.desc())
        
        # 计算总数和总页数
        total = query.count()
        total_pages = (total + page_size - 1) // page_size
        
        # 分页
        skip = (page - 1) * page_size
        comments = query.offset(skip).limit(page_size).all()
        
        # 转换为响应模型
        comment_responses = []
        for comment in comments:
            comment_dict = CommentResponse.model_validate(comment).model_dump()
            comment_dict["user_name"] = comment.user.username if comment.user else None
            comment_dict["article_title"] = comment.article.title if comment.article else None
            comment_dict["reply_count"] = db.query(Comment).filter(Comment.parent_id == comment.id).count()
            comment_responses.append(CommentResponse(**comment_dict))
        
        return Response(
            code=200,
            message="获取子评论列表成功",
            data=PaginatedResponse(
                items=comment_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{comment_id}/move", response_model=Response[CommentResponse])
def move_comment(
    comment_id: int,
    new_parent_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """移动评论（修改父评论）"""
    try:
        # 检查评论是否存在
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")
        
        # 检查权限
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 如果指定了新的父评论，检查其是否存在
        if new_parent_id:
            new_parent = db.query(Comment).filter(Comment.id == new_parent_id).first()
            if not new_parent:
                raise HTTPException(status_code=404, detail="新的父评论不存在")
            if new_parent.article_id != comment.article_id:
                raise HTTPException(status_code=400, detail="父评论必须属于同一篇文章")
            if new_parent.id == comment.id:
                raise HTTPException(status_code=400, detail="评论不能作为自己的父评论")
            
            # 检查是否会形成循环引用
            current = new_parent
            while current.parent_id:
                if current.parent_id == comment.id:
                    raise HTTPException(status_code=400, detail="不能将评论移动到其子评论下")
                current = db.query(Comment).filter(Comment.id == current.parent_id).first()
        
        # 更新父评论ID
        comment.parent_id = new_parent_id
        db.commit()
        db.refresh(comment)
        
        # 构建响应数据
        comment_dict = CommentResponse.model_validate(comment).model_dump()
        comment_dict["user_name"] = comment.user.username if comment.user else None
        comment_dict["article_title"] = comment.article.title if comment.article else None
        comment_dict["reply_count"] = db.query(Comment).filter(Comment.parent_id == comment.id).count()
        
        return Response(
            code=200,
            message="移动评论成功",
            data=CommentResponse(**comment_dict)
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{comment_id}/approve", response_model=Response[CommentResponse])
def approve_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """批准评论"""
    try:
        # 检查权限
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 检查评论是否存在
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")
        
        # 更新评论状态
        comment.is_approved = True
        comment.is_spam = False
        db.commit()
        db.refresh(comment)
        
        # 构建响应数据
        comment_dict = CommentResponse.model_validate(comment).model_dump()
        comment_dict["user_name"] = comment.user.username if comment.user else None
        comment_dict["article_title"] = comment.article.title if comment.article else None
        comment_dict["reply_count"] = db.query(Comment).filter(Comment.parent_id == comment.id).count()
        
        return Response(
            code=200,
            message="批准评论成功",
            data=CommentResponse(**comment_dict)
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{comment_id}/spam", response_model=Response[CommentResponse])
def mark_comment_as_spam(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """将评论标记为垃圾评论"""
    try:
        # 检查权限
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 检查评论是否存在
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")
        
        # 更新评论状态
        comment.is_spam = True
        comment.is_approved = False
        db.commit()
        db.refresh(comment)
        
        # 构建响应数据
        comment_dict = CommentResponse.model_validate(comment).model_dump()
        comment_dict["user_name"] = comment.user.username if comment.user else None
        comment_dict["article_title"] = comment.article.title if comment.article else None
        comment_dict["reply_count"] = db.query(Comment).filter(Comment.parent_id == comment.id).count()
        
        return Response(
            code=200,
            message="标记垃圾评论成功",
            data=CommentResponse(**comment_dict)
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch-approve", response_model=Response[List[CommentResponse]])
def batch_approve_comments(
    data: BatchCommentIds,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """批量批准评论"""
    try:
        # 检查权限
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 获取所有评论
        comments = db.query(Comment).filter(Comment.id.in_(data.comment_ids)).all()
        if len(comments) != len(data.comment_ids):
            raise HTTPException(status_code=404, detail="部分评论不存在")
        
        # 更新评论状态
        comment_responses = []
        for comment in comments:
            comment.is_approved = True
            comment.is_spam = False
            
            # 构建响应数据
            comment_dict = CommentResponse.model_validate(comment).model_dump()
            comment_dict["user_name"] = comment.user.username if comment.user else None
            comment_dict["article_title"] = comment.article.title if comment.article else None
            comment_dict["reply_count"] = db.query(Comment).filter(Comment.parent_id == comment.id).count()
            comment_responses.append(CommentResponse(**comment_dict))
        
        db.commit()
        
        return Response(
            code=200,
            message="批量批准评论成功",
            data=comment_responses
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{comment_id}", response_model=Response[None])
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """删除评论"""
    try:
        # 检查评论是否存在
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")
        
        # 检查权限
        if comment.user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 检查是否有子评论
        if db.query(Comment).filter(Comment.parent_id == comment_id).first():
            raise HTTPException(status_code=400, detail="该评论有子评论，无法删除")
        
        # 删除评论
        db.delete(comment)
        db.commit()
        
        return Response(
            code=200,
            message="删除评论成功"
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch-spam", response_model=Response[List[CommentResponse]])
def batch_mark_as_spam(
    data: BatchCommentIds,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """批量标记垃圾评论"""
    try:
        # 检查权限
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 获取所有评论
        comments = db.query(Comment).filter(Comment.id.in_(data.comment_ids)).all()
        if len(comments) != len(data.comment_ids):
            raise HTTPException(status_code=404, detail="部分评论不存在")
        
        # 更新评论状态
        comment_responses = []
        for comment in comments:
            comment.is_spam = True
            comment.is_approved = False
            
            # 构建响应数据
            comment_dict = CommentResponse.model_validate(comment).model_dump()
            comment_dict["user_name"] = comment.user.username if comment.user else None
            comment_dict["article_title"] = comment.article.title if comment.article else None
            comment_dict["reply_count"] = db.query(Comment).filter(Comment.parent_id == comment.id).count()
            comment_responses.append(CommentResponse(**comment_dict))
        
        db.commit()
        
        return Response(
            code=200,
            message="批量标记垃圾评论成功",
            data=comment_responses
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))