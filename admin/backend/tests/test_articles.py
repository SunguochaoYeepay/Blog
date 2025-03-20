import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.models.article import Article
from tests.factories import ArticleFactory, CategoryFactory, TagFactory

pytestmark = pytest.mark.asyncio

class TestArticleAPI:
    def test_create_article(self, authorized_client: TestClient, test_user):
        """测试创建文章"""
        article_data = {
            "title": "Test Article",
            "slug": "test-article",
            "content": "Test content",
            "summary": "Test summary",
            "status": "draft",
            "is_featured": False,
            "allow_comments": True,
            "is_published": True,
            "category_ids": [],
            "tag_ids": []
        }
        response = authorized_client.post("/api/articles", json=article_data)
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["title"] == article_data["title"]
        assert data["content"] == article_data["content"]
        assert response.json()["message"] == "创建文章成功"

    def test_get_articles(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试获取文章列表"""
        # 创建多篇文章
        for i in range(3):
            ArticleFactory(
                title=f"Test Article {i}",
                slug=f"test-article-{i}",
                author=test_user,
                session=db_session
            )

        response = authorized_client.get("/api/articles")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 3
        assert isinstance(data, list)
        assert response.json()["message"] == "获取文章列表成功"

    def test_get_article(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试获取单篇文章"""
        article = ArticleFactory(
            title="Test Article Detail",
            slug="test-article-detail",
            author=test_user,
            session=db_session
        )
        response = authorized_client.get(f"/api/articles/{article.id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["title"] == article.title
        assert data["content"] == article.content
        assert response.json()["message"] == "获取文章详情成功"

    def test_update_article(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试更新文章"""
        article = ArticleFactory(
            title="Original Article",
            slug="original-article",
            author=test_user,
            session=db_session
        )
        update_data = {
            "title": "Updated Title",
            "content": "Updated content",
            "summary": "Updated summary",
            "status": "draft",
            "is_featured": False,
            "allow_comments": True,
            "is_published": False
        }
        response = authorized_client.put(f"/api/articles/{article.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert response.json()["message"] == "更新文章成功"

    def test_delete_article(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试删除文章"""
        article = ArticleFactory(
            title="Article to Delete",
            slug="article-to-delete",
            author=test_user,
            session=db_session
        )
        response = authorized_client.delete(f"/api/articles/{article.id}")
        assert response.status_code == 204
        # 删除 204 状态码时不应该有响应体
        assert response.content == b""

    def test_search_articles(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试搜索文章"""
        # 创建一些文章
        ArticleFactory(
            title="Python Programming",
            content="Python is awesome",
            slug="python-programming",
            author=test_user,
            session=db_session
        )
        ArticleFactory(
            title="JavaScript Tips",
            content="JavaScript is great",
            slug="javascript-tips",
            author=test_user,
            session=db_session
        )

        # 搜索 Python 相关文章
        response = authorized_client.get("/api/articles?search=Python")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert "Python" in data[0]["title"]
        assert response.json()["message"] == "获取文章列表成功"

    def test_filter_articles(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试过滤文章"""
        # 创建分类和标签
        category = CategoryFactory(session=db_session)
        tag = TagFactory(session=db_session)

        # 创建带有分类和标签的文章
        article = ArticleFactory(
            title="Filtered Article",
            slug="filtered-article",
            author=test_user,
            session=db_session
        )
        article.categories.append(category)
        article.tags.append(tag)
        db_session.commit()

        # 按分类过滤
        response = authorized_client.get(f"/api/articles?category_id={category.id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["id"] == article.id
        assert response.json()["message"] == "获取文章列表成功"

        # 按标签过滤
        response = authorized_client.get(f"/api/articles?tag_id={tag.id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["id"] == article.id
        assert response.json()["message"] == "获取文章列表成功"

    @pytest.mark.parametrize(
        "invalid_data,expected_detail",
        [
            ({"content": "Test content", "summary": "Test summary"}, "Field required"),
            ({"title": "Test", "summary": "Test summary"}, "Field required"),
            ({"title": "Test", "content": "Test content"}, None),
        ]
    )
    def test_create_article_validation(
        self,
        authorized_client: TestClient,
        invalid_data: dict,
        expected_detail: str
    ):
        """测试创建文章的字段验证"""
        response = authorized_client.post("/api/articles", json=invalid_data)
        assert response.status_code == 422
        if expected_detail:
            assert response.json()["detail"][0]["msg"] == expected_detail