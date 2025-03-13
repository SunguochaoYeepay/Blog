from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..database import Base

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    slug = Column(String(50), unique=True, index=True)
    description = Column(Text)
    
    # Relations
    articles = relationship("ArticleTag", back_populates="tag") 