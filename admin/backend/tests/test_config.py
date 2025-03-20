import os
import pytest
from app.core.config import Settings

def test_default_settings():
    settings = Settings()
    assert settings.PROJECT_NAME == "Blog Admin"
    assert settings.VERSION == "0.1.0"
    assert settings.API_V1_STR == "/api"

def test_cors_origins_parsing():
    settings = Settings()
    assert isinstance(settings.cors_origins, list)
    assert len(settings.cors_origins) > 0
    assert all(isinstance(origin, str) for origin in settings.cors_origins)

def test_env_override():
    os.environ["PROJECT_NAME"] = "Test Project"
    settings = Settings()
    assert settings.PROJECT_NAME == "Test Project"
    del os.environ["PROJECT_NAME"]

def test_database_url_mysql_config():
    # 保存原始环境变量
    original_database_url = os.environ.get("DATABASE_URL")
    original_test_mode = os.environ.get("TEST_MODE")
    
    try:
        # 清理环境变量
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        os.environ["TEST_MODE"] = "false"
        
        # 使用构造函数参数
        settings = Settings(
            MYSQL_USER="testuser",
            MYSQL_PASSWORD="testpass",
            MYSQL_HOST="testhost",
            MYSQL_PORT="3307",
            MYSQL_DATABASE="testdb"
        )
        assert settings.DATABASE_URL == "mysql+pymysql://testuser:testpass@testhost:3307/testdb"
    finally:
        # 恢复环境变量
        if original_database_url:
            os.environ["DATABASE_URL"] = original_database_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
            
        if original_test_mode:
            os.environ["TEST_MODE"] = original_test_mode
        elif "TEST_MODE" in os.environ:
            del os.environ["TEST_MODE"]

def test_database_url_env_override():
    # 保存原始环境变量
    original_database_url = os.environ.get("DATABASE_URL")
    original_test_mode = os.environ.get("TEST_MODE")
    
    try:
        # 清理环境变量
        if "TEST_MODE" in os.environ:
            del os.environ["TEST_MODE"]
        os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
        
        settings = Settings()
        assert settings.DATABASE_URL == "postgresql://user:pass@localhost:5432/db"
    finally:
        # 恢复环境变量
        if original_database_url:
            os.environ["DATABASE_URL"] = original_database_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
            
        if original_test_mode:
            os.environ["TEST_MODE"] = original_test_mode
        elif "TEST_MODE" in os.environ:
            del os.environ["TEST_MODE"]

def test_test_mode_database_url():
    # 保存原始环境变量
    original_database_url = os.environ.get("DATABASE_URL")
    original_test_mode = os.environ.get("TEST_MODE")
    
    try:
        # 清理环境变量
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        os.environ["TEST_MODE"] = "true"
        
        settings = Settings()
        assert settings.DATABASE_URL == "sqlite:///./test.db"
    finally:
        # 恢复环境变量
        if original_database_url:
            os.environ["DATABASE_URL"] = original_database_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
            
        if original_test_mode:
            os.environ["TEST_MODE"] = original_test_mode
        elif "TEST_MODE" in os.environ:
            del os.environ["TEST_MODE"]

def test_allowed_file_types():
    settings = Settings()
    assert isinstance(settings.allowed_image_types, list)
    assert isinstance(settings.allowed_document_types, list)
    assert len(settings.allowed_image_types) > 0
    assert len(settings.allowed_document_types) > 0