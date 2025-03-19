from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import json
import os

class Settings(BaseSettings):
    """应用配置"""
    # 环境配置
    ENV: str = os.getenv("ENV", "dev")  # 默认为开发环境
    
    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str
    
    # MySQL settings
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_DATABASE: str
    
    # JWT配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 上传文件配置
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: List[str]
    ALLOWED_DOCUMENT_TYPES: List[str]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_EXPIRE_IN_SECONDS: int = 3600  # 1小时
    
    # 日志配置
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str
    
    # CORS配置
    CORS_ORIGINS: List[str]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # 七牛云配置
    QINIU_ACCESS_KEY: str
    QINIU_SECRET_KEY: str
    QINIU_BUCKET_NAME: str
    QINIU_DOMAIN: str  # 例如：http://cdn.example.com
    QINIU_BUCKET_DOMAIN: str  # 例如：http://bucket.u.qiniucs.com
    QINIU_CALLBACK_URL: Optional[str] = None  # 上传回调地址
    
    # 模型配置
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV', 'dev')}",  # 根据环境变量选择配置文件
        case_sensitive=True,
        env_file_encoding='utf-8'
    )
    
    def model_post_init(self, *args, **kwargs):
        """后处理配置值"""
        # 处理字符串形式的列表
        if isinstance(self.CORS_ORIGINS, str):
            try:
                self.CORS_ORIGINS = json.loads(self.CORS_ORIGINS)
            except json.JSONDecodeError:
                self.CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS.strip('[]').split(',')]
        
        if isinstance(self.ALLOWED_IMAGE_TYPES, str):
            try:
                self.ALLOWED_IMAGE_TYPES = json.loads(self.ALLOWED_IMAGE_TYPES)
            except json.JSONDecodeError:
                self.ALLOWED_IMAGE_TYPES = [t.strip() for t in self.ALLOWED_IMAGE_TYPES.strip('[]').split(',')]
        
        if isinstance(self.ALLOWED_DOCUMENT_TYPES, str):
            try:
                self.ALLOWED_DOCUMENT_TYPES = json.loads(self.ALLOWED_DOCUMENT_TYPES)
            except json.JSONDecodeError:
                self.ALLOWED_DOCUMENT_TYPES = [t.strip() for t in self.ALLOWED_DOCUMENT_TYPES.strip('[]').split(',')]

settings = Settings()