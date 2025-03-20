import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.database import engine, Base
from app.api import users, articles, categories, tags, comments, auth, upload, dashboard

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化数据库
def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建成功")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    init_db()
    logger.info("FastAPI application started")
    yield
    # 关闭时执行
    engine.dispose()
    logger.info("FastAPI application shutdown")

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth")
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users")
app.include_router(articles.router, prefix=f"{settings.API_V1_STR}/articles")
app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories")
app.include_router(tags.router, prefix=f"{settings.API_V1_STR}/tags")
app.include_router(comments.router, prefix=f"{settings.API_V1_STR}/comments")
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/upload")
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard")

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 全局异常处理
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"message": "数据库错误"}
    )