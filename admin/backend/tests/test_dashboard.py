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

@pytest.fixture(autouse=True)
def setup_db(test_db):
    """设置测试数据库"""
    init_test_db()
    # 创建测试用户
    db = next(override_get_db())
    try:
        test_user = User(
            username="admin",
            email="admin@example.com",
            full_name="Test Admin",
            department="IT",
            role="admin",
            hashed_password=get_password_hash("admin"),
            is_active=True
        )
        db.add(test_user)
        db.commit()
    finally:
        db.close()
    yield
    cleanup_test_db()

@pytest.fixture
def test_token():
    """生成测试用token"""
    access_token = create_access_token(data={"sub": "admin"})
    return access_token

def test_get_dashboard_data(test_token):
    """测试获取仪表盘数据"""
    response = client.get("/api/dashboard", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200
    resp = response.json()
    assert resp["code"] == 200
    assert resp["message"] == "获取仪表盘数据成功"
    assert "data" in resp
    data = resp["data"]
    assert "statistics" in data
    assert "chart_data" in data
    assert "recent_activities" in data
    assert "category_stats" in data
    assert "system_status" in data

def test_get_statistics(test_token):
    """测试获取统计数据"""
    response = client.get("/api/dashboard/statistics", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200
    resp = response.json()
    assert resp["code"] == 200
    assert resp["message"] == "获取统计数据成功"
    assert "data" in resp
    data = resp["data"]
    assert "total_users" in data
    assert "total_articles" in data
    assert "total_views" in data
    assert "total_likes" in data

def test_get_chart_data(test_token):
    """测试获取图表数据"""
    response = client.get("/api/dashboard/chart", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200
    resp = response.json()
    assert resp["code"] == 200
    assert resp["message"] == "获取图表数据成功"
    assert "data" in resp
    data = resp["data"]
    assert "dates" in data
    assert "views" in data
    assert "likes" in data

def test_get_recent_activities(test_token):
    """测试获取最近活动"""
    response = client.get("/api/dashboard/activities", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200
    resp = response.json()
    assert resp["code"] == 200
    assert resp["message"] == "获取最近活动成功"
    assert "data" in resp
    data = resp["data"]
    assert isinstance(data, list)

def test_get_category_stats(test_token):
    """测试获取分类统计"""
    response = client.get("/api/dashboard/categories", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200
    resp = response.json()
    assert resp["code"] == 200
    assert resp["message"] == "获取分类统计成功"
    assert "data" in resp
    data = resp["data"]
    assert isinstance(data, list)

def test_get_system_status(test_token):
    """测试获取系统状态"""
    response = client.get("/api/dashboard/system", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200
    resp = response.json()
    assert resp["code"] == 200
    assert resp["message"] == "获取系统状态成功"
    assert "data" in resp
    data = resp["data"]
    
    # CPU信息测试
    assert "cpu_percent" in data
    assert isinstance(data["cpu_percent"], float)
    assert 0 <= data["cpu_percent"] <= 100
    
    assert "cpu_count" in data
    assert isinstance(data["cpu_count"], int)
    assert data["cpu_count"] > 0
    
    assert "cpu_freq" in data
    assert isinstance(data["cpu_freq"], float)
    assert data["cpu_freq"] >= 0
    
    # 内存信息测试
    assert "memory_percent" in data
    assert isinstance(data["memory_percent"], float)
    assert 0 <= data["memory_percent"] <= 100
    
    assert "memory_total" in data
    assert isinstance(data["memory_total"], int)
    assert data["memory_total"] > 0
    
    assert "memory_available" in data
    assert isinstance(data["memory_available"], int)
    assert data["memory_available"] >= 0
    
    assert "memory_used" in data
    assert isinstance(data["memory_used"], int)
    assert data["memory_used"] >= 0
    assert data["memory_used"] <= data["memory_total"]
    
    # 磁盘信息测试
    assert "disk_percent" in data
    assert isinstance(data["disk_percent"], float)
    assert 0 <= data["disk_percent"] <= 100
    
    assert "disk_total" in data
    assert isinstance(data["disk_total"], int)
    assert data["disk_total"] > 0
    
    assert "disk_free" in data
    assert isinstance(data["disk_free"], int)
    assert data["disk_free"] >= 0
    
    assert "disk_used" in data
    assert isinstance(data["disk_used"], int)
    assert data["disk_used"] >= 0
    assert data["disk_used"] <= data["disk_total"]
    
    # 运行时间测试
    assert "uptime_days" in data
    assert isinstance(data["uptime_days"], int)
    assert data["uptime_days"] >= 0
    
    assert "uptime_hours" in data
    assert isinstance(data["uptime_hours"], int)
    assert 0 <= data["uptime_hours"] < 24
    
    assert "uptime_minutes" in data
    assert isinstance(data["uptime_minutes"], int)
    assert 0 <= data["uptime_minutes"] < 60
    
    # 系统负载测试
    assert "load_avg_1" in data
    assert isinstance(data["load_avg_1"], float)
    assert data["load_avg_1"] >= 0
    
    assert "load_avg_5" in data
    assert isinstance(data["load_avg_5"], float)
    assert data["load_avg_5"] >= 0
    
    assert "load_avg_15" in data
    assert isinstance(data["load_avg_15"], float)
    assert data["load_avg_15"] >= 0