from functools import wraps
from app.models.user import User
from app.core.config import settings
from redis import Redis
from typing import Callable, Any, Optional
import json
import logging

class RedisCache:
    def __init__(self):
        self.client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    def set(self, key: str, value: Any, expire: int = None) -> bool:
        """设置缓存"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            if expire:
                return self.client.setex(key, expire, value)
            return self.client.set(key, value)
        except Exception as e:
            logging.error(f"Redis set error: {str(e)}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logging.error(f"Redis get error: {str(e)}")
            return None

    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logging.error(f"Redis delete error: {str(e)}")
            return False

    def clear(self) -> bool:
        """清空缓存"""
        try:
            return bool(self.client.flushdb())
        except Exception as e:
            logging.error(f"Redis clear error: {str(e)}")
            return False

# 创建Redis连接
redis_client = Redis(
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