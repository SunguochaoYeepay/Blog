import os
import sys
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.api import users, articles, categories, tags, comments, auth, upload
from app.database import Base, engine
from app.logger import setup_logger
from app.schemas.response import Response
from app.config import settings

# 创建应用日志记录器
logger = setup_logger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blog API",
    description="博客系统后端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False
)

# 配置静态文件服务
uploads_dir = os.path.join(settings.UPLOAD_DIR)
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 配置 CORS
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["http://127.0.0.1:3000", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} "
        f"Process Time: {process_time:.2f}ms"
    )
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        if "Not authenticated" in str(exc.detail):
            message = "未提供认证凭据"
        elif "Could not validate credentials" in str(exc.detail):
            message = "无效的认证凭据"
        else:
            message = str(exc.detail)
    else:
        message = str(exc.detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=Response(
            code=exc.status_code,
            message=message,
            data=None
        ).model_dump()
    )

# 注册路由
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(articles.router, prefix="/api", tags=["articles"])
app.include_router(categories.router, prefix="/api", tags=["categories"])
app.include_router(tags.router, prefix="/api", tags=["tags"])
app.include_router(comments.router, prefix="/api", tags=["comments"])
app.include_router(upload.router, prefix="/api", tags=["upload"])

@app.get("/", response_model=Response[dict])
def read_root():
    logger.debug("Root endpoint accessed")
    return Response(
        code=200,
        message="API is running",
        data={"status": "ok"}
    )

# 启动时记录
logger.info("FastAPI application started")