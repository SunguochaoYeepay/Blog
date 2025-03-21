"""认证相关测试用例"""

import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.core.errors import ErrorCode, ErrorMessages
from tests.factories import UserFactory
from app.models.user import User
from app.main import app

client = TestClient(app)

# 测试数据
test_user_data = {
    "username": "test_user",
    "email": "test@example.com",
    "password": "Test@123",
    "full_name": "Test User",
    "department": "IT",
    "role": "user",
    "is_active": True,
    "is_superuser": False
}

def create_test_user(db_session: Session, **kwargs) -> User:
    """创建测试用户的辅助函数"""
    user_data = test_user_data.copy()
    user_data.update(kwargs)
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        full_name=user_data["full_name"],
        department=user_data["department"],
        role=user_data["role"],
        is_active=user_data["is_active"],
        is_superuser=user_data["is_superuser"]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

class TestAuthAPI:
    """认证 API 测试类"""
    
    def test_login_success_form(self, client: TestClient, db_session: Session):
        """测试表单登录成功"""
        # 创建测试用户
        user = create_test_user(db_session)

        # OAuth2 表单登录数据
        login_data = {
            "username": user.email,  # 使用邮箱登录
            "password": test_user_data["password"],
            "grant_type": "password",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        
        # 测试邮箱登录
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.SUCCESS
        assert resp_data["message"] == ErrorMessages.LOGIN_SUCCESS
        assert "data" in resp_data
        data = resp_data["data"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data  # 检查令牌过期时间
        
        # 测试用户名登录
        login_data["username"] = user.username  # 使用用户名登录
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.SUCCESS
        assert resp_data["message"] == ErrorMessages.LOGIN_SUCCESS
        assert "data" in resp_data
        data = resp_data["data"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_login_success_json(self, client: TestClient, db_session: Session):
        """测试JSON登录成功"""
        # 创建测试用户
        user = create_test_user(db_session)

        # 登录数据
        login_data = {
            "username": user.username,
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login/json", json=login_data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.SUCCESS
        assert resp_data["message"] == ErrorMessages.LOGIN_SUCCESS
        assert "data" in resp_data
        data = resp_data["data"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, db_session: Session):
        """测试登录失败 - 无效的凭证"""
        # 创建测试用户
        user = create_test_user(db_session)
        
        login_data = {
            "username": user.username,
            "password": "wrong_password"
        }
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.INVALID_CREDENTIALS
        assert resp_data["message"] == ErrorMessages.INVALID_CREDENTIALS
        assert resp_data["data"] is None

    def test_login_inactive_user(self, client: TestClient, db_session: Session):
        """测试未激活用户登录"""
        # 创建未激活的测试用户
        user = create_test_user(db_session, is_active=False)

        # 登录数据
        login_data = {
            "username": user.username,
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.INACTIVE_USER
        assert resp_data["message"] == ErrorMessages.INACTIVE_USER
        assert resp_data["data"] is None

    def test_get_current_user_no_token(self, client: TestClient):
        """测试获取当前用户失败 - 无令牌"""
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.UNAUTHORIZED
        assert resp_data["message"] == ErrorMessages.NOT_AUTHENTICATED
        assert resp_data["data"] is None

    def test_get_current_user(self, authorized_client: TestClient):
        """测试获取当前用户成功"""
        response = authorized_client.get("/api/auth/me")
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.SUCCESS
        assert resp_data["message"] == ErrorMessages.USER_INFO_SUCCESS
        assert "data" in resp_data
        data = resp_data["data"]
        assert "username" in data

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
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.UNAUTHORIZED
        assert resp_data["message"] == ErrorMessages.NOT_AUTHENTICATED
        assert resp_data["data"] is None

    def test_refresh_token(self, authorized_client: TestClient):
        """测试刷新令牌"""
        # 先获取访问令牌
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
            "grant_type": "password",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        response = authorized_client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        resp_data = response.json()
        access_token = resp_data["data"]["access_token"]

        # 使用访问令牌作为刷新令牌
        response = authorized_client.post("/api/auth/refresh", json={"refresh_token": access_token})
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.SUCCESS
        assert resp_data["message"] == ErrorMessages.TOKEN_REFRESH_SUCCESS
        assert "data" in resp_data
        data = resp_data["data"]
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_change_password(self, authorized_client: TestClient, test_user):
        """测试修改密码"""
        data = {
            "current_password": "password123",
            "new_password": "new_password123"
        }
        response = authorized_client.post("/api/auth/change-password", json=data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.SUCCESS
        assert resp_data["message"] == ErrorMessages.PASSWORD_CHANGED
        assert resp_data["data"] is None

    def test_change_password_invalid_current(self, authorized_client: TestClient, test_user):
        """测试修改密码 - 当前密码错误"""
        data = {
            "current_password": "wrong_password",
            "new_password": "new_password123"
        }
        response = authorized_client.post("/api/auth/change-password", json=data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.VALIDATION_ERROR
        assert resp_data["message"] == ErrorMessages.INVALID_CREDENTIALS
        assert resp_data["data"] is None

    def test_change_password_invalid_new(self, authorized_client: TestClient, test_user):
        """测试修改密码 - 新密码不符合要求"""
        data = {
            "current_password": "password123",
            "new_password": "weak"
        }
        response = authorized_client.post("/api/auth/change-password", json=data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.VALIDATION_ERROR
        assert resp_data["message"] == ErrorMessages.INVALID_PASSWORD_LENGTH
        assert resp_data["data"] is None

    def test_request_password_reset(self, client: TestClient, db_session: Session):
        """测试请求密码重置"""
        # 创建测试用户
        user = create_test_user(db_session)

        # 请求密码重置
        data = {"email": user.email}
        response = client.post("/api/auth/password-reset/request", json=data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.SUCCESS
        assert resp_data["message"] == ErrorMessages.PASSWORD_RESET_EMAIL_SENT
        assert resp_data["data"] is None

    def test_request_password_reset_invalid_email(self, client: TestClient):
        """测试请求密码重置 - 无效邮箱"""
        data = {"email": "nonexistent@example.com"}
        response = client.post("/api/auth/password-reset/request", json=data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.USER_NOT_FOUND
        assert resp_data["message"] == ErrorMessages.USER_NOT_FOUND
        assert resp_data["data"] is None

    def test_reset_password(self, client: TestClient, db_session: Session):
        """测试重置密码"""
        # 创建测试用户并设置重置令牌
        user = create_test_user(db_session)
        reset_token = "valid_reset_token"  # 在实际应用中应该是一个有效的JWT令牌
        
        data = {
            "token": reset_token,
            "new_password": "NewTest@123"
        }
        response = client.post("/api/auth/password-reset/verify", json=data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.SUCCESS
        assert resp_data["message"] == ErrorMessages.PASSWORD_RESET_SUCCESS
        assert resp_data["data"] is None

    def test_reset_password_invalid_token(self, client: TestClient):
        """测试重置密码 - 无效令牌"""
        data = {
            "token": "invalid_token",
            "new_password": "NewTest@123"
        }
        response = client.post("/api/auth/password-reset/verify", json=data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.INVALID_TOKEN
        assert resp_data["message"] == ErrorMessages.INVALID_TOKEN
        assert resp_data["data"] is None

    def test_verify_email(self, client: TestClient, db_session: Session):
        """测试邮箱验证"""
        # 创建未验证邮箱的测试用户
        user = create_test_user(db_session, is_email_verified=False)
        verification_token = "valid_verification_token"  # 在实际应用中应该是一个有效的JWT令牌

        response = client.get(f"/api/auth/verify-email?token={verification_token}")
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.SUCCESS
        assert resp_data["message"] == ErrorMessages.EMAIL_VERIFIED
        assert resp_data["data"] is None

    def test_verify_email_invalid_token(self, client: TestClient):
        """测试邮箱验证 - 无效令牌"""
        response = client.get("/api/auth/verify-email?token=invalid_token")
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.INVALID_TOKEN
        assert resp_data["message"] == ErrorMessages.INVALID_TOKEN
        assert resp_data["data"] is None

    def test_resend_verification_email(self, client: TestClient, db_session: Session):
        """测试重新发送验证邮件"""
        # 创建未验证邮箱的测试用户
        user = create_test_user(db_session, is_email_verified=False)

        data = {"email": user.email}
        response = client.post("/api/auth/resend-verification", json=data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.SUCCESS
        assert resp_data["message"] == ErrorMessages.VERIFICATION_EMAIL_SENT
        assert resp_data["data"] is None

    def test_resend_verification_email_already_verified(self, client: TestClient, db_session: Session):
        """测试重新发送验证邮件 - 邮箱已验证"""
        # 创建已验证邮箱的测试用户
        user = create_test_user(db_session, is_email_verified=True)

        data = {"email": user.email}
        response = client.post("/api/auth/resend-verification", json=data)
        assert response.status_code == 200
        resp_data = response.json()
        assert resp_data["code"] == ErrorCode.EMAIL_ALREADY_VERIFIED
        assert resp_data["message"] == ErrorMessages.EMAIL_ALREADY_VERIFIED
        assert resp_data["data"] is None