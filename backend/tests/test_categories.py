import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
from app.models.category import Category
from app.database import get_db
from app.api.auth import create_access_token, get_password_hash
from datetime import datetime
from tests.test_config import override_get_db, init_test_db, cleanup_test_db

# 替换应用程序的数据库依赖
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 测试数据
test_category = {
    "name": "Test Category",
    "slug": "test-category"
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
    hashed_password = get_password_hash("password123")
    admin = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        department="Management",
        role="admin",
        created_at=datetime.utcnow(),
        hashed_password=hashed_password
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    
    token = create_access_token({"sub": admin.username})
    return token

def test_create_category(admin_token: str):
    """测试创建分类"""
    response = client.post(
        "/api/categories",
        json={"name": "Test Category", "description": "Test Description"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 201
    assert data["message"] == "分类创建成功"
    assert data["data"]["name"] == "Test Category"
    assert data["data"]["description"] == "Test Description"

def test_get_categories():
    """测试获取分类列表"""
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "获取成功"
    assert isinstance(data["data"], list)

def test_get_category(test_db: Session):
    """测试获取单个分类"""
    # 创建测试分类
    category = Category(name="Test Category", description="Test Description")
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)

    response = client.get(f"/api/categories/{category.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "获取成功"
    assert data["data"]["name"] == "Test Category"

def test_update_category(admin_token: str, test_db: Session):
    """测试更新分类"""
    # 创建测试分类
    category = Category(name="Old Name", description="Old Description")
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)

    response = client.put(
        f"/api/categories/{category.id}",
        json={"name": "New Name", "description": "New Description"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "更新成功"
    assert data["data"]["name"] == "New Name"
    assert data["data"]["description"] == "New Description"

def test_delete_category(admin_token: str, test_db: Session):
    """测试删除分类"""
    # 创建测试分类
    category = Category(name="To Delete", description="To be deleted")
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)

    response = client.delete(
        f"/api/categories/{category.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "删除成功"

def test_create_category_unauthorized():
    """测试未授权创建分类"""
    response = client.post(
        "/api/categories",
        json={"name": "Test Category", "description": "Test Description"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 401

def test_create_duplicate_category(admin_token: str, test_db: Session):
    """测试创建重复分类"""
    # 创建第一个分类
    category = Category(name="Duplicate", description="First one")
    test_db.add(category)
    test_db.commit()

    # 尝试创建同名分类
    response = client.post(
        "/api/categories",
        json={"name": "Duplicate", "description": "Second one"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "已存在" in data["message"] 