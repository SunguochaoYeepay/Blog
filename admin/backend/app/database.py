from typing import Generator, Dict, Any
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """获取数据库 URL"""
    return os.getenv("DATABASE_URL", "sqlite:///./blog.db")

def get_connect_args() -> Dict[str, Any]:
    """获取数据库连接参数"""
    database_url = get_database_url()
    if database_url.startswith('sqlite'):
        return {"check_same_thread": False}
    return {}

# 创建同步引擎
engine = create_engine(
    get_database_url(),
    connect_args=get_connect_args()
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    try:
        db = SessionLocal()
        logger.info(f"成功连接到数据库：{get_database_url()}")
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass