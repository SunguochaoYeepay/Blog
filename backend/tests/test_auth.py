import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
from app.database import get_db
from app.api.auth import create_access_token, get_password_hash
from datetime import datetime, timedelta
from tests.test_config import override_get_db, init_test_db, cleanup_test_db
from unittest.mock import patch, MagicMock

# 替换应用程序的数据库依赖
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 测试数据
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User",
    "department": "IT",
    "role": "user"
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
def test_user_data(test_db: Session):
    """创建测试用户"""
    hashed_password = get_password_hash(test_user["password"])
    db_user = User(
        username=test_user["username"],
        email=test_user["email"],
        hashed_password=hashed_password,
        full_name=test_user["full_name"],
        department=test_user["department"],
        role=test_user["role"],
        created_at=datetime.utcnow()
    )
    test_db.add(db_user)
    test_db.commit()
    test_db.refresh(db_user)
    return db_user

@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis functionality"""
    with patch('app.api.auth.is_token_blacklisted', return_value=False) as _mock:
        yield _mock

def test_login_success(test_user_data: User):
    """测试登录成功"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "登录成功"
    assert "access_token" in data["data"]
    assert "token_type" in data["data"]
    assert data["data"]["token_type"] == "bearer"

def test_login_invalid_username():
    """测试使用无效用户名登录"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 401
    assert "用户名或密码错误" in data["message"]

def test_login_invalid_password(test_user_data: User):
    """测试使用错误密码登录"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 401
    assert "用户名或密码错误" in data["message"]

def test_get_current_user(test_user_data: User):
    """测试获取当前用户信息"""
    # 先登录获取token
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    token = login_response.json()["data"]["access_token"]
    
    # 使用token获取用户信息
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "获取成功"
    assert data["data"]["username"] == test_user["username"]
    assert data["data"]["email"] == test_user["email"]
    assert data["data"]["full_name"] == test_user["full_name"]

def test_get_current_user_invalid_token():
    """测试使用无效token获取用户信息"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 401
    assert "无效的认证凭据" in data["message"]

def test_get_current_user_no_token():
    """测试不提供token获取用户信息"""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 401
    assert "未提供认证凭据" in data["message"]

def test_token_expired():
    """测试过期token"""
    # 创建一个已过期的token
    expired_token = create_access_token(
        data={"sub": test_user["username"]},
        expires_delta=timedelta(seconds=-1)  # 使用负数时间差确保token已过期
    )
    
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 401
    assert "认证凭据已过期" in data["message"]

def test_logout_success(test_user_data: User, mock_redis):
    """测试注销成功"""
    # 先登录获取token
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    token = login_response.json()["data"]["access_token"]
    
    # 注销
    with patch('app.api.auth.add_token_to_blacklist') as mock_blacklist:
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "注销成功"
        
        # 验证令牌被加入黑名单
        mock_blacklist.assert_called_once()

def test_logout_invalid_token(mock_redis):
    """测试使用无效token注销"""
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 401
    assert "无效的认证凭据" in data["message"]

def test_access_after_logout(test_user_data: User, mock_redis):
    """测试注销后访问受保护的资源"""
    # 先登录获取token
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    token = login_response.json()["data"]["access_token"]
    
    # 注销
    with patch('app.api.auth.add_token_to_blacklist') as mock_blacklist:
        client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # 使用已注销的token访问受保护的资源
    with patch('app.api.auth.is_token_blacklisted', return_value=True):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == 401
        assert "令牌已失效" in data["message"] 