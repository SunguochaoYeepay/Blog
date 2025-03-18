-- Active: 1741598341111@@127.0.0.1@3306
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag
from app.core.security import get_password_hash

def init_db(db: Session):
    # 创建管理员用户
    admin = User(
        username="admin",
        email="admin@example.com",
        full_name="System Administrator",
        department="IT",
        role="admin",
        hashed_password=get_password_hash("admin"),
        is_active=True
    )
    db.add(admin)
    
    # 创建普通用户
    user = User(
        username="user",
        email="user@example.com",
        full_name="Normal User",
        department="Marketing",
        role="user",
        hashed_password=get_password_hash("user123"),
        is_active=True
    )
    db.add(user)
    
    # 创建分类
    categories = [
        Category(name="Technology", slug="technology", description="Technology related articles"),
        Category(name="Marketing", slug="marketing", description="Marketing related articles"),
        Category(name="Design", slug="design", description="Design related articles")
    ]
    for category in categories:
        db.add(category)
    
    # 创建标签
    tags = [
        Tag(name="Python", slug="python", description="Python programming"),
        Tag(name="Web", slug="web", description="Web development"),
        Tag(name="UI/UX", slug="ui-ux", description="User Interface and Experience"),
        Tag(name="SEO", slug="seo", description="Search Engine Optimization")
    ]
    for tag in tags:
        db.add(tag)
    
    # 提交以获取ID
    db.commit()
    
    # 创建文章
    articles = [
        Article(
            title="Getting Started with FastAPI",
            slug="getting-started-with-fastapi",
            content="FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.6+ based on standard Python type hints.",
            summary="A beginner's guide to FastAPI",
            meta_title="FastAPI Tutorial - Getting Started Guide",
            meta_description="Learn how to build high-performance APIs with FastAPI",
            keywords="fastapi,python,api,web development",
            status="published",
            is_featured=True,
            author_id=admin.id,
            published_at=datetime.utcnow()
        ),
        Article(
            title="Modern Web Design Principles",
            slug="modern-web-design-principles",
            content="Modern web design is all about creating user-friendly, responsive, and accessible websites.",
            summary="Essential principles of modern web design",
            meta_title="Web Design Principles for Modern Websites",
            meta_description="Learn about modern web design principles and best practices",
            keywords="web design,ui,ux,responsive design",
            status="published",
            author_id=user.id,
            published_at=datetime.utcnow()
        )
    ]
    
    for article in articles:
        # 添加分类和标签
        if "FastAPI" in article.title:
            article.categories.append(categories[0])  # Technology
            article.tags.extend([tags[0], tags[1]])  # Python, Web
        else:
            article.categories.append(categories[2])  # Design
            article.tags.extend([tags[2], tags[3]])  # UI/UX, SEO
        db.add(article)
    
    # 最终提交
    db.commit()
    
    return {"message": "Initial data created successfully"}

if __name__ == "__main__":
    print("开始初始化数据...")
    init_db()
    print("数据初始化完成！") 