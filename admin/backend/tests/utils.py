from app.core.config import settings

def get_api_path(path: str) -> str:
    """
    获取完整的API路径
    """
    return f"{settings.API_V1_STR}{path}"