from redis import Redis
from fastapi import Depends
from ..config import settings
import json
from typing import Optional, Any, Dict
from datetime import timedelta, datetime

# Redis 客户端实例
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

# 缓存键前缀
USER_PREFIX = "user:"
ARTICLE_PREFIX = "article:"
COMMENT_PREFIX = "comment:"
ARTICLE_VIEW_COUNT = "article_views:"
ARTICLE_LIKE_COUNT = "article_likes:"
COMMENT_LIKE_PREFIX = "comment_like:"
COMMENT_LIKE_COUNT_PREFIX = "comment_like_count:"

# 缓存过期时间（秒）
USER_CACHE_TTL = 3600    # 1小时
ARTICLE_CACHE_TTL = 3600  # 1小时
COMMENT_CACHE_TTL = 3600  # 1小时
VIEW_COUNT_TTL = 86400  # 24小时

class DateTimeEncoder(json.JSONEncoder):
    """处理 datetime 对象的 JSON 编码器"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def get_redis() -> Redis:
    """获取 Redis 连接"""
    try:
        redis_client.ping()
        return redis_client
    except Exception as e:
        raise Exception(f"Redis connection error: {str(e)}")

def add_token_to_blacklist(token: str, expires_in: int):
    """将令牌添加到黑名单"""
    redis_client.setex(f"blacklist_token:{token}", expires_in, "1")

def is_token_blacklisted(token: str) -> bool:
    """检查令牌是否在黑名单中"""
    return bool(redis_client.exists(f"blacklist_token:{token}"))

# 用户缓存相关方法
def cache_user(user_id: int, user_data: dict):
    """缓存用户信息"""
    key = f"{USER_PREFIX}{user_id}"
    redis_client.setex(key, USER_CACHE_TTL, json.dumps(user_data))

def get_cached_user(user_id: int) -> Optional[dict]:
    """获取缓存的用户信息"""
    key = f"{USER_PREFIX}{user_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else None

def delete_user_cache(user_id: int):
    """删除用户缓存"""
    key = f"{USER_PREFIX}{user_id}"
    redis_client.delete(key)

# 文章缓存相关方法
def cache_article(article_id: int, article_data: dict):
    """缓存文章信息"""
    key = f"{ARTICLE_PREFIX}{article_id}"
    redis_client.setex(key, ARTICLE_CACHE_TTL, json.dumps(article_data, cls=DateTimeEncoder))

def get_cached_article(article_id: int) -> Optional[dict]:
    """获取缓存的文章信息"""
    key = f"{ARTICLE_PREFIX}{article_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else None

def delete_article_cache(article_id: int):
    """删除文章缓存"""
    key = f"{ARTICLE_PREFIX}{article_id}"
    redis_client.delete(key)

def increment_article_view(article_id: int):
    """增加文章浏览次数"""
    key = f"{ARTICLE_VIEW_COUNT}{article_id}"
    if not redis_client.exists(key):
        redis_client.setex(key, VIEW_COUNT_TTL, 1)
    else:
        redis_client.incr(key)

def get_article_views(article_id: int) -> int:
    """获取文章浏览次数"""
    key = f"{ARTICLE_VIEW_COUNT}{article_id}"
    views = redis_client.get(key)
    return int(views) if views else 0

def toggle_article_like(article_id: int, user_id: int) -> bool:
    """切换文章点赞状态，返回是否点赞"""
    key = f"{ARTICLE_LIKE_COUNT}{article_id}"
    if redis_client.sismember(key, user_id):
        redis_client.srem(key, user_id)
        return False
    redis_client.sadd(key, user_id)
    return True

def get_article_likes(article_id: int) -> int:
    """获取文章点赞数"""
    key = f"{ARTICLE_LIKE_COUNT}{article_id}"
    return redis_client.scard(key)

# 评论缓存相关方法
def cache_comment(comment_id: int, comment_data: Dict[str, Any]) -> None:
    """缓存评论数据"""
    try:
        key = f"{COMMENT_PREFIX}{comment_id}"
        redis_client.setex(key, COMMENT_CACHE_TTL, json.dumps(comment_data, cls=DateTimeEncoder))
    except Exception as e:
        # 记录错误但不中断程序
        print(f"Error caching comment: {e}")

def get_cached_comment(comment_id: int) -> Optional[dict]:
    """获取缓存的评论数据"""
    try:
        key = f"{COMMENT_PREFIX}{comment_id}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        print(f"Error getting cached comment: {e}")
    return None

def delete_comment_cache(comment_id: int) -> None:
    """删除评论缓存"""
    try:
        key = f"{COMMENT_PREFIX}{comment_id}"
        redis_client.delete(key)
    except Exception as e:
        print(f"Error deleting comment cache: {e}")

def toggle_comment_like(comment_id: int, user_id: int) -> bool:
    """切换评论点赞状态"""
    try:
        key = f"{COMMENT_LIKE_COUNT_PREFIX}{comment_id}"
        if redis_client.sismember(key, user_id):
            redis_client.srem(key, user_id)
            return False
        redis_client.sadd(key, user_id)
        return True
    except Exception as e:
        print(f"Error toggling comment like: {e}")
        return False

def get_comment_likes(comment_id: int) -> int:
    """获取评论点赞数"""
    try:
        key = f"{COMMENT_LIKE_COUNT_PREFIX}{comment_id}"
        return redis_client.scard(key)
    except Exception as e:
        print(f"Error getting comment likes: {e}")
        return 0

def is_comment_liked_by_user(comment_id: int, user_id: int) -> bool:
    """检查用户是否已点赞评论"""
    try:
        key = f"{COMMENT_LIKE_COUNT_PREFIX}{comment_id}"
        return redis_client.sismember(key, user_id)
    except Exception as e:
        print(f"Error checking comment like status: {e}")
        return False

# 批量操作方法
def cache_multiple_articles(articles: list[dict], prefix: str = "recent"):
    """缓存多篇文章（如最近文章、热门文章等）"""
    key = f"{ARTICLE_PREFIX}{prefix}"
    redis_client.setex(key, ARTICLE_CACHE_TTL, json.dumps(articles, cls=DateTimeEncoder))

def get_cached_multiple_articles(prefix: str = "recent") -> Optional[list]:
    """获取缓存的多篇文章"""
    key = f"{ARTICLE_PREFIX}{prefix}"
    data = redis_client.get(key)
    return json.loads(data) if data else None

def clear_comment_likes():
    """清理评论点赞数据"""
    try:
        # 获取所有评论点赞相关的键
        keys = redis_client.keys(f"{COMMENT_LIKE_COUNT_PREFIX}*")
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        print(f"Error clearing comment likes: {e}")

def clear_article_likes():
    """清理文章点赞数据"""
    try:
        # 获取所有文章点赞相关的键
        keys = redis_client.keys(f"{ARTICLE_LIKE_COUNT}*")
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        print(f"Error clearing article likes: {e}")

def clear_all_likes():
    """清理所有点赞数据"""
    clear_comment_likes()
    clear_article_likes() 