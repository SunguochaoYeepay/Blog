import logging
import os
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 首先导入配置
from app.core.config import settings

# 然后导入数据库
from app.database import engine, Base, SessionLocal

# 导入模型
from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.dashboard import Dashboard
from app.models.article_relationships import ArticleTag

# 最后导入其他依赖
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect

# 导入路由
from app.api import users, articles, categories, tags, comments, auth, dashboard, upload

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        logger.info("FastAPI application started")
        yield
    finally:
        logger.info("FastAPI application shutdown")

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["认证"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["用户"])
app.include_router(articles.router, prefix=f"{settings.API_V1_STR}/articles", tags=["文章"])
app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["分类"])
app.include_router(tags.router, prefix=f"{settings.API_V1_STR}/tags", tags=["标签"])
app.include_router(comments.router, prefix=f"{settings.API_V1_STR}/comments", tags=["评论"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["仪表盘"])
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/upload", tags=["上传"])

# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        inspector = inspect(engine)
        inspector.get_table_names()
        return {
            "status": "ok",
            "database": "connected",
            "version": settings.VERSION,
            "env": settings.ENV
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "服务异常",
                "version": settings.VERSION,
                "detail": str(e) if settings.DEBUG else None
            }
        )

# 全局异常处理
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """数据库异常处理器"""
    error_msg = str(exc)
    logger.error(f"数据库错误: {error_msg}")
    logger.error(f"请求路径: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "数据库错误",
            "detail": error_msg if settings.DEBUG else None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    error_msg = str(exc)
    logger.error(f"未处理的异常: {error_msg}")
    logger.error(f"请求路径: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "服务器内部错误",
            "detail": error_msg if settings.DEBUG else None
        }
    )