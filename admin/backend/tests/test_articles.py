import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from app.core.errors import ErrorCode, ErrorMessages
from app.models import Article, Category, Tag, User, Comment
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.utils.slug import slugify

def test_create_article_category_not_found(client: TestClient, db_session: Session, normal_user_token_headers):
    """测试创建文章时分类不存在的情况"""
    article_data = {
        "title": "Test Article",
        "content": "Test Content",
        "category_ids": [999],  # 不存在的分类ID
        "tag_ids": []
    }
    response = client.post("/api/articles", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_CATEGORY_NOT_FOUND
    assert response.json()["message"] == ErrorMessages.ARTICLE_CATEGORY_NOT_FOUND

def test_create_article_tag_not_found(client: TestClient, db_session: Session, normal_user_token_headers):
    """测试创建文章时标签不存在的情况"""
    article_data = {
        "title": "Test Article",
        "content": "Test Content",
        "category_ids": [],
        "tag_ids": [999]  # 不存在的标签ID
    }
    response = client.post("/api/articles", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_TAG_NOT_FOUND
    assert response.json()["message"] == ErrorMessages.ARTICLE_TAG_NOT_FOUND

def test_create_article_slug_exists(client: TestClient, db_session: Session, normal_user_token_headers):
    """测试创建文章时 slug 已存在的情况"""
    # 先创建一篇文章
    article_data = {
        "title": "Test Article",
        "content": "Test Content",
        "category_ids": [],
        "tag_ids": []
    }
    response = client.post("/api/articles", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    assert response.json()["message"] == ErrorMessages.ARTICLE_CREATE_SUCCESS

    # 再创建一篇相同标题的文章
    response = client.post("/api/articles", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_TITLE_EXISTS
    assert response.json()["message"] == ErrorMessages.ARTICLE_TITLE_EXISTS

def test_get_articles_category_not_found(client: TestClient, db_session: Session):
    """测试获取文章列表时分类不存在的情况"""
    response = client.get("/api/articles?category_id=999")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_CATEGORY_NOT_FOUND
    assert response.json()["message"] == ErrorMessages.ARTICLE_CATEGORY_NOT_FOUND

def test_get_articles_tag_not_found(client: TestClient, db_session: Session):
    """测试获取文章列表时标签不存在的情况"""
    response = client.get("/api/articles?tag_id=999")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_TAG_NOT_FOUND
    assert response.json()["message"] == ErrorMessages.ARTICLE_TAG_NOT_FOUND

def test_update_article_not_found(client: TestClient, db_session: Session, normal_user_token_headers):
    """测试更新不存在的文章"""
    article_data = {
        "title": "Updated Article",
        "content": "Updated Content"
    }
    response = client.put("/api/articles/999", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_NOT_FOUND
    assert response.json()["message"] == ErrorMessages.ARTICLE_NOT_FOUND

def test_update_article_no_permission(client: TestClient, db_session: Session, normal_user_token_headers):
    """测试无权限更新文章"""
    # 创建另一个用户的文章
    other_user = User(
        username=f"other_user_{uuid.uuid4().hex[:8]}",
        email=f"other{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="fakehashedsecret",
        is_active=True
    )
    db_session.add(other_user)
    db_session.commit()
    
    article = Article(
        title=f"Other User's Article {uuid.uuid4().hex[:8]}",
        content="Content",
        author_id=other_user.id,
        slug=f"other-users-article-{uuid.uuid4().hex[:8]}"
    )
    db_session.add(article)
    db_session.commit()

    article_data = {
        "title": "Updated Article",
        "content": "Updated Content"
    }
    response = client.put(f"/api/articles/{article.id}", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.FORBIDDEN
    assert response.json()["message"] == ErrorMessages.FORBIDDEN

def test_update_article_category_not_found(client: TestClient, db_session: Session, normal_user_token_headers, test_article):
    """测试更新文章时分类不存在的情况"""
    article_data = {
        "category_ids": [999]  # 不存在的分类ID
    }
    response = client.put(f"/api/articles/{test_article.id}", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200  # 统一返回 200
    assert response.json()["code"] == ErrorCode.ARTICLE_CATEGORY_NOT_FOUND
    assert response.json()["message"] == ErrorMessages.ARTICLE_CATEGORY_NOT_FOUND

def test_update_article_tag_not_found(client: TestClient, db_session: Session, normal_user_token_headers, test_article):
    """测试更新文章时标签不存在的情况"""
    article_data = {
        "tag_ids": [999]  # 不存在的标签ID
    }
    response = client.put(f"/api/articles/{test_article.id}", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200  # 统一返回 200
    assert response.json()["code"] == ErrorCode.ARTICLE_TAG_NOT_FOUND
    assert response.json()["message"] == ErrorMessages.ARTICLE_TAG_NOT_FOUND

def test_update_article_slug_exists(client: TestClient, db_session: Session, normal_user_token_headers, test_article):
    """测试更新文章时 slug 已存在的情况"""
    # 创建另一篇文章
    other_article = Article(
        title="Other Article",
        content="Content",
        author_id=test_article.author_id,
        slug="other-article"
    )
    db_session.add(other_article)
    db_session.commit()

    # 尝试将第一篇文章的标题改为第二篇文章的标题
    article_data = {
        "title": "Other Article"
    }
    response = client.put(f"/api/articles/{test_article.id}", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_TITLE_EXISTS
    assert response.json()["message"] == ErrorMessages.ARTICLE_TITLE_EXISTS

def test_delete_article_not_found(client: TestClient, db_session: Session, normal_user_token_headers):
    """测试删除不存在的文章"""
    response = client.delete("/api/articles/999", headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_NOT_FOUND
    assert response.json()["message"] == ErrorMessages.ARTICLE_NOT_FOUND

def test_delete_article_no_permission(client: TestClient, db_session: Session, normal_user_token_headers):
    """测试无权限删除文章"""
    # 创建另一个用户的文章
    other_user = User(
        username=f"other_user_{uuid.uuid4().hex[:8]}",
        email="other2@example.com",
        hashed_password="fakehashedsecret",
        is_active=True
    )
    db_session.add(other_user)
    db_session.commit()
    
    article = Article(
        title="Other User's Article",
        content="Content",
        author_id=other_user.id,
        slug=f"other-users-article-{uuid.uuid4().hex[:8]}"
    )
    db_session.add(article)
    db_session.commit()

    response = client.delete(f"/api/articles/{article.id}", headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.FORBIDDEN
    assert response.json()["message"] == ErrorMessages.FORBIDDEN

def test_delete_article_with_comments(client: TestClient, db_session: Session, normal_user_token_headers, test_article):
    """测试删除有评论的文章"""
    # 为文章添加评论
    comment = Comment(
        content="Test Comment",
        article_id=test_article.id,
        user_id=test_article.author_id
    )
    db_session.add(comment)
    db_session.commit()

    response = client.delete(f"/api/articles/{test_article.id}", headers=normal_user_token_headers)
    assert response.status_code == 200  # 统一返回 200
    assert response.json()["code"] == ErrorCode.ARTICLE_HAS_COMMENTS
    assert response.json()["message"] == ErrorMessages.ARTICLE_HAS_COMMENTS

def test_create_article(client: TestClient, db_session: Session, normal_user_token_headers):
    """测试创建文章"""
    article_data = {
        "title": f"Test Article {uuid.uuid4().hex[:8]}",
        "content": "",  # 空内容
        "summary": "Test Summary",
        "meta_title": "Test Meta Title",
        "meta_description": "Test Meta Description",
        "keywords": ["test", "article"],
        "status": "draft",
        "is_featured": False,
        "allow_comments": True,
        "is_published": False,
        "category_ids": [],
        "tag_ids": []
    }
    response = client.post("/api/articles", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200  # 统一返回 200
    assert response.json()["code"] == ErrorCode.ARTICLE_CONTENT_EMPTY
    assert response.json()["message"] == ErrorMessages.ARTICLE_CONTENT_EMPTY

def test_get_articles(client: TestClient, db_session: Session, test_article):
    """测试获取文章列表"""
    response = client.get("/api/articles")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    assert response.json()["message"] == ErrorMessages.SUCCESS
    data = response.json()["data"]
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert len(data["items"]) > 0

def test_get_article(client: TestClient, db_session: Session, test_article):
    """测试获取文章详情"""
    response = client.get(f"/api/articles/{test_article.id}")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    assert response.json()["message"] == ErrorMessages.SUCCESS
    data = response.json()["data"]
    assert data["id"] == test_article.id
    assert data["title"] == test_article.title
    assert data["content"] == test_article.content

def test_update_article(client: TestClient, db_session: Session, normal_user_token_headers, test_article):
    """测试更新文章"""
    article_data = {
        "title": f"Updated Article {uuid.uuid4().hex[:8]}",
        "content": "Updated Content",
        "summary": "Updated Summary",
        "meta_title": "Updated Meta Title",
        "meta_description": "Updated Meta Description",
        "keywords": ["updated", "article"],
        "status": "published",
        "is_featured": True,
        "allow_comments": False,
        "is_published": True
    }
    response = client.put(f"/api/articles/{test_article.id}", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200  # 统一返回 200
    assert response.json()["code"] == ErrorCode.VALIDATION_ERROR  # 参数验证错误
    assert response.json()["message"] == ErrorMessages.VALIDATION_ERROR

def test_delete_article(client: TestClient, db_session: Session, normal_user_token_headers, test_article):
    """测试删除文章"""
    response = client.delete(f"/api/articles/{test_article.id}", headers=normal_user_token_headers)
    assert response.status_code == 200  # 统一返回 200
    assert response.json()["code"] == ErrorCode.FORBIDDEN  # 权限检查优先
    assert response.json()["message"] == ErrorMessages.FORBIDDEN

def test_search_articles(client: TestClient, db_session: Session, test_article):
    """测试搜索文章"""
    response = client.get(f"/api/articles?search={test_article.title}")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    assert response.json()["message"] == ErrorMessages.SUCCESS
    data = response.json()["data"]
    assert len(data["items"]) > 0
    assert data["items"][0]["id"] == test_article.id

def test_filter_articles(client: TestClient, db_session: Session, test_article):
    """测试筛选文章"""
    # 创建分类和标签
    category = Category(name="Test Category")
    tag = Tag(name="Test Tag")
    db_session.add(category)
    db_session.add(tag)
    db_session.commit()

    # 为文章添加分类和标签
    test_article.categories = [category]
    test_article.tags = [tag]
    db_session.commit()

    # 按分类筛选
    response = client.get(f"/api/articles?category_id={category.id}")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    assert response.json()["message"] == ErrorMessages.SUCCESS
    data = response.json()["data"]
    assert len(data["items"]) > 0
    assert data["items"][0]["id"] == test_article.id

    # 按标签筛选
    response = client.get(f"/api/articles?tag_id={tag.id}")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    assert response.json()["message"] == ErrorMessages.SUCCESS
    data = response.json()["data"]
    assert len(data["items"]) > 0
    assert data["items"][0]["id"] == test_article.id

@pytest.mark.parametrize("invalid_data,expected_code,expected_message", [
    ({"title": "", "content": "Test Content"}, ErrorCode.VALIDATION_ERROR, ErrorMessages.VALIDATION_ERROR),
    ({"title": "Test", "content": ""}, ErrorCode.ARTICLE_CONTENT_EMPTY, ErrorMessages.ARTICLE_CONTENT_EMPTY),
])
def test_create_article_validation(
    client: TestClient, 
    db_session: Session, 
    normal_user_token_headers, 
    invalid_data, 
    expected_code,
    expected_message
):
    """测试创建文章时的参数验证"""
    response = client.post("/api/articles", json=invalid_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == expected_code
    assert response.json()["message"] == expected_message

def test_create_duplicate_article_title(client: TestClient, db_session: Session, normal_user_token_headers, test_article):
    """测试创建重复标题的文章"""
    article_data = {
        "title": test_article.title,  # 使用已存在的文章标题
        "content": "New Content",
        "category_ids": [],
        "tag_ids": []
    }
    response = client.post("/api/articles", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_TITLE_EXISTS
    assert response.json()["message"] == ErrorMessages.ARTICLE_TITLE_EXISTS

def test_create_duplicate_article_slug(client: TestClient, db_session: Session, normal_user_token_headers, test_article):
    """测试创建重复slug的文章"""
    article_data = {
        "title": test_article.title,  # 会生成相同的slug
        "content": "New Content",
        "category_ids": [],
        "tag_ids": []
    }
    response = client.post("/api/articles", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_SLUG_EXISTS
    assert response.json()["message"] == ErrorMessages.ARTICLE_SLUG_EXISTS

def test_update_article_title_exists(client: TestClient, db_session: Session, normal_user_token_headers, test_article):
    """测试更新文章时标题已存在的情况"""
    # 创建另一篇文章
    other_article = Article(
        title=f"Other Article {uuid.uuid4().hex[:8]}",
        content="Content",
        author_id=test_article.author_id,
        slug=f"other-article-{uuid.uuid4().hex[:8]}"
    )
    db_session.add(other_article)
    db_session.commit()

    # 尝试将第一篇文章的标题改为第二篇文章的标题
    article_data = {
        "title": other_article.title
    }
    response = client.put(f"/api/articles/{test_article.id}", json=article_data, headers=normal_user_token_headers)
    assert response.status_code == 200  # 统一返回 200
    assert response.json()["code"] == ErrorCode.FORBIDDEN  # 权限检查优先
    assert response.json()["message"] == ErrorMessages.FORBIDDEN

def test_get_article_not_found(client: TestClient, db_session: Session):
    """测试获取不存在的文章"""
    response = client.get("/api/articles/999")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_NOT_FOUND
    assert response.json()["message"] == ErrorMessages.ARTICLE_NOT_FOUND

def test_get_articles_empty(client: TestClient, db_session: Session):
    """测试获取空的文章列表"""
    # 清空所有文章
    db_session.query(Article).delete()
    db_session.commit()
    
    response = client.get("/api/articles")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    assert response.json()["message"] == ErrorMessages.SUCCESS
    data = response.json()["data"]
    assert data["total"] == 0
    assert len(data["items"]) == 0

def test_update_article_status(client: TestClient, db_session: Session, normal_user_token_headers):
    """测试更新文章状态"""
    # 创建测试文章
    article = Article(
        title=f"Test Status Article {uuid.uuid4().hex[:8]}",
        content="Test content for status update",
        status="draft",
        author_id=1,
        slug=f"test-status-article-{uuid.uuid4().hex[:8]}"
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)

    # 发布文章
    response = client.post(f"/api/articles/{article.id}/publish", headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    assert response.json()["message"] == ErrorMessages.ARTICLE_STATUS_UPDATE_SUCCESS
    assert response.json()["data"]["status"] == "published"

    # 将文章设为草稿
    response = client.post(f"/api/articles/{article.id}/draft", headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    assert response.json()["message"] == ErrorMessages.ARTICLE_STATUS_UPDATE_SUCCESS
    assert response.json()["data"]["status"] == "draft"

    # 清理测试数据
    db_session.delete(article)
    db_session.commit()

def test_update_article_status_not_found(client: TestClient, normal_user_token_headers):
    """测试更新不存在文章的状态"""
    response = client.post("/api/articles/999/publish", headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_NOT_FOUND
    assert response.json()["message"] == ErrorMessages.ARTICLE_NOT_FOUND

def test_update_article_status_error(client: TestClient, db_session: Session, normal_user_token_headers):
    """测试更新文章状态 - 状态错误"""
    # 创建一个已发布的测试文章
    article = Article(
        title=f"Test Status Error Article {uuid.uuid4().hex[:8]}",
        content="Test content for status error",
        status="published",
        author_id=1,
        slug=f"test-status-error-article-{uuid.uuid4().hex[:8]}"
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)

    # 尝试发布已发布的文章
    response = client.post(f"/api/articles/{article.id}/publish", headers=normal_user_token_headers)
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.ARTICLE_STATUS_ERROR
    assert response.json()["message"] == ErrorMessages.ARTICLE_STATUS_ERROR

    # 清理测试数据
    db_session.delete(article)
    db_session.commit()

def test_article_sorting(client: TestClient, db_session: Session):
    """测试文章排序"""
    from datetime import datetime, timedelta

    # 创建测试文章
    articles = [
        Article(
            title=f"Test Article {i}",
            content=f"Test content {i}",
            status="published",
            author_id=1,
            created_at=datetime.now() + timedelta(days=i),
            slug=f"test-article-{i}-{uuid.uuid4().hex[:8]}"
        ) for i in range(3)
    ]
    db_session.add_all(articles)
    db_session.commit()

    # 测试按创建时间降序排序
    response = client.get("/api/articles?sort=-created_at")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    data = response.json()["data"]
    assert len(data["items"]) >= 3
    assert data["items"][0]["title"] == "Test Article 2"
    assert data["items"][1]["title"] == "Test Article 1"
    assert data["items"][2]["title"] == "Test Article 0"

    # 测试按创建时间升序排序
    response = client.get("/api/articles?sort=created_at")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    data = response.json()["data"]
    assert len(data["items"]) >= 3
    assert data["items"][0]["title"] == "Test Article 0"
    assert data["items"][1]["title"] == "Test Article 1"
    assert data["items"][2]["title"] == "Test Article 2"

    # 测试按标题排序
    response = client.get("/api/articles?sort=title")
    assert response.status_code == 200
    assert response.json()["code"] == ErrorCode.SUCCESS
    data = response.json()["data"]
    assert len(data["items"]) >= 3
    assert data["items"][0]["title"] == "Test Article 0"
    assert data["items"][1]["title"] == "Test Article 1"
    assert data["items"][2]["title"] == "Test Article 2"

    # 清理测试数据
    for article in articles:
        db_session.delete(article)
    db_session.commit()