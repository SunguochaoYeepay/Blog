from .user import User
from .article import Article
from .category import Category
from .tag import Tag
from .comment import Comment
from .dashboard import Dashboard
from .article_relationships import ArticleTag

# 导入所有模型以确保它们被注册到Base.metadata
from app.database import Base

__all__ = [
    "User",
    "Article",
    "Category",
    "Tag",
    "Comment",
    "Dashboard",
    "ArticleTag",
    "Base"
]

# 验证所有表是否都在metadata中
all_tables = Base.metadata.tables