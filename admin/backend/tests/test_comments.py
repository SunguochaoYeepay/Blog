import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
from app.main import app
from app.models.article import Article
from app.models.user import User
from app.models.comment import Comment
from app.database import get_db
from app.api.auth import create_access_token, get_password_hash
from tests.test_config import override_get_db, init_test_db, cleanup_test_db
from unittest.mock import patch
import json

# 替换应用程序的数据库依赖
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 测试数据
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User",
    "department": "IT",
    "role": "user"
}

test_article = {
    "title": "Test Article",
    "slug": "test-article",
    "content": "This is a test article content",
    "summary": "Test summary",
    "status": "published",
    "allow_comments": True
}

test_comment = {
    "content": "This is a test comment",
    "parent_id": None
}

@pytest.fixture(autouse=True)
def setup_db():
    """设置测试数据库"""
    init_test_db()
    yield
    cleanup_test_db()

@pytest.fixture
def test_db():
    """创建测试数据库会话"""
    db = next(override_get_db())
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user_data(test_db: Session):
    """创建测试用户"""
    hashed_password = get_password_hash(test_user["password"])
    db_user = User(
        username=test_user["username"],
        email=test_user["email"],
        hashed_password=hashed_password,
        full_name=test_user["full_name"],
        department=test_user["department"],
        role=test_user["role"],
        created_at=datetime.utcnow()
    )
    test_db.add(db_user)
    test_db.commit()
    test_db.refresh(db_user)
    return db_user

@pytest.fixture
def test_token(test_user_data: User):
    """创建测试令牌"""
    access_token = create_access_token(data={"sub": test_user_data.username})
    return access_token

@pytest.fixture
def test_article_data(test_db: Session, test_user_data: User):
    """创建测试文章"""
    db_article = Article(
        **test_article,
        author_id=test_user_data.id,
        created_at=datetime.utcnow()
    )
    test_db.add(db_article)
    test_db.commit()
    test_db.refresh(db_article)
    return db_article

@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis functionality"""
    with patch('app.dependencies.redis.cache_comment'), \
         patch('app.dependencies.redis.get_cached_comment', return_value=None), \
         patch('app.dependencies.redis.delete_comment_cache'), \
         patch('app.dependencies.redis.toggle_comment_like', return_value=True), \
         patch('app.dependencies.redis.get_comment_likes', return_value=0), \
         patch('app.dependencies.redis.is_token_blacklisted', return_value=False):
        yield

def test_create_comment(test_token: str, test_article_data: Article):
    """测试创建评论"""
    response = client.post(
        f"/api/articles/{test_article_data.id}/comments",
        headers={"Authorization": f"Bearer {test_token}"},
        json=test_comment
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 201
    assert data["message"] == "评论创建成功"
    assert data["data"]["content"] == test_comment["content"]

def test_create_comment_article_not_found(test_token: str):
    """测试在不存在的文章下创建评论"""
    response = client.post(
        "/api/articles/999999/comments",
        headers={"Authorization": f"Bearer {test_token}"},
        json=test_comment
    )
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "文章不存在" in data["message"]

def test_list_comments(test_token: str, test_db: Session, test_article_data: Article, test_user_data: User):
    """测试获取评论列表"""
    # 创建测试评论
    db_comment = Comment(
        content=test_comment["content"],
        article_id=test_article_data.id,
        user_id=test_user_data.id,
        created_at=datetime.utcnow()
    )
    test_db.add(db_comment)
    test_db.commit()

    response = client.get(
        f"/api/articles/{test_article_data.id}/comments",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "查询成功"
    assert len(data["data"]["items"]) == 1
    assert data["data"]["items"][0]["content"] == test_comment["content"]

def test_get_comment(test_token: str, test_db: Session, test_article_data: Article, test_user_data: User):
    """测试获取评论详情"""
    # 创建测试评论
    db_comment = Comment(
        content=test_comment["content"],
        article_id=test_article_data.id,
        user_id=test_user_data.id,
        created_at=datetime.utcnow()
    )
    test_db.add(db_comment)
    test_db.commit()

    response = client.get(
        f"/api/comments/{db_comment.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "查询成功"
    assert data["data"]["content"] == test_comment["content"]

def test_update_comment(test_token: str, test_db: Session, test_article_data: Article, test_user_data: User):
    """测试更新评论"""
    # 创建测试评论
    db_comment = Comment(
        content=test_comment["content"],
        article_id=test_article_data.id,
        user_id=test_user_data.id,
        created_at=datetime.utcnow()
    )
    test_db.add(db_comment)
    test_db.commit()

    update_data = {
        "content": "Updated comment content"
    }

    response = client.put(
        f"/api/comments/{db_comment.id}",
        headers={"Authorization": f"Bearer {test_token}"},
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "更新成功"
    assert data["data"]["content"] == update_data["content"]

def test_delete_comment(test_token: str, test_db: Session, test_article_data: Article, test_user_data: User):
    """测试删除评论"""
    # 创建测试评论
    db_comment = Comment(
        content=test_comment["content"],
        article_id=test_article_data.id,
        user_id=test_user_data.id,
        created_at=datetime.utcnow()
    )
    test_db.add(db_comment)
    test_db.commit()

    response = client.delete(
        f"/api/comments/{db_comment.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "删除成功"

    # 使用新的会话验证删除结果
    from app.database import SessionLocal
    new_db = SessionLocal()
    try:
        comment = new_db.query(Comment).filter(Comment.id == db_comment.id).first()
        assert comment is None
    finally:
        new_db.close()

def test_like_comment(test_token: str, test_db: Session, test_article_data: Article, test_user_data: User):
    """测试评论点赞"""
    # 创建测试评论
    db_comment = Comment(
        content=test_comment["content"],
        article_id=test_article_data.id,
        user_id=test_user_data.id,
        created_at=datetime.utcnow()
    )
    test_db.add(db_comment)
    test_db.commit()

    response = client.post(
        f"/api/comments/{db_comment.id}/like",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "操作成功"
    assert data["data"]["is_liked"] is True
    assert "like_count" in data["data"]

def test_comment_not_found(test_token: str):
    """测试访问不存在的评论"""
    response = client.get(
        "/api/comments/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "评论不存在" in data["message"] 