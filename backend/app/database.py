from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# 使用配置中的数据库 URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=True,  # 启用 SQL 日志
        pool_pre_ping=True  # 自动检测断开的连接
    )
    logger.info(f"成功连接到数据库：{SQLALCHEMY_DATABASE_URL}")
except Exception as e:
    logger.error(f"数据库连接失败：{str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库表创建失败：{str(e)}")
        raise