from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    department = Column(String(100))
    role = Column(String(50))
    created_at = Column(DateTime)
    last_login = Column(DateTime)

    # 添加与文章的关系
    articles = relationship("Article", back_populates="author") 