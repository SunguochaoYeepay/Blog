from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.main import app
from app.database import get_db
from app.config import settings
from app.dependencies.redis import clear_all_likes

# 使用内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# 创建测试数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 创建测试会话
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """重写数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def init_test_db():
    """初始化测试数据库"""
    # 删除所有表
    Base.metadata.drop_all(bind=engine)
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    # 清理点赞数据
    clear_all_likes()

def cleanup_test_db():
    """清理测试数据库"""
    Base.metadata.drop_all(bind=engine)
    # 清理点赞数据
    clear_all_likes()

# 替换应用的数据库依赖
app.dependency_overrides[get_db] = override_get_db 