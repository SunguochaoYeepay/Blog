from datetime import datetime
from typing import Any, Dict, Optional

import factory
from factory import LazyAttribute, Sequence
from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.article import Article
from app.models.category import Category
from app.models.comment import Comment
from app.models.tag import Tag
from app.models.user import User
from app.utils.slug import slugify

class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""
    
    class Meta:
        abstract = True
        sqlalchemy_session = None

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> Any:
        """Create an instance of the model, and save it to the database."""
        session: Optional[Session] = kwargs.pop("session", None)
        if session is None:
            raise ValueError("Session is required")
        obj = model_class(*args, **kwargs)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

class UserFactory(BaseFactory):
    """User factory."""
    
    class Meta:
        model = User
        sqlalchemy_session = None

    username = Sequence(lambda n: f"test_user_{n}")
    email = LazyAttribute(lambda obj: f"{obj.username}@example.com")
    hashed_password = LazyAttribute(lambda _: get_password_hash("password123"))
    full_name = factory.Faker("name")
    department = factory.Faker("company")
    role = "user"
    is_active = True
    is_superuser = False
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")

class CategoryFactory(BaseFactory):
    """Category factory."""
    
    class Meta:
        model = Category
        sqlalchemy_session = None

    name = factory.Faker("word")
    description = factory.Faker("text")
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")

class TagFactory(BaseFactory):
    """Tag factory."""
    
    class Meta:
        model = Tag
        sqlalchemy_session = None

    name = factory.Faker("word")
    description = factory.Faker("text")
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")

class ArticleFactory(BaseFactory):
    """Article factory."""
    
    class Meta:
        model = Article
        sqlalchemy_session = None

    title = Sequence(lambda n: f"test_article_{n}")
    slug = LazyAttribute(lambda obj: slugify(obj.title))
    content = factory.Faker("text")
    summary = factory.Faker("text")
    meta_title = None
    meta_description = None
    keywords = None
    status = "draft"
    is_featured = False
    allow_comments = True
    is_published = True
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
    published_at = None
    view_count = 0
    comment_count = 0
    like_count = 0

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        """Add categories to the article."""
        if not create:
            return

        if extracted:
            for category in extracted:
                self.categories.append(category)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags to the article."""
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.append(tag)

class CommentFactory(BaseFactory):
    """Comment factory."""
    
    class Meta:
        model = Comment
        sqlalchemy_session = None

    content = factory.Faker("text")
    is_approved = True
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")