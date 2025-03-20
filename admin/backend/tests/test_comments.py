import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.models.article import Article
from app.schemas.comment import CommentCreate
from tests.utils import get_api_path

pytestmark = pytest.mark.asyncio

class TestCommentAPI:
    def test_create_comment(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试创建评论"""
        # 先创建一篇文章
        article = Article(
            title="Test Article",
            content="Test content",
            slug="test-article",
            author_id=test_user.id
        )
        db_session.add(article)
        db_session.commit()
        db_session.refresh(article)

        comment_data = {
            "content": "Test comment",
            "article_id": article.id
        }
        response = authorized_client.post(get_api_path("/comments"), json=comment_data)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["content"] == comment_data["content"]
        assert response.json()["message"] == "创建评论成功"

    def test_get_comments(self, authorized_client: TestClient):
        """测试获取评论列表"""
        response = authorized_client.get(get_api_path("/comments"))
        assert response.status_code == 200
        assert "data" in response.json()
        assert response.json()["message"] == "获取评论列表成功" 