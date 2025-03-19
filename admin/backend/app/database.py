from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.logger import setup_logger
import time

logger = setup_logger(__name__)

# 使用配置中的数据库 URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

def create_db_engine(max_retries=3, retry_delay=1):
    """创建数据库引擎，带重试机制"""
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                echo=True,  # 启用 SQL 日志
                pool_pre_ping=True,  # 自动检测断开的连接
                pool_recycle=3600,  # 一小时后回收连接
                pool_size=5,  # 连接池大小
                max_overflow=10  # 最大溢出连接数
            )
            # 测试连接
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"成功连接到数据库：{SQLALCHEMY_DATABASE_URL}")
            return engine
        except Exception as e:
            logger.warning(f"数据库连接尝试 {attempt + 1} 失败：{str(e)}")
            if attempt == max_retries - 1:
                logger.error(f"数据库连接失败，已重试 {max_retries} 次")
                raise
            time.sleep(retry_delay)

engine = create_db_engine()
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