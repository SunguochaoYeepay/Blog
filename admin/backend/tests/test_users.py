import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.models.user import User
from .factories import UserFactory
from app.core.security import get_password_hash

pytestmark = pytest.mark.asyncio

class TestUserAPI:
    def test_create_user(self, client: TestClient, db_session: Session):
        """测试创建用户"""
        user_data = {
            "username": "new_test_user_1",
            "email": "new_user1@example.com",
            "password": "password123",
            "full_name": "New User",
            "department": "IT",
            "role": "user",
            "is_active": True
        }
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert response.json()["message"] == "创建用户成功"

    def test_create_user_duplicate_username(self, client: TestClient, db_session: Session, test_user):
        """测试创建用户 - 用户名重复"""
        user_data = {
            "username": test_user.username,
            "email": "new_test@example.com",
            "password": "password123",
            "full_name": "New User",
            "department": "IT",
            "role": "user",
            "is_active": True
        }
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "用户名已存在"

    def test_get_users(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试获取用户列表"""
        # 创建多个用户
        users = []
        for i in range(3):
            user = User(
                username=f"list_test_user_{i}",
                email=f"list_test{i}@example.com",
                hashed_password=get_password_hash("password123"),
                full_name=f"Test User {i}",
                is_active=True
            )
            db_session.add(user)
            users.append(user)
        db_session.commit()

        response = authorized_client.get("/api/users/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["items"]) >= 3
        assert response.json()["message"] == "获取用户列表成功"

        # 清理创建的测试用户
        for user in users:
            db_session.delete(user)
        db_session.commit()

    def test_get_user(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试获取单个用户"""
        # 确保 test_user 已经在数据库中
        db_session.refresh(test_user)
        
        response = authorized_client.get(f"/api/users/{test_user.id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert response.json()["message"] == "获取用户详情成功"

    def test_update_user(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试更新用户"""
        # 确保 test_user 已经在数据库中
        db_session.refresh(test_user)
        
        update_data = {
            "full_name": "Updated User",
            "department": "HR",
            "role": "admin"
        }
        response = authorized_client.put(f"/api/users/{test_user.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["full_name"] == update_data["full_name"]
        assert data["department"] == update_data["department"]
        assert data["role"] == update_data["role"]
        assert response.json()["message"] == "更新用户成功"

    def test_delete_user(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试删除用户"""
        # 创建一个新用户用于删除测试
        user = User(
            username="delete_test_user",
            email="delete_test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # 获取新创建用户的 ID
        user_id = user.id

        response = authorized_client.delete(f"/api/users/{user_id}")
        assert response.status_code == 204
        assert response.content == b""

    def test_user_permission(self, authorized_client: TestClient, db_session: Session, test_user):
        """测试用户权限"""
        # 创建一个新用户用于权限测试
        user = User(
            username="permission_test_user",
            email="permission_test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Normal User",
            is_active=True,
            is_superuser=False
        )
        db_session.add(user)
        db_session.commit()
        
        # 获取新创建用户的 ID
        user_id = user.id

        # 尝试删除其他用户
        response = authorized_client.delete(f"/api/users/{user_id}")
        assert response.status_code == 204  # 因为 test_user 是超级管理员，所以应该可以删除
        assert response.content == b""

    @pytest.mark.parametrize(
        "invalid_data,expected_detail",
        [
            ({"email": "test@example.com", "password": "test"}, "Field required"),
            ({"username": "test", "password": "test"}, "Field required"),
            ({"username": "test", "email": "test@example.com"}, "Field required"),
        ]
    )
    def test_create_user_validation(
        self,
        client: TestClient,
        invalid_data: dict,
        expected_detail: str
    ):
        """测试创建用户的字段验证"""
        response = client.post("/api/users", json=invalid_data)
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == expected_detail