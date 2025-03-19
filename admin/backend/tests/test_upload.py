import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
from app.database import get_db
from app.api.auth import create_access_token, get_password_hash
from datetime import datetime
from tests.test_config import override_get_db, init_test_db, cleanup_test_db
from qiniu import Auth, put_data
from app.config import settings
from PIL import Image
from io import BytesIO
import requests

# 替换应用程序的数据库依赖
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 测试数据
test_image_content = b"fake image content"
test_document_content = b"fake document content"

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

def test_upload_image(admin_token: str):
    """测试上传图片文件"""
    files = {
        "file": ("test.jpg", test_image_content, "image/jpeg")
    }
    response = client.post(
        "/api/upload",
        files=files,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 201
    assert data["message"] == "文件上传成功"
    assert "filename" in data["data"]
    assert "file_type" in data["data"]
    assert "file_size" in data["data"]
    assert data["data"]["file_type"] == "image"
    
    # 清理上传的文件
    if "file_path" in data["data"] and os.path.exists(data["data"]["file_path"]):
        os.remove(data["data"]["file_path"])

def test_upload_document(admin_token: str):
    """测试上传文档文件"""
    files = {
        "file": ("test.pdf", test_document_content, "application/pdf")
    }
    response = client.post(
        "/api/upload",
        files=files,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 201
    assert data["message"] == "文件上传成功"
    assert "filename" in data["data"]
    assert "file_type" in data["data"]
    assert "file_size" in data["data"]
    assert data["data"]["file_type"] == "document"
    
    # 清理上传的文件
    if "file_path" in data["data"] and os.path.exists(data["data"]["file_path"]):
        os.remove(data["data"]["file_path"])

def test_upload_unauthorized():
    """测试未授权上传文件"""
    files = {
        "file": ("test.jpg", test_image_content, "image/jpeg")
    }
    response = client.post("/api/upload", files=files)
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 401

def test_upload_invalid_file_type(admin_token: str):
    """测试上传不支持的文件类型"""
    files = {
        "file": ("test.xyz", b"invalid content", "application/xyz")
    }
    response = client.post(
        "/api/upload",
        files=files,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "不支持的文件类型" in data["message"]

def test_upload_empty_file(admin_token: str):
    """测试上传空文件"""
    files = {
        "file": ("test.jpg", b"", "image/jpeg")
    }
    response = client.post(
        "/api/upload",
        files=files,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "文件内容为空" in data["message"]

def test_upload_to_qiniu(admin_token: str):
    """测试上传图片到七牛云"""
    # 创建测试图片
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # 构造文件上传请求
    files = {
        "file": ("test.png", img_byte_arr, "image/png")
    }
    response = client.post(
        "/api/upload",
        files=files,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 201
    assert data["message"] == "文件上传成功"
    assert "url" in data["data"]
    
    # 验证图片是否可以访问
    image_url = data["data"]["url"]
    print(f"\nImage URL: {image_url}\n")  # 打印图片 URL
    img_response = requests.get(image_url, verify=False)  # 禁用 SSL 证书验证
    assert img_response.status_code == 200

def test_qiniu_config():
    """测试七牛云配置是否正确"""
    assert settings.QINIU_ACCESS_KEY
    assert settings.QINIU_SECRET_KEY
    assert settings.QINIU_BUCKET_NAME
    assert settings.QINIU_DOMAIN
    
    # 测试鉴权是否正确
    q = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
    token = q.upload_token(settings.QINIU_BUCKET_NAME)
    assert token 