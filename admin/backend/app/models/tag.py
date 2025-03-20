from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
from .article_relationships import article_tags

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    slug = Column(String(50), unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    articles = relationship("Article", secondary=article_tags, back_populates="tags")
    article_tags = relationship("ArticleTag", back_populates="tag", cascade="all, delete-orphan")

    class Config:
        from_attributes = True