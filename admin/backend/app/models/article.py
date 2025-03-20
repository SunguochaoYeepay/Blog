from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from ..database import Base
from .article_relationships import article_categories, article_tags
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .category import Category  # noqa: F401
    from .comment import Comment  # noqa: F401
    from .tag import Tag  # noqa: F401
    from .user import User  # noqa: F401

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(String(200))
    
    # SEO fields
    meta_title: Mapped[Optional[str]] = mapped_column(String(200))
    meta_description: Mapped[Optional[str]] = mapped_column(String(500))
    keywords: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Status and visibility
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, published, archived
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_comments: Mapped[bool] = mapped_column(Boolean, default=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relations
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="articles")
    
    # Categories and Tags (Many-to-Many)
    categories = relationship("Category", secondary=article_categories, back_populates="articles")
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")
    article_tags = relationship("ArticleTag", back_populates="article", cascade="all, delete-orphan")
    
    # Statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Comments
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")

    from pydantic import ConfigDict
    model_config = ConfigDict(arbitrary_types_allowed=True) 