"""统一的错误码定义"""
from typing import Dict, Any

class ErrorCode:
    """错误码定义"""
    SUCCESS = 200  # 成功
    PARAM_ERROR = 400  # 参数错误
    UNAUTHORIZED = 401  # 未授权
    FORBIDDEN = 403  # 禁止访问
    NOT_FOUND = 404  # 资源不存在
    SERVER_ERROR = 500  # 服务器错误

def success(data: Any = None, message: str = "success") -> Dict[str, Any]:
    """成功响应"""
    return {
        "code": ErrorCode.SUCCESS,
        "message": message,
        "data": data
    }

def error(code: int = ErrorCode.SERVER_ERROR, message: str = "error", data: Any = None) -> Dict[str, Any]:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    } 