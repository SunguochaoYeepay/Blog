import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.errors import ErrorCode, ErrorMessages
from app.models.tag import Tag
from app.models.article import Article
from app.models.article_relationships import ArticleTag
from tests.utils import get_api_path

class TestTagAPI:
    @pytest.fixture(autouse=True)
    def setup_test_data(self, db_session: Session, test_user):
        """为每个测试用例设置测试数据"""
        # 创建测试标签
        self.tag1 = Tag(
            name="Test Tag 1",
            slug="test-tag-1",
            description="Test Description 1"
        )
        self.tag2 = Tag(
            name="Test Tag 2",
            slug="test-tag-2",
            description="Test Description 2"
        )
        db_session.add_all([self.tag1, self.tag2])
        db_session.commit()
        db_session.refresh(self.tag1)
        db_session.refresh(self.tag2)

        # 创建一篇测试文章并关联标签
        self.article = Article(
            title="Test Article",
            content="Test content",
            slug="test-article",
            author_id=test_user.id
        )
        db_session.add(self.article)
        db_session.commit()
        db_session.refresh(self.article)

        # 关联文章和标签
        article_tag = ArticleTag(article_id=self.article.id, tag_id=self.tag1.id)
        db_session.add(article_tag)
        db_session.commit()

        yield

        # 清理测试数据
        try:
            db_session.query(ArticleTag).filter(
                ArticleTag.article_id == self.article.id
            ).delete()
            db_session.commit()

            db_session.query(Article).filter(
                Article.id == self.article.id
            ).delete()
            db_session.commit()

            db_session.query(Tag).filter(
                Tag.id.in_([self.tag1.id, self.tag2.id])
            ).delete()
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise e

    def test_create_tag(self, client: TestClient):
        """测试创建标签"""
        tag_data = {
            "name": "New Tag",
            "slug": "new-tag",
            "description": "New tag description"
        }
        response = client.post(get_api_path("/tags"), json=tag_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.TAG_CREATE_SUCCESS
        data = response.json()["data"]
        assert data["name"] == tag_data["name"]
        assert data["slug"] == tag_data["slug"]
        assert data["description"] == tag_data["description"]

    def test_create_tag_name_exists(self, client: TestClient):
        """测试创建标签 - 名称已存在"""
        tag_data = {
            "name": "Test Tag 1",  # 使用已存在的标签名
            "slug": "new-tag",
            "description": "New tag description"
        }
        response = client.post(get_api_path("/tags"), json=tag_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.TAG_NAME_EXISTS
        assert response.json()["message"] == ErrorMessages.TAG_NAME_EXISTS

    def test_create_tag_slug_exists(self, client: TestClient):
        """测试创建标签 - 别名已存在"""
        tag_data = {
            "name": "New Tag",
            "slug": "test-tag-1",  # 使用已存在的标签别名
            "description": "New tag description"
        }
        response = client.post(get_api_path("/tags"), json=tag_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.TAG_SLUG_EXISTS
        assert response.json()["message"] == ErrorMessages.TAG_SLUG_EXISTS

    def test_get_tags(self, client: TestClient):
        """测试获取标签列表"""
        response = client.get(get_api_path("/tags"))
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) >= 2
        assert data["total"] >= 2

    def test_get_tags_with_pagination(self, client: TestClient):
        """测试带分页的标签列表获取"""
        response = client.get(get_api_path("/tags?page=1&page_size=1"))
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) == 1
        assert data["page"] == 1
        assert data["page_size"] == 1
        assert data["total"] >= 2

    def test_update_tag(self, client: TestClient):
        """测试更新标签"""
        update_data = {
            "name": "Updated Tag",
            "description": "Updated description"
        }
        response = client.put(
            get_api_path(f"/tags/{self.tag2.id}"),
            json=update_data
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.TAG_UPDATE_SUCCESS
        data = response.json()["data"]
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_update_tag_not_found(self, client: TestClient):
        """测试更新标签 - 标签不存在"""
        update_data = {
            "name": "Updated Tag",
            "description": "Updated description"
        }
        response = client.put(get_api_path("/tags/999"), json=update_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.TAG_NOT_FOUND
        assert response.json()["message"] == ErrorMessages.TAG_NOT_FOUND

    def test_update_tag_name_exists(self, client: TestClient):
        """测试更新标签 - 名称已存在"""
        update_data = {
            "name": "Test Tag 1",  # 使用已存在的标签名
            "description": "Updated description"
        }
        response = client.put(
            get_api_path(f"/tags/{self.tag2.id}"),
            json=update_data
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.TAG_NAME_EXISTS
        assert response.json()["message"] == ErrorMessages.TAG_NAME_EXISTS

    def test_delete_tag(self, client: TestClient):
        """测试删除标签"""
        # 删除未被文章使用的标签
        response = client.delete(get_api_path(f"/tags/{self.tag2.id}"))
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.TAG_DELETE_SUCCESS

    def test_delete_tag_not_found(self, client: TestClient):
        """测试删除标签 - 标签不存在"""
        response = client.delete(get_api_path("/tags/999"))
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.TAG_NOT_FOUND
        assert response.json()["message"] == ErrorMessages.TAG_NOT_FOUND

    def test_delete_tag_has_articles(self, client: TestClient):
        """测试删除标签 - 标签下有文章"""
        # 尝试删除被文章使用的标签
        response = client.delete(get_api_path(f"/tags/{self.tag1.id}"))
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.TAG_HAS_ARTICLES
        assert response.json()["message"] == ErrorMessages.TAG_HAS_ARTICLES

    def test_merge_tags(self, client: TestClient, db_session: Session):
        """测试合并标签"""
        # 创建一个新的标签用于合并测试
        tag3 = Tag(name="Test Tag 3", slug="test-tag-3")
        db_session.add(tag3)
        db_session.commit()
        db_session.refresh(tag3)

        # 将 tag3 合并到 tag2
        response = client.post(
            get_api_path(f"/tags/{tag3.id}/merge"),
            json={"target_tag_id": self.tag2.id}
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.TAG_MERGE_SUCCESS

        # 清理测试数据
        db_session.delete(tag3)
        db_session.commit()

    def test_merge_tags_not_found(self, client: TestClient):
        """测试合并标签 - 标签不存在"""
        response = client.post(
            get_api_path("/tags/999/merge"),
            json={"target_tag_id": self.tag2.id}
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.TAG_NOT_FOUND
        assert response.json()["message"] == ErrorMessages.TAG_NOT_FOUND

        response = client.post(
            get_api_path(f"/tags/{self.tag1.id}/merge"),
            json={"target_tag_id": 999}
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.TAG_NOT_FOUND
        assert response.json()["message"] == ErrorMessages.TAG_NOT_FOUND

    def test_merge_tags_same_tag(self, client: TestClient):
        """测试合并标签 - 源标签和目标标签相同"""
        response = client.post(
            get_api_path(f"/tags/{self.tag1.id}/merge"),
            json={"target_tag_id": self.tag1.id}
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.TAG_ALREADY_EXISTS
        assert response.json()["message"] == ErrorMessages.TAG_ALREADY_EXISTS