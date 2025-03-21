import os
import pytest
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from dotenv import load_dotenv
import uuid
from app.utils.slug import slugify

# 添加项目根目录到 Python 路径
import sys
from pathlib import Path
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# 加载测试环境配置
load_dotenv(os.path.join(root_dir, '.env.test'))

from app.main import app
from app.database import Base, get_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from tests.factories import UserFactory, ArticleFactory
from app.api import deps
from app.models.user import User
from app.models.article import Article

# 设置测试环境变量
os.environ["TESTING"] = "1"

# 测试数据库配置
TEST_MYSQL_USER = os.getenv("TEST_MYSQL_USER", "root")
TEST_MYSQL_PASSWORD = os.getenv("TEST_MYSQL_PASSWORD", "tZ_,;qP1?CtV")
TEST_MYSQL_HOST = os.getenv("TEST_MYSQL_HOST", "localhost")
TEST_MYSQL_PORT = os.getenv("TEST_MYSQL_PORT", "3306")
TEST_MYSQL_DATABASE = os.getenv("TEST_MYSQL_DATABASE", "blog_test")

# 构建测试数据库 URL
TEST_DATABASE_URL = f"mysql+pymysql://{TEST_MYSQL_USER}:{TEST_MYSQL_PASSWORD}@{TEST_MYSQL_HOST}:{TEST_MYSQL_PORT}/{TEST_MYSQL_DATABASE}"

# 创建测试数据库引擎
test_engine = create_engine(TEST_DATABASE_URL)

# 创建测试会话工厂
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

@pytest.fixture(scope="session")
def db_engine():
    """创建测试数据库引擎"""
    # 保存原始环境变量
    original_database_url = os.environ.get("DATABASE_URL")
    original_test_mode = os.environ.get("TEST_MODE")
    
    try:
        # 设置测试数据库环境变量
        os.environ["DATABASE_URL"] = TEST_DATABASE_URL
        os.environ["TEST_MODE"] = "false"

        # 创建数据库（如果不存在）
        tmp_engine = create_engine(
            f"mysql+pymysql://{TEST_MYSQL_USER}:{TEST_MYSQL_PASSWORD}@{TEST_MYSQL_HOST}:{TEST_MYSQL_PORT}"
        )
        with tmp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {TEST_MYSQL_DATABASE}"))
            conn.execute(text(f"USE {TEST_MYSQL_DATABASE}"))

        # 创建所有表
        Base.metadata.create_all(bind=test_engine)

        yield test_engine

        # 删除所有表
        Base.metadata.drop_all(bind=test_engine)

        # 删除测试数据库
        with tmp_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_MYSQL_DATABASE}"))
    finally:
        # 恢复原始环境变量
        if original_database_url:
            os.environ["DATABASE_URL"] = original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)
            
        if original_test_mode:
            os.environ["TEST_MODE"] = original_test_mode
        else:
            os.environ.pop("TEST_MODE", None)

@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """创建数据库会话"""
    connection = db_engine.connect()
    session = TestingSessionLocal(bind=connection)

    # 设置工厂类的默认会话
    UserFactory._meta.sqlalchemy_session = session

    yield session

    # 清理会话中的所有数据
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator:
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[deps.get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session: Session) -> Any:
    """创建测试用户"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"test_user_{unique_id}",
        email=f"test_{unique_id}@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True,
        is_superuser=True,  # 设置为超级管理员
        department="测试部门",  # 添加部门
        role="测试角色"  # 添加角色
    )
    db_session.add(user)
    db_session.commit()  # 直接提交，确保其他会话可以看到
    db_session.refresh(user)
    return user

@pytest.fixture
def test_superuser(db_session: Session) -> Any:
    """创建超级用户"""
    user = UserFactory(
        username=f"admin_{uuid.uuid4().hex[:8]}",
        email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
        is_active=True,
        is_superuser=True,
        session=db_session
    )
    return user

@pytest.fixture
def test_user_token(test_user, db_session: Session) -> str:
    """生成测试用户的访问令牌"""
    # 确保用户已经在数据库中
    db_session.refresh(test_user)
    return create_access_token(test_user.id)

@pytest.fixture
def test_superuser_token(test_superuser) -> str:
    """生成超级用户的访问令牌"""
    return create_access_token(test_superuser.id)

@pytest.fixture
def authorized_client(client: TestClient, test_user_token: str) -> TestClient:
    """创建已授权的测试客户端"""
    client.headers["Authorization"] = f"Bearer {test_user_token}"
    return client

@pytest.fixture
def superuser_client(client: TestClient, test_superuser_token: str) -> TestClient:
    """创建超级用户的测试客户端"""
    client.headers["Authorization"] = f"Bearer {test_superuser_token}"
    return client

@pytest.fixture(scope="session", autouse=True)
def test_env():
    """设置测试环境变量"""
    os.environ["TESTING"] = "1"
    os.environ["ENV"] = "test"
    os.environ["DEBUG"] = "true"
    yield
    os.environ.pop("TESTING", None)
    os.environ.pop("ENV", None)
    os.environ.pop("DEBUG", None)

@pytest.fixture
def normal_user(db_session: Session) -> User:
    """创建普通用户"""
    UserFactory._meta.sqlalchemy_session = db_session
    user = UserFactory(
        username=f"normal_{uuid.uuid4().hex[:8]}",
        email=f"normal_{uuid.uuid4().hex[:8]}@example.com",
        is_active=True,
        is_superuser=False
    )
    return user

@pytest.fixture
def normal_user_token(normal_user) -> str:
    """生成普通用户的访问令牌"""
    return create_access_token(normal_user.id)

@pytest.fixture
def normal_user_token_headers(normal_user_token: str) -> Dict[str, str]:
    """生成普通用户的请求头"""
    return {"Authorization": f"Bearer {normal_user_token}"}

@pytest.fixture
def test_article(db_session: Session, normal_user: User) -> Article:
    """创建测试文章"""
    ArticleFactory._meta.sqlalchemy_session = db_session
    title = f"test_article_{uuid.uuid4().hex[:8]}"
    article = ArticleFactory(
        title=title,
        content="Test content",
        author_id=normal_user.id,
        slug=slugify(title)  # 从标题生成 slug
    )
    return article