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

# 替换应用程序的数据库依赖
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 测试数据
test_article = {
    "title": "Test Article",
    "slug": "test-article",
    "content": "This is a test article content.",
    "summary": "Test article summary",
    "status": "published",
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
def admin_user(test_db: Session):
    """创建管理员用户"""
    hashed_password = get_password_hash("password123")
    admin = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        department="Management",
        role="admin",
        created_at=datetime.utcnow(),
        hashed_password=hashed_password
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin

@pytest.fixture
def admin_token(admin_user: User):
    """生成管理员用户的令牌"""
    token = create_access_token({"sub": admin_user.username})
    return token

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
        status=article_data["status"],
        allow_comments=article_data["allow_comments"],
        author_id=author.id,
        created_at=datetime.utcnow()
    )
    test_db.add(db_article)
    test_db.commit()
    test_db.refresh(db_article)
    return db_article

def test_create_article(admin_token: str, admin_user: User, test_categories: list, test_tags: list):
    """测试创建文章"""
    article_data = test_article.copy()
    article_data["category_ids"] = [c.id for c in test_categories]
    article_data["tag_ids"] = [t.id for t in test_tags]
    
    response = client.post(
        "/api/articles",
        json=article_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 201
    assert data["message"] == "文章创建成功"
    assert data["data"]["title"] == article_data["title"]
    assert data["data"]["slug"] == article_data["slug"]
    assert "id" in data["data"]

def test_create_article_with_invalid_category(admin_token: str):
    """测试使用无效分类创建文章"""
    article_data = test_article.copy()
    article_data["category_ids"] = [999]  # 不存在的分类ID
    
    response = client.post(
        "/api/articles",
        json=article_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "部分分类不存在" in data["message"]

def test_create_article_with_invalid_tag(admin_token: str):
    """测试使用无效标签创建文章"""
    article_data = test_article.copy()
    article_data["tag_ids"] = [999]  # 不存在的标签ID
    
    response = client.post(
        "/api/articles",
        json=article_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "部分标签不存在" in data["message"]

def test_get_articles(admin_token: str, admin_user: User, test_db: Session):
    """测试获取文章列表"""
    # 创建测试文章
    articles = [
        Article(
            title="Article 1",
            slug="article-1",
            content="Content 1",
            summary="Summary 1",
            status="published",
            allow_comments=True,
            author_id=admin_user.id,
            created_at=datetime.utcnow()
        ),
        Article(
            title="Article 2",
            slug="article-2",
            content="Content 2",
            summary="Summary 2",
            status="draft",
            allow_comments=False,
            author_id=admin_user.id,
            created_at=datetime.utcnow()
        )
    ]
    test_db.add_all(articles)
    test_db.commit()
    
    response = client.get(
        "/api/articles",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "查询成功"
    assert len(data["data"]["data"]) >= 2
    assert data["data"]["total"] >= 2

def test_get_articles_with_filter(admin_token: str, admin_user: User, test_db: Session):
    """测试按条件筛选文章"""
    # 创建测试文章
    articles = [
        Article(
            title="Article About Python",
            slug="article-python",
            content="Python content",
            summary="Python summary",
            status="published",
            allow_comments=True,
            author_id=admin_user.id,
            created_at=datetime.utcnow()
        ),
        Article(
            title="Article About JavaScript",
            slug="article-javascript",
            content="JavaScript content",
            summary="JavaScript summary",
            status="published",
            allow_comments=True,
            author_id=admin_user.id,
            created_at=datetime.utcnow()
        )
    ]
    test_db.add_all(articles)
    test_db.commit()
    
    response = client.get(
        "/api/articles?title=Python",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert all("Python" in article["title"] for article in data["data"]["data"])

def test_get_article_by_id(admin_token: str, admin_user: User, test_db: Session):
    """测试根据ID获取文章"""
    # 创建测试文章
    article = Article(
        title="Test Article",
        slug="test-article",
        content="Test content",
        summary="Test summary",
        status="published",
        allow_comments=True,
        author_id=admin_user.id,
        created_at=datetime.utcnow()
    )
    test_db.add(article)
    test_db.commit()
    test_db.refresh(article)
    
    response = client.get(
        f"/api/articles/{article.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "查询成功"
    assert data["data"]["id"] == article.id
    assert data["data"]["title"] == article.title
    assert data["data"]["slug"] == article.slug

def test_get_article_not_found(admin_token: str):
    """测试获取不存在的文章"""
    response = client.get(
        "/api/articles/999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "文章不存在" in data["message"]

def test_update_article(admin_token: str, admin_user: User, test_db: Session):
    """测试更新文章"""
    # 创建测试文章
    article = create_test_article(test_article, admin_user, test_db)
    
    update_data = {
        "title": "Updated Article",
        "slug": "updated-article",
        "content": "Updated content",
        "summary": "Updated summary",
        "status": "draft",
        "allow_comments": False,
        "category_ids": [],
        "tag_ids": []
    }
    
    response = client.put(
        f"/api/articles/{article.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "更新成功"
    assert data["data"]["title"] == update_data["title"]
    assert data["data"]["slug"] == update_data["slug"]
    assert data["data"]["content"] == update_data["content"]
    assert data["data"]["status"] == update_data["status"]
    assert data["data"]["allow_comments"] == update_data["allow_comments"]

def test_update_article_not_found(admin_token: str):
    """测试更新不存在的文章"""
    update_data = {
        "title": "Updated Article",
        "slug": "updated-article",
        "content": "Updated content",
        "summary": "Updated summary",
        "status": "draft",
        "allow_comments": False,
        "category_ids": [],
        "tag_ids": []
    }
    
    response = client.put(
        "/api/articles/999",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "文章不存在" in data["message"]

def test_delete_article(admin_token: str, admin_user: User, test_db: Session):
    """测试删除文章"""
    # 创建测试文章
    article = create_test_article(test_article, admin_user, test_db)
    
    response = client.delete(
        f"/api/articles/{article.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "删除成功"
    
    # 验证文章已被删除
    deleted_article = test_db.query(Article).filter(Article.id == article.id).first()
    assert deleted_article is None

def test_delete_article_not_found(admin_token: str):
    """测试删除不存在的文章"""
    response = client.delete(
        "/api/articles/999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "文章不存在" in data["message"] 