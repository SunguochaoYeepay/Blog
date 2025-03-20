import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import asyncio
from app.core.config import settings
from app.database import engine, Base
from app.api import users, articles, categories, tags, comments, auth, upload, dashboard

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
async def init_db():
    if os.getenv("TESTING") == "1":
        # 测试环境使用同步方式
        Base.metadata.create_all(bind=engine)
    else:
        # 生产环境使用异步方式
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

# 启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    await init_db()
    logger.info("FastAPI application started")

# 包含路由
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(articles.router, prefix=settings.API_V1_STR)
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(tags.router, prefix=settings.API_V1_STR)
app.include_router(comments.router, prefix=settings.API_V1_STR)
app.include_router(upload.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 全局异常处理
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "数据库错误"},
    )

# 关闭事件
@app.on_event("shutdown")
async def shutdown():
    # 关闭数据库连接
    if not os.getenv("TESTING"):
        await engine.dispose()
    logger.info("FastAPI application shutdown")