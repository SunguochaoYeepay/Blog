import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
from app.models.article import Article
from app.models.comment import Comment
from app.database import get_db
from app.api.auth import create_access_token, get_password_hash
from datetime import datetime
from tests.test_config import override_get_db, init_test_db, cleanup_test_db

# 替换应用程序的数据库依赖
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 测试数据
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword",
    "full_name": "Test User",
    "role": "admin"
}

test_article = {
    "title": "Test Article",
    "content": "Test content",
    "summary": "Test summary",
    "status": "published",
    "allow_comments": True
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
def test_user_token(test_db: Session):
    """创建测试用户并返回token"""
    # 创建测试用户
    hashed_password = get_password_hash(test_user["password"])
    db_user = User(
        username=test_user["username"],
        email=test_user["email"],
        hashed_password=hashed_password,  # 使用哈希后的密码
        full_name=test_user["full_name"],
        role=test_user["role"],
        is_active=True,  # 确保用户是激活的
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(db_user)
    test_db.commit()
    test_db.refresh(db_user)
    
    # 生成token
    access_token = create_access_token(data={"sub": db_user.username})
    return access_token

@pytest.fixture
def test_article_data(test_db: Session, test_user_token: str):
    """创建测试文章"""
    # 获取测试用户
    db_user = test_db.query(User).filter(User.username == test_user["username"]).first()
    
    # 创建测试文章
    db_article = Article(
        title=test_article["title"],
        content=test_article["content"],
        summary=test_article["summary"],
        status=test_article["status"],
        allow_comments=test_article["allow_comments"],
        author_id=db_user.id,
        slug="test-article"  # 添加必需的 slug 字段
    )
    test_db.add(db_article)
    test_db.commit()
    test_db.refresh(db_article)
    return db_article

def test_create_comment(test_db: Session, test_user_token: str, test_article_data: Article):
    """测试创建评论"""
    response = client.post(
        f"/api/articles/{test_article_data.id}/comments",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "content": "Test comment",
            "parent_id": None,
            "is_approved": False,
            "is_spam": False
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 201
    assert data["message"] == "评论创建成功"
    assert data["data"]["content"] == "Test comment"
    assert data["data"]["article_id"] == test_article_data.id

def test_get_article_comments(test_db: Session, test_user_token: str, test_article_data: Article):
    """测试获取文章评论列表"""
    # 先创建一条评论
    db_user = test_db.query(User).filter(User.username == test_user["username"]).first()
    comment = Comment(
        content="Test comment",
        article_id=test_article_data.id,
        user_id=db_user.id,
        parent_id=None,
        is_approved=True,
        is_spam=False
    )
    test_db.add(comment)
    test_db.commit()
    
    # 获取评论列表
    response = client.get(f"/api/articles/{test_article_data.id}/comments")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "查询成功"
    assert len(data["data"]) > 0

def test_approve_comment(test_db: Session, test_user_token: str, test_article_data: Article):
    """测试审核评论"""
    # 先创建一条未审核的评论
    db_user = test_db.query(User).filter(User.username == test_user["username"]).first()
    comment = Comment(
        content="Test comment",
        article_id=test_article_data.id,
        user_id=db_user.id,
        parent_id=None,
        is_approved=False,
        is_spam=False
    )
    test_db.add(comment)
    test_db.commit()
    
    # 审核评论
    response = client.put(
        f"/api/comments/{comment.id}/approve",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "评论审核成功"
    assert data["data"]["is_approved"] == True
    assert data["data"]["is_spam"] == False

def test_mark_comment_spam(test_db: Session, test_user_token: str, test_article_data: Article):
    """测试标记评论为垃圾评论"""
    # 先创建一条评论
    db_user = test_db.query(User).filter(User.username == test_user["username"]).first()
    comment = Comment(
        content="Test comment",
        article_id=test_article_data.id,
        user_id=db_user.id,
        parent_id=None,
        is_approved=True,
        is_spam=False
    )
    test_db.add(comment)
    test_db.commit()
    
    # 标记为垃圾评论
    response = client.put(
        f"/api/comments/{comment.id}/mark-spam",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "评论已标记为垃圾评论"
    assert data["data"]["is_spam"] == True
    assert data["data"]["is_approved"] == False

def test_delete_comment(test_db: Session, test_user_token: str, test_article_data: Article):
    """测试删除评论"""
    # 先创建一条评论
    db_user = test_db.query(User).filter(User.username == test_user["username"]).first()
    comment = Comment(
        content="Test comment",
        article_id=test_article_data.id,
        user_id=db_user.id,
        parent_id=None,
        is_approved=True,
        is_spam=False
    )
    test_db.add(comment)
    test_db.commit()
    
    # 删除评论
    response = client.delete(
        f"/api/comments/{comment.id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "删除成功"
    
    # 验证评论已被删除
    deleted_comment = test_db.query(Comment).filter(Comment.id == comment.id).first()
    assert deleted_comment is None

def test_create_comment_unauthorized(test_article_data: Article):
    """测试未授权创建评论"""
    response = client.post(
        f"/api/articles/{test_article_data.id}/comments",
        json={
            "content": "Test comment",
            "parent_id": None
        }
    )
    assert response.status_code == 401

def test_create_comment_article_not_found(test_user_token: str):
    """测试在不存在文章上创建评论"""
    response = client.post(
        "/api/articles/999/comments",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "content": "Test comment",
            "parent_id": None
        }
    )
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert data["message"] == "文章不存在"

def test_create_comment_article_comments_disabled(test_db: Session, test_user_token: str):
    """测试在禁用评论的文章上创建评论"""
    # 创建禁用评论的文章
    db_user = test_db.query(User).filter(User.username == test_user["username"]).first()
    article = Article(
        title="Test Article",
        content="Test content",
        summary="Test summary",
        status="published",
        allow_comments=False,
        author_id=db_user.id,
        slug="test-article-2"  # 添加必需的 slug 字段
    )
    test_db.add(article)
    test_db.commit()

    response = client.post(
        f"/api/articles/{article.id}/comments",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "content": "Test comment",
            "parent_id": None
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert data["message"] == "该文章不允许评论" 