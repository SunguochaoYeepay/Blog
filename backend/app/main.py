from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import users, articles, categories, tags, comments, auth, upload
from app.database import Base, engine
from app.logger import app_logger
from app.schemas.response import Response
import time

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(redirect_slashes=False)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    app_logger.info(
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
    app_logger.debug("Root endpoint accessed")
    return Response(
        code=200,
        message="API is running",
        data={"status": "ok"}
    )

# 启动时记录
app_logger.info("FastAPI application started")