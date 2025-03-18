from functools import wraps
from app.models.user import User
from app.config import settings
import redis
import json
from typing import Callable
import logging

# 创建Redis连接
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

def cache_user(func: Callable):
    """
    用户信息缓存装饰器
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 获取用户ID
        user_id = kwargs.get('user_id')
        if not user_id:
            return await func(*args, **kwargs)

        # 尝试从缓存获取用户信息
        cache_key = f"user:{user_id}"
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logging.error(f"Redis cache error: {str(e)}")
            return await func(*args, **kwargs)

        # 如果缓存中没有，执行原函数
        result = await func(*args, **kwargs)
        
        # 将结果存入缓存
        try:
            if result:
                redis_client.setex(
                    cache_key,
                    settings.CACHE_EXPIRE_IN_SECONDS,
                    json.dumps(result)
                )
        except Exception as e:
            logging.error(f"Redis cache error: {str(e)}")

        return result

    return wrapper
