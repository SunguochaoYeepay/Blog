import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from app.main import app
from app.database import engine
from sqlalchemy import inspect
from tests.conftest import test_engine

client = TestClient(app)

@pytest.mark.asyncio
async def test_health_check(db_session):
    """测试健康检查接口"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "version" in data
    assert "env" in data

def test_health_check_database_error(mocker):
    """测试健康检查接口在数据库错误时的行为"""
    # 模拟数据库错误
    def mock_inspect(*args, **kwargs):
        raise SQLAlchemyError("Database error")
    
    mocker.patch("app.main.inspect", mock_inspect)
    
    response = client.get("/health")
    assert response.status_code == 500
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "服务异常"
    assert "version" in data

def test_global_sqlalchemy_exception_handler():
    """测试全局 SQLAlchemy 异常处理"""
    # 创建一个会触发 SQLAlchemy 错误的测试路由
    @app.get("/test_db_error")
    async def test_db_error():
        raise SQLAlchemyError("Test database error")
    
    response = client.get("/test_db_error")
    assert response.status_code == 500
    data = response.json()
    assert data["message"] == "数据库错误"
    assert "detail" in data

def test_global_exception_handler():
    """测试全局异常处理"""
    # 创建一个会触发普通异常的测试路由
    @app.get("/test_error")
    async def test_error():
        raise ValueError("Test error")
    
    try:
        response = client.get("/test_error")
        assert response.status_code == 500
        data = response.json()
        assert data["message"] == "服务器内部错误"
        assert "detail" in data
    except ValueError:
        pytest.fail("异常应该被全局异常处理器捕获")

@pytest.fixture
async def test_app_lifespan():
    """测试应用生命周期管理"""
    async with app.router.lifespan_context(app) as lifespan:
        yield lifespan

@pytest.mark.asyncio
async def test_app_startup(test_app_lifespan):
    """测试应用启动时的行为"""
    # 验证数据库连接是否正常
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()
    assert len(tables) > 0  # 确保至少有一些表存在

def test_cors_configuration():
    """测试 CORS 配置"""
    # 发送预检请求
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers 