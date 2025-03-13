from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_name = Column(String(100))  # 用于未登录用户
    author_email = Column(String(100))  # 用于未登录用户
    
    # Status
    is_approved = Column(Boolean, default=False)
    is_spam = Column(Boolean, default=False)
    
    # Relations
    article_id = Column(Integer, ForeignKey("articles.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 可以是匿名评论
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    article = relationship("Article", backref="comments")
    user = relationship("User", backref="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies") 