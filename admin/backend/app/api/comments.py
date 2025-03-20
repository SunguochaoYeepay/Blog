from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.schemas.response import Response

router = APIRouter(
    tags=["comments"]
)

@router.get("/", response_model=Response[List[CommentResponse]])
def get_comments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    获取评论列表
    """
    comments = db.query(Comment).offset(skip).limit(limit).all()
    return Response(
        code=200,
        data=comments,
        message="获取评论列表成功"
    )

@router.post("/", response_model=Response[CommentResponse])
def create_comment(
    *,
    db: Session = Depends(get_db),
    comment_in: CommentCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    创建新评论
    """
    comment = Comment(
        **comment_in.model_dump(),
        user_id=current_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return Response(
        code=200,
        data=comment,
        message="创建评论成功"
    )

@router.put("/{comment_id}", response_model=Response[CommentResponse])
def update_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: int,
    comment_in: CommentUpdate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    更新评论
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    if comment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="权限不足")
    
    for field, value in comment_in.model_dump(exclude_unset=True).items():
        setattr(comment, field, value)
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return Response(
        data=comment,
        message="更新评论成功"
    )

@router.delete("/{comment_id}", response_model=Response)
def delete_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    删除评论
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    if comment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="权限不足")
    
    db.delete(comment)
    db.commit()
    return Response(message="删除评论成功")