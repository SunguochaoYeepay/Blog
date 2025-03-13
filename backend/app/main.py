from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import users, articles
from app.database import Base, engine
from app.logger import app_logger
import time

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

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

@app.get("/")
def read_root():
    app_logger.debug("Root endpoint accessed")
    return {"Hello": "World"}

# Include routers
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(articles.router, prefix="/api", tags=["articles"])

# 启动时记录
app_logger.info("FastAPI application started") 