import pytest
from fastapi import HTTPException, UploadFile
from unittest.mock import Mock, patch
from app.services.storage import StorageService
from app.core.config import settings
import io
from starlette.datastructures import Headers

@pytest.fixture
def storage_service():
    """创建存储服务实例"""
    return StorageService()

@pytest.fixture
def mock_file():
    """创建模拟的上传文件"""
    file = UploadFile(
        filename="test.jpg",
        file=io.BytesIO(b"test content")
    )
    file.headers = Headers({"content-type": "image/jpeg"})
    return file

def test_storage_service_initialization(storage_service):
    """测试存储服务初始化"""
    assert storage_service.auth is not None
    assert storage_service.bucket_name == settings.QINIU_BUCKET_NAME
    assert storage_service.domain == settings.QINIU_DOMAIN

def test_generate_key(storage_service, mock_file):
    """测试文件名生成"""
    key = storage_service._generate_key(mock_file.filename)
    assert key.startswith("images/")
    assert key.endswith(".jpg")
    assert len(key.split("/")) == 4  # 格式: images/YYYYMM/DD/HHMMSS.jpg

def test_validate_image_valid(storage_service, mock_file):
    """测试有效图片验证"""
    # 不应该抛出异常
    storage_service._validate_image(mock_file)

def test_validate_image_invalid_type(storage_service):
    """测试无效图片类型验证"""
    invalid_file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(b"test content")
    )
    invalid_file.headers = Headers({"content-type": "text/plain"})
    
    with pytest.raises(HTTPException) as exc:
        storage_service._validate_image(invalid_file)
    assert exc.value.status_code == 400
    assert "不支持的文件类型" in str(exc.value.detail)

def test_validate_image_size_limit(storage_service):
    """测试图片大小限制验证"""
    # 创建一个超过大小限制的文件
    large_content = b"x" * (settings.MAX_FILE_SIZE + 1)
    large_file = UploadFile(
        filename="large.jpg",
        file=io.BytesIO(large_content)
    )
    large_file.headers = Headers({"content-type": "image/jpeg"})
    
    with pytest.raises(HTTPException) as exc:
        storage_service._validate_image(large_file)
    assert exc.value.status_code == 400
    assert "文件大小超过限制" in str(exc.value.detail)

@pytest.mark.asyncio
async def test_upload_image_success(storage_service, mock_file):
    """测试成功上传图片"""
    # 模拟七牛云的响应
    mock_ret = {"hash": "FakeHash"}
    mock_info = Mock(status_code=200, req_id="12345")
    
    with patch("app.services.storage.put_data", return_value=(mock_ret, mock_info)):
        result = await storage_service.upload_image(mock_file)
        
        assert result["url"].startswith(settings.QINIU_DOMAIN)
        assert result["hash"] == "FakeHash"
        assert result["mime_type"] == "image/jpeg"
        assert result["original_name"] == "test.jpg"

@pytest.mark.asyncio
async def test_upload_image_failure(storage_service, mock_file):
    """测试上传图片失败"""
    # 模拟上传失败
    mock_info = Mock(status_code=500, error="Upload failed")
    
    with patch("app.services.storage.put_data", return_value=(None, mock_info)):
        with pytest.raises(HTTPException) as exc:
            await storage_service.upload_image(mock_file)
        assert exc.value.status_code == 500
        assert "文件上传失败" in str(exc.value.detail)

@pytest.mark.asyncio
async def test_storage_service_no_config():
    """测试配置缺失情况"""
    # 模拟配置缺失
    with patch("app.services.storage.settings") as mock_settings:
        mock_settings.QINIU_ACCESS_KEY = ""
        storage = StorageService()
        assert storage.auth is None
        
        # 尝试上传应该失败
        with pytest.raises(HTTPException) as exc:
            await storage.upload_image(Mock())
        assert exc.value.status_code == 500
        assert "七牛云配置不完整" in str(exc.value.detail) 