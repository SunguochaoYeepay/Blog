from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from .article_relationships import article_categories

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    slug = Column(String(50), unique=True, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Relations
    parent = relationship("Category", remote_side=[id], backref="children")
    articles = relationship("Article", secondary=article_categories, back_populates="categories") 