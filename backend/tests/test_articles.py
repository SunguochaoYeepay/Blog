import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag
from app.database import get_db
from app.api.auth import create_access_token, get_password_hash
from datetime import datetime
from tests.test_config import override_get_db, init_test_db, cleanup_test_db
from unittest.mock import patch

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
    "meta_title": "Test Meta Title",
    "meta_description": "Test meta description",
    "keywords": "test,article",
    "status": "published",
    "is_featured": False,
    "allow_comments": True,
    "category_ids": [],
    "tag_ids": []
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
def test_categories(test_db: Session):
    """创建测试分类"""
    categories = [
        Category(name="Test Category 1", slug="test-category-1"),
        Category(name="Test Category 2", slug="test-category-2")
    ]
    test_db.add_all(categories)
    test_db.commit()
    
    for category in categories:
        test_db.refresh(category)
    
    return categories

@pytest.fixture
def test_tags(test_db: Session):
    """创建测试标签"""
    tags = [
        Tag(name="Test Tag 1", slug="test-tag-1"),
        Tag(name="Test Tag 2", slug="test-tag-2")
    ]
    test_db.add_all(tags)
    test_db.commit()
    
    for tag in tags:
        test_db.refresh(tag)
    
    return tags

def create_test_article(article_data: dict, author: User, test_db: Session) -> Article:
    """创建测试文章的辅助函数"""
    db_article = Article(
        title=article_data["title"],
        slug=article_data["slug"],
        content=article_data["content"],
        summary=article_data["summary"],
        meta_title=article_data["meta_title"],
        meta_description=article_data["meta_description"],
        keywords=article_data["keywords"],
        status=article_data["status"],
        is_featured=article_data["is_featured"],
        allow_comments=article_data["allow_comments"],
        author_id=author.id,
        created_at=datetime.utcnow()
    )
    test_db.add(db_article)
    test_db.commit()
    test_db.refresh(db_article)
    return db_article

def test_create_article(test_token: str, test_user_data: User, test_db: Session):
    """测试创建文章"""
    article_data = test_article.copy()
    article_data["author_id"] = test_user_data.id

    response = client.post(
        "/api/articles",
        headers={"Authorization": f"Bearer {test_token}"},
        json=article_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 201
    assert data["message"] == "文章创建成功"
    assert data["data"]["title"] == article_data["title"]
    assert data["data"]["content"] == article_data["content"]
    assert data["data"]["author_id"] == test_user_data.id

def test_list_articles(test_token: str, test_db: Session, test_user_data: User):
    """测试获取文章列表"""
    # 创建测试文章
    db_article = create_test_article(test_article, test_user_data, test_db)

    response = client.get(
        "/api/articles",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "查询成功"
    assert len(data["data"]["data"]) == 1
    assert data["data"]["data"][0]["title"] == test_article["title"]

def test_get_article(test_token: str, test_db: Session, test_user_data: User):
    """测试获取文章详情"""
    # 创建测试文章
    db_article = create_test_article(test_article, test_user_data, test_db)

    response = client.get(
        f"/api/articles/{db_article.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "查询成功"
    assert data["data"]["title"] == test_article["title"]

def test_update_article(test_token: str, test_db: Session, test_user_data: User):
    """测试更新文章"""
    # 创建测试文章
    db_article = create_test_article(test_article, test_user_data, test_db)

    update_data = {
        "title": "Updated Title",
        "content": "Updated content"
    }

    response = client.put(
        f"/api/articles/{db_article.id}",
        headers={"Authorization": f"Bearer {test_token}"},
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "更新成功"
    assert data["data"]["title"] == update_data["title"]
    assert data["data"]["content"] == update_data["content"]

def test_delete_article(test_token: str, test_db: Session, test_user_data: User):
    """测试删除文章"""
    # 创建测试文章
    db_article = create_test_article(test_article, test_user_data, test_db)

    response = client.delete(
        f"/api/articles/{db_article.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "删除成功"

    # 验证文章已被删除
    article = test_db.query(Article).filter(Article.id == db_article.id).first()
    assert article is None

def test_like_article(test_token: str, test_db: Session, test_user_data: User):
    """测试文章点赞"""
    # 创建测试文章
    db_article = create_test_article(test_article, test_user_data, test_db)

    response = client.post(
        f"/api/articles/{db_article.id}/like",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "操作成功"
    assert data["data"]["is_liked"] is True
    assert "like_count" in data["data"]

def test_article_not_found(test_token: str):
    """测试访问不存在的文章"""
    response = client.get(
        "/api/articles/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "文章不存在" in data["message"] 