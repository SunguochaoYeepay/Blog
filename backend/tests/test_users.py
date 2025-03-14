import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
from app.database import get_db
from app.api.auth import create_access_token, get_password_hash
from datetime import datetime
from tests.test_config import override_get_db, init_test_db, cleanup_test_db

# 替换应用程序的数据库依赖
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 测试数据
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword",
    "full_name": "Test User",
    "department": "IT",
    "role": "user"
}

test_user_2 = {
    "username": "testuser2",
    "email": "test2@example.com",
    "password": "testpassword123",  # 添加密码字段
    "full_name": "Test User 2",
    "department": "HR",
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
def admin_token(test_db: Session):
    """创建管理员用户并生成令牌"""
    admin = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        department="Management",
        role="admin",
        hashed_password=get_password_hash("password123"),
        created_at=datetime.utcnow()
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    
    token = create_access_token({"sub": admin.username})
    return token

def create_test_user(user_data: dict, test_db: Session) -> User:
    """创建测试用户的辅助函数"""
    db_user = User(
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        department=user_data["department"],
        role=user_data["role"],
        hashed_password=get_password_hash(user_data["password"]),
        created_at=datetime.utcnow()
    )
    test_db.add(db_user)
    test_db.commit()
    test_db.refresh(db_user)
    return db_user

def test_create_user(admin_token: str, test_db: Session):
    """测试创建用户"""
    response = client.post(
        "/api/users",
        json=test_user,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 201
    assert data["message"] == "用户创建成功"
    assert data["data"]["username"] == test_user["username"]
    assert data["data"]["email"] == test_user["email"]

def test_create_user_duplicate_username(admin_token: str, test_db: Session):
    """测试创建重复用户名的用户"""
    # 先创建一个用户
    create_test_user(test_user, test_db)

    # 尝试创建同名用户
    new_user = test_user.copy()
    new_user["email"] = "test2@example.com"
    response = client.post(
        "/api/users",
        json=new_user,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "用户名已存在" in data["message"]

def test_create_user_duplicate_email(admin_token: str, test_db: Session):
    """测试创建重复邮箱的用户"""
    # 先创建一个用户
    create_test_user(test_user, test_db)

    # 尝试创建相同邮箱的用户
    new_user = test_user.copy()
    new_user["username"] = "testuser2"
    response = client.post(
        "/api/users",
        json=new_user,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "邮箱已存在" in data["message"]

def test_get_users(admin_token: str, test_db: Session):
    """测试获取用户列表"""
    # 创建测试用户
    create_test_user(test_user, test_db)

    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "获取成功"
    assert len(data["data"]["data"]) >= 1

def test_get_users_with_filter(admin_token: str, test_db: Session):
    """测试按条件筛选用户"""
    # 创建测试用户
    create_test_user(test_user, test_db)

    response = client.get(
        "/api/users?department=IT",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "获取成功"
    assert len(data["data"]["data"]) >= 1
    assert all(user["department"] == "IT" for user in data["data"]["data"])

def test_get_user(admin_token: str, test_db: Session):
    """测试获取单个用户"""
    # 创建测试用户
    db_user = create_test_user(test_user, test_db)

    response = client.get(
        f"/api/users/{db_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "获取成功"
    assert data["data"]["username"] == test_user["username"]

def test_update_user(admin_token: str, test_db: Session):
    """测试更新用户"""
    # 创建测试用户
    db_user = create_test_user(test_user, test_db)

    update_data = {
        "full_name": "Updated Name",
        "department": "HR"
    }
    response = client.put(
        f"/api/users/{db_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "更新成功"
    assert data["data"]["full_name"] == update_data["full_name"]
    assert data["data"]["department"] == update_data["department"]

def test_update_user_not_found(admin_token: str):
    """测试更新不存在的用户"""
    response = client.put(
        "/api/users/999",
        json={"full_name": "New Name"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "用户不存在" in data["message"]

def test_update_user_duplicate_email(admin_token: str, test_db: Session):
    """测试更新用户时使用已存在的邮箱"""
    # 创建两个测试用户
    db_user1 = create_test_user(test_user, test_db)

    user2_data = test_user.copy()
    user2_data["username"] = "testuser2"
    user2_data["email"] = "test2@example.com"
    db_user2 = create_test_user(user2_data, test_db)

    # 尝试将用户2的邮箱更新为用户1的邮箱
    update_data = {
        "email": test_user["email"]
    }
    response = client.put(
        f"/api/users/{db_user2.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "邮箱已被使用" in data["message"]

def test_delete_user(admin_token: str, test_db: Session):
    """测试删除用户"""
    # 创建测试用户
    db_user = create_test_user(test_user, test_db)

    response = client.delete(
        f"/api/users/{db_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "删除成功"

def test_delete_user_not_found(admin_token: str):
    """测试删除不存在的用户"""
    response = client.delete(
        "/api/users/999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 404
    assert "用户不存在" in data["message"] 