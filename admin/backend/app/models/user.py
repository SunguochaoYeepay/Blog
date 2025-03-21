from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100))
    department = Column(String(100), nullable=True)
    role = Column(String(50), nullable=True)
    avatar = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    bio = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # 虚拟字段，不存储在数据库中
    articles_count: int = 0
    comments_count: int = 0
    
    # Relationships
    articles = relationship("Article", back_populates="author")
    comments = relationship("Comment", back_populates="user")