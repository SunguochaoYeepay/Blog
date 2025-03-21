import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.models.article import Article
from app.schemas.comment import CommentCreate
from tests.utils import get_api_path
from app.core.errors import ErrorCode, ErrorMessages
from datetime import datetime, timedelta

class TestCommentAPI:
    @pytest.fixture(autouse=True)
    def setup_test_data(self, db_session: Session, test_user):
        """为每个测试用例设置测试数据"""
        # 创建测试文章
        self.article = Article(
            title="Test Article for Comments",
            content="Test content",
            slug="test-article-comments",
            author_id=test_user.id
        )
        db_session.add(self.article)
        db_session.commit()
        db_session.refresh(self.article)
        
        # 创建测试评论数据
        root_comments = [
            # 根评论
            Comment(
                content="Root comment 1",
                article_id=self.article.id,
                user_id=test_user.id,
                is_approved=True,
                created_at=datetime.utcnow()
            ),
            Comment(
                content="Root comment 2",
                article_id=self.article.id,
                user_id=test_user.id,
                is_spam=True,
                created_at=datetime.utcnow() - timedelta(days=1)
            )
        ]
        
        db_session.add_all(root_comments)
        db_session.commit()
        
        # 保存根评论ID
        self.root_comment_1_id = root_comments[0].id
        self.root_comment_2_id = root_comments[1].id
        
        # 创建子评论
        child_comments = [
            Comment(
                content="Child comment 1",
                article_id=self.article.id,
                user_id=test_user.id,
                parent_id=self.root_comment_1_id,  # 设置父评论ID
                created_at=datetime.utcnow() - timedelta(days=2)
            ),
            Comment(
                content="Child comment 2",
                article_id=self.article.id,
                user_id=test_user.id,
                parent_id=self.root_comment_1_id,  # 设置父评论ID
                is_approved=True,
                created_at=datetime.utcnow() - timedelta(days=3)
            )
        ]
        
        db_session.add_all(child_comments)
        db_session.commit()
        
        # 保存子评论ID
        self.child_comment_1_id = child_comments[0].id
        self.child_comment_2_id = child_comments[1].id
        
        yield
        
        # 清理测试数据（保留其他测试创建的数据）
        try:
            # 确保实例已绑定到会话
            db_session.add(self.article)
            
            # 先删除子评论，再删除根评论，避免外键约束问题
            db_session.query(Comment).filter(
                Comment.article_id == self.article.id,
                Comment.parent_id.isnot(None)
            ).delete(synchronize_session=False)
            db_session.commit()
            
            db_session.query(Comment).filter(
                Comment.article_id == self.article.id,
                Comment.parent_id.is_(None)
            ).delete(synchronize_session=False)
            db_session.commit()
            
            db_session.query(Article).filter(Article.id == self.article.id).delete()
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise e

    def test_create_comment(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试创建评论"""
        comment_data = {
            "content": "Test comment",
            "article_id": self.article.id
        }
        response = authorized_client.post(get_api_path("/comments"), json=comment_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.COMMENT_CREATE_SUCCESS
        data = response.json()["data"]
        assert data["content"] == comment_data["content"]

    def test_create_comment_empty_content(self, authorized_client: TestClient):
        """测试创建评论 - 内容为空"""
        comment_data = {
            "content": "",
            "article_id": self.article.id
        }
        response = authorized_client.post(get_api_path("/comments"), json=comment_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.COMMENT_CONTENT_EMPTY
        assert response.json()["message"] == ErrorMessages.COMMENT_CONTENT_EMPTY

    def test_create_comment_article_not_found(self, authorized_client: TestClient):
        """测试创建评论 - 文章不存在"""
        comment_data = {
            "content": "Test comment",
            "article_id": 999999
        }
        response = authorized_client.post(get_api_path("/comments"), json=comment_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.COMMENT_ARTICLE_NOT_FOUND
        assert response.json()["message"] == ErrorMessages.COMMENT_ARTICLE_NOT_FOUND

    def test_create_reply_parent_not_found(self, authorized_client: TestClient):
        """测试创建回复 - 父评论不存在"""
        comment_data = {
            "content": "Test reply",
            "article_id": self.article.id,
            "parent_id": 999999
        }
        response = authorized_client.post(get_api_path("/comments"), json=comment_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.COMMENT_PARENT_NOT_FOUND
        assert response.json()["message"] == ErrorMessages.COMMENT_PARENT_NOT_FOUND

    def test_get_comments(self, authorized_client: TestClient):
        """测试获取评论列表"""
        response = authorized_client.get(get_api_path("/comments"))
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.SUCCESS
        assert "data" in response.json()

    def test_get_comments_with_filters(self, authorized_client: TestClient):
        """测试带筛选条件的评论列表获取"""
        # 测试关键词搜索
        response = authorized_client.get(get_api_path("/comments?keyword=Root"))
        assert response.status_code == 200
        data = response.json()["data"]
        assert len([item for item in data["items"] if "Root" in item["content"]]) > 0
        
        # 测试状态筛选
        response = authorized_client.get(get_api_path("/comments?status=approved"))
        assert response.status_code == 200
        data = response.json()["data"]
        assert all(item["is_approved"] for item in data["items"] if "is_approved" in item)
        
        # 测试时间范围筛选
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        response = authorized_client.get(get_api_path(f"/comments?start_date={yesterday}"))
        assert response.status_code == 200

    def test_get_comment_tree(self, authorized_client: TestClient):
        """测试获取评论树结构"""
        response = authorized_client.get(
            get_api_path(f"/comments/tree/{self.article.id}")
        )
        assert response.status_code == 200
        data = response.json()["data"]
        
        # 验证树结构
        root_comments = [c for c in data if c["parent_id"] is None]
        assert len(root_comments) == 2  # 两个根评论
        
        # 验证第一个根评论的子评论
        root_1 = next(c for c in root_comments if c["id"] == self.root_comment_1_id)
        assert len(root_1["replies"]) == 2
        assert all(reply["parent_id"] == self.root_comment_1_id 
                  for reply in root_1["replies"])

    def test_get_child_comments(self, authorized_client: TestClient):
        """测试获取子评论列表"""
        response = authorized_client.get(
            get_api_path(f"/comments/{self.root_comment_1_id}/children")
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert all(item["parent_id"] == self.root_comment_1_id 
                  for item in data["items"])

    def test_move_comment(self, authorized_client: TestClient):
        """测试移动评论"""
        # 将 child_comment_1 移动到 root_comment_2 下
        response = authorized_client.put(
            get_api_path(f"/comments/{self.child_comment_1_id}/move"),
            params={"new_parent_id": self.root_comment_2_id}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["parent_id"] == self.root_comment_2_id

    def test_comment_status_management(self, authorized_client: TestClient):
        """测试评论状态管理"""
        # 测试审核通过
        response = authorized_client.post(
            get_api_path(f"/comments/{self.child_comment_1_id}/approve")
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.COMMENT_APPROVE_SUCCESS
        data = response.json()["data"]
        assert data["is_approved"] is True
        assert data["is_spam"] is False
        
        # 测试标记垃圾评论
        response = authorized_client.post(
            get_api_path(f"/comments/{self.child_comment_2_id}/spam")
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.COMMENT_SPAM_SUCCESS
        data = response.json()["data"]
        assert data["is_spam"] is True
        assert data["is_approved"] is False

    def test_comment_status_error(self, authorized_client: TestClient):
        """测试评论状态错误"""
        # 尝试审核已经是垃圾评论的评论
        response = authorized_client.post(
            get_api_path(f"/comments/{self.root_comment_2_id}/approve")  # root_comment_2 是垃圾评论
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.COMMENT_STATUS_ERROR
        assert response.json()["message"] == ErrorMessages.COMMENT_STATUS_ERROR

    def test_comment_forbidden(self, unauthorized_client: TestClient):
        """测试无权限操作评论"""
        response = unauthorized_client.post(
            get_api_path(f"/comments/{self.child_comment_1_id}/approve")
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.COMMENT_FORBIDDEN
        assert response.json()["message"] == ErrorMessages.COMMENT_FORBIDDEN

    def test_batch_operations(self, authorized_client: TestClient):
        """测试批量操作评论"""
        # 测试批量审核通过
        response = authorized_client.post(
            get_api_path("/comments/batch-approve"),
            json={"comment_ids": [self.child_comment_1_id, self.child_comment_2_id]}
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.COMMENT_APPROVE_SUCCESS
        comments = response.json()["data"]
        for comment in comments:
            assert comment["is_approved"] is True
            assert comment["is_spam"] is False

        # 测试批量标记垃圾评论
        response = authorized_client.post(
            get_api_path("/comments/batch-spam"),
            json={"comment_ids": [self.child_comment_1_id, self.child_comment_2_id]}
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.COMMENT_SPAM_SUCCESS
        comments = response.json()["data"]
        for comment in comments:
            assert comment["is_spam"] is True
            assert comment["is_approved"] is False

    def test_batch_operations_not_found(self, authorized_client: TestClient):
        """测试批量操作 - 评论不存在"""
        response = authorized_client.post(
            get_api_path("/comments/batch-approve"),
            json={"comment_ids": [999999]}
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.COMMENT_NOT_FOUND
        assert response.json()["message"] == ErrorMessages.COMMENT_NOT_FOUND

    def test_batch_operations_forbidden(self, unauthorized_client: TestClient):
        """测试批量操作 - 无权限"""
        response = unauthorized_client.post(
            get_api_path("/comments/batch-approve"),
            json={"comment_ids": [self.child_comment_1_id]}
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.COMMENT_FORBIDDEN
        assert response.json()["message"] == ErrorMessages.COMMENT_FORBIDDEN

    def test_comment_sorting(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试评论排序"""
        # 创建测试评论数据
        comments = [
            Comment(
                content=f"Sort Test Comment {i}",
                article_id=self.article.id,
                user_id=test_user.id,
                created_at=datetime.utcnow() + timedelta(days=i),
                likes=i * 10
            ) for i in range(3)
        ]
        db_session.add_all(comments)
        db_session.commit()

        # 测试按创建时间降序排序
        response = authorized_client.get(get_api_path("/comments?sort=-created_at"))
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) >= 3
        assert data["items"][0]["content"] == "Sort Test Comment 2"
        assert data["items"][1]["content"] == "Sort Test Comment 1"
        assert data["items"][2]["content"] == "Sort Test Comment 0"

        # 测试按创建时间升序排序
        response = authorized_client.get(get_api_path("/comments?sort=created_at"))
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) >= 3
        assert data["items"][0]["content"] == "Sort Test Comment 0"
        assert data["items"][1]["content"] == "Sort Test Comment 1"
        assert data["items"][2]["content"] == "Sort Test Comment 2"

        # 测试按点赞数降序排序
        response = authorized_client.get(get_api_path("/comments?sort=-likes"))
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) >= 3
        assert data["items"][0]["content"] == "Sort Test Comment 2"  # 20 likes
        assert data["items"][1]["content"] == "Sort Test Comment 1"  # 10 likes
        assert data["items"][2]["content"] == "Sort Test Comment 0"  # 0 likes

        # 测试按点赞数升序排序
        response = authorized_client.get(get_api_path("/comments?sort=likes"))
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) >= 3
        assert data["items"][0]["content"] == "Sort Test Comment 0"  # 0 likes
        assert data["items"][1]["content"] == "Sort Test Comment 1"  # 10 likes
        assert data["items"][2]["content"] == "Sort Test Comment 2"  # 20 likes

        # 清理测试数据
        for comment in comments:
            db_session.delete(comment)
        db_session.commit()