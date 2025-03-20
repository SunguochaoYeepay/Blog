import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from tests.factories import UserFactory
from app.models.user import User

class TestAuthAPI:
    def test_login_success_form(self, client: TestClient, db_session: Session):
        """测试表单登录成功"""
        # 创建测试用户
        hashed_password = get_password_hash("password123")
        user = User(
            username="auth_test_user_1",
            email="auth_test1@example.com",
            hashed_password=hashed_password,
            full_name="Test User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        login_data = {
            "username": "auth_test_user_1",
            "password": "password123"
        }
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()["data"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert response.json()["message"] == "登录成功"

    def test_login_success_json(self, client: TestClient, db_session: Session):
        """测试JSON登录成功"""
        # 创建测试用户
        hashed_password = get_password_hash("password123")
        user = User(
            username="auth_test_user_2",
            email="auth_test2@example.com",
            hashed_password=hashed_password,
            full_name="Test User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        login_data = {
            "username": "auth_test_user_2",
            "password": "password123"
        }
        response = client.post("/api/auth/login/json", json=login_data)
        assert response.status_code == 200
        data = response.json()["data"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert response.json()["message"] == "登录成功"

    def test_login_invalid_credentials(self, client: TestClient, db_session: Session):
        """测试登录失败 - 无效的凭证"""
        login_data = {
            "username": "nonexistent_user",
            "password": "wrong_password"
        }
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 401
        assert response.json()["detail"] == "用户名或密码错误"

    def test_login_inactive_user(self, client: TestClient, db_session: Session):
        """测试登录失败 - 非活跃用户"""
        # 创建非活跃用户
        hashed_password = get_password_hash("password123")
        user = User(
            username="inactive_test_user",
            email="inactive_test@example.com",
            hashed_password=hashed_password,
            full_name="Inactive User",
            is_active=False
        )
        db_session.add(user)
        db_session.commit()

        login_data = {
            "username": "inactive_test_user",
            "password": "password123"
        }
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "用户未激活"

    def test_get_current_user_no_token(self, client: TestClient):
        """测试获取当前用户失败 - 无令牌"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_current_user(self, authorized_client: TestClient):
        """测试获取当前用户成功"""
        response = authorized_client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "username" in data
        assert response.json()["message"] == "获取用户信息成功"

    @pytest.mark.parametrize(
        "token",
        [
            "invalid_token",
            "Bearer invalid_token",
            "",
            "Bearer "
        ]
    )
    def test_invalid_token(self, client: TestClient, token: str):
        """测试无效的令牌"""
        client.headers["Authorization"] = token
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_refresh_token(self, authorized_client: TestClient):
        """测试刷新令牌"""
        response = authorized_client.post("/api/auth/refresh")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert response.json()["message"] == "刷新令牌成功"

    def test_change_password(self, authorized_client: TestClient, test_user):
        """测试修改密码"""
        data = {
            "current_password": "password123",
            "new_password": "new_password123"
        }
        response = authorized_client.post("/api/auth/change-password", json=data)
        assert response.status_code == 200
        assert response.json()["message"] == "密码修改成功"