import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory import Sequence, LazyAttribute
from app.models.user import User
from app.models.article import Article
from app.core.security import get_password_hash
from app.utils.slug import slugify

class BaseFactory(SQLAlchemyModelFactory):
    """基础工厂类"""
    class Meta:
        abstract = True
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

class UserFactory(BaseFactory):
    """用户工厂类"""
    class Meta:
        model = User
        sqlalchemy_session = None

    username = Sequence(lambda n: f"test_user_{n}")
    email = Sequence(lambda n: f"test{n}@example.com")
    hashed_password = LazyAttribute(lambda _: get_password_hash("password123"))
    full_name = Sequence(lambda n: f"Test User {n}")
    is_active = True
    is_superuser = False
    department = "测试部门"
    role = "测试角色"

class ArticleFactory(BaseFactory):
    """文章工厂类"""
    class Meta:
        model = Article
        sqlalchemy_session = None

    title = Sequence(lambda n: f"test_article_{n}")
    content = "Test content"
    summary = "Test summary"
    meta_title = LazyAttribute(lambda obj: obj.title)
    meta_description = "Test meta description"
    keywords = "test,article"
    status = "draft"
    is_featured = False
    allow_comments = True
    is_published = False
    slug = LazyAttribute(lambda obj: slugify(obj.title))
    author_id = factory.SelfAttribute('author.id')
    author = factory.SubFactory(UserFactory)