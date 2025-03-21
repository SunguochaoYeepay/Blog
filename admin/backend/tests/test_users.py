import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.models.user import User
from .factories import UserFactory
from app.core.security import get_password_hash
from app.core.errors import ErrorCode, ErrorMessages

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
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.USER_CREATE_SUCCESS
        data = response.json()["data"]
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]

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
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.USER_USERNAME_EXISTS
        assert response.json()["message"] == ErrorMessages.USER_USERNAME_EXISTS

    def test_create_user_duplicate_email(self, client: TestClient, db_session: Session, test_user):
        """测试创建用户 - 邮箱重复"""
        user_data = {
            "username": "new_test_user_2",
            "email": test_user.email,
            "password": "password123",
            "full_name": "New User",
            "department": "IT",
            "role": "user",
            "is_active": True
        }
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.USER_EMAIL_EXISTS
        assert response.json()["message"] == ErrorMessages.USER_EMAIL_EXISTS

    def test_create_user_invalid_role(self, client: TestClient, db_session: Session):
        """测试创建用户 - 角色无效"""
        user_data = {
            "username": "new_test_user_3",
            "email": "new_test3@example.com",
            "password": "password123",
            "full_name": "New User",
            "department": "IT",
            "role": "invalid_role",
            "is_active": True
        }
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.USER_ROLE_INVALID
        assert response.json()["message"] == ErrorMessages.USER_ROLE_INVALID

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
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) >= 3

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
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.SUCCESS
        data = response.json()["data"]
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email

    def test_get_user_not_found(self, authorized_client: TestClient, db_session: Session):
        """测试获取不存在的用户"""
        response = authorized_client.get("/api/users/999")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.NOT_FOUND
        assert response.json()["message"] == ErrorMessages.USER_NOT_FOUND

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
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.USER_UPDATE_SUCCESS
        data = response.json()["data"]
        assert data["full_name"] == update_data["full_name"]
        assert data["department"] == update_data["department"]
        assert data["role"] == update_data["role"]

    def test_update_user_not_found(self, authorized_client: TestClient, db_session: Session):
        """测试更新不存在的用户"""
        update_data = {
            "full_name": "Updated User",
            "department": "HR",
            "role": "admin"
        }
        response = authorized_client.put("/api/users/999", json=update_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.NOT_FOUND
        assert response.json()["message"] == ErrorMessages.USER_NOT_FOUND

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
        
        response = authorized_client.delete(f"/api/users/{user.id}")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.USER_DELETE_SUCCESS

    def test_delete_user_not_found(self, authorized_client: TestClient, db_session: Session):
        """测试删除不存在的用户"""
        response = authorized_client.delete("/api/users/999")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.NOT_FOUND
        assert response.json()["message"] == ErrorMessages.USER_NOT_FOUND

    def test_user_no_permission(self, client: TestClient, db_session: Session, test_user):
        """测试无权限操作用户"""
        response = client.delete(f"/api/users/{test_user.id}")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.FORBIDDEN
        assert response.json()["message"] == ErrorMessages.FORBIDDEN

    def test_update_user_status(self, authorized_client: TestClient, db_session: Session):
        """测试更新用户状态"""
        # 创建测试用户
        user = User(
            username="status_test_user",
            email="status_test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Status Test User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 禁用用户
        response = authorized_client.post(f"/api/users/{user.id}/deactivate")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.USER_STATUS_UPDATE_SUCCESS
        assert not response.json()["data"]["is_active"]

        # 启用用户
        response = authorized_client.post(f"/api/users/{user.id}/activate")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.USER_STATUS_UPDATE_SUCCESS
        assert response.json()["data"]["is_active"]

        # 清理测试数据
        db_session.delete(user)
        db_session.commit()

    def test_update_user_status_not_found(self, authorized_client: TestClient):
        """测试更新不存在用户的状态"""
        response = authorized_client.post("/api/users/999/deactivate")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.NOT_FOUND
        assert response.json()["message"] == ErrorMessages.USER_NOT_FOUND

    def test_update_user_status_error(self, authorized_client: TestClient, db_session: Session):
        """测试更新用户状态 - 状态错误"""
        # 创建一个已禁用的测试用户
        user = User(
            username="status_error_test_user",
            email="status_error_test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Status Error Test User",
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 尝试禁用已经禁用的用户
        response = authorized_client.post(f"/api/users/{user.id}/deactivate")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.USER_STATUS_ERROR
        assert response.json()["message"] == ErrorMessages.USER_STATUS_ERROR

        # 清理测试数据
        db_session.delete(user)
        db_session.commit()

    def test_update_user_role(self, authorized_client: TestClient, db_session: Session):
        """测试更新用户角色"""
        # 创建测试用户
        user = User(
            username="role_test_user",
            email="role_test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Role Test User",
            role="user"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 更新用户角色
        response = authorized_client.put(
            f"/api/users/{user.id}/role",
            json={"role": "admin"}
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.USER_ROLE_UPDATE_SUCCESS
        assert response.json()["data"]["role"] == "admin"

        # 清理测试数据
        db_session.delete(user)
        db_session.commit()

    def test_update_user_role_invalid(self, authorized_client: TestClient, db_session: Session):
        """测试更新用户角色 - 无效角色"""
        # 创建测试用户
        user = User(
            username="role_invalid_test_user",
            email="role_invalid_test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Role Invalid Test User",
            role="user"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # 尝试更新为无效角色
        response = authorized_client.put(
            f"/api/users/{user.id}/role",
            json={"role": "invalid_role"}
        )
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.USER_ROLE_INVALID
        assert response.json()["message"] == ErrorMessages.USER_ROLE_INVALID

        # 清理测试数据
        db_session.delete(user)
        db_session.commit()

    @pytest.mark.parametrize(
        "invalid_data,expected_code,expected_message",
        [
            (
                {"email": "test@example.com", "password": "test"},
                ErrorCode.VALIDATION_ERROR,
                ErrorMessages.VALIDATION_ERROR
            ),
            (
                {"username": "test", "password": "test"},
                ErrorCode.VALIDATION_ERROR,
                ErrorMessages.VALIDATION_ERROR
            ),
            (
                {"username": "test", "email": "test@example.com"},
                ErrorCode.VALIDATION_ERROR,
                ErrorMessages.VALIDATION_ERROR
            ),
        ]
    )
    def test_create_user_validation(
        self,
        client: TestClient,
        invalid_data: dict,
        expected_code: int,
        expected_message: str
    ):
        """测试创建用户的字段验证"""
        response = client.post("/api/users", json=invalid_data)
        assert response.status_code == 200
        assert response.json()["code"] == expected_code
        assert response.json()["message"] == expected_message