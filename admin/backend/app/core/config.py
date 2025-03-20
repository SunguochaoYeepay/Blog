from typing import List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, validator
from pydantic_settings import BaseSettings
import json
import os

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "Blog Admin"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key"  # 在生产环境中应该使用环境变量
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置
    DATABASE_URL: str = ""
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_HOST: str = ""
    MYSQL_PORT: str = "3306"
    MYSQL_DATABASE: str = ""
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_EXPIRE_IN_SECONDS: int = 3600
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_ORIGINS: str = '["http://127.0.0.1:3000", "http://localhost:3000", "http://localhost:8080"]'
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # 上传文件配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif"]
    ALLOWED_IMAGE_TYPES: str = '["image/jpeg", "image/png", "image/gif"]'
    ALLOWED_DOCUMENT_TYPES: str = '["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]'
    
    # 日志配置
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 邮件配置
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @property
    def cors_origins(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)
    
    @property
    def allowed_image_types(self) -> List[str]:
        return json.loads(self.ALLOWED_IMAGE_TYPES)
    
    @property
    def allowed_document_types(self) -> List[str]:
        return json.loads(self.ALLOWED_DOCUMENT_TYPES)
    
    def model_post_init(self, __context) -> None:
        # 处理 DATABASE_URL
        # 1. 优先使用环境变量中的 DATABASE_URL
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            self.DATABASE_URL = database_url
            return

        # 2. 如果是测试模式，使用 SQLite
        test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        if test_mode:
            self.DATABASE_URL = "sqlite:///./test.db"
            return

        # 3. 如果提供了 MySQL 配置，则构建 DATABASE_URL
        if all(getattr(self, key, "") != "" for key in ["MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_HOST", "MYSQL_DATABASE"]):
            self.DATABASE_URL = f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            return

        # 4. 最后使用默认的 SQLite
        self.DATABASE_URL = "sqlite:///./blog.db"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()