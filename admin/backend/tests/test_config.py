import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.main import app
from app.database import get_db
from app.config import settings
from app.dependencies.redis import clear_all_likes

# 设置测试环境变量
os.environ["ENV"] = "test"

# 获取项目根目录
root_dir = Path(__file__).parent.parent

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
        if db:
            db.close()

def init_test_db():
    """初始化测试数据库"""
    try:
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        # 清理点赞数据
        clear_all_likes()
    except Exception as e:
        print(f"初始化测试数据库失败: {e}")
        raise

def cleanup_test_db():
    """清理测试数据库"""
    try:
        Base.metadata.drop_all(bind=engine)
        # 清理点赞数据
        clear_all_likes()
    except Exception as e:
        print(f"清理测试数据库失败: {e}")
        raise

# 替换应用的数据库依赖
app.dependency_overrides[get_db] = override_get_db