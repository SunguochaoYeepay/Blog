from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from ..database import Base

class ArticleCategory(Base):
    __tablename__ = "article_categories"

    article_id = Column(Integer, ForeignKey("articles.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)
    
    article = relationship("Article", backref="categories")
    category = relationship("Category", back_populates="articles")

class ArticleTag(Base):
    __tablename__ = "article_tags"

    article_id = Column(Integer, ForeignKey("articles.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    
    article = relationship("Article", backref="tags")
    tag = relationship("Tag", back_populates="articles") 