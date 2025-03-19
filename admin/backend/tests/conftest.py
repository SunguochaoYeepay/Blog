import os
import sys
import pytest
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

# 添加项目根目录到 Python 路径
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app
from app.database import Base, engine, get_db
from app.models.user import User
from app.models.article import Article
from app.models.comment import Comment
from app.models.category import Category
from app.models.tag import Tag
from app.core.security import get_password_hash

# 测试数据库会话
@pytest.fixture
async def test_db():
    # 创建测试数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # 提供数据库会话
    try:
        yield
    finally:
        # 清理数据库
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

# 测试客户端
@pytest.fixture
def test_client():
    return TestClient(app)

# 异步测试客户端
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# 测试用户
@pytest.fixture
async def test_user(test_db):
    async with AsyncSession(engine) as session:
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

# 测试分类
@pytest.fixture
async def test_categories(test_db) -> List[Category]:
    categories = []
    async with AsyncSession(engine) as session:
        for i in range(3):
            category = Category(
                name=f"测试分类{i+1}",
                description=f"测试分类描述{i+1}"
            )
            session.add(category)
            categories.append(category)
        await session.commit()
        for category in categories:
            await session.refresh(category)
    return categories

# 测试标签
@pytest.fixture
async def test_tags(test_db) -> List[Tag]:
    tags = []
    async with AsyncSession(engine) as session:
        for i in range(3):
            tag = Tag(
                name=f"测试标签{i+1}"
            )
            session.add(tag)
            tags.append(tag)
        await session.commit()
        for tag in tags:
            await session.refresh(tag)
    return tags

# 测试文章
@pytest.fixture
async def test_articles(test_db, test_user, test_categories, test_tags) -> List[Article]:
    articles = []
    async with AsyncSession(engine) as session:
        for i in range(5):
            article = Article(
                title=f"测试文章{i+1}",
                content=f"测试文章内容{i+1}",
                author_id=test_user.id,
                category_id=test_categories[i % len(test_categories)].id,
                created_at=datetime.now() - timedelta(days=i)
            )
            session.add(article)
            articles.append(article)
        await session.commit()
        for article in articles:
            await session.refresh(article)
            # 添加标签
            article.tags = test_tags[:2]
            await session.commit()
    return articles

# 测试评论
@pytest.fixture
async def test_comments(test_db, test_user, test_articles) -> List[Comment]:
    comments = []
    async with AsyncSession(engine) as session:
        for i, article in enumerate(test_articles):
            comment = Comment(
                content=f"测试评论{i+1}",
                article_id=article.id,
                user_id=test_user.id,
                created_at=datetime.now() - timedelta(days=i)
            )
            session.add(comment)
            comments.append(comment)
        await session.commit()
        for comment in comments:
            await session.refresh(comment)
    return comments