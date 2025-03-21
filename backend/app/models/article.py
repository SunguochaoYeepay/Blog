from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
from .article_relationships import article_categories, article_tags

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(200))
    
    # SEO fields
    meta_title = Column(String(200))
    meta_description = Column(String(500))
    keywords = Column(String(200))
    
    # Status and visibility
    status = Column(String(20), default="draft")  # draft, published, archived
    is_featured = Column(Boolean, default=False)
    allow_comments = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # Relations
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="articles")
    
    # Categories and Tags (Many-to-Many)
    categories = relationship("Category", secondary=article_categories, back_populates="articles")
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")
    
    # Statistics
    view_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # Comments
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")

    class Config:
        from_attributes = True 