from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # MySQL settings
    mysql_user: str
    mysql_password: str
    mysql_host: str
    mysql_port: str
    mysql_database: str
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key"  # 在生产环境中应该使用环境变量
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 上传文件配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: set = {"image/jpeg", "image/png", "image/gif"}
    ALLOWED_DOCUMENT_TYPES: set = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings() 