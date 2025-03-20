import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # 使用 0.0.0.0 允许外部访问
        port=8000,  # 使用固定端口
        reload=True  # 开发环境启用热重载
    )